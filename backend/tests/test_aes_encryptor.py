"""
Unit tests for AES Encryptor Service

Tests encryption, decryption, key derivation, and error handling.
"""

import pytest
from backend.services.aes_encryptor import AESEncryptor


class TestAESEncryptor:
    """Test suite for AESEncryptor class"""
    
    @pytest.fixture
    def encryptor(self):
        """Create an AESEncryptor instance with test server secret"""
        return AESEncryptor("test_server_secret_32_bytes_long!!")
    
    @pytest.fixture
    def phone_hash(self):
        """Sample phone hash for testing"""
        return "0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    
    def test_init_with_valid_secret(self):
        """Test initialization with valid server secret"""
        encryptor = AESEncryptor("valid_secret_32_bytes_or_more!!!")
        assert encryptor.server_secret == b"valid_secret_32_bytes_or_more!!!"
    
    def test_init_with_short_secret(self):
        """Test initialization fails with short server secret"""
        with pytest.raises(ValueError, match="at least 32 bytes"):
            AESEncryptor("short")
    
    def test_init_with_empty_secret(self):
        """Test initialization fails with empty server secret"""
        with pytest.raises(ValueError, match="at least 32 bytes"):
            AESEncryptor("")
    
    def test_derive_key_returns_32_bytes(self, encryptor, phone_hash):
        """Test key derivation returns 32-byte key for AES-256"""
        key = encryptor.derive_key(phone_hash)
        assert len(key) == 32
        assert isinstance(key, bytes)
    
    def test_derive_key_with_0x_prefix(self, encryptor):
        """Test key derivation handles phone hash with 0x prefix"""
        phone_hash = "0xabc123"
        key = encryptor.derive_key(phone_hash)
        assert len(key) == 32
    
    def test_derive_key_without_0x_prefix(self, encryptor):
        """Test key derivation handles phone hash without 0x prefix"""
        phone_hash = "abc123"
        key = encryptor.derive_key(phone_hash)
        assert len(key) == 32
    
    def test_derive_key_deterministic(self, encryptor, phone_hash):
        """Test key derivation is deterministic for same inputs"""
        key1 = encryptor.derive_key(phone_hash)
        key2 = encryptor.derive_key(phone_hash)
        assert key1 == key2
    
    def test_derive_key_different_for_different_phones(self, encryptor):
        """Test different phone hashes produce different keys"""
        key1 = encryptor.derive_key("0xabc123")
        key2 = encryptor.derive_key("0xdef456")
        assert key1 != key2
    
    def test_encrypt_returns_tuple(self, encryptor, phone_hash):
        """Test encrypt returns (encrypted_data, iv) tuple"""
        plaintext = b"Medical report data"
        result = encryptor.encrypt(plaintext, phone_hash)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        encrypted_data, iv = result
        assert isinstance(encrypted_data, bytes)
        assert isinstance(iv, bytes)
    
    def test_encrypt_iv_is_16_bytes(self, encryptor, phone_hash):
        """Test IV is 16 bytes (AES block size)"""
        plaintext = b"Medical report data"
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        assert len(iv) == 16
    
    def test_encrypt_produces_different_iv_each_time(self, encryptor, phone_hash):
        """Test unique IV is generated for each encryption"""
        plaintext = b"Medical report data"
        
        encrypted1, iv1 = encryptor.encrypt(plaintext, phone_hash)
        encrypted2, iv2 = encryptor.encrypt(plaintext, phone_hash)
        
        # IVs should be different
        assert iv1 != iv2
        # Ciphertexts should be different due to different IVs
        assert encrypted1 != encrypted2
    
    def test_encrypt_produces_ciphertext(self, encryptor, phone_hash):
        """Test encryption produces ciphertext different from plaintext"""
        plaintext = b"Medical report data"
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        
        # Ciphertext should be different from plaintext
        assert encrypted_data != plaintext
        # Ciphertext should not be empty
        assert len(encrypted_data) > 0
    
    def test_decrypt_recovers_plaintext(self, encryptor, phone_hash):
        """Test decryption recovers original plaintext (round-trip property)"""
        plaintext = b"Medical report data"
        
        # Encrypt
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted_data, iv, phone_hash)
        
        # Should recover original plaintext
        assert decrypted == plaintext
    
    def test_decrypt_with_wrong_key_fails(self, encryptor):
        """Test decryption fails with incorrect phone hash (wrong key)"""
        plaintext = b"Medical report data"
        phone_hash1 = "0xabc123"
        phone_hash2 = "0xdef456"
        
        # Encrypt with phone_hash1
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash1)
        
        # Try to decrypt with phone_hash2 (wrong key)
        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor.decrypt(encrypted_data, iv, phone_hash2)
    
    def test_decrypt_with_corrupted_ciphertext_fails(self, encryptor, phone_hash):
        """Test decryption fails with corrupted ciphertext"""
        plaintext = b"Medical report data"
        
        # Encrypt
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        
        # Corrupt the ciphertext
        corrupted = encrypted_data[:-1] + b'\x00'
        
        # Decryption should fail
        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor.decrypt(corrupted, iv, phone_hash)
    
    def test_decrypt_with_wrong_iv_fails(self, encryptor, phone_hash):
        """Test decryption fails with incorrect IV"""
        plaintext = b"Medical report data"
        
        # Encrypt
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        
        # Use wrong IV (all zeros)
        wrong_iv = b'\x00' * 16
        
        # Decryption should fail (either ValueError or produce wrong plaintext)
        try:
            decrypted = encryptor.decrypt(encrypted_data, wrong_iv, phone_hash)
            # If decryption succeeds, the plaintext should be different
            assert decrypted != plaintext, "Decryption with wrong IV should not produce correct plaintext"
        except ValueError:
            # This is the expected behavior - decryption fails
            pass
    
    def test_round_trip_with_empty_data(self, encryptor, phone_hash):
        """Test encryption/decryption round-trip with empty data"""
        plaintext = b""
        
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        decrypted = encryptor.decrypt(encrypted_data, iv, phone_hash)
        
        assert decrypted == plaintext
    
    def test_round_trip_with_large_data(self, encryptor, phone_hash):
        """Test encryption/decryption round-trip with large data"""
        # Create a large plaintext (10KB)
        plaintext = b"Medical report data " * 500
        
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        decrypted = encryptor.decrypt(encrypted_data, iv, phone_hash)
        
        assert decrypted == plaintext
    
    def test_round_trip_with_unicode_data(self, encryptor, phone_hash):
        """Test encryption/decryption round-trip with unicode data"""
        plaintext = "Medical report with unicode: 你好 مرحبا".encode('utf-8')
        
        encrypted_data, iv = encryptor.encrypt(plaintext, phone_hash)
        decrypted = encryptor.decrypt(encrypted_data, iv, phone_hash)
        
        assert decrypted == plaintext
    
    def test_different_encryptors_with_same_secret(self, phone_hash):
        """Test different encryptor instances with same secret produce compatible results"""
        secret = "shared_server_secret_32_bytes!!!"
        plaintext = b"Medical report data"
        
        # Encrypt with first encryptor
        encryptor1 = AESEncryptor(secret)
        encrypted_data, iv = encryptor1.encrypt(plaintext, phone_hash)
        
        # Decrypt with second encryptor (same secret)
        encryptor2 = AESEncryptor(secret)
        decrypted = encryptor2.decrypt(encrypted_data, iv, phone_hash)
        
        assert decrypted == plaintext
    
    def test_different_encryptors_with_different_secrets(self, phone_hash):
        """Test different encryptor instances with different secrets are incompatible"""
        plaintext = b"Medical report data"
        
        # Encrypt with first encryptor
        encryptor1 = AESEncryptor("secret1_32_bytes_or_more_long!!!")
        encrypted_data, iv = encryptor1.encrypt(plaintext, phone_hash)
        
        # Try to decrypt with second encryptor (different secret)
        encryptor2 = AESEncryptor("secret2_32_bytes_or_more_long!!!")
        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor2.decrypt(encrypted_data, iv, phone_hash)

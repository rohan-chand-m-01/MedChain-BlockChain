"""
AES Encryptor Service

Provides AES-256-CBC encryption for medical reports using phone-derived keys.

This module implements:
- Key derivation using PBKDF2-HMAC-SHA256 with 100,000 iterations
- AES-256-CBC encryption with unique IV per encryption
- Secure decryption with IV extraction

Security Features:
- Phone hash + server secret for key material
- Unique IV prevents pattern analysis
- PBKDF2 iterations protect against brute force
"""

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class AESEncryptor:
    """
    AES-256-CBC encryption service for medical reports.
    
    This class provides encryption and decryption using:
    - AES-256 in CBC mode
    - PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)
    - Unique IV per encryption operation
    - Phone hash + server secret as key material
    """
    
    def __init__(self, server_secret: str):
        """
        Initialize AES encryptor with server secret.
        
        Args:
            server_secret: Server-side secret for key derivation.
                          Should be 32+ bytes of cryptographic randomness.
                          
        Raises:
            ValueError: If server_secret is empty or too short
        """
        if not server_secret or len(server_secret) < 32:
            raise ValueError("server_secret must be at least 32 bytes")
        
        self.server_secret = server_secret.encode('utf-8')
    
    def derive_key(self, phone_hash: str) -> bytes:
        """
        Derive encryption key from phone hash + server secret.
        
        Uses PBKDF2-HMAC-SHA256 with 100,000 iterations to derive a 32-byte
        AES-256 key. The phone hash provides user-specific key derivation,
        while the server secret adds an additional layer of security.
        
        Args:
            phone_hash: SHA-256 hash of patient's phone number (with "0x" prefix)
            
        Returns:
            32-byte encryption key suitable for AES-256
            
        Example:
            >>> encryptor = AESEncryptor("my_server_secret_32_bytes_long!")
            >>> key = encryptor.derive_key("0xabc123...")
            >>> len(key)
            32
        """
        # Remove "0x" prefix if present
        if phone_hash.startswith("0x"):
            phone_hash = phone_hash[2:]
        
        # Combine phone hash with server secret as key material
        key_material = phone_hash.encode('utf-8') + self.server_secret
        
        # Use PBKDF2-HMAC-SHA256 with 100,000 iterations
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits for AES-256
            salt=self.server_secret,  # Use server secret as salt
            iterations=100000,
            backend=default_backend()
        )
        
        return kdf.derive(key_material)
    
    def encrypt(self, plaintext: bytes, phone_hash: str) -> tuple[bytes, bytes]:
        """
        Encrypt data with AES-256-CBC.
        
        Generates a unique 16-byte IV for each encryption operation to prevent
        pattern analysis. The IV must be transmitted with the ciphertext for
        decryption.
        
        Args:
            plaintext: Raw data to encrypt (e.g., medical report)
            phone_hash: SHA-256 hash of patient's phone number
            
        Returns:
            Tuple of (encrypted_data, iv)
            - encrypted_data: AES-256-CBC ciphertext
            - iv: 16-byte initialization vector used for encryption
            
        Example:
            >>> encryptor = AESEncryptor("my_server_secret_32_bytes_long!")
            >>> plaintext = b"Medical report data"
            >>> encrypted, iv = encryptor.encrypt(plaintext, "0xabc123...")
            >>> len(iv)
            16
        """
        # Derive encryption key from phone hash
        key = self.derive_key(phone_hash)
        
        # Generate unique 16-byte IV for this encryption
        iv = os.urandom(16)
        
        # Create AES-256-CBC cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Apply PKCS7 padding to plaintext
        padded_plaintext = self._pad(plaintext)
        
        # Encrypt the padded plaintext
        encrypted_data = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return encrypted_data, iv
    
    def decrypt(self, encrypted_data: bytes, iv: bytes, phone_hash: str) -> bytes:
        """
        Decrypt data with AES-256-CBC.
        
        Extracts the IV and uses it along with the derived key to decrypt
        the ciphertext back to plaintext.
        
        Args:
            encrypted_data: AES-256-CBC ciphertext
            iv: 16-byte initialization vector used during encryption
            phone_hash: SHA-256 hash of patient's phone number
            
        Returns:
            Decrypted plaintext (original data)
            
        Raises:
            ValueError: If decryption fails (wrong key, corrupted data, etc.)
            
        Example:
            >>> encryptor = AESEncryptor("my_server_secret_32_bytes_long!")
            >>> encrypted, iv = encryptor.encrypt(b"Medical report", "0xabc123...")
            >>> decrypted = encryptor.decrypt(encrypted, iv, "0xabc123...")
            >>> decrypted
            b"Medical report"
        """
        # Derive decryption key from phone hash (same as encryption)
        key = self.derive_key(phone_hash)
        
        # Create AES-256-CBC cipher with the provided IV
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        try:
            # Decrypt the ciphertext
            padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove PKCS7 padding
            plaintext = self._unpad(padded_plaintext)
            
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def _pad(self, data: bytes) -> bytes:
        """
        Apply PKCS7 padding to data.
        
        PKCS7 padding adds bytes to make the data length a multiple of the
        block size (16 bytes for AES). Each padding byte contains the number
        of padding bytes added.
        
        Args:
            data: Data to pad
            
        Returns:
            Padded data
        """
        block_size = 16  # AES block size
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad(self, data: bytes) -> bytes:
        """
        Remove PKCS7 padding from data.
        
        Reads the last byte to determine how many padding bytes to remove.
        
        Args:
            data: Padded data
            
        Returns:
            Unpadded data
            
        Raises:
            ValueError: If padding is invalid
        """
        if not data:
            raise ValueError("Cannot unpad empty data")
        
        padding_length = data[-1]
        
        # Validate padding
        if padding_length > 16 or padding_length == 0:
            raise ValueError("Invalid padding length")
        
        # Verify all padding bytes are correct
        if data[-padding_length:] != bytes([padding_length] * padding_length):
            raise ValueError("Invalid padding bytes")
        
        return data[:-padding_length]

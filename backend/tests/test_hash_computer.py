"""
Unit tests for HashComputer utility.

Tests SHA-256 and Keccak-256 hash computation for privacy-preserving
identifiers and blockchain commitment hashes.
"""

import pytest
from services.hash_computer import HashComputer


class TestHashComputer:
    """Test suite for HashComputer utility."""
    
    def test_sha256_basic(self):
        """Test SHA-256 hash computation with basic input."""
        phone_number = "+1234567890"
        result = HashComputer.sha256(phone_number)
        
        # Verify format: starts with "0x" and has 64 hex characters
        assert result.startswith("0x")
        assert len(result) == 66  # "0x" + 64 hex chars
        assert all(c in "0123456789abcdef" for c in result[2:])
    
    def test_sha256_determinism(self):
        """Test SHA-256 produces same hash for same input."""
        phone_number = "+1234567890"
        hash1 = HashComputer.sha256(phone_number)
        hash2 = HashComputer.sha256(phone_number)
        
        assert hash1 == hash2
    
    def test_sha256_different_inputs(self):
        """Test SHA-256 produces different hashes for different inputs."""
        phone1 = "+1234567890"
        phone2 = "+0987654321"
        
        hash1 = HashComputer.sha256(phone1)
        hash2 = HashComputer.sha256(phone2)
        
        assert hash1 != hash2
    
    def test_sha256_empty_string(self):
        """Test SHA-256 handles empty string."""
        result = HashComputer.sha256("")
        
        # Empty string should still produce valid hash
        assert result.startswith("0x")
        assert len(result) == 66
        
        # Known SHA-256 hash of empty string
        expected = "0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected
    
    def test_sha256_unicode(self):
        """Test SHA-256 handles unicode characters."""
        data = "测试数据🔒"
        result = HashComputer.sha256(data)
        
        assert result.startswith("0x")
        assert len(result) == 66
    
    def test_keccak256_basic(self):
        """Test Keccak-256 hash computation with basic input."""
        data = "QmXxx1234567890+1234567890"
        result = HashComputer.keccak256(data)
        
        # Verify format: starts with "0x" and has 64 hex characters
        assert result.startswith("0x")
        assert len(result) == 66  # "0x" + 64 hex chars
        assert all(c in "0123456789abcdef" for c in result[2:])
    
    def test_keccak256_determinism(self):
        """Test Keccak-256 produces same hash for same input."""
        data = "commitment_data_12345"
        hash1 = HashComputer.keccak256(data)
        hash2 = HashComputer.keccak256(data)
        
        assert hash1 == hash2
    
    def test_keccak256_different_inputs(self):
        """Test Keccak-256 produces different hashes for different inputs."""
        data1 = "commitment_data_1"
        data2 = "commitment_data_2"
        
        hash1 = HashComputer.keccak256(data1)
        hash2 = HashComputer.keccak256(data2)
        
        assert hash1 != hash2
    
    def test_keccak256_empty_string(self):
        """Test Keccak-256 handles empty string."""
        result = HashComputer.keccak256("")
        
        # Empty string should still produce valid hash
        assert result.startswith("0x")
        assert len(result) == 66
        
        # Known Keccak-256 hash of empty string (Ethereum-compatible)
        expected = "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
        assert result == expected
    
    def test_keccak256_unicode(self):
        """Test Keccak-256 handles unicode characters."""
        data = "区块链数据🔗"
        result = HashComputer.keccak256(data)
        
        assert result.startswith("0x")
        assert len(result) == 66
    
    def test_sha256_vs_keccak256(self):
        """Test SHA-256 and Keccak-256 produce different hashes for same input."""
        data = "test_data_12345"
        
        sha_hash = HashComputer.sha256(data)
        keccak_hash = HashComputer.keccak256(data)
        
        # Different algorithms should produce different hashes
        assert sha_hash != keccak_hash
    
    def test_commitment_hash_format(self):
        """Test commitment hash computation with realistic data."""
        # Simulate commitment hash computation
        ipfs_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        risk_score = "75"
        timestamp = "1234567890"
        phone_hash = "0xabc123def456"
        
        # Concatenate commitment data
        commitment_data = f"{ipfs_cid}{risk_score}{timestamp}{phone_hash}"
        commitment_hash = HashComputer.keccak256(commitment_data)
        
        # Verify format
        assert commitment_hash.startswith("0x")
        assert len(commitment_hash) == 66
    
    def test_phone_hash_privacy(self):
        """Test phone hash is irreversible (one-way function)."""
        phone_number = "+1234567890"
        phone_hash = HashComputer.sha256(phone_number)
        
        # Hash should not contain original phone number
        assert phone_number not in phone_hash
        assert phone_number.replace("+", "") not in phone_hash
    
    def test_hash_collision_resistance(self):
        """Test hash functions are collision-resistant with similar inputs."""
        # Test with very similar inputs
        data1 = "test_data_1"
        data2 = "test_data_2"
        
        sha_hash1 = HashComputer.sha256(data1)
        sha_hash2 = HashComputer.sha256(data2)
        
        keccak_hash1 = HashComputer.keccak256(data1)
        keccak_hash2 = HashComputer.keccak256(data2)
        
        # Even similar inputs should produce completely different hashes
        assert sha_hash1 != sha_hash2
        assert keccak_hash1 != keccak_hash2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

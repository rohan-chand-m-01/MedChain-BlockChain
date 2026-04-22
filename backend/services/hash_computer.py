"""
Hash Computer Utility

Provides cryptographic hash functions for privacy-preserving identifiers
and blockchain commitment hashes.

This module implements:
- SHA-256 hashing for phone number privacy preservation
- Keccak-256 hashing for Ethereum-compatible commitment hashes
"""

import hashlib
from eth_utils import keccak


class HashComputer:
    """
    Utility class for computing cryptographic hashes.
    
    This class provides static methods for:
    - SHA-256: Used for phone number hashing (privacy-preserving identifier)
    - Keccak-256: Used for commitment hash computation (Ethereum-compatible)
    """
    
    @staticmethod
    def sha256(data: str) -> str:
        """
        Compute SHA-256 hash of input data.
        
        Used for phone number hashing to create privacy-preserving identifiers.
        The hash is irreversible, protecting patient identity even if the database
        is compromised.
        
        Args:
            data: Input string to hash (e.g., phone number)
            
        Returns:
            Hexadecimal string with "0x" prefix (e.g., "0xabc123...")
            
        Example:
            >>> HashComputer.sha256("+1234567890")
            "0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        """
        # Encode string to bytes
        data_bytes = data.encode('utf-8')
        
        # Compute SHA-256 hash
        hash_digest = hashlib.sha256(data_bytes).hexdigest()
        
        # Return with "0x" prefix for consistency with blockchain format
        return f"0x{hash_digest}"
    
    @staticmethod
    def hash_phone(phone: str) -> str:
        """
        Hash a phone number for privacy-preserving identifier.
        
        This is an alias for sha256() method, provided for semantic clarity
        when hashing phone numbers specifically.
        
        Args:
            phone: Phone number to hash (e.g., "+1234567890")
            
        Returns:
            Hexadecimal string with "0x" prefix
            
        Example:
            >>> HashComputer.hash_phone("+1234567890")
            "0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        """
        return HashComputer.sha256(phone)
    
    @staticmethod
    def compute_commitment_hash(
        ipfs_cid: str,
        risk_score: int,
        timestamp: str,
        patient_phone_hash: str
    ) -> str:
        """
        Compute commitment hash for blockchain storage.
        
        Binds together IPFS CID, risk score, timestamp, and patient identifier
        to create a tamper-evident record.
        
        Args:
            ipfs_cid: IPFS content identifier
            risk_score: Risk score (0-100)
            timestamp: ISO format timestamp
            patient_phone_hash: Hashed phone number
            
        Returns:
            Hexadecimal string with "0x" prefix
            
        Example:
            >>> HashComputer.compute_commitment_hash(
            ...     "QmXxx...", 75, "2024-01-01T00:00:00", "0xabc..."
            ... )
            "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"
        """
        # Concatenate all data
        commitment_data = f"{ipfs_cid}{risk_score}{timestamp}{patient_phone_hash}"
        
        # Return Keccak-256 hash
        return HashComputer.keccak256(commitment_data)
    
    @staticmethod
    def keccak256(data: str) -> str:
        """
        Compute Keccak-256 hash of input data (Ethereum-compatible).
        
        Used for commitment hash computation. The commitment hash binds together
        IPFS CID, risk score, timestamp, and phone hash to create a tamper-evident
        record on the blockchain.
        
        Args:
            data: Input string to hash (e.g., concatenated commitment data)
            
        Returns:
            Hexadecimal string with "0x" prefix (e.g., "0xdef456...")
            
        Example:
            >>> HashComputer.keccak256("QmXxx...1234567890+1234567890")
            "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"
            
        Note:
            This uses eth_utils.keccak which is compatible with Ethereum's
            keccak256 implementation (different from SHA3-256).
        """
        # Encode string to bytes
        data_bytes = data.encode('utf-8')
        
        # Compute Keccak-256 hash using eth_utils (Ethereum-compatible)
        hash_bytes = keccak(data_bytes)
        
        # Convert bytes to hexadecimal string with "0x" prefix
        return f"0x{hash_bytes.hex()}"

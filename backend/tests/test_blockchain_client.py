"""
Unit tests for BlockchainClient service

Tests blockchain interaction including:
- Commitment hash computation
- Transaction signing and submission
- Gas estimation
- Record verification
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.blockchain_client import (
    BlockchainClient,
    BlockchainGasError,
    BlockchainNetworkError,
    BlockchainTransactionError
)


@pytest.fixture
def mock_web3():
    """Fixture that provides a fully mocked Web3 instance for all tests"""
    with patch('services.blockchain_client.Web3') as mock_web3_class:
        # Create mock Web3 instance
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_w3.is_address.return_value = True
        mock_w3.to_checksum_address = Web3.to_checksum_address
        mock_w3.eth.contract.return_value = Mock()
        
        # Setup Web3 class methods
        mock_web3_class.return_value = mock_w3
        mock_web3_class.HTTPProvider = Mock()
        mock_web3_class.to_checksum_address = Web3.to_checksum_address
        mock_web3_class.to_bytes = Web3.to_bytes
        mock_web3_class.to_hex = Web3.to_hex
        
        yield mock_web3_class


class TestCommitmentHashComputation:
    """Test commitment hash computation - doesn't need network connection"""
    
    def test_compute_commitment_hash_deterministic(self, mock_web3):
        """Commitment hash should be deterministic for same inputs"""
        client = BlockchainClient(
            rpc_url="http://127.0.0.1:8545",
            contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        
        ipfs_cid = "QmXxx123"
        risk_score = 75
        timestamp = 1234567890
        phone_hash = "0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        
        # Compute hash twice
        hash1 = client.compute_commitment_hash(ipfs_cid, risk_score, timestamp, phone_hash)
        hash2 = client.compute_commitment_hash(ipfs_cid, risk_score, timestamp, phone_hash)
        
        # Should be identical
        assert hash1 == hash2
        assert hash1.startswith("0x")
        assert len(hash1) == 66  # 0x + 64 hex chars
    
    def test_compute_commitment_hash_different_inputs(self, mock_web3):
        """Different inputs should produce different hashes"""
        client = BlockchainClient(
            rpc_url="http://127.0.0.1:8545",
            contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        
        phone_hash = "0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        
        hash1 = client.compute_commitment_hash("QmXxx123", 75, 1234567890, phone_hash)
        hash2 = client.compute_commitment_hash("QmYyy456", 75, 1234567890, phone_hash)
        hash3 = client.compute_commitment_hash("QmXxx123", 80, 1234567890, phone_hash)
        hash4 = client.compute_commitment_hash("QmXxx123", 75, 9876543210, phone_hash)
        
        # All should be different
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash1 != hash4
        assert hash2 != hash3
    
    def test_compute_commitment_hash_format(self, mock_web3):
        """Commitment hash should have correct format"""
        client = BlockchainClient(
            rpc_url="http://127.0.0.1:8545",
            contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        
        hash_result = client.compute_commitment_hash(
            "QmTest",
            50,
            1000000000,
            "0x1234567890abcdef"
        )
        
        assert hash_result.startswith("0x")
        assert len(hash_result) == 66
        # Should be valid hex
        int(hash_result, 16)


class TestBlockchainClientInitialization:
    """Test blockchain client initialization"""
    
    def test_initialization_success(self, mock_web3):
        """Client should initialize successfully with valid config"""
        client = BlockchainClient(
            rpc_url="http://127.0.0.1:8545",
            contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        
        assert client.rpc_url == "http://127.0.0.1:8545"
        assert client.contract_address == "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    
    def test_initialization_connection_failure(self, mock_web3):
        """Client should raise error if connection fails"""
        # Configure mock to simulate connection failure
        mock_w3_instance = mock_web3.return_value
        mock_w3_instance.is_connected.return_value = False
        
        with pytest.raises(BlockchainNetworkError):
            BlockchainClient(
                rpc_url="http://invalid:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )


class TestStoreRecord:
    """Test storing records on blockchain"""
    
    @pytest.mark.asyncio
    @patch('services.blockchain_client.Web3')
    async def test_store_record_success(self, mock_web3):
        """Should successfully store record and return tx hash"""
        # Setup mocks
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.is_address.return_value = True
        mock_w3_instance.eth.get_transaction_count.return_value = 0
        mock_w3_instance.eth.estimate_gas.return_value = 100000
        mock_w3_instance.eth.gas_price = 20000000000
        mock_w3_instance.eth.get_balance.return_value = 10**18  # 1 ETH
        mock_w3_instance.eth.send_raw_transaction.return_value = Web3.to_bytes(hexstr="0x123abc")
        
        # Mock receipt
        mock_receipt = {
            'status': 1,
            'blockNumber': 12345,
            'transactionHash': Web3.to_bytes(hexstr="0x123abc")
        }
        mock_w3_instance.eth.wait_for_transaction_receipt.return_value = mock_receipt
        
        # Mock contract
        mock_contract = Mock()
        mock_function = Mock()
        mock_function.build_transaction.return_value = {
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'nonce': 0,
            'gas': 0,
            'gasPrice': 0
        }
        mock_contract.functions.storeRecord.return_value = mock_function
        mock_w3_instance.eth.contract.return_value = mock_contract
        
        mock_web3.return_value = mock_w3_instance
        mock_web3.HTTPProvider.return_value = Mock()
        mock_web3.to_bytes = Web3.to_bytes
        mock_web3.to_checksum_address = Web3.to_checksum_address
        
        # Create client
        with patch('services.blockchain_client.Account') as mock_account:
            mock_acc = Mock()
            mock_acc.address = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
            mock_signed = Mock()
            mock_signed.rawTransaction = b'signed_tx'
            mock_acc.sign_transaction.return_value = mock_signed
            mock_account.from_key.return_value = mock_acc
            
            client = BlockchainClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            # Store record
            tx_hash = await client.store_record(
                "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8",
                "QmMetadata"
            )
            
            assert tx_hash == "123abc"  # hex() returns without 0x prefix
    
    @pytest.mark.asyncio
    @patch('services.blockchain_client.Web3')
    async def test_store_record_insufficient_gas(self, mock_web3):
        """Should raise BlockchainGasError if balance too low"""
        # Setup mocks
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.is_address.return_value = True
        mock_w3_instance.eth.get_transaction_count.return_value = 0
        mock_w3_instance.eth.estimate_gas.return_value = 100000
        mock_w3_instance.eth.gas_price = 20000000000
        mock_w3_instance.eth.get_balance.return_value = 100  # Very low balance
        
        # Mock contract
        mock_contract = Mock()
        mock_function = Mock()
        mock_function.build_transaction.return_value = {
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'nonce': 0,
            'gas': 0,
            'gasPrice': 0
        }
        mock_contract.functions.storeRecord.return_value = mock_function
        mock_w3_instance.eth.contract.return_value = mock_contract
        
        mock_web3.return_value = mock_w3_instance
        mock_web3.HTTPProvider.return_value = Mock()
        mock_web3.to_bytes = Web3.to_bytes
        mock_web3.to_checksum_address = Web3.to_checksum_address
        
        with patch('services.blockchain_client.Account') as mock_account:
            mock_acc = Mock()
            mock_acc.address = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
            mock_account.from_key.return_value = mock_acc
            
            client = BlockchainClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            with pytest.raises(BlockchainGasError):
                await client.store_record(
                    "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8",
                    "QmMetadata"
                )
    
    @pytest.mark.asyncio
    @patch('services.blockchain_client.Web3')
    async def test_store_record_transaction_revert(self, mock_web3):
        """Should raise BlockchainTransactionError if transaction reverts"""
        # Setup mocks
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.is_address.return_value = True
        mock_w3_instance.eth.get_transaction_count.return_value = 0
        mock_w3_instance.eth.estimate_gas.return_value = 100000
        mock_w3_instance.eth.gas_price = 20000000000
        mock_w3_instance.eth.get_balance.return_value = 10**18
        mock_w3_instance.eth.send_raw_transaction.return_value = Web3.to_bytes(hexstr="0x123abc")
        
        # Mock reverted receipt
        mock_receipt = {
            'status': 0,  # Reverted
            'blockNumber': 12345,
            'transactionHash': Web3.to_bytes(hexstr="0x123abc")
        }
        mock_w3_instance.eth.wait_for_transaction_receipt.return_value = mock_receipt
        
        # Mock contract
        mock_contract = Mock()
        mock_function = Mock()
        mock_function.build_transaction.return_value = {
            'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'nonce': 0,
            'gas': 0,
            'gasPrice': 0
        }
        mock_contract.functions.storeRecord.return_value = mock_function
        mock_w3_instance.eth.contract.return_value = mock_contract
        
        mock_web3.return_value = mock_w3_instance
        mock_web3.HTTPProvider.return_value = Mock()
        mock_web3.to_bytes = Web3.to_bytes
        mock_web3.to_checksum_address = Web3.to_checksum_address
        
        with patch('services.blockchain_client.Account') as mock_account:
            mock_acc = Mock()
            mock_acc.address = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
            mock_signed = Mock()
            mock_signed.rawTransaction = b'signed_tx'
            mock_acc.sign_transaction.return_value = mock_signed
            mock_account.from_key.return_value = mock_acc
            
            client = BlockchainClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            with pytest.raises(BlockchainTransactionError):
                await client.store_record(
                    "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8",
                    "QmMetadata"
                )


class TestVerifyRecord:
    """Test verifying records on blockchain"""
    
    @pytest.mark.asyncio
    @patch('services.blockchain_client.Web3')
    async def test_verify_record_exists(self, mock_web3):
        """Should return record data if it exists"""
        # Setup mocks
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.is_address.return_value = True
        
        # Mock contract call
        mock_contract = Mock()
        commitment_bytes = Web3.to_bytes(hexstr="0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8")
        mock_contract.functions.records.return_value.call.return_value = (
            commitment_bytes,
            "QmMetadata",
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            1234567890,
            True
        )
        mock_w3_instance.eth.contract.return_value = mock_contract
        
        mock_web3.return_value = mock_w3_instance
        mock_web3.HTTPProvider.return_value = Mock()
        mock_web3.to_checksum_address = Web3.to_checksum_address
        mock_web3.to_hex = Web3.to_hex
        
        with patch('services.blockchain_client.Account'):
            client = BlockchainClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            result = await client.verify_record(123)
            
            assert result['exists'] is True
            assert result['metadata_cid'] == "QmMetadata"
            assert result['patient'] == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
            assert result['timestamp'] == 1234567890
    
    @pytest.mark.asyncio
    @patch('services.blockchain_client.Web3')
    async def test_verify_record_not_exists(self, mock_web3):
        """Should return exists=False if record doesn't exist"""
        # Setup mocks
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.is_address.return_value = True
        
        # Mock contract call for non-existent record
        mock_contract = Mock()
        mock_contract.functions.records.return_value.call.return_value = (
            b'\x00' * 32,  # Empty bytes32
            "",
            "0x0000000000000000000000000000000000000000",
            0,
            False
        )
        mock_w3_instance.eth.contract.return_value = mock_contract
        
        mock_web3.return_value = mock_w3_instance
        mock_web3.HTTPProvider.return_value = Mock()
        mock_web3.to_checksum_address = Web3.to_checksum_address
        mock_web3.to_hex = Web3.to_hex
        
        with patch('services.blockchain_client.Account'):
            client = BlockchainClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
            )
            
            result = await client.verify_record(999)
            
            assert result['exists'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

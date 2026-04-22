"""
Blockchain Client Service

Provides interaction with Ethereum smart contract for storing and verifying
commitment hashes on the blockchain.

This module implements:
- Transaction signing and submission to Ethereum network
- Gas estimation and transaction confirmation logic
- Commitment hash computation using keccak256
- On-chain record verification
"""

import os
import logging
from typing import Optional, Dict, Any
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted
from eth_account import Account
from .hash_computer import HashComputer

logger = logging.getLogger(__name__)


# Custom Exceptions
class BlockchainGasError(Exception):
    """Raised when there is insufficient gas for a transaction"""
    pass


class BlockchainNetworkError(Exception):
    """Raised when there is a network connectivity issue"""
    pass


class BlockchainTransactionError(Exception):
    """Raised when a transaction fails or reverts"""
    pass


class BlockchainClient:
    """
    Client for interacting with the MediChainRecords smart contract.
    
    This class provides methods for:
    - Storing commitment hashes on the blockchain
    - Verifying records exist on-chain
    - Computing commitment hashes from record components
    - Gas estimation and transaction confirmation
    """
    
    # Smart contract ABI (updated for new MediChainRecords contract)
    CONTRACT_ABI = [
        {
            "inputs": [
                {"internalType": "bytes32", "name": "commitmentHash", "type": "bytes32"},
                {"internalType": "uint256", "name": "riskScore", "type": "uint256"},
                {"internalType": "string", "name": "riskLevel", "type": "string"}
            ],
            "name": "storeRecord",
            "outputs": [{"internalType": "bytes32", "name": "recordId", "type": "bytes32"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "recordId", "type": "bytes32"}],
            "name": "verifyRecord",
            "outputs": [
                {"internalType": "bool", "name": "exists", "type": "bool"},
                {"internalType": "uint256", "name": "riskScore", "type": "uint256"},
                {"internalType": "string", "name": "riskLevel", "type": "string"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "name": "records",
            "outputs": [
                {"internalType": "bytes32", "name": "commitmentHash", "type": "bytes32"},
                {"internalType": "uint256", "name": "riskScore", "type": "uint256"},
                {"internalType": "string", "name": "riskLevel", "type": "string"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "bool", "name": "exists", "type": "bool"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        contract_address: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize blockchain client with Ethereum connection details.
        
        Args:
            rpc_url: Ethereum RPC endpoint (defaults to env ETHEREUM_RPC_URL)
            contract_address: Deployed contract address (defaults to env CONTRACT_ADDRESS)
            private_key: Private key for signing transactions (defaults to env GAS_WALLET_PRIVATE_KEY or ETHEREUM_PRIVATE_KEY)
            
        Raises:
            BlockchainNetworkError: If connection to RPC fails
        """
        self.rpc_url = rpc_url or os.getenv("ETHEREUM_RPC_URL", "http://127.0.0.1:8545")
        self.contract_address = contract_address or os.getenv("CONTRACT_ADDRESS", "")
        # Try GAS_WALLET_PRIVATE_KEY first, then fall back to ETHEREUM_PRIVATE_KEY
        self.private_key = private_key or os.getenv("GAS_WALLET_PRIVATE_KEY") or os.getenv("ETHEREUM_PRIVATE_KEY", "")
        
        # Validate configuration
        if not self.contract_address:
            logger.warning("CONTRACT_ADDRESS not set - blockchain features will be disabled")
        if not self.private_key:
            logger.warning("ETHEREUM_PRIVATE_KEY not set - blockchain features will be disabled")
        
        # Initialize Web3
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                raise BlockchainNetworkError(f"Failed to connect to Ethereum RPC at {self.rpc_url}")
            
            logger.info(f"Connected to Ethereum network at {self.rpc_url}")
            
            # Initialize account from private key
            if self.private_key:
                # Remove '0x' prefix if present
                clean_key = self.private_key.replace('0x', '')
                self.account = Account.from_key(clean_key)
                logger.info(f"Initialized account: {self.account.address}")
            else:
                self.account = None
            
            # Initialize contract
            if self.contract_address and self.w3.is_address(self.contract_address):
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=self.CONTRACT_ABI
                )
                logger.info(f"Initialized contract at {self.contract_address}")
            else:
                self.contract = None
                if self.contract_address:
                    logger.warning(f"Invalid contract address: {self.contract_address}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize blockchain client: {e}")
            raise BlockchainNetworkError(f"Blockchain initialization failed: {e}")
    
    def compute_commitment_hash(
        self,
        ipfs_cid: str,
        risk_score: int,
        timestamp: int,
        phone_hash: str
    ) -> str:
        """
        Compute keccak256 commitment hash from record components.
        
        The commitment hash binds together all record components to create
        a tamper-evident record. Formula:
        keccak256(ipfs_cid + risk_score + timestamp + phone_hash)
        
        Args:
            ipfs_cid: IPFS content identifier (e.g., "QmXxx..." or "bafyxxx...")
            risk_score: Numeric risk score (0-100)
            timestamp: Unix timestamp of record creation
            phone_hash: SHA-256 hash of patient phone number
            
        Returns:
            Hexadecimal string with "0x" prefix (e.g., "0xabc123...")
            
        Example:
            >>> client.compute_commitment_hash(
            ...     "QmXxx...",
            ...     75,
            ...     1234567890,
            ...     "0x5e884898..."
            ... )
            "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"
        """
        # Concatenate all components as strings
        data = f"{ipfs_cid}{risk_score}{timestamp}{phone_hash}"
        
        # Compute keccak256 hash
        commitment_hash = HashComputer.keccak256(data)
        
        logger.debug(f"Computed commitment hash: {commitment_hash}")
        return commitment_hash
    
    async def store_record(
        self,
        commitment_hash: str,
        risk_score: int,
        risk_level: str
    ) -> str:
        """
        Store commitment hash on blockchain with risk score and level.
        
        This method:
        1. Estimates gas required for the transaction
        2. Builds and signs the transaction
        3. Submits to the network
        4. Waits for confirmation (1 block)
        5. Returns the record ID (bytes32)
        
        Args:
            commitment_hash: Keccak256 hash to store (with "0x" prefix)
            risk_score: Numeric risk score (0-100)
            risk_level: Risk level string ("LOW", "MEDIUM", "HIGH")
            
        Returns:
            Record ID (bytes32 as hex string, e.g., "0xdef456...")
            
        Raises:
            BlockchainGasError: If insufficient gas or balance
            BlockchainNetworkError: If network connection fails
            BlockchainTransactionError: If transaction reverts
            
        Example:
            >>> record_id = await client.store_record(
            ...     "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8",
            ...     75,
            ...     "MEDIUM"
            ... )
            "0x9fc76417374aa880d4449a1f7f31ec597f00b1f6f3dd2d66f4c9c6c445836d8b"
        """
        if not self.contract:
            raise BlockchainNetworkError("Contract not initialized - check CONTRACT_ADDRESS")
        if not self.account:
            raise BlockchainNetworkError("Account not initialized - check ETHEREUM_PRIVATE_KEY")
        
        try:
            # Convert commitment hash to bytes32
            commitment_bytes = Web3.to_bytes(hexstr=commitment_hash)
            
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Build transaction
            transaction = self.contract.functions.storeRecord(
                commitment_bytes,
                risk_score,
                risk_level.upper()
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 0,  # Will be estimated
                'gasPrice': 0,  # Will be estimated
            })
            
            # Estimate gas
            try:
                gas_estimate = self.w3.eth.estimate_gas(transaction)
                # Add 20% buffer to gas estimate
                transaction['gas'] = int(gas_estimate * 1.2)
                logger.info(f"Estimated gas: {gas_estimate}, using: {transaction['gas']}")
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                raise BlockchainGasError(f"Failed to estimate gas: {e}")
            
            # Get gas price
            try:
                gas_price = self.w3.eth.gas_price
                # Use medium priority (1.2x base gas price)
                transaction['gasPrice'] = int(gas_price * 1.2)
                logger.info(f"Gas price: {gas_price}, using: {transaction['gasPrice']}")
            except Exception as e:
                logger.error(f"Failed to get gas price: {e}")
                raise BlockchainNetworkError(f"Failed to get gas price: {e}")
            
            # Check balance
            balance = self.w3.eth.get_balance(self.account.address)
            total_cost = transaction['gas'] * transaction['gasPrice']
            if balance < total_cost:
                raise BlockchainGasError(
                    f"Insufficient balance: {balance} wei, need {total_cost} wei"
                )
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction)
            
            # Send transaction
            try:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_hash_hex = tx_hash.hex()
                logger.info(f"Transaction sent: {tx_hash_hex}")
            except Exception as e:
                logger.error(f"Failed to send transaction: {e}")
                raise BlockchainNetworkError(f"Failed to send transaction: {e}")
            
            # Wait for confirmation (1 block, 120 second timeout)
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=120,
                    poll_latency=2
                )
                
                if receipt['status'] == 0:
                    raise BlockchainTransactionError(
                        f"Transaction reverted: {tx_hash_hex}"
                    )
                
                # Extract recordId from logs (RecordStored event)
                # For now, return tx_hash as record identifier
                # TODO: Parse logs to extract actual recordId
                logger.info(
                    f"Transaction confirmed in block {receipt['blockNumber']}: {tx_hash_hex}"
                )
                return tx_hash_hex
                
            except TimeExhausted:
                logger.warning(f"Transaction confirmation timeout: {tx_hash_hex}")
                # Return hash anyway - transaction may still be pending
                return tx_hash_hex
            except Exception as e:
                logger.error(f"Error waiting for confirmation: {e}")
                raise BlockchainTransactionError(f"Confirmation failed: {e}")
                
        except (BlockchainGasError, BlockchainNetworkError, BlockchainTransactionError):
            # Re-raise our custom exceptions
            raise
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            raise BlockchainTransactionError(f"Contract error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error storing record: {e}")
            raise BlockchainTransactionError(f"Unexpected error: {e}")
    
    async def verify_record(self, record_id: str) -> Dict[str, Any]:
        """
        Verify record exists on blockchain and retrieve its data.
        
        This method queries the smart contract to check if a record exists
        and returns its details if found.
        
        Args:
            record_id: The record ID (bytes32 as hex string with "0x" prefix)
            
        Returns:
            Dictionary with record data:
            {
                'exists': bool,
                'risk_score': int,
                'risk_level': str,
                'timestamp': int
            }
            
        Raises:
            BlockchainNetworkError: If network connection fails
            
        Example:
            >>> record = await client.verify_record("0xabc123...")
            {
                'exists': True,
                'risk_score': 75,
                'risk_level': 'MEDIUM',
                'timestamp': 1234567890
            }
        """
        if not self.contract:
            raise BlockchainNetworkError("Contract not initialized - check CONTRACT_ADDRESS")
        
        try:
            # Convert record_id to bytes32
            record_id_bytes = Web3.to_bytes(hexstr=record_id)
            
            # Call verifyRecord function
            exists, risk_score, risk_level, timestamp = self.contract.functions.verifyRecord(
                record_id_bytes
            ).call()
            
            result = {
                'exists': exists,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'timestamp': timestamp
            }
            
            logger.debug(f"Verified record {record_id}: exists={exists}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to verify record {record_id}: {e}")
            raise BlockchainNetworkError(f"Verification failed: {e}")

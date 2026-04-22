#!/usr/bin/env python3
"""Script to write the fixed stellar_client.py file"""

content = '''import os
import logging
import base64
from typing import Optional, Dict, Any
from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset
from stellar_sdk.exceptions import NotFoundError, BadRequestError
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class StellarNetworkError(Exception):
    pass

class StellarTransactionError(Exception):
    pass

class StellarClient:
    def __init__(self, network='testnet', horizon_url=None, gas_wallet_secret=None):
        self.network = network
        if network == 'testnet':
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or 'https://horizon-testnet.stellar.org'
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or 'https://horizon.stellar.org'
        
        self.server = Server(horizon_url=self.horizon_url)
        self.gas_wallet_secret = gas_wallet_secret or os.getenv('STELLAR_GAS_WALLET_SECRET', '')
        
        if self.gas_wallet_secret:
            self.gas_wallet = Keypair.from_secret(self.gas_wallet_secret)
        else:
            self.gas_wallet = None
        
        vault_key = os.getenv('VAULT_MASTER_KEY', '')
        if vault_key:
            self.cipher = Fernet(base64.urlsafe_b64encode(vault_key[:32].encode()))
        else:
            self.cipher = None

    def create_account_for_user(self, privy_user_id):
        keypair = Keypair.random()
        if self.cipher:
            encrypted_secret = self.cipher.encrypt(keypair.secret.encode()).decode()
        else:
            encrypted_secret = keypair.secret
        return {
            'public_key': keypair.public_key,
            'encrypted_secret': encrypted_secret
        }

    def decrypt_secret(self, encrypted_secret):
        if self.cipher:
            return self.cipher.decrypt(encrypted_secret.encode()).decode()
        return encrypted_secret

    async def store_proof_on_stellar(self, patient_public_key, ipfs_hash, risk_score, risk_level):
        """Store medical record proof on Stellar - all data on gas wallet"""
        if not self.gas_wallet:
            raise StellarNetworkError('Gas wallet not configured')
        
        gas_account = self.server.load_account(self.gas_wallet.public_key)
        record_id = ipfs_hash[:8]
        patient_id = patient_public_key[:16] if len(patient_public_key) > 16 else patient_public_key
        
        transaction = (
            TransactionBuilder(
                source_account=gas_account,
                network_passphrase=self.network_passphrase,
                base_fee=100
            )
            .append_manage_data_op(
                data_name=f'ipfs_{record_id}',
                data_value=f'{patient_id}:{ipfs_hash}'.encode()
            )
            .append_manage_data_op(
                data_name=f'risk_{record_id}',
                data_value=f'{patient_id}:{risk_score}:{risk_level}'.encode()
            )
            .add_text_memo(f'MEDICAL_RECORD:{record_id}')
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(self.gas_wallet)
        response = self.server.submit_transaction(transaction)
        return response['hash']

    async def grant_access(self, patient_encrypted_secret, doctor_public_key, duration_hours, record_id):
        patient_secret = self.decrypt_secret(patient_encrypted_secret)
        patient_keypair = Keypair.from_secret(patient_secret)
        patient_account = self.server.load_account(patient_keypair.public_key)
        
        import time
        expiry_timestamp = int(time.time()) + (duration_hours * 3600)
        
        transaction = (
            TransactionBuilder(
                source_account=patient_account,
                network_passphrase=self.network_passphrase,
                base_fee=100
            )
            .append_manage_data_op(
                data_name=f'access_{record_id}_{doctor_public_key[:8]}',
                data_value=str(expiry_timestamp).encode()
            )
            .add_text_memo(f'ACCESS_GRANT:{record_id}:{doctor_public_key[:8]}')
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(patient_keypair)
        response = self.server.submit_transaction(transaction)
        return response['hash']

    async def verify_access(self, patient_public_key, doctor_public_key, record_id):
        try:
            account = self.server.accounts().account_id(patient_public_key).call()
            access_key = f'access_{record_id}_{doctor_public_key[:8]}'
            
            if access_key in account.get('data', {}):
                expiry_data = account['data'][access_key]
                expiry_timestamp = int(base64.b64decode(expiry_data).decode())
                
                import time
                return time.time() < expiry_timestamp
            
            return False
        except:
            return False

    async def pay_doctor(self, patient_encrypted_secret, doctor_public_key, amount='0.5'):
        patient_secret = self.decrypt_secret(patient_encrypted_secret)
        patient_keypair = Keypair.from_secret(patient_secret)
        patient_account = self.server.load_account(patient_keypair.public_key)
        
        transaction = (
            TransactionBuilder(
                source_account=patient_account,
                network_passphrase=self.network_passphrase,
                base_fee=100
            )
            .append_payment_op(
                destination=doctor_public_key,
                asset=Asset.native(),
                amount=amount
            )
            .add_text_memo('CONSULTATION_FEE')
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(patient_keypair)
        response = self.server.submit_transaction(transaction)
        return response['hash']
'''

with open('backend/services/stellar_client.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File written successfully")
print(f"✅ File size: {len(content)} bytes")

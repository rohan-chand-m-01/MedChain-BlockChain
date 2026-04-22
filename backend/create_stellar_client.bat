@echo off
echo Creating stellar_client.py...

(
echo import os
echo import logging
echo import base64
echo from typing import Optional, Dict, Any
echo from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset
echo from stellar_sdk.exceptions import NotFoundError, BadRequestError
echo from cryptography.fernet import Fernet
echo.
echo logger = logging.getLogger^(__name__^)
echo.
echo class StellarNetworkError^(Exception^):
echo     pass
echo.
echo class StellarTransactionError^(Exception^):
echo     pass
echo.
echo class StellarClient:
echo     def __init__^(self, network='testnet', horizon_url=None, gas_wallet_secret=None^):
echo         self.network = network
echo         if network == 'testnet':
echo             self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
echo             self.horizon_url = horizon_url or 'https://horizon-testnet.stellar.org'
echo         else:
echo             self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
echo             self.horizon_url = horizon_url or 'https://horizon.stellar.org'
echo         self.server = Server^(horizon_url=self.horizon_url^)
echo         self.gas_wallet_secret = gas_wallet_secret or os.getenv^('STELLAR_GAS_WALLET_SECRET', ''^)
echo         if self.gas_wallet_secret:
echo             self.gas_wallet = Keypair.from_secret^(self.gas_wallet_secret^)
echo         else:
echo             self.gas_wallet = None
echo         vault_key = os.getenv^('VAULT_MASTER_KEY', ''^)
echo         if vault_key:
echo             self.cipher = Fernet^(base64.urlsafe_b64encode^(vault_key[:32].encode^(^)^)^)
echo         else:
echo             self.cipher = None
echo.
echo     def create_account_for_user^(self, privy_user_id^):
echo         keypair = Keypair.random^(^)
echo         if self.cipher:
echo             encrypted_secret = self.cipher.encrypt^(keypair.secret.encode^(^)^).decode^(^)
echo         else:
echo             encrypted_secret = keypair.secret
echo         return {'public_key': keypair.public_key, 'encrypted_secret': encrypted_secret}
echo.
echo     def decrypt_secret^(self, encrypted_secret^):
echo         if self.cipher:
echo             return self.cipher.decrypt^(encrypted_secret.encode^(^)^).decode^(^)
echo         return encrypted_secret
echo.
echo     async def store_proof_on_stellar^(self, patient_public_key, ipfs_hash, risk_score, risk_level^):
echo         if not self.gas_wallet:
echo             raise StellarNetworkError^('Gas wallet not configured'^)
echo         gas_account = self.server.load_account^(self.gas_wallet.public_key^)
echo         record_id = ipfs_hash[:8]
echo         transaction = ^(
echo             TransactionBuilder^(source_account=gas_account, network_passphrase=self.network_passphrase, base_fee=100^)
echo             .append_manage_data_op^(data_name=f'ipfs_{record_id}', data_value=ipfs_hash.encode^(^), source=patient_public_key^)
echo             .append_manage_data_op^(data_name=f'risk_{record_id}', data_value=f'{risk_score}:{risk_level}'.encode^(^), source=patient_public_key^)
echo             .add_text_memo^(f'MEDICAL_RECORD:{record_id}'^)
echo             .set_timeout^(30^)
echo             .build^(^)
echo         ^)
echo         transaction.sign^(self.gas_wallet^)
echo         response = self.server.submit_transaction^(transaction^)
echo         return response['hash']
echo.
echo     async def grant_access^(self, patient_encrypted_secret, doctor_public_key, duration_hours, record_id^):
echo         patient_secret = self.decrypt_secret^(patient_encrypted_secret^)
echo         patient_keypair = Keypair.from_secret^(patient_secret^)
echo         patient_account = self.server.load_account^(patient_keypair.public_key^)
echo         import time
echo         expiry_timestamp = int^(time.time^(^)^) + ^(duration_hours * 3600^)
echo         transaction = ^(
echo             TransactionBuilder^(source_account=patient_account, network_passphrase=self.network_passphrase, base_fee=100^)
echo             .append_manage_data_op^(data_name=f'access_{record_id}_{doctor_public_key[:8]}', data_value=str^(expiry_timestamp^).encode^(^)^)
echo             .add_text_memo^(f'ACCESS_GRANT:{record_id}:{doctor_public_key[:8]}'^)
echo             .set_timeout^(30^)
echo             .build^(^)
echo         ^)
echo         transaction.sign^(patient_keypair^)
echo         response = self.server.submit_transaction^(transaction^)
echo         return response['hash']
echo.
echo     async def verify_access^(self, patient_public_key, doctor_public_key, record_id^):
echo         try:
echo             account = self.server.accounts^(^).account_id^(patient_public_key^).call^(^)
echo             access_key = f'access_{record_id}_{doctor_public_key[:8]}'
echo             if access_key in account.get^('data', {}^):
echo                 expiry_data = account['data'][access_key]
echo                 expiry_timestamp = int^(base64.b64decode^(expiry_data^).decode^(^)^)
echo                 import time
echo                 return time.time^(^) ^< expiry_timestamp
echo             return False
echo         except:
echo             return False
echo.
echo     async def pay_doctor^(self, patient_encrypted_secret, doctor_public_key, amount='0.5'^):
echo         patient_secret = self.decrypt_secret^(patient_encrypted_secret^)
echo         patient_keypair = Keypair.from_secret^(patient_secret^)
echo         patient_account = self.server.load_account^(patient_keypair.public_key^)
echo         transaction = ^(
echo             TransactionBuilder^(source_account=patient_account, network_passphrase=self.network_passphrase, base_fee=100^)
echo             .append_payment_op^(destination=doctor_public_key, asset=Asset.native^(^), amount=amount^)
echo             .add_text_memo^('CONSULTATION_FEE'^)
echo             .set_timeout^(30^)
echo             .build^(^)
echo         ^)
echo         transaction.sign^(patient_keypair^)
echo         response = self.server.submit_transaction^(transaction^)
echo         return response['hash']
) > services\stellar_client.py

echo Done! File created.
echo Testing import...
py -c "from services.stellar_client import StellarClient; print('✅ Success!')"
pause

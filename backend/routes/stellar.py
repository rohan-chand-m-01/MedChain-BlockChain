"""
Stellar API Routes

Handles Stellar blockchain operations for MediChain.
Bridges Privy authentication with Stellar transactions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from services.stellar_client import StellarClient, StellarTransactionError, StellarNetworkError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stellar Blockchain"])

# Initialize Stellar client
stellar_client = StellarClient()


# Request/Response Models
class StoreProofRequest(BaseModel):
    ipfs_hash: str
    risk_score: int
    risk_level: str


class GrantAccessRequest(BaseModel):
    doctor_public_key: str
    record_id: str
    duration_hours: int


class VerifyAccessRequest(BaseModel):
    patient_public_key: str
    doctor_public_key: str
    record_id: str


class PayDoctorRequest(BaseModel):
    doctor_public_key: str
    amount: str = "0.5"


class StellarResponse(BaseModel):
    success: bool
    tx_hash: Optional[str] = None
    message: Optional[str] = None


class AccessVerificationResponse(BaseModel):
    has_access: bool
    message: Optional[str] = None


@router.post("/stellar/store-proof", response_model=StellarResponse)
async def store_proof_on_stellar(request: StoreProofRequest):
    """
    Store medical record proof on Stellar blockchain.
    
    Called after IPFS upload completes.
    Uses gas wallet to pay transaction fees.
    """
    try:
        logger.info(f"Received store-proof request: ipfs_hash={request.ipfs_hash[:20]}..., risk_score={request.risk_score}, risk_level={request.risk_level}")
        
        # Use the gas wallet's public key as the patient account
        # In production, this should be the patient's own Stellar account
        # For now, we store all proofs on the gas wallet account
        from services.stellar_client import Keypair
        import os
        
        gas_wallet_secret = os.getenv('STELLAR_GAS_WALLET_SECRET', '')
        if not gas_wallet_secret:
            logger.error("STELLAR_GAS_WALLET_SECRET not configured")
            raise HTTPException(status_code=500, detail="Stellar gas wallet not configured")
        
        gas_wallet = Keypair.from_secret(gas_wallet_secret)
        patient_public_key = gas_wallet.public_key
        
        logger.info(f"Using gas wallet account: {patient_public_key}")
        
        # Store proof on Stellar
        tx_hash = await stellar_client.store_proof_on_stellar(
            patient_public_key=patient_public_key,
            ipfs_hash=request.ipfs_hash,
            risk_score=request.risk_score,
            risk_level=request.risk_level
        )
        
        logger.info(f"✅ Stellar transaction successful: {tx_hash}")
        logger.info(f"View on Stellar Expert: https://stellar.expert/explorer/testnet/tx/{tx_hash}")
        
        return StellarResponse(
            success=True,
            tx_hash=tx_hash,
            message="Proof stored on Stellar"
        )
        
    except StellarTransactionError as e:
        logger.error(f"❌ Stellar transaction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error in store_proof_on_stellar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to store proof: {str(e)}")


@router.post("/stellar/grant-access", response_model=StellarResponse)
async def grant_doctor_access(request: GrantAccessRequest):
    """
    Grant doctor access to medical record.
    
    Patient signs transaction with access grant.
    Doctor receives WhatsApp notification.
    """
    try:
        # TODO: Get from authenticated user session
        patient_encrypted_secret = "TEMPORARY"  # Will be replaced
        
        # Grant access on Stellar
        tx_hash = await stellar_client.grant_access(
            patient_encrypted_secret=patient_encrypted_secret,
            doctor_public_key=request.doctor_public_key,
            duration_hours=request.duration_hours,
            record_id=request.record_id
        )
        
        # TODO: Send WhatsApp notification to doctor
        
        return StellarResponse(
            success=True,
            tx_hash=tx_hash,
            message="Access granted successfully"
        )
        
    except StellarTransactionError as e:
        logger.error(f"Access grant failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to grant access")


@router.post("/stellar/verify-access", response_model=AccessVerificationResponse)
async def verify_doctor_access(request: VerifyAccessRequest):
    """
    Verify doctor has valid access to patient's record.
    
    Called before showing medical data to doctor.
    Checks Stellar blockchain for access grant.
    """
    try:
        has_access = await stellar_client.verify_access(
            patient_public_key=request.patient_public_key,
            doctor_public_key=request.doctor_public_key,
            record_id=request.record_id
        )
        
        return AccessVerificationResponse(
            has_access=has_access,
            message="Access verified" if has_access else "Access denied or expired"
        )
        
    except Exception as e:
        logger.error(f"Access verification failed: {e}")
        return AccessVerificationResponse(
            has_access=False,
            message="Verification failed"
        )


@router.post("/stellar/pay-doctor", response_model=StellarResponse)
async def pay_doctor_consultation(request: PayDoctorRequest):
    """
    Process consultation payment from patient to doctor.
    
    Patient signs payment transaction.
    Amount in XLM (default: 0.5 XLM per consultation).
    """
    try:
        # TODO: Get from authenticated user session
        patient_encrypted_secret = "TEMPORARY"  # Will be replaced
        
        # Process payment
        tx_hash = await stellar_client.pay_doctor(
            patient_encrypted_secret=patient_encrypted_secret,
            doctor_public_key=request.doctor_public_key,
            amount=request.amount
        )
        
        return StellarResponse(
            success=True,
            tx_hash=tx_hash,
            message=f"Payment of {request.amount} XLM processed"
        )
        
    except StellarTransactionError as e:
        logger.error(f"Payment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Payment failed")


@router.get("/stellar/account/{public_key}")
async def get_stellar_account_info(public_key: str):
    """
    Get Stellar account information.
    
    Returns balance, transaction count, etc.
    """
    try:
        account = stellar_client.server.accounts().account_id(public_key).call()
        
        # Extract native balance (XLM)
        native_balance = next(
            (b['balance'] for b in account['balances'] if b['asset_type'] == 'native'),
            '0'
        )
        
        return {
            "public_key": public_key,
            "balance": native_balance,
            "sequence": account['sequence'],
            "subentry_count": account['subentry_count']
        }
        
    except Exception as e:
        logger.error(f"Failed to get account info: {e}")
        raise HTTPException(status_code=404, detail="Account not found")


@router.post("/stellar/create-account")
async def create_stellar_account():
    """
    Create Stellar account for Privy user.
    
    Called automatically on user registration.
    Generates keypair, encrypts secret, stores in database.
    """
    try:
        # TODO: Get from authenticated user session
        privy_user_id = "temp_user_id"
        
        # Create new Stellar account
        account_data = stellar_client.create_account_for_user(privy_user_id)
        
        # Fund testnet account
        if stellar_client.network == "testnet":
            await stellar_client.fund_testnet_account(account_data['public_key'])
        
        # TODO: Store in InsForge database
        # UPDATE users SET 
        #   stellar_public_key = account_data['public_key'],
        #   stellar_encrypted_secret = account_data['encrypted_secret']
        # WHERE id = privy_user_id
        
        return {
            "success": True,
            "message": "Stellar account created",
            "public_key": account_data['public_key']
        }
        
    except Exception as e:
        logger.error(f"Failed to create Stellar account: {e}")
        raise HTTPException(status_code=500, detail="Account creation failed")

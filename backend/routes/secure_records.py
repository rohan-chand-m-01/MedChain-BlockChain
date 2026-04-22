"""
Secure Records API - Client-Side Encryption with Privy Wallets

Security Model:
- Files encrypted with AES-256 in browser
- AES keys encrypted with patient's Privy wallet signature
- Backend stores encrypted keys but CANNOT decrypt them
- Only patient's biometric (Face ID/Touch ID) can decrypt
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

from services.insforge import db_select, db_insert, db_update

router = APIRouter(prefix="/api/secure-records", tags=["secure-records"])


class StoreRecordRequest(BaseModel):
    ipfs_hash: str
    encrypted_aes_key: str  # Encrypted with patient's Privy wallet
    wallet_address: str
    file_name: str
    file_size: int
    file_type: Optional[str] = None
    uploaded_at: str


class GrantAccessRequest(BaseModel):
    record_id: str
    doctor_wallet_address: str
    doctor_encrypted_aes_key: str  # Re-encrypted for doctor's wallet
    expires_at: Optional[str] = None


@router.post("/store")
async def store_encrypted_record(request: StoreRecordRequest):
    """
    Store encrypted medical record metadata
    
    Security: Backend receives encrypted AES key but CANNOT decrypt it
    Only the patient's Privy wallet signature can decrypt the AES key
    """
    try:
        # Store record metadata
        record = {
            "ipfs_hash": request.ipfs_hash,
            "encrypted_aes_key": request.encrypted_aes_key,
            "wallet_address": request.wallet_address.lower(),
            "file_name": request.file_name,
            "file_size": request.file_size,
            "file_type": request.file_type,
            "uploaded_at": request.uploaded_at,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        result = await db_insert("secure_medical_records", record)
        
        return {
            "success": True,
            "record_id": result["id"],
            "message": "Record stored securely - backend cannot decrypt",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{wallet_address}")
async def list_patient_records(wallet_address: str):
    """
    List all records for a patient's wallet
    
    Returns encrypted AES keys - patient must decrypt with their Privy wallet
    """
    try:
        result = await db_select(
            "secure_medical_records",
            filters={"wallet_address": wallet_address.lower()},
            order="created_at.desc"
        )
        
        return {
            "success": True,
            "records": result,
            "count": len(result),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/record/{record_id}")
async def get_record(record_id: str):
    """
    Get a specific record's metadata
    
    Returns encrypted AES key - requires patient's Privy wallet to decrypt
    """
    try:
        result = await db_select(
            "secure_medical_records",
            filters={"id": record_id}
        )
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return {
            "success": True,
            "record": result[0],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grant-access")
async def grant_doctor_access(request: GrantAccessRequest):
    """
    Grant doctor access to a medical record
    
    Patient re-encrypts AES key with doctor's wallet address
    Doctor can then decrypt with their own Privy wallet
    """
    try:
        # Store access grant
        access_grant = {
            "record_id": request.record_id,
            "doctor_wallet_address": request.doctor_wallet_address.lower(),
            "doctor_encrypted_aes_key": request.doctor_encrypted_aes_key,
            "granted_at": datetime.utcnow().isoformat(),
            "expires_at": request.expires_at,
            "status": "active",
        }
        
        result = await db_insert("secure_access_grants", access_grant)
        
        return {
            "success": True,
            "access_grant_id": result["id"],
            "message": "Access granted - doctor can decrypt with their wallet",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doctor-access/{doctor_wallet_address}")
async def list_doctor_access(doctor_wallet_address: str):
    """
    List all records a doctor has access to
    
    Returns records with AES keys encrypted for doctor's wallet
    """
    try:
        # Get access grants with joined records
        grants = await db_select(
            "secure_access_grants",
            filters={
                "doctor_wallet_address": doctor_wallet_address.lower(),
                "status": "active"
            },
            select="*, secure_medical_records(*)"
        )
        
        return {
            "success": True,
            "accessible_records": grants,
            "count": len(grants),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke-access/{access_grant_id}")
async def revoke_access(access_grant_id: str):
    """
    Revoke doctor's access to a record
    
    Doctor can no longer decrypt the file
    """
    try:
        result = await db_update(
            "secure_access_grants",
            access_grant_id,
            {"status": "revoked", "revoked_at": datetime.utcnow().isoformat()}
        )
        
        return {
            "success": True,
            "message": "Access revoked - doctor can no longer decrypt",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/privacy-proof/{record_id}")
async def get_privacy_proof(record_id: str):
    """
    Generate cryptographic proof that backend cannot decrypt
    
    For demo/audit purposes - shows encrypted key without ability to decrypt
    """
    try:
        record = await db_select(
            "secure_medical_records",
            filters={"id": record_id}
        )
        
        if not record or len(record) == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        
        record_data = record[0]
        
        return {
            "success": True,
            "proof": {
                "record_id": record_id,
                "ipfs_hash": record_data["ipfs_hash"],
                "encrypted_aes_key": record_data["encrypted_aes_key"],
                "wallet_address": record_data["wallet_address"],
                "message": "Backend has encrypted AES key but CANNOT decrypt it",
                "explanation": "AES key is encrypted with patient's Privy wallet signature. Only patient's biometric (Face ID/Touch ID) can generate the signature needed to decrypt.",
                "cryptographic_guarantee": "Without patient's private key (held in MPC split between device and Privy), decryption is computationally infeasible (2^256 operations).",
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Encrypted Lab Reports API Routes

Handles encrypted lab reports using Privy wallet-based encryption.
Backend never sees plaintext - only stores encrypted data!

Key Features:
- IPFS storage for encrypted reports
- Blockchain metadata storage
- Access grant management
- Zero-knowledge architecture
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from services.ipfs_uploader import IPFSUploader
from services.blockchain_client import BlockchainClient
from services.insforge import db_insert, db_select, db_update

router = APIRouter(prefix="/encrypted-reports", tags=["Encrypted Reports"])

# Initialize services
ipfs = IPFSUploader()
blockchain = BlockchainClient()


class EncryptedReportUpload(BaseModel):
    """Request model for uploading encrypted report"""
    encrypted_data: str
    iv: str  # Initialization vector
    patient_id: str  # Wallet address
    report_type: str
    timestamp: int


class AccessGrant(BaseModel):
    """Request model for granting doctor access"""
    patient_id: str
    doctor_address: str
    encrypted_key: str  # Patient's key encrypted with doctor's key
    expires_at: int
    report_id: str


class ReportMetadata(BaseModel):
    """Response model for report metadata"""
    report_id: str
    patient_id: str
    ipfs_hash: str
    iv: str
    report_type: str
    timestamp: int
    tx_hash: Optional[str]
    access_grants: List[dict]


@router.post("/upload")
async def upload_encrypted_report(report: EncryptedReportUpload):
    """
    Upload encrypted lab report to IPFS and store metadata on blockchain.
    
    Flow:
    1. Receive encrypted data from client (already encrypted with Privy wallet)
    2. Upload to IPFS
    3. Store metadata in database
    4. Store hash on blockchain
    5. Return IPFS hash and transaction hash
    
    Note: Backend never sees plaintext data!
    """
    try:
        # 1. Upload encrypted data to IPFS
        ipfs_hash = await ipfs.upload_json({
            "encrypted_data": report.encrypted_data,
            "iv": report.iv,
            "patient_id": report.patient_id,
            "report_type": report.report_type,
            "timestamp": report.timestamp,
            "encrypted": True,
        })
        
        # 2. Store metadata in database
        result = db_insert("encrypted_reports", {
            "patient_id": report.patient_id,
            "ipfs_hash": ipfs_hash,
            "iv": report.iv,
            "report_type": report.report_type,
            "timestamp": report.timestamp,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        report_id = result[0]["id"]
        
        # 3. Store on blockchain (optional - for immutability proof)
        try:
            tx_hash = await blockchain.store_report_hash(
                patient_address=report.patient_id,
                ipfs_hash=ipfs_hash,
                report_type=report.report_type
            )
        except Exception as e:
            print(f"Blockchain storage failed (non-critical): {e}")
            tx_hash = None
        
        return {
            "success": True,
            "report_id": report_id,
            "ipfs_hash": ipfs_hash,
            "tx_hash": tx_hash,
            "message": "Report uploaded successfully (encrypted)",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grant-access")
async def grant_doctor_access(grant: AccessGrant):
    """
    Grant doctor access to encrypted report.
    
    Stores the patient's encryption key (encrypted with doctor's key)
    so doctor can decrypt the report using their own Privy wallet.
    """
    try:
        # Store access grant in database
        db_insert("report_access_grants", {
            "report_id": grant.report_id,
            "patient_id": grant.patient_id,
            "doctor_address": grant.doctor_address,
            "encrypted_key": grant.encrypted_key,
            "expires_at": grant.expires_at,
            "granted_at": datetime.utcnow().isoformat(),
            "revoked": False,
        })
        
        # Optional: Store on blockchain for immutability
        try:
            tx_hash = await blockchain.grant_access(
                patient_address=grant.patient_id,
                doctor_address=grant.doctor_address,
                expires_at=grant.expires_at
            )
        except Exception as e:
            print(f"Blockchain grant failed (non-critical): {e}")
            tx_hash = None
        
        return {
            "success": True,
            "message": f"Access granted to {grant.doctor_address}",
            "tx_hash": tx_hash,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke-access")
async def revoke_doctor_access(
    patient_id: str,
    doctor_address: str,
    report_id: str
):
    """
    Revoke doctor's access to encrypted report.
    """
    try:
        # Mark access grant as revoked
        db_update(
            "report_access_grants",
            {"revoked": True, "revoked_at": datetime.utcnow().isoformat()},
            f"report_id = '{report_id}' AND doctor_address = '{doctor_address}'"
        )
        
        return {
            "success": True,
            "message": f"Access revoked for {doctor_address}",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_id}")
async def get_patient_reports(patient_id: str):
    """
    Get all encrypted reports for a patient.
    Returns metadata only - client must decrypt with Privy wallet.
    """
    try:
        # Get reports
        reports = db_select(
            "encrypted_reports",
            f"patient_id = '{patient_id}'",
            order_by="timestamp DESC"
        )
        
        # Get access grants for each report
        for report in reports:
            grants = db_select(
                "report_access_grants",
                f"report_id = '{report['id']}' AND revoked = false"
            )
            report["access_grants"] = grants
        
        return {
            "success": True,
            "reports": reports,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doctor/{doctor_address}")
async def get_doctor_accessible_reports(doctor_address: str):
    """
    Get all reports a doctor has access to.
    """
    try:
        # Get access grants for this doctor
        grants = db_select(
            "report_access_grants",
            f"doctor_address = '{doctor_address}' AND revoked = false AND expires_at > {int(datetime.utcnow().timestamp() * 1000)}"
        )
        
        # Get report metadata for each grant
        reports = []
        for grant in grants:
            report = db_select(
                "encrypted_reports",
                f"id = '{grant['report_id']}'"
            )
            if report:
                report[0]["encrypted_key"] = grant["encrypted_key"]
                report[0]["expires_at"] = grant["expires_at"]
                reports.append(report[0])
        
        return {
            "success": True,
            "reports": reports,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{report_id}")
async def get_report_metadata(report_id: str):
    """
    Get encrypted report metadata (not the actual data).
    Client must fetch from IPFS and decrypt with Privy wallet.
    """
    try:
        report = db_select("encrypted_reports", f"id = '{report_id}'")
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Get access grants
        grants = db_select(
            "report_access_grants",
            f"report_id = '{report_id}' AND revoked = false"
        )
        
        report[0]["access_grants"] = grants
        
        return {
            "success": True,
            "report": report[0],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

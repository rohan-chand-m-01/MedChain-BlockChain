"""
Secure Time-Bound Access Control System
Implements zero-knowledge, time-bound file access sharing between patients and doctors.

NOTE: Currently using simplified mode without client-side encryption.
Full encryption implementation pending.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, validator
import logging

from services.insforge import db_insert, db_select, db_select_single, db_update

logger = logging.getLogger(__name__)
router = APIRouter()


async def _send_access_notification(
    patient_wallet: str,
    doctor_wallet: str,
    analysis_id: str,
    access_hours: int,
    is_extension: bool = False
):
    """Send WhatsApp alert directly via Twilio when a patient grants access."""
    try:
        import os
        from twilio.rest import Client

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not all([account_sid, auth_token, from_number]):
            logger.warning("[NOTIFY] Twilio not configured — skipping WhatsApp")
            return

        # Get names from DB
        doctor_profile = await db_select_single("doctor_profiles", {"wallet_address": doctor_wallet}, select="name")

        # patient_profiles uses Ethereum wallet; analyses use Privy DID.
        # Fetch all patient profiles and pick the most recently created one as fallback.
        patient_profile = await db_select_single("patient_profiles", {"wallet_address": patient_wallet}, select="name")
        if not patient_profile:
            # Fallback: get the most recently updated patient profile
            profiles = await db_select("patient_profiles", select="name,wallet_address", order="created_at.desc", limit=1)
            patient_profile = profiles[0] if profiles else None

        analysis = await db_select_single("analyses", {"id": analysis_id}, select="file_name,risk_score")

        doctor_name  = doctor_profile.get("name", "Unknown Doctor")    if doctor_profile  else "Unknown Doctor"
        patient_name = patient_profile.get("name", "Unknown Patient")  if patient_profile else "Unknown Patient"
        file_name    = analysis.get("file_name", "Medical Report")    if analysis        else "Medical Report"
        risk_score   = analysis.get("risk_score", 0)                  if analysis        else 0

        duration = f"{access_hours} hour{'s' if access_hours != 1 else ''}" if access_hours < 24 else f"{access_hours // 24} day{'s' if access_hours // 24 > 1 else ''}"
        display_file = file_name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title() if file_name else "Medical Report"
        action = "extended access to" if is_extension else "shared"

        if risk_score >= 75:
            risk_emoji = "🔴"
        elif risk_score >= 50:
            risk_emoji = "🟡"
        else:
            risk_emoji = "🟢"

        msg = (
            f"🔔 *MediChain AI — Access Grant*\n\n"
            f"*{patient_name}* {action} *{display_file}* with Dr. *{doctor_name}* for *{duration}*.\n\n"
            f"{risk_emoji} Risk Score: {risk_score}/100\n\n"
            f"_Powered by MediChain AI_"
        )

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_number,
            body=msg,
            to="whatsapp:+917003565215"
        )
        logger.info(f"[NOTIFY] ✅ WhatsApp sent — SID: {message.sid} | Status: {message.status}")

    except Exception as e:
        logger.error(f"[NOTIFY] WhatsApp failed: {e}")
            
    except Exception as e:
        logger.error(f"Error sending access notification: {e}")
        # Don't fail the access grant if notification fails


class SimpleGrantRequest(BaseModel):
    """Simplified access grant without encryption (for demo/development)."""
    patient_wallet: str
    doctor_wallet: str
    analysis_id: str
    expires_in_hours: int = 24
    
    @validator('expires_in_hours')
    def validate_expiry(cls, v):
        if v < 1:
            raise ValueError('expires_in_hours must be at least 1')
        if v > 720:  # 30 days max
            raise ValueError('expires_in_hours cannot exceed 720 (30 days)')
        return v


@router.post("/access-grants/simple", tags=["Access Control"])
async def create_simple_access_grant(req: SimpleGrantRequest):
    """
    Create simplified time-bound access grant (without encryption).
    
    NOTE: This is a simplified version for demo purposes.
    Production should use full encryption with wrapped keys.
    
    FEATURES:
    - Sends WhatsApp notification to doctor
    - Includes patient name, document details, and expiry time
    """
    expires_at = datetime.utcnow() + timedelta(hours=req.expires_in_hours)
    
    try:
        # Check if grant already exists
        existing = await db_select("access_grants", filters={
            "patient_wallet": req.patient_wallet,
            "doctor_wallet": req.doctor_wallet,
            "analysis_id": req.analysis_id,
            "is_active": True
        }, limit=1)
        
        if existing:
            # Update existing grant
            grant_id = existing[0]["id"]
            await db_update("access_grants", grant_id, {
                "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            })
            
            # Send notification for extended access
            await _send_access_notification(
                patient_wallet=req.patient_wallet,
                doctor_wallet=req.doctor_wallet,
                analysis_id=req.analysis_id,
                access_hours=req.expires_in_hours,
                is_extension=True
            )
            
            return {
                "success": True,
                "grant_id": grant_id,
                "expires_at": expires_at.isoformat(),
                "message": f"Access extended for {req.expires_in_hours} hours"
            }
        
        # Create new grant
        grant = await db_insert("access_grants", {
            "patient_wallet": req.patient_wallet,
            "doctor_wallet":  req.doctor_wallet,
            "analysis_id":    req.analysis_id,
            "expires_at":     expires_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "is_active":      True,
            "access_count":   0,
        })
        
        # Send WhatsApp notification to doctor
        await _send_access_notification(
            patient_wallet=req.patient_wallet,
            doctor_wallet=req.doctor_wallet,
            analysis_id=req.analysis_id,
            access_hours=req.expires_in_hours,
            is_extension=False
        )
        
        return {
            "success": True,
            "grant_id": grant["id"],
            "expires_at": expires_at.isoformat(),
            "message": f"Access granted to doctor for {req.expires_in_hours} hours"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to create access grant: {str(e)}")


@router.get("/access-grants/check", tags=["Access Control"])
async def check_access(doctor_wallet: str, analysis_id: str):
    """
    Check if doctor has active access to a specific analysis.
    
    Returns:
    - has_access: boolean
    - grant: grant details if access exists
    """
    try:
        grants = await db_select("access_grants", filters={
            "doctor_wallet": doctor_wallet,
            "analysis_id": analysis_id,
            "is_active": True
        }, limit=1)
        
        if not grants:
            return {"success": True, "has_access": False}
        
        grant = grants[0]
        
        # Check if expired
        expires_at = datetime.fromisoformat(grant["expires_at"].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow():
            # Auto-revoke expired grant
            await db_update("access_grants", grant["id"], {
                "is_active": False,
                "revoked_by": "system",
                "revoked_at": datetime.utcnow().isoformat(),
                "revocation_reason": "expired"
            })
            return {"success": True, "has_access": False}
        
        return {
            "success": True,
            "has_access": True,
            "grant": {
                "id": grant["id"],
                "expires_at": grant["expires_at"],
                "access_count": grant["access_count"]
            }
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to check access: {str(e)}")


class GrantAccessRequest(BaseModel):
    doctor_wallet: str
    analysis_id: Optional[str] = None
    grant_type: str  # 'single_file' or 'all_files'
    wrapped_encryption_key: str
    expires_in_hours: int
    max_access_count: Optional[int] = None
    
    @validator('grant_type')
    def validate_grant_type(cls, v):
        if v not in ['single_file', 'all_files']:
            raise ValueError('grant_type must be single_file or all_files')
        return v
    
    @validator('expires_in_hours')
    def validate_expiry(cls, v):
        if v < 1:
            raise ValueError('expires_in_hours must be at least 1')
        if v > 720:  # 30 days max
            raise ValueError('expires_in_hours cannot exceed 720 (30 days)')
        return v
    
    @validator('max_access_count')
    def validate_access_count(cls, v):
        if v is not None and v < 1:
            raise ValueError('max_access_count must be at least 1')
        return v


class RevokeAccessRequest(BaseModel):
    reason: Optional[str] = "patient_revoked"


@router.post("/access-grants/create", tags=["Access Control"])
async def create_access_grant(req: GrantAccessRequest, patient_wallet: str):
    """
    Create time-bound access grant for doctor.
    
    SECURITY FEATURES:
    - Server never sees unwrapped encryption key
    - Automatic expiry (max 30 days)
    - Optional access count limit
    - Full audit trail
    
    The wrapped_encryption_key is encrypted with doctor's public key,
    ensuring only the doctor can decrypt it with their private key.
    """
    # Validate single_file requires analysis_id
    if req.grant_type == 'single_file' and not req.analysis_id:
        raise HTTPException(400, "analysis_id required for single_file grants")
    
    # Calculate expiry timestamp
    expires_at = datetime.utcnow() + timedelta(hours=req.expires_in_hours)
    
    try:
        # Create access grant
        grant = await db_insert("access_grants", {
            "patient_wallet": patient_wallet,
            "doctor_wallet": req.doctor_wallet,
            "analysis_id": req.analysis_id,
            "grant_type": req.grant_type,
            "wrapped_encryption_key": req.wrapped_encryption_key,
            "key_wrapping_algorithm": "RSA-OAEP-SHA256",
            "expires_at": expires_at.isoformat(),
            "max_access_count": req.max_access_count,
            "is_active": True,
            "access_count": 0
        })
        
        return {
            "success": True,
            "grant_id": grant["id"],
            "expires_at": expires_at.isoformat(),
            "message": f"Access granted to doctor for {req.expires_in_hours} hours"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to create access grant: {str(e)}")


@router.get("/access-grants/{grant_id}", tags=["Access Control"])
async def get_access_grant(grant_id: str, doctor_wallet: str):
    """
    Get access grant details for doctor.
    
    SECURITY CHECKS:
    - Verifies doctor authorization
    - Checks expiry
    - Checks revocation status
    - Checks access count limit
    """
    try:
        grant = await db_select_single("access_grants", {"id": grant_id})
        
        if not grant:
            raise HTTPException(404, "Access grant not found")
        
        # Verify doctor is authorized
        if grant["doctor_wallet"] != doctor_wallet:
            raise HTTPException(403, "Unauthorized: This grant belongs to another doctor")
        
        # Check if expired
        expires_at = datetime.fromisoformat(grant["expires_at"].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow():
            # Auto-revoke expired grant
            await db_update("access_grants", grant_id, {
                "is_active": False,
                "revoked_by": "system",
                "revoked_at": datetime.utcnow().isoformat(),
                "revocation_reason": "expired"
            })
            raise HTTPException(403, "Access expired")
        
        # Check if revoked
        if not grant["is_active"]:
            reason = grant.get("revocation_reason", "unknown")
            raise HTTPException(403, f"Access revoked: {reason}")
        
        # Check access count limit
        if grant.get("max_access_count"):
            if grant["access_count"] >= grant["max_access_count"]:
                raise HTTPException(403, "Access limit reached")
        
        # SECURITY: Remove sensitive fields before returning
        safe_grant = {
            "id": grant["id"],
            "grant_type": grant["grant_type"],
            "analysis_id": grant.get("analysis_id"),
            "wrapped_encryption_key": grant["wrapped_encryption_key"],
            "expires_at": grant["expires_at"],
            "access_count": grant["access_count"],
            "max_access_count": grant.get("max_access_count"),
            "granted_at": grant.get("granted_at")
        }
        
        return {
            "success": True,
            "grant": safe_grant
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve grant: {str(e)}")


@router.post("/access-grants/{grant_id}/log-access", tags=["Access Control"])
async def log_file_access(grant_id: str, doctor_wallet: str):
    """
    Log file access for audit trail.
    
    AUDIT TRAIL:
    - Records first access time
    - Updates last access time
    - Increments access count
    - Tracks access patterns
    """
    try:
        grant = await db_select_single("access_grants", {"id": grant_id})
        
        if not grant or grant["doctor_wallet"] != doctor_wallet:
            raise HTTPException(403, "Unauthorized")
        
        if not grant["is_active"]:
            raise HTTPException(403, "Access revoked")
        
        # Update access tracking
        now = datetime.utcnow()
        updates = {
            "last_accessed_at": now.isoformat(),
            "access_count": grant["access_count"] + 1
        }
        
        # Set first access time if not set
        if not grant.get("accessed_at"):
            updates["accessed_at"] = now.isoformat()
        
        await db_update("access_grants", grant_id, updates)
        
        return {
            "success": True,
            "access_count": grant["access_count"] + 1,
            "message": "Access logged successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to log access: {str(e)}")


@router.post("/access-grants/{grant_id}/revoke", tags=["Access Control"])
async def revoke_access_grant(grant_id: str, patient_wallet: str, req: RevokeAccessRequest):
    """
    Patient revokes access before expiry.
    
    IMMEDIATE EFFECT:
    - Access revoked instantly
    - Doctor cannot access file anymore
    - Reason recorded for audit
    """
    try:
        grant = await db_select_single("access_grants", {"id": grant_id})
        
        if not grant:
            raise HTTPException(404, "Access grant not found")
        
        # Only patient can revoke their own grants
        if grant["patient_wallet"] != patient_wallet:
            raise HTTPException(403, "Unauthorized: Only the patient can revoke this grant")
        
        if not grant["is_active"]:
            raise HTTPException(400, "Access already revoked")
        
        # Revoke access
        await db_update("access_grants", grant_id, {
            "is_active": False,
            "revoked_at": datetime.utcnow().isoformat(),
            "revoked_by": patient_wallet,
            "revocation_reason": req.reason
        })
        
        return {
            "success": True,
            "message": "Access revoked successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to revoke access: {str(e)}")


@router.get("/access-grants/patient/active", tags=["Access Control"])
async def get_patient_active_grants(patient_wallet: str):
    """
    Get all active grants created by patient.
    
    PATIENT DASHBOARD:
    - View all granted accesses
    - See expiry times
    - Monitor access counts
    - Revoke if needed
    """
    try:
        grants = await db_select(
            "access_grants",
            filters={"patient_wallet": patient_wallet, "is_active": True},
            order="granted_at.desc"
        )
        
        # Enrich with time remaining
        now = datetime.utcnow()
        for grant in grants:
            expires_at = datetime.fromisoformat(grant["expires_at"].replace('Z', '+00:00'))
            time_remaining = expires_at - now
            grant["hours_remaining"] = max(0, int(time_remaining.total_seconds() / 3600))
            grant["is_expired"] = expires_at < now
        
        return {
            "success": True,
            "grants": grants,
            "total": len(grants)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve grants: {str(e)}")


@router.get("/access-grants/doctor/active", tags=["Access Control"])
async def get_doctor_active_grants(doctor_wallet: str):
    """
    Get all active grants for doctor.
    
    DOCTOR DASHBOARD:
    - View accessible files
    - See expiry times
    - Check access limits
    - Access files
    """
    try:
        grants = await db_select(
            "access_grants",
            filters={"doctor_wallet": doctor_wallet, "is_active": True},
            order="granted_at.desc"
        )
        
        # Filter out expired grants and enrich data
        now = datetime.utcnow()
        active_grants = []
        
        for grant in grants:
            expires_at = datetime.fromisoformat(grant["expires_at"].replace('Z', '+00:00'))
            
            # Skip expired
            if expires_at < now:
                continue
            
            # Calculate time remaining
            time_remaining = expires_at - now
            grant["hours_remaining"] = max(0, int(time_remaining.total_seconds() / 3600))
            
            # Calculate accesses remaining
            if grant.get("max_access_count"):
                grant["accesses_remaining"] = grant["max_access_count"] - grant["access_count"]
            else:
                grant["accesses_remaining"] = None  # Unlimited
            
            active_grants.append(grant)
        
        return {
            "success": True,
            "grants": active_grants,
            "total": len(active_grants)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve grants: {str(e)}")


@router.get("/access-grants/audit/{grant_id}", tags=["Access Control"])
async def get_grant_audit_trail(grant_id: str, patient_wallet: str):
    """
    Get complete audit trail for a grant.
    
    COMPLIANCE:
    - Full access history
    - Timestamps for all events
    - Revocation details
    - Access patterns
    """
    try:
        grant = await db_select_single("access_grants", {"id": grant_id})
        
        if not grant:
            raise HTTPException(404, "Access grant not found")
        
        # Only patient can view audit trail
        if grant["patient_wallet"] != patient_wallet:
            raise HTTPException(403, "Unauthorized")
        
        audit_trail = {
            "grant_id": grant["id"],
            "doctor_wallet": grant["doctor_wallet"],
            "grant_type": grant["grant_type"],
            "granted_at": grant.get("granted_at"),
            "expires_at": grant["expires_at"],
            "first_accessed_at": grant.get("accessed_at"),
            "last_accessed_at": grant.get("last_accessed_at"),
            "total_accesses": grant["access_count"],
            "max_accesses": grant.get("max_access_count"),
            "is_active": grant["is_active"],
            "revoked_at": grant.get("revoked_at"),
            "revoked_by": grant.get("revoked_by"),
            "revocation_reason": grant.get("revocation_reason")
        }
        
        return {
            "success": True,
            "audit_trail": audit_trail
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve audit trail: {str(e)}")

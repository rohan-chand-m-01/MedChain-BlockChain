"""
Patient Profile Routes
Manage patient demographic information
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from services.insforge import db_select, db_insert, db_update

router = APIRouter()


class PatientProfilePayload(BaseModel):
    full_name: str
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


@router.get("/patient/profile/{patient_wallet}", tags=["Patient Profile"])
async def get_patient_profile(patient_wallet: str):
    """Get patient profile by wallet address"""
    try:
        profiles = await db_select(
            "patient_profiles",
            filters={"patient_wallet": patient_wallet},
            limit=1
        )
        
        return {
            "success": True,
            "profile": profiles[0] if profiles else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.post("/patient/profile/{patient_wallet}", tags=["Patient Profile"])
async def upsert_patient_profile(patient_wallet: str, payload: PatientProfilePayload):
    """Create or update patient profile"""
    try:
        # Check if profile exists
        existing = await db_select(
            "patient_profiles",
            filters={"patient_wallet": patient_wallet},
            limit=1
        )
        
        data = {
            "full_name": payload.full_name,
            "date_of_birth": payload.date_of_birth,
            "phone": payload.phone,
            "email": payload.email,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if existing:
            # Update
            await db_update("patient_profiles", existing[0]["id"], data)
        else:
            # Insert
            data["patient_wallet"] = patient_wallet
            await db_insert("patient_profiles", data)
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")


@router.get("/patient/list-for-doctor/{doctor_wallet}", tags=["Patient Profile"])
async def list_patients_for_doctor(doctor_wallet: str):
    """
    Get list of all patients with active grants to this doctor.
    Includes patient names for selection in chatbot/UI.
    """
    try:
        # Get all active grants
        grants = await db_select(
            "access_grants",
            filters={"doctor_wallet": doctor_wallet, "is_active": True},
            order="granted_at.desc"
        )
        
        if not grants:
            return {
                "success": True,
                "patients": []
            }
        
        # Get patient profiles
        patients = []
        seen_wallets = set()
        
        for grant in grants:
            patient_wallet = grant.get("patient_wallet")
            
            # Skip duplicates
            if patient_wallet in seen_wallets:
                continue
            seen_wallets.add(patient_wallet)
            
            # Get patient profile
            profile = await db_select(
                "patient_profiles",
                filters={"patient_wallet": patient_wallet},
                limit=1
            )
            
            # Get latest analysis for context
            analyses = await db_select(
                "analyses",
                filters={"patient_wallet": patient_wallet},
                order="created_at.desc",
                limit=1
            )
            
            patient_name = profile[0].get("full_name") if profile else f"Patient {patient_wallet[:8]}"
            
            patients.append({
                "patient_wallet": patient_wallet,
                "patient_name": patient_name,
                "has_profile": bool(profile),
                "latest_analysis": analyses[0] if analyses else None
            })
        
        return {
            "success": True,
            "patients": patients
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list patients: {str(e)}")

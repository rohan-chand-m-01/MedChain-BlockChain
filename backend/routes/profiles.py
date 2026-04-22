"""
Profile Management Routes
Handles patient and doctor profile CRUD operations including phone numbers
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from services.insforge import db_select_single, db_insert, db_update
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Profiles"])


class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class DoctorProfileUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None


@router.get("/profiles/patient/{wallet_address}")
async def get_patient_profile(wallet_address: str):
    """Get patient profile by wallet address"""
    try:
        profile = await db_select_single(
            table="patient_profiles",
            filters={"wallet_address": wallet_address},
            select="*"
        )
        
        if not profile:
            return {
                "exists": False,
                "wallet_address": wallet_address
            }
        
        # Map database fields to expected API fields
        return {
            "exists": True,
            "patient_wallet": profile.get("wallet_address"),
            "full_name": profile.get("name"),
            "whatsapp_phone": profile.get("whatsapp_phone"),
            "date_of_birth": profile.get("date_of_birth"),
            "email": profile.get("email"),
            "gender": profile.get("gender"),
            "blood_type": profile.get("blood_type"),
            "allergies": profile.get("allergies"),
            "emergency_contact": profile.get("emergency_contact"),
            "emergency_contact_phone": profile.get("emergency_contact_phone"),
            **profile
        }
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/patient/{wallet_address}")
async def create_or_update_patient_profile(
    wallet_address: str,
    profile: PatientProfileUpdate
):
    """Create or update patient profile"""
    try:
        # Check if profile exists
        existing = await db_select_single(
            table="patient_profiles",
            filters={"wallet_address": wallet_address},
            select="id"
        )
        
        # Prepare data (only include non-None fields)
        data = {"wallet_address": wallet_address}
        if profile.full_name:
            data["name"] = profile.full_name  # Map full_name to name
        if profile.whatsapp_phone:
            # Ensure WhatsApp format
            phone = profile.whatsapp_phone
            if not phone.startswith("whatsapp:"):
                phone = f"whatsapp:{phone}"
            data["whatsapp_phone"] = phone
        if profile.date_of_birth:
            data["date_of_birth"] = profile.date_of_birth
        if profile.email:
            data["email"] = profile.email
        if profile.gender:
            data["gender"] = profile.gender
        if profile.blood_type:
            data["blood_type"] = profile.blood_type
        if profile.allergies:
            data["allergies"] = profile.allergies
        if profile.emergency_contact:
            data["emergency_contact"] = profile.emergency_contact
        if profile.emergency_contact_phone:
            phone = profile.emergency_contact_phone
            if not phone.startswith("whatsapp:"):
                phone = f"whatsapp:{phone}"
            data["emergency_contact_phone"] = phone
        
        if existing:
            # Update existing profile using the ID
            await db_update(
                table="patient_profiles",
                row_id=existing["id"],
                payload=data
            )
            logger.info(f"✓ Updated patient profile for {wallet_address}")
        else:
            # Create new profile
            if not profile.full_name:
                raise HTTPException(status_code=400, detail="full_name is required for new profiles")
            
            # Ensure required fields are set for new profiles
            data["name"] = profile.full_name  # name is required (NOT NULL)
            data["wallet_address"] = wallet_address  # wallet_address is required (NOT NULL)
            
            logger.info(f"Creating new patient profile with data: {data}")
            try:
                result = await db_insert("patient_profiles", data)
                logger.info(f"✓ Created patient profile for {wallet_address}: {result}")
            except Exception as e:
                logger.error(f"Failed to create patient profile: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")
        
        # Return updated profile
        return await get_patient_profile(wallet_address)
        
    except Exception as e:
        logger.error(f"Error creating/updating patient profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/doctor/{wallet_address}")
async def get_doctor_profile(wallet_address: str):
    """Get doctor profile by wallet address"""
    try:
        profile = await db_select_single(
            table="doctor_profiles",
            filters={"wallet_address": wallet_address},
            select="*"
        )
        
        if not profile:
            return {
                "exists": False,
                "wallet_address": wallet_address
            }
        
        return {
            "exists": True,
            **profile
        }
    except Exception as e:
        logger.error(f"Error fetching doctor profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/doctor/{wallet_address}")
async def create_or_update_doctor_profile(
    wallet_address: str,
    profile: DoctorProfileUpdate
):
    """Create or update doctor profile"""
    try:
        # Check if profile exists
        existing = await db_select_single(
            table="doctor_profiles",
            filters={"wallet_address": wallet_address},
            select="id"
        )
        
        # Prepare data (only include non-None fields)
        data = {"wallet_address": wallet_address}
        if profile.name:
            data["name"] = profile.name
        if profile.specialty:
            data["specialty"] = profile.specialty
        if profile.whatsapp_phone:
            # Ensure WhatsApp format
            phone = profile.whatsapp_phone
            if not phone.startswith("whatsapp:"):
                phone = f"whatsapp:{phone}"
            data["whatsapp_phone"] = phone
        if profile.email:
            data["email"] = profile.email
        if profile.bio:
            data["bio"] = profile.bio
        
        if existing:
            # Update existing profile using the ID
            await db_update(
                table="doctor_profiles",
                row_id=existing["id"],
                payload=data
            )
            logger.info(f"✓ Updated doctor profile for {wallet_address}")
        else:
            # Create new profile
            if not profile.name:
                raise HTTPException(status_code=400, detail="name is required for new profiles")
            
            await db_insert("doctor_profiles", [data])
            logger.info(f"✓ Created doctor profile for {wallet_address}")
        
        # Return updated profile
        return await get_doctor_profile(wallet_address)
        
    except Exception as e:
        logger.error(f"Error creating/updating doctor profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/doctors/all")
async def get_all_doctors():
    """Get all doctor profiles (for patient to select doctors)"""
    try:
        from services.insforge import db_select
        
        doctors = await db_select(
            table="doctor_profiles",
            select="wallet_address,name,specialty,bio,whatsapp_phone,email",
            filters={}
        )
        
        return {"doctors": doctors or []}
    except Exception as e:
        logger.error(f"Error fetching all doctors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

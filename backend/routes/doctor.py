from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from services.insforge import db_select, db_insert, db_update, db_select_single

router = APIRouter()

class DoctorProfilePayload(BaseModel):
    name: str
    specialty: str
    bio: str

class ConsultationNotePayload(BaseModel):
    patient_wallet: str
    analysis_id: str
    note: str

@router.get("/doctors")
async def get_all_doctors(specialty: str = None):
    try:
        filters = {}
        if specialty:
            # Note: exact match here, might need ilike equivalent in db_select if supported
            # Insforge db_select in this project seems to only support exact match or we can fetch all and filter
            pass
            
        profiles = await db_select("doctor_profiles", order="name.asc")
        
        if specialty and profiles:
            profiles = [p for p in profiles if specialty.lower() in p.get("specialty", "").lower()]
            
        return {"success": True, "doctors": profiles or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch doctors: {str(e)}")


@router.get("/doctor/profile/{wallet}")
async def get_doctor_profile(wallet: str):
    if not wallet:
        raise HTTPException(status_code=400, detail="wallet address is required")
    try:
        profiles = await db_select("doctor_profiles", filters={"wallet_address": wallet}, limit=1)
        return {"success": True, "profiles": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.post("/doctor/profile/{wallet}")
async def upsert_doctor_profile(wallet: str, payload: DoctorProfilePayload):
    try:
        profiles = await db_select("doctor_profiles", filters={"wallet_address": wallet}, limit=1)
        data = {
            "name": payload.name,
            "specialty": payload.specialty,
            "bio": payload.bio,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if profiles:
            profile_id = profiles[0]["id"]
            await db_update("doctor_profiles", profile_id, data)
        else:
            data["wallet_address"] = wallet
            await db_insert("doctor_profiles", data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

@router.get("/doctor/grants/{wallet}")
async def get_doctor_grants(wallet: str):
    if not wallet:
        raise HTTPException(status_code=400, detail="wallet is required")
    try:
        grants = await db_select(
            "access_grants",
            filters={"doctor_wallet": wallet, "is_active": "true"},
            order="granted_at.desc"
        )
        
        if not grants:
            return {"success": True, "grants": []}
            
        enriched_grants = []
        for g in grants:
            analysis_id = g.get("analysis_id")
            patient_wallet = g.get("patient_wallet")
            
            analysis = None
            if analysis_id:
                analyses = await db_select("analyses", filters={"id": analysis_id}, limit=1)
                if analyses:
                    analysis = analyses[0]
            
            # Fetch patient profile
            patient_profile = None
            if patient_wallet:
                profile_data = await db_select_single(
                    "patient_profiles",
                    filters={"wallet_address": patient_wallet},
                    select="name,date_of_birth,gender,blood_type"
                )
                if profile_data:
                    patient_profile = {
                        "full_name": profile_data.get("name"),
                        "date_of_birth": profile_data.get("date_of_birth"),
                        "gender": profile_data.get("gender"),
                        "blood_type": profile_data.get("blood_type")
                    }
            
            enriched_grants.append({
                **g, 
                "analysis": analysis,
                "patient_profile": patient_profile
            })
            
        return {"success": True, "grants": enriched_grants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch grants: {str(e)}")

@router.get("/doctor/appointments/{wallet}")
async def get_doctor_appointments(wallet: str):
    if not wallet:
        raise HTTPException(status_code=400, detail="wallet is required")
    try:
        appts = await db_select(
            "appointments",
            filters={"doctor_wallet": wallet},
            order="date.asc"
        )
        return {"success": True, "appointments": appts or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")

class AppointmentStatusPayload(BaseModel):
    status: str

@router.patch("/doctor/appointments/{appointment_id}")
async def update_appointment_status(appointment_id: str, payload: AppointmentStatusPayload):
    try:
        await db_update("appointments", appointment_id, {
            "status": payload.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update appointment: {str(e)}")

@router.get("/doctor/notes/{doctor_wallet}/{patient_wallet}")
async def get_consultation_notes(doctor_wallet: str, patient_wallet: str):
    try:
        notes = await db_select(
            "consultation_notes",
            filters={"doctor_wallet": doctor_wallet, "patient_wallet": patient_wallet},
            order="created_at.desc"
        )
        return {"success": True, "notes": notes or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notes: {str(e)}")

@router.post("/doctor/notes/{doctor_wallet}")
async def add_consultation_note(doctor_wallet: str, payload: ConsultationNotePayload):
    try:
        await db_insert("consultation_notes", {
            "doctor_wallet": doctor_wallet,
            "patient_wallet": payload.patient_wallet,
            "analysis_id": payload.analysis_id,
            "note": payload.note
        })
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add note: {str(e)}")


# ─── Payment Requests ────────────────────────────────────────────────────────

class PaymentRequestPayload(BaseModel):
    patient_wallet: str
    amount: str
    reason: str

class PaymentRequestUpdatePayload(BaseModel):
    status: str
    tx_hash: str = None


@router.post("/payment-requests")
async def create_payment_request(doctor_wallet: str, payload: PaymentRequestPayload):
    """Doctor creates a payment request to a patient."""
    try:
        # Enrich with doctor name
        profiles = await db_select("doctor_profiles", filters={"wallet_address": doctor_wallet}, limit=1)
        doctor_name = profiles[0]["name"] if profiles else "Unknown Doctor"

        record = await db_insert("payment_requests", {
            "doctor_wallet": doctor_wallet,
            "doctor_name": doctor_name,
            "patient_wallet": payload.patient_wallet,
            "amount": payload.amount,
            "reason": payload.reason,
            "status": "pending",
        })
        return {"success": True, "request": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment request: {str(e)}")


@router.get("/payment-requests/patient/{wallet}")
async def get_patient_payment_requests(wallet: str):
    """Patient fetches all payment requests sent to them."""
    try:
        requests = await db_select(
            "payment_requests",
            filters={"patient_wallet": wallet},
            order="created_at.desc"
        )
        return {"success": True, "requests": requests or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment requests: {str(e)}")


@router.get("/payment-requests/doctor/{wallet}")
async def get_doctor_payment_requests(wallet: str):
    """Doctor fetches all payment requests they have sent."""
    try:
        requests = await db_select(
            "payment_requests",
            filters={"doctor_wallet": wallet},
            order="created_at.desc"
        )
        return {"success": True, "requests": requests or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sent requests: {str(e)}")


@router.patch("/payment-requests/{request_id}")
async def update_payment_request(request_id: str, payload: PaymentRequestUpdatePayload):
    """Patient approves/declines a payment request."""
    try:
        update_data = {
            "status": payload.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if payload.tx_hash:
            update_data["tx_hash"] = payload.tx_hash
        await db_update("payment_requests", request_id, update_data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payment request: {str(e)}")

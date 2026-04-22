"""
AI Medical Intern Routes
Provides intelligent assistance endpoints for doctors
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.insforge import db_select
from services.ai_medical_intern import get_ai_intern

router = APIRouter()


class ChatRequest(BaseModel):
    patient_wallet: str
    query: str


class TreatmentPlanRequest(BaseModel):
    diagnosis: str
    patient_context: Dict[str, Any]


class DocumentAnalysisRequest(BaseModel):
    document_text: str
    document_type: str


@router.post("/ai/briefing/{patient_wallet}", tags=["AI Medical Intern"])
async def generate_patient_briefing(patient_wallet: str):
    """
    Generate comprehensive AI briefing for a patient.
    Like a medical intern preparing notes before the doctor sees the patient.
    """
    try:
        ai_intern = get_ai_intern()
        
        # Gather all patient data
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": patient_wallet},
            order="created_at.desc",
            limit=10
        )
        
        appointments = await db_select(
            "appointments",
            filters={"patient_wallet": patient_wallet},
            order="date.desc",
            limit=10
        )
        
        notes = await db_select(
            "consultation_notes",
            filters={"patient_wallet": patient_wallet},
            order="created_at.desc",
            limit=10
        )
        
        patient_data = {
            "patient_wallet": patient_wallet,
            "analyses": analyses or [],
            "appointments": appointments or [],
            "consultation_notes": notes or []
        }
        
        # Generate AI briefing
        briefing = await ai_intern.generate_patient_briefing(patient_data)
        
        return {
            "success": True,
            "briefing": briefing
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate briefing: {str(e)}")


@router.get("/ai/priority-patients/{doctor_wallet}", tags=["AI Medical Intern"])
async def get_priority_patients(doctor_wallet: str, limit: int = 20):
    """
    Get prioritized list of patients for doctor.
    Sorted by urgency/priority score.
    Includes patient names for better UX.
    """
    try:
        ai_intern = get_ai_intern()
        
        # Get all patients with active grants to this doctor
        grants = await db_select(
            "access_grants",
            filters={"doctor_wallet": doctor_wallet, "is_active": True},
            order="granted_at.desc"
        )
        
        if not grants:
            return {
                "success": True,
                "patients": [],
                "total": 0
            }
        
        # Get patient data and calculate priorities
        priority_patients = []
        
        for grant in grants[:limit]:
            patient_wallet = grant.get("patient_wallet")
            
            # Get patient profile for name
            patient_profile = await db_select(
                "patient_profiles",
                filters={"patient_wallet": patient_wallet},
                limit=1
            )
            patient_name = patient_profile[0].get("full_name") if patient_profile else f"Patient {patient_wallet[:8]}"
            
            # Get patient's latest analysis
            analyses = await db_select(
                "analyses",
                filters={"patient_wallet": patient_wallet},
                order="created_at.desc",
                limit=5
            )
            
            if not analyses:
                continue
            
            appointments = await db_select(
                "appointments",
                filters={"patient_wallet": patient_wallet, "doctor_wallet": doctor_wallet},
                order="date.desc",
                limit=5
            )
            
            patient_data = {
                "patient_wallet": patient_wallet,
                "analyses": analyses,
                "appointments": appointments or [],
                "consultation_notes": []
            }
            
            # Calculate priority
            priority_score = await ai_intern.calculate_priority_score(patient_data)
            
            latest = analyses[0]
            
            priority_patients.append({
                "patient_wallet": patient_wallet,
                "patient_name": patient_name,  # Added patient name
                "priority_score": priority_score,
                "risk_score": latest.get("risk_score", 0),
                "urgency": latest.get("urgency", "low"),
                "conditions": latest.get("conditions", []),
                "last_analysis_date": latest.get("created_at"),
                "file_name": latest.get("file_name"),
                "summary": latest.get("summary", "")[:200],  # First 200 chars
                "grant_id": grant.get("id"),
                "analysis_id": latest.get("id")
            })
        
        # Sort by priority score (highest first)
        priority_patients.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return {
            "success": True,
            "patients": priority_patients,
            "total": len(priority_patients)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get priority patients: {str(e)}")


@router.post("/ai/chat", tags=["AI Medical Intern"])
async def chat_with_ai(request: ChatRequest):
    """
    RAG-based chat: Ask questions about a specific patient.
    AI answers using patient's actual medical records.
    """
    try:
        ai_intern = get_ai_intern()
        
        # Gather patient data for context
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": request.patient_wallet},
            order="created_at.desc",
            limit=10
        )
        
        appointments = await db_select(
            "appointments",
            filters={"patient_wallet": request.patient_wallet},
            order="date.desc",
            limit=10
        )
        
        notes = await db_select(
            "consultation_notes",
            filters={"patient_wallet": request.patient_wallet},
            order="created_at.desc",
            limit=10
        )
        
        patient_data = {
            "patient_wallet": request.patient_wallet,
            "analyses": analyses or [],
            "appointments": appointments or [],
            "consultation_notes": notes or []
        }
        
        # Get AI response
        response = await ai_intern.rag_chat(request.query, patient_data)
        
        return {
            "success": True,
            "response": response,
            "query": request.query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/ai/treatment-plan", tags=["AI Medical Intern"])
async def suggest_treatment_plan(request: TreatmentPlanRequest):
    """
    Generate evidence-based treatment plan suggestions.
    """
    try:
        ai_intern = get_ai_intern()
        
        plan = await ai_intern.suggest_treatment_plan(
            request.diagnosis,
            request.patient_context
        )
        
        return {
            "success": True,
            "treatment_plan": plan
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate treatment plan: {str(e)}")


@router.post("/ai/analyze-document", tags=["AI Medical Intern"])
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze uploaded medical document and extract key information.
    """
    try:
        ai_intern = get_ai_intern()
        
        analysis = await ai_intern.analyze_document(
            request.document_text,
            request.document_type
        )
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@router.get("/ai/task-board/{doctor_wallet}", tags=["AI Medical Intern"])
async def get_task_board(doctor_wallet: str):
    """
    Jira-style task board for doctors.
    Shows all pending tasks organized by priority.
    """
    try:
        # Get all patients
        grants = await db_select(
            "access_grants",
            filters={"doctor_wallet": doctor_wallet, "is_active": True}
        )
        
        # Get appointments
        appointments = await db_select(
            "appointments",
            filters={"doctor_wallet": doctor_wallet},
            order="date.asc"
        )
        
        # Organize tasks
        tasks = {
            "urgent": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "completed": []
        }
        
        # Pending appointments
        for apt in appointments or []:
            if apt.get("status") == "pending":
                tasks["high_priority"].append({
                    "type": "appointment_approval",
                    "title": f"Approve appointment request",
                    "patient": apt.get("patient_wallet"),
                    "date": apt.get("date"),
                    "time": apt.get("time"),
                    "reason": apt.get("reason"),
                    "id": apt.get("id")
                })
            elif apt.get("status") == "confirmed":
                # Upcoming appointments
                tasks["medium_priority"].append({
                    "type": "upcoming_appointment",
                    "title": f"Upcoming appointment",
                    "patient": apt.get("patient_wallet"),
                    "date": apt.get("date"),
                    "time": apt.get("time"),
                    "reason": apt.get("reason"),
                    "id": apt.get("id")
                })
        
        # New patient records to review
        for grant in grants or []:
            if grant.get("access_count", 0) == 0:
                tasks["high_priority"].append({
                    "type": "new_record",
                    "title": "Review new patient record",
                    "patient": grant.get("patient_wallet"),
                    "analysis_id": grant.get("analysis_id"),
                    "granted_at": grant.get("granted_at"),
                    "id": grant.get("id")
                })
        
        # Count tasks
        task_counts = {
            "urgent": len(tasks["urgent"]),
            "high_priority": len(tasks["high_priority"]),
            "medium_priority": len(tasks["medium_priority"]),
            "low_priority": len(tasks["low_priority"]),
            "completed": len(tasks["completed"]),
            "total": sum([
                len(tasks["urgent"]),
                len(tasks["high_priority"]),
                len(tasks["medium_priority"]),
                len(tasks["low_priority"])
            ])
        }
        
        return {
            "success": True,
            "tasks": tasks,
            "counts": task_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task board: {str(e)}")

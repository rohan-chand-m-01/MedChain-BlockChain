"""
Doctor Patient View - Comprehensive Patient Management
Provides complete patient profile, medical history, RAG analysis, and consultation tools
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from services.insforge import db_select, db_select_single, db_insert, db_update

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Doctor Patient View"])


class ConsultationNoteCreate(BaseModel):
    patient_wallet: str
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    is_draft: bool = True


@router.get("/doctor/patient/{patient_wallet}/complete")
async def get_patient_complete_profile(patient_wallet: str, doctor_wallet: str):
    """
    Get complete patient profile including:
    - Demographics
    - All medical files/analyses
    - Consultation notes
    - Medical data points for graphs
    """
    try:
        # Check if doctor has access
        grants = await db_select(
            "access_grants",
            filters={
                "patient_wallet": patient_wallet,
                "doctor_wallet": doctor_wallet,
                "is_active": True
            },
            limit=1
        )
        
        if not grants:
            raise HTTPException(403, "No active access to this patient")
        
        # Get patient profile
        patient_profile = await db_select_single(
            "patient_profiles",
            filters={"wallet_address": patient_wallet},
            select="*"
        )
        
        # Map database fields to expected API fields
        if patient_profile:
            patient_profile = {
                "patient_wallet": patient_profile.get("wallet_address"),
                "full_name": patient_profile.get("name"),
                "whatsapp_phone": patient_profile.get("whatsapp_phone"),
                "date_of_birth": patient_profile.get("date_of_birth"),
                "email": patient_profile.get("email"),
                "gender": patient_profile.get("gender"),
                "blood_type": patient_profile.get("blood_type"),
                "allergies": patient_profile.get("allergies"),
                "emergency_contact": patient_profile.get("emergency_contact"),
                "emergency_contact_phone": patient_profile.get("emergency_contact_phone"),
            }
        
        # Get all analyses for this patient
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": patient_wallet},
            select="*",
            order="created_at.desc"
        )
        
        # Get consultation notes
        consultation_notes = await db_select(
            "consultation_notes",
            filters={
                "patient_wallet": patient_wallet,
                "doctor_wallet": doctor_wallet
            },
            order="consultation_date.desc"
        )
        
        # Get medical data points for graphs
        medical_data = await db_select(
            "medical_data_points",
            filters={"patient_wallet": patient_wallet},
            order="measured_at.asc"
        )
        
        # Organize data by type for graphs
        data_by_type = {}
        for point in medical_data or []:
            data_type = point["data_type"]
            if data_type not in data_by_type:
                data_by_type[data_type] = []
            data_by_type[data_type].append({
                "value": float(point["value"]),
                "unit": point.get("unit"),
                "date": point["measured_at"]
            })
        
        return {
            "success": True,
            "patient": patient_profile or {},
            "analyses": analyses or [],
            "consultation_notes": consultation_notes or [],
            "medical_data": data_by_type,
            "total_files": len(analyses or [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient complete profile: {e}")
        raise HTTPException(500, str(e))


@router.post("/doctor/patient/{patient_wallet}/comprehensive-analysis")
async def generate_comprehensive_analysis(patient_wallet: str, doctor_wallet: str):
    """
    RAG-based comprehensive analysis of ALL patient files.
    Uses Gemini AI to analyze complete medical history and provide insights.
    """
    try:
        # Check access
        grants = await db_select(
            "access_grants",
            filters={
                "patient_wallet": patient_wallet,
                "doctor_wallet": doctor_wallet,
                "is_active": True
            },
            limit=1
        )
        
        if not grants:
            raise HTTPException(403, "No active access to this patient")
        
        # Get all analyses
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": patient_wallet},
            select="file_name,summary,risk_score,conditions,specialist,created_at",
            order="created_at.asc"
        )
        
        if not analyses:
            return {
                "success": True,
                "analysis": "No medical records available for analysis."
            }
        
        # Build comprehensive context
        context = "Complete Medical History:\n\n"
        for i, analysis in enumerate(analyses, 1):
            date = analysis.get("created_at", "Unknown date")
            context += f"Record {i} ({date}):\n"
            context += f"File: {analysis.get('file_name', 'Unknown')}\n"
            context += f"Summary: {analysis.get('summary', 'N/A')}\n"
            context += f"Risk Score: {analysis.get('risk_score', 0)}\n"
            context += f"Conditions: {', '.join(analysis.get('conditions', []))}\n\n"
        
        # Generate comprehensive analysis using Gemini
        prompt = f"""You are an expert medical AI assistant analyzing a patient's complete medical history.

{context}

Provide a comprehensive medical analysis including:

1. **Longitudinal Health Trends**: How has the patient's health evolved over time?
2. **Disease Progression**: Are there any chronic conditions? How are they progressing?
3. **Risk Factors**: What are the key risk factors identified across all records?
4. **Treatment Effectiveness**: If treatments were mentioned, are they working?
5. **Preventive Care Recommendations**: What preventive measures should be taken?
6. **Red Flags**: Any concerning patterns or urgent issues?
7. **Follow-up Priorities**: What should the doctor focus on in the next consultation?

Provide a detailed, professional medical analysis (8-10 paragraphs).
"""
        
        try:
            import google.generativeai as genai
            import os
            
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            response = model.generate_content(prompt)
            comprehensive_analysis = response.text
            
            logger.info(f"✓ Generated comprehensive analysis for patient {patient_wallet}")
            
            return {
                "success": True,
                "analysis": comprehensive_analysis,
                "total_records_analyzed": len(analyses),
                "date_range": {
                    "from": analyses[0].get("created_at") if analyses else None,
                    "to": analyses[-1].get("created_at") if analyses else None
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise HTTPException(500, f"AI analysis failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive analysis: {e}")
        raise HTTPException(500, str(e))


@router.post("/doctor/consultation-notes")
async def create_consultation_note(note: ConsultationNoteCreate, doctor_wallet: str):
    """Create or update consultation note"""
    try:
        # Check access
        grants = await db_select(
            "access_grants",
            filters={
                "patient_wallet": note.patient_wallet,
                "doctor_wallet": doctor_wallet,
                "is_active": True
            },
            limit=1
        )
        
        if not grants:
            raise HTTPException(403, "No active access to this patient")
        
        # Create note
        note_data = {
            "patient_wallet": note.patient_wallet,
            "doctor_wallet": doctor_wallet,
            "chief_complaint": note.chief_complaint,
            "diagnosis": note.diagnosis,
            "treatment_plan": note.treatment_plan,
            "notes": note.notes,
            "is_draft": note.is_draft,
            "consultation_date": datetime.utcnow().isoformat()
        }
        
        result = await db_insert("consultation_notes", [note_data])
        
        logger.info(f"✓ Created consultation note for patient {note.patient_wallet}")
        
        return {
            "success": True,
            "note_id": result["id"],
            "message": "Consultation note saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating consultation note: {e}")
        raise HTTPException(500, str(e))


@router.post("/doctor/patient/{patient_wallet}/extract-medical-data")
async def extract_medical_data_from_analyses(patient_wallet: str, doctor_wallet: str):
    """
    Extract structured medical data points from analyses for graphing.
    Uses AI to parse values like glucose, BP, cholesterol from summaries.
    """
    try:
        # Check access
        grants = await db_select(
            "access_grants",
            filters={
                "patient_wallet": patient_wallet,
                "doctor_wallet": doctor_wallet,
                "is_active": True
            },
            limit=1
        )
        
        if not grants:
            raise HTTPException(403, "No active access to this patient")
        
        # Get all analyses
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": patient_wallet},
            select="id,summary,created_at",
            order="created_at.asc"
        )
        
        if not analyses:
            return {"success": True, "extracted_count": 0}
        
        # Use Gemini to extract structured data
        import google.generativeai as genai
        import os
        import json
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        extracted_count = 0
        
        for analysis in analyses:
            summary = analysis.get("summary", "")
            analysis_id = analysis["id"]
            measured_at = analysis.get("created_at")
            
            prompt = f"""Extract medical data points from this summary:

{summary}

Return ONLY a JSON array of data points in this exact format:
[
  {{"type": "glucose", "value": 120, "unit": "mg/dL"}},
  {{"type": "bp_systolic", "value": 130, "unit": "mmHg"}},
  {{"type": "bp_diastolic", "value": 85, "unit": "mmHg"}},
  {{"type": "cholesterol_total", "value": 200, "unit": "mg/dL"}}
]

Only include data points that are explicitly mentioned. Return empty array [] if none found.
"""
            
            try:
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                # Extract JSON from response
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                data_points = json.loads(text)
                
                # Insert into database
                for point in data_points:
                    await db_insert("medical_data_points", [{
                        "patient_wallet": patient_wallet,
                        "analysis_id": analysis_id,
                        "data_type": point["type"],
                        "value": point["value"],
                        "unit": point["unit"],
                        "measured_at": measured_at
                    }])
                    extracted_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to extract data from analysis {analysis_id}: {e}")
                continue
        
        logger.info(f"✓ Extracted {extracted_count} medical data points for patient {patient_wallet}")
        
        return {
            "success": True,
            "extracted_count": extracted_count,
            "message": f"Extracted {extracted_count} data points for graphing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting medical data: {e}")
        raise HTTPException(500, str(e))

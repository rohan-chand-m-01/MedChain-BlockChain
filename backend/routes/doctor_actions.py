"""
Doctor Actions API
Endpoints for doctor-specific actions: notifications, PDF generation, etc.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import Response

from services.doctor_notifier import get_doctor_notifier
from services.pdf_generator import get_pdf_generator
from services.fraud_detector import get_fraud_detector
from services.insforge import db_select, db_insert

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Doctor Actions"])


class NotifyDoctorRequest(BaseModel):
    doctor_phone: str
    patient_name: str
    risk_score: int
    conditions: List[str]
    specialist: str
    access_hours: int
    record_id: Optional[str] = None


class GenerateClaimRequest(BaseModel):
    analysis_id: str
    patient_data: dict
    doctor_data: dict


class FraudCheckRequest(BaseModel):
    analysis_id: str
    patient_id: str


@router.post("/doctor/notify-access")
async def notify_doctor_access(req: NotifyDoctorRequest):
    """
    Send WhatsApp notification to doctor when patient grants access.
    
    This is typically called automatically when access is granted via smart contract,
    but can also be triggered manually.
    """
    try:
        notifier = get_doctor_notifier()
        
        if not notifier.is_available():
            raise HTTPException(status_code=503, detail="Doctor notification service not configured")
        
        success = await notifier.notify_access_granted(
            doctor_phone=req.doctor_phone,
            patient_name=req.patient_name,
            risk_score=req.risk_score,
            conditions=req.conditions,
            specialist=req.specialist,
            access_hours=req.access_hours,
            record_id=req.record_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": f"Notification sent to {req.doctor_phone}"
        }
        
    except Exception as e:
        logger.error(f"Failed to notify doctor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doctor/generate-claim")
async def generate_insurance_claim(req: GenerateClaimRequest):
    """
    Generate insurance claim PDF with ICD-10 codes, fraud certificate, and blockchain verification.
    
    Returns PDF file as downloadable response.
    """
    try:
        # Fetch analysis data from database
        analysis_result = await db_select("analyses", filters={"id": req.analysis_id})
        
        if not analysis_result or len(analysis_result) == 0:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_data = analysis_result[0]
        
        # Run fraud detection
        fraud_detector = get_fraud_detector()
        
        # Fetch previous reports for same patient
        previous_reports = await db_select(
            "analyses",
            filters={"patient_wallet": analysis_data.get("patient_wallet")},
            order="created_at",
            limit=10
        )
        
        # Prepare current report for fraud detection
        current_report = {
            "biomarkers": analysis_data.get("biomarkers", {}),
            "report_date": analysis_data.get("created_at", ""),
            "risk_score": analysis_data.get("risk_score", 50),
            "patient_id": analysis_data.get("patient_wallet", "")
        }
        
        # Filter out current report from previous reports
        previous_reports = [
            {
                "biomarkers": r.get("biomarkers", {}),
                "report_date": r.get("created_at", ""),
                "risk_score": r.get("risk_score", 50)
            }
            for r in previous_reports
            if r.get("id") != req.analysis_id
        ]
        
        fraud_data = fraud_detector.detect_fraud(current_report, previous_reports)
        
        logger.info(f"Fraud detection: score={fraud_data['fraud_score']}, suspicious={fraud_data['is_suspicious']}")
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        
        pdf_bytes = pdf_generator.generate_insurance_claim(
            patient_data=req.patient_data,
            analysis_data=analysis_data,
            doctor_data=req.doctor_data,
            fraud_data=fraud_data
        )
        
        # Store fraud data in database
        try:
            await db_insert("fraud_checks", {
                "analysis_id": req.analysis_id,
                "patient_id": req.patient_data.get("id"),
                "fraud_score": fraud_data["fraud_score"],
                "is_suspicious": fraud_data["is_suspicious"],
                "flags": fraud_data["flags"],
                "confidence": fraud_data["confidence"]
            })
        except Exception as db_error:
            logger.warning(f"Failed to store fraud data: {db_error}")
        
        # Return PDF as downloadable file
        filename = f"insurance_claim_{req.analysis_id}_{req.patient_data.get('name', 'patient').replace(' ', '_')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate claim: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doctor/check-fraud")
async def check_fraud(req: FraudCheckRequest):
    """
    Run fraud detection on a specific analysis.
    Returns fraud score and flags without generating PDF.
    """
    try:
        # Fetch analysis data
        analysis_result = await db_select("analyses", filters={"id": req.analysis_id})
        
        if not analysis_result or len(analysis_result) == 0:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_data = analysis_result[0]
        
        # Fetch previous reports
        previous_reports = await db_select(
            "analyses",
            filters={"patient_wallet": req.patient_id},
            order="created_at",
            limit=10
        )
        
        # Prepare reports for fraud detection
        current_report = {
            "biomarkers": analysis_data.get("biomarkers", {}),
            "report_date": analysis_data.get("created_at", ""),
            "risk_score": analysis_data.get("risk_score", 50),
            "patient_id": req.patient_id
        }
        
        previous_reports = [
            {
                "biomarkers": r.get("biomarkers", {}),
                "report_date": r.get("created_at", ""),
                "risk_score": r.get("risk_score", 50)
            }
            for r in previous_reports
            if r.get("id") != req.analysis_id
        ]
        
        # Run fraud detection
        fraud_detector = get_fraud_detector()
        fraud_data = fraud_detector.detect_fraud(current_report, previous_reports)
        
        # Store results
        try:
            await db_insert("fraud_checks", {
                "analysis_id": req.analysis_id,
                "patient_id": req.patient_id,
                "fraud_score": fraud_data["fraud_score"],
                "is_suspicious": fraud_data["is_suspicious"],
                "flags": fraud_data["flags"],
                "confidence": fraud_data["confidence"]
            })
        except Exception as db_error:
            logger.warning(f"Failed to store fraud data: {db_error}")
        
        return {
            "success": True,
            "fraud_data": fraud_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fraud check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doctor/fraud-history/{patient_id}")
async def get_fraud_history(patient_id: str):
    """
    Get fraud detection history for a patient.
    Shows trend of fraud scores over time.
    """
    try:
        fraud_checks = await db_select(
            "fraud_checks",
            filters={"patient_id": patient_id},
            order="created_at",
            limit=20
        )
        
        return {
            "success": True,
            "patient_id": patient_id,
            "total_checks": len(fraud_checks),
            "checks": fraud_checks
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch fraud history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import hashlib
import json
import re
import base64
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ollama_medgemma import get_ollama_client
from services.insforge import db_insert
from services.privacy_service import get_privacy_service
from services.stellar_client import StellarClient

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyzeRequest(BaseModel):
    file_base64: str
    file_type: str = "application/pdf"
    patient_wallet: str
    file_name: str = "report"
    enable_privacy: bool = False


@router.post("/analyze-report")
async def analyze_report(req: AnalyzeRequest):
    """
    AI analysis pipeline powered exclusively by Ollama MedGemma 4B (local).
    1. OCR / multimodal extraction
    2. MedGemma analysis → risk_score, risk_level, conditions, biomarkers, summary
    3. Store result in DB
    """
    if not req.file_base64 or not req.patient_wallet:
        raise HTTPException(status_code=400, detail="file_base64 and patient_wallet are required")

    ollama = get_ollama_client()
    if not ollama.is_available():
        raise HTTPException(
            status_code=503,
            detail="MedGemma local model is not available. Run: ollama pull medgemma:4b"
        )

    file_bytes = base64.b64decode(req.file_base64)

    is_image = req.file_type.startswith("image/") or req.file_name.lower().endswith(('.jpg', '.jpeg', '.png'))
    is_pdf   = req.file_type == "application/pdf" or req.file_name.lower().endswith('.pdf')

    # ------------------------------------------------------------------ #
    # Step 1: Get raw analysis from MedGemma                              #
    # ------------------------------------------------------------------ #
    ai_result = {}
    ocr_text  = ""

    if is_image:
        logger.info("[ANALYZE] Image → Ollama MedGemma multimodal")
        try:
            ai_result = await ollama.analyze_xray_image(file_bytes)
            ocr_text  = "[Image analyzed via Ollama MedGemma multimodal]"
            logger.info("✓ Ollama multimodal image analysis complete")
        except Exception as e:
            logger.warning(f"Ollama multimodal failed, falling back to OCR: {e}")

    # For PDFs, plain text, or multimodal fallback — use OCR then text analysis
    if not ai_result:
        from services.ocr_extractor import get_ocr_extractor
        ocr_extractor = get_ocr_extractor()

        if is_pdf:
            ocr_text = ocr_extractor.extract_from_pdf(file_bytes)
        elif is_image:
            ocr_text = ocr_extractor.extract_from_image(file_bytes)
        else:
            try:
                ocr_text = file_bytes.decode('utf-8', errors='ignore')
            except Exception:
                ocr_text = f"[Unable to extract text from {req.file_name}]"

        logger.info(f"[OCR] Extracted {len(ocr_text)} chars — sending to Ollama MedGemma")
        ai_result = await ollama.analyze_report(ocr_text)
        logger.info("✓ Ollama text analysis complete")

    # ------------------------------------------------------------------ #
    # Step 2: Extract all fields from MedGemma response                   #
    # ------------------------------------------------------------------ #
    report_type      = ai_result.get("report_type") or "general"
    biomarkers       = ai_result.get("biomarkers") or {}
    conditions_raw   = ai_result.get("conditions") or []
    abnormal_findings= ai_result.get("abnormal_findings") or []
    specialist       = ai_result.get("specialist") or _specialist_for(report_type)
    nim_summary      = ai_result.get("summary") or ""
    urgency          = ai_result.get("urgency") or "low"

    # risk_score — use what MedGemma returned, derive from urgency if missing
    risk_score = ai_result.get("risk_score")
    if risk_score is None:
        risk_score = _derive_risk_score(urgency, abnormal_findings)
        logger.info(f"[ANALYZE] risk_score not in AI response, derived: {risk_score}")
    else:
        try:
            risk_score = int(risk_score)
        except (TypeError, ValueError):
            risk_score = _derive_risk_score(urgency, abnormal_findings)

    # risk_level — use what MedGemma returned, derive from score if missing
    risk_level = ai_result.get("risk_level")
    if not risk_level:
        risk_level = _risk_level_from_score(risk_score)

    # Validate urgency against DB constraint
    valid_urgency = {'low', 'medium', 'high', 'critical'}
    if urgency not in valid_urgency:
        urgency = _urgency_from_risk_level(risk_level)

    # Normalise conditions to plain strings
    conditions = []
    for c in conditions_raw:
        if isinstance(c, dict):
            conditions.append(c.get('name') or c.get('condition') or str(c))
        elif isinstance(c, str):
            conditions.append(c)

    logger.info(
        f"[ANALYZE] report_type={report_type} | risk_score={risk_score} | "
        f"risk_level={risk_level} | urgency={urgency} | "
        f"conditions={len(conditions)} | biomarkers={len(biomarkers)} | "
        f"abnormal={len(abnormal_findings)}"
    )

    # ------------------------------------------------------------------ #
    # Step 3: Build summary                                                #
    # ------------------------------------------------------------------ #
    if nim_summary and len(nim_summary) > 150:
        summary = nim_summary
    else:
        summary = _build_summary(
            report_type, risk_level, urgency, specialist,
            conditions, biomarkers, abnormal_findings, nim_summary
        )

    # ------------------------------------------------------------------ #
    # Step 4: Improvement plan                                             #
    # ------------------------------------------------------------------ #
    improvement_plan = _generate_improvement_plan(report_type, risk_level)

    # ------------------------------------------------------------------ #
    # Step 5: Hash                                                         #
    # ------------------------------------------------------------------ #
    analysis_payload = {
        "summary": summary, "risk_score": risk_score, "risk_level": risk_level,
        "conditions": conditions, "biomarkers": biomarkers, "specialist": specialist,
        "urgency": urgency, "improvement_plan": improvement_plan,
        "report_type": report_type,
    }
    record_hash = "0x" + hashlib.sha256(json.dumps(analysis_payload).encode()).hexdigest()

    # ------------------------------------------------------------------ #
    # Step 6: Persist to DB                                                #
    # ------------------------------------------------------------------ #
    db_record_id = None
    try:
        db_payload = {
            "patient_wallet":  req.patient_wallet,
            "file_name":       req.file_name,
            "file_url":        "direct-upload",
            "ocr_text":        ocr_text[:1000],
            "summary":         summary,
            "risk_score":      risk_score,
            "conditions":      conditions if conditions else [],
            "biomarkers":      biomarkers if biomarkers else {},
            "specialist":      specialist,
            "urgency":         urgency,
            "improvement_plan": improvement_plan if improvement_plan else [],
            "record_hash":     record_hash,
        }
        db_record    = await db_insert("analyses", db_payload)
        db_record_id = db_record.get("id")
        logger.info(f"[ANALYZE] ✅ Stored in DB: {db_record_id}")
    except Exception as db_err:
        logger.error(f"[ANALYZE] DB storage failed: {db_err}")
        db_record_id = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # ------------------------------------------------------------------ #
    # Step 6b: Store proof on Stellar blockchain                           #
    # ------------------------------------------------------------------ #
    stellar_tx_hash = None
    try:
        import os
        from stellar_sdk import Keypair as StellarKeypair
        gas_wallet_secret = os.getenv('STELLAR_GAS_WALLET_SECRET', '')
        if gas_wallet_secret:
            stellar = StellarClient()
            gas_kp  = StellarKeypair.from_secret(gas_wallet_secret)
            # Use record_hash (without 0x prefix) as the proof identifier
            proof_id = record_hash[2:] if record_hash.startswith("0x") else record_hash
            stellar_tx_hash = await stellar.store_proof_on_stellar(
                patient_public_key=gas_kp.public_key,
                ipfs_hash=proof_id,
                risk_score=risk_score,
                risk_level=risk_level,
            )
            logger.info(f"[ANALYZE] ✅ Stellar proof stored: {stellar_tx_hash}")
        else:
            logger.warning("[ANALYZE] STELLAR_GAS_WALLET_SECRET not set — skipping blockchain proof")
    except Exception as stellar_err:
        logger.error(f"[ANALYZE] Stellar storage failed (non-critical): {stellar_err}")

    # ------------------------------------------------------------------ #
    # Step 7: Optional privacy layer                                       #
    # ------------------------------------------------------------------ #
    privacy_analysis = None
    if req.enable_privacy:
        try:
            privacy_service  = get_privacy_service()
            privacy_analysis = privacy_service.analyze_with_privacy(biomarkers, risk_score)
        except Exception as pe:
            logger.warning(f"[ANALYZE] Privacy analysis failed (non-critical): {pe}")
            privacy_analysis = {"error": str(pe), "enabled": False}

    # ------------------------------------------------------------------ #
    # Response                                                             #
    # ------------------------------------------------------------------ #
    response = {
        "success": True,
        "analysis": {
            "id":               db_record_id,
            "summary":          summary,
            "risk_score":       risk_score,
            "risk_level":       risk_level,
            "conditions":       conditions if conditions else ["No specific conditions detected"],
            "specialist":       specialist,
            "urgency":          urgency,
            "biomarkers":       biomarkers,
            "abnormal_findings": abnormal_findings,
            "improvement_plan": improvement_plan,
            "report_type":      report_type,
            "record_hash":      record_hash,
        },
        "pipeline": {
            "model":      "Ollama MedGemma 4B (Local)",
            "ai_analysis": "✓ MedGemma analysis with risk assessment",
            "blockchain":  f"✓ Stellar proof: {stellar_tx_hash}" if stellar_tx_hash else "⚠ Stellar not configured",
        }
    }

    if stellar_tx_hash:
        response["stellar_tx_hash"] = stellar_tx_hash

    if privacy_analysis:
        response["privacy"] = privacy_analysis

    return response


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _derive_risk_score(urgency: str, abnormal_findings: list) -> int:
    """
    Derive a numeric risk score from urgency + number of abnormal findings
    when MedGemma doesn't return one explicitly.
    """
    base = {"low": 15, "medium": 45, "high": 70, "critical": 90}.get(urgency, 40)
    # Each abnormal finding adds a small bump (capped)
    bump = min(len(abnormal_findings) * 3, 20)
    return min(base + bump, 99)


def _risk_level_from_score(score: int) -> str:
    if score >= 75:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def _urgency_from_risk_level(risk_level: str) -> str:
    return {"low": "low", "medium": "medium", "high": "high", "critical": "critical"}.get(risk_level, "medium")


def _specialist_for(report_type: str) -> str:
    return {
        "diabetes": "Endocrinologist",
        "heart":    "Cardiologist",
        "kidney":   "Nephrologist",
    }.get(report_type, "General Practitioner")


def _build_summary(
    report_type, risk_level, urgency, specialist,
    conditions, biomarkers, abnormal_findings, short_summary
) -> str:
    names = {
        "diabetes": "Diabetes Screening and Metabolic Panel",
        "heart":    "Cardiovascular Health and Lipid Profile Assessment",
        "kidney":   "Kidney Function and Renal Health Evaluation",
        "general":  "Complete Medical Laboratory",
    }
    summary = f"This {names.get(report_type, 'Medical Laboratory')} analysis provides a detailed evaluation of your health status. "

    if short_summary:
        summary += short_summary + " "

    if abnormal_findings:
        summary += "Key findings include: "
        for i, f in enumerate(abnormal_findings[:3]):
            name  = f.get('name', 'Unknown test')
            value = f.get('value', 'N/A')
            normal= f.get('normal', 'N/A')
            expl  = f.get('explanation', '')
            summary += f"{name} at {value} (normal: {normal})"
            if expl:
                summary += f" — {expl[:120]}"
            summary += ("; " if i < min(len(abnormal_findings), 3) - 1 else ". ")
        if len(abnormal_findings) > 3:
            summary += f"Additionally, {len(abnormal_findings) - 3} other parameters show deviations. "
    elif conditions:
        summary += f"Clinical findings: {', '.join(conditions[:3])}. "
    else:
        summary += "No significant abnormalities detected across the tested parameters. "

    if biomarkers:
        details = [f"{k} at {v}" for k, v in list(biomarkers.items())[:5]]
        summary += f"Key biomarkers: {', '.join(details)}. "

    risk_desc = {
        "low":      "indicating favorable health markers within expected ranges",
        "medium":   "suggesting some parameters warrant monitoring",
        "high":     "indicating significant abnormalities requiring medical attention",
        "critical": "revealing urgent findings requiring immediate evaluation",
    }.get(risk_level, "based on the analyzed parameters")
    summary += f"Overall risk level is {risk_level}, {risk_desc}. "

    urgency_ctx = {
        "low":      "at your convenience for routine monitoring",
        "medium":   "within the next 1-2 weeks",
        "high":     "as soon as possible, ideally within 48-72 hours",
        "critical": "immediately — this requires urgent medical attention",
    }.get(urgency, "for personalized medical guidance")
    summary += f"Consult a {specialist} {urgency_ctx}."

    return summary


def _generate_improvement_plan(report_type: str, risk_level: str) -> list:
    plans = {
        "diabetes": [
            "Monitor blood glucose levels daily and maintain a log",
            "Follow a low-glycemic diet with controlled carbohydrate intake",
            "Engage in 30 minutes of moderate exercise 5 days per week",
            "Schedule regular HbA1c tests every 3 months",
        ],
        "heart": [
            "Adopt a heart-healthy diet low in saturated fats and sodium",
            "Monitor blood pressure daily at the same time",
            "Incorporate cardiovascular exercise into your routine",
            "Manage stress through meditation or relaxation techniques",
        ],
        "kidney": [
            "Stay well-hydrated with 8-10 glasses of water daily",
            "Limit protein intake and avoid high-sodium foods",
            "Monitor blood pressure regularly",
            "Avoid NSAIDs and nephrotoxic medications",
        ],
        "general": [
            "Maintain a balanced diet rich in fruits and vegetables",
            "Get 7-8 hours of quality sleep each night",
            "Stay physically active with regular exercise",
            "Schedule annual health checkups",
        ],
    }
    plan = plans.get(report_type, plans["general"])
    if risk_level in ("high", "critical"):
        plan = ["⚠️ Schedule an appointment with a specialist within 48-72 hours"] + plan
    return plan[:5]

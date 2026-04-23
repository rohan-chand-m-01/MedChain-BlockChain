import json
import re
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ollama_medgemma import get_ollama_client
from services.insforge import db_select, db_insert

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    patient_wallet: str
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    if not req.patient_wallet or not req.message:
        raise HTTPException(status_code=400, detail="patient_wallet and message are required")

    # Fetch patient analyses and chat history
    analyses, history = await _fetch_context(req.patient_wallet)

    # Build compact context string from patient records
    analysis_context = "\n".join([
        f"[{i+1}] {a.get('summary','')} | Risk:{a.get('risk_score',0)} | "
        f"{','.join(a.get('conditions',[]))} | {a.get('specialist','')} | {a.get('urgency','')}"
        for i, a in enumerate(analyses)
    ]) if analyses else "No reports found."

    system_prompt = f"""You are MediLock AI, an advanced, empathetic, and highly professional medical assistant powered by MedGemma.

CORE PERSONALITY & TONE:
- Empathetic and Reassuring: Always start with a warm, caring, and professional tone.
- Clear and Accessible: Explain complex medical terms using simple, everyday language.
- Structured and Organized: Use standard Markdown. Use ### for headers. For lists use - (dash + space) and **bold** for key terms. Leave a blank line before and after lists or headers.
- Objective yet Supportive: Provide factual insights from the reports without causing unnecessary panic.

STRICT SAFETY RULES:
1. NEVER diagnose a condition or prescribe medication.
2. ALWAYS include a clear disclaimer that your advice is informational only.
3. For high risk scores or emergencies, urgently recommend consulting a healthcare professional.
4. If a question is outside the report scope, offer general health information but reiterate your limitations.

AVAILABLE PATIENT REPORTS:
{analysis_context}

Return your response STRICTLY as a JSON object with no markdown wrapper:
{{
  "answer": "Your detailed Markdown response here",
  "warning": "Brief disclaimer or empty string",
  "confidence": 0.9
}}"""

    # Build messages list: system + history + current message
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (most recent last)
    if history:
        for h in reversed(history):
            role = "user" if h.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": h.get("message", "")})

    # Add current user message
    messages.append({"role": "user", "content": req.message})

    # Call Ollama MedGemma
    ollama = get_ollama_client()
    if not ollama.is_available():
        raise HTTPException(
            status_code=503,
            detail="MedGemma local model is not available. Make sure Ollama is running with: ollama run medgemma:4b"
        )

    try:
        logger.info(f"[Chatbot] Sending to Ollama MedGemma for {req.patient_wallet}")
        raw = ollama._chat(messages, temperature=0.3, max_tokens=1024)
        logger.info(f"[Chatbot] Response received ({len(raw)} chars)")
    except Exception as e:
        logger.error(f"[Chatbot] Ollama error: {e}")
        raise HTTPException(status_code=500, detail=f"MedGemma error: {str(e)}")

    # Parse JSON response
    try:
        cleaned = re.sub(r"```json\s*|\s*```|```", "", raw).strip()
        response = json.loads(cleaned)
    except Exception:
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            try:
                response = json.loads(json_match.group(0))
            except Exception:
                response = {"answer": raw, "warning": "", "confidence": 0.5}
        else:
            response = {"answer": raw, "warning": "", "confidence": 0.5}

    # Save chat to DB (non-blocking)
    try:
        await db_insert("chat_history", {
            "patient_wallet": req.patient_wallet,
            "role": "user",
            "message": req.message,
        })
        await db_insert("chat_history", {
            "patient_wallet": req.patient_wallet,
            "role": "assistant",
            "message": response.get("answer", ""),
            "warning": response.get("warning", ""),
            "confidence": response.get("confidence", 0.5),
        })
    except Exception as e:
        logger.warning(f"[DB] Failed to save chat: {e}")

    return response


async def _fetch_context(patient_wallet: str):
    try:
        analyses = await db_select(
            "analyses",
            filters={"patient_wallet": patient_wallet},
            select="summary,risk_score,conditions,specialist,urgency,created_at",
            order="created_at.desc",
            limit=5,
        )
    except Exception:
        analyses = []

    try:
        history = await db_select(
            "chat_history",
            filters={"patient_wallet": patient_wallet},
            select="role,message",
            order="created_at.desc",
            limit=10,
        )
    except Exception:
        history = []

    return analyses, history

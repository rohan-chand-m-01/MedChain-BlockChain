import json
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ollama_medgemma import get_ollama_client

router = APIRouter()


class OrganRequest(BaseModel):
    organName: str
    analysisText: dict


@router.post("/analyze-organ")
async def analyze_organ(req: OrganRequest):
    if not req.organName or not req.analysisText:
        raise HTTPException(status_code=400, detail="organName and analysisText are required")

    ollama = get_ollama_client()
    if not ollama.is_available():
        raise HTTPException(
            status_code=503,
            detail="MedGemma local model is not available. Run: ollama pull medgemma:4b"
        )

    prompt = f"""You are an expert AI medical consultant. Analyze the provided clinical data exclusively for the specific organ.

Organ to Analyze: {req.organName}

Clinical Analysis Data:
{json.dumps(req.analysisText)}

Instructions:
- Focus ONLY on findings relevant to the {req.organName}.
- If the data does not explicitly mention the {req.organName}, logically connect the patient's conditions, risk_score, and biomarkers to potential risks for this organ.
- score MUST be an integer 0-100 reflecting the organ-specific risk:
    0-29 = safe (no significant findings)
    30-54 = warning (mild or indirect findings)
    55-74 = risk (direct findings or significant indirect risk)
    75-100 = critical (severe or life-threatening findings)
- status must match the score: safe(<30), warning(30-54), risk(55+)

Return ONLY a valid JSON object (no markdown) with exactly this structure:
{{
  "status": "safe|warning|risk",
  "score": 42,
  "details": "One sentence summary of this organ's state based on the report.",
  "aiInsights": ["Clinical observation 1", "Observation 2", "Observation 3"],
  "recommendations": ["Actionable recommendation 1", "Recommendation 2", "Recommendation 3"],
  "markers": [
    {{"name": "Marker Name", "value": "value with unit", "status": "safe|warning|risk"}}
  ],
  "normalRange": "Reference range for the primary marker"
}}"""

    try:
        raw = ollama._generate(prompt, temperature=0.3, max_tokens=1024)
        cleaned = re.sub(r"```json\s*|\s*```|```", "", raw).strip()

        # Extract JSON object
        start = cleaned.find("{")
        if start != -1:
            depth, end = 0, start
            for i in range(start, len(cleaned)):
                if cleaned[i] == "{":
                    depth += 1
                elif cleaned[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            cleaned = cleaned[start:end]

        organ_analysis = json.loads(cleaned)

        # Ensure score is an int and status is consistent
        score = int(organ_analysis.get("score", 10))
        organ_analysis["score"] = score
        if "status" not in organ_analysis or organ_analysis["status"] not in ("safe", "warning", "risk"):
            if score >= 55:
                organ_analysis["status"] = "risk"
            elif score >= 30:
                organ_analysis["status"] = "warning"
            else:
                organ_analysis["status"] = "safe"

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse MedGemma organ analysis response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Organ analysis error: {str(e)}")

    return {"organAnalysis": organ_analysis}

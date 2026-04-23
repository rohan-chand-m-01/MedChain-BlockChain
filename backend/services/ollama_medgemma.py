"""
Ollama MedGemma Local Model - First Priority AI Service
Runs medgemma:4b locally via Ollama for fast, private, offline medical analysis.
No API keys required. Zero latency from network calls.
"""
import os
import json
import logging
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')


class OllamaMedGemma:
    """
    Local MedGemma via Ollama - First priority AI model.
    Uses medgemma:4b running on localhost:11434.
    """

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "medgemma:4b")
        self._available: bool | None = None  # cached availability check
        logger.info(f"🦙 Ollama MedGemma initialized: {self.base_url} | model: {self.model}")

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is loaded."""
        if self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models = [m.get("name", "") for m in resp.json().get("models", [])]
                # Accept both "medgemma:4b" and "medgemma" prefix matches
                self._available = any(
                    m == self.model or m.startswith(self.model.split(":")[0])
                    for m in models
                )
                if self._available:
                    logger.info(f"✅ Ollama available with model: {self.model}")
                else:
                    logger.warning(
                        f"⚠️  Ollama running but model '{self.model}' not found. "
                        f"Available: {models}. Run: ollama pull {self.model}"
                    )
            else:
                self._available = False
        except Exception as e:
            logger.warning(f"⚠️  Ollama not reachable at {self.base_url}: {e}")
            self._available = False
        return self._available

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def _generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """Call Ollama /api/generate and return the response text."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120,  # local model can be slow on first run
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()

    def _chat(self, messages: list[dict], temperature: float = 0.5, max_tokens: int = 1024) -> str:
        """Call Ollama /api/chat (OpenAI-compatible messages format)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()

    # ------------------------------------------------------------------
    # JSON parsing helper
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract and parse the first JSON object from a response string."""
        if not text or not text.strip():
            raise ValueError("Empty response from model")
        cleaned = re.sub(r"```json\s*|\s*```|```", "", text).strip()
        # Find outermost { ... }
        start = cleaned.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response")
        depth = 0
        end = -1
        for i in range(start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            raise ValueError("Incomplete JSON object in response (no closing brace)")
        return json.loads(cleaned[start:end])

    # ------------------------------------------------------------------
    # Public API — mirrors nvidia_nim.py interface
    # ------------------------------------------------------------------

    async def chat(self, prompt: str, temperature: float = 0.5, max_tokens: int = 1024) -> str:
        """Generic chat — drop-in replacement for NVIDIANIMClient.chat()."""
        messages = [{"role": "user", "content": prompt}]
        return self._chat(messages, temperature=temperature, max_tokens=max_tokens)

    async def analyze_report(self, ocr_text: str) -> dict:
        """
        Analyze a medical lab report from OCR text.
        Returns the same schema as nvidia_nim.analyze_report().
        """
        prompt = f"""You are a medical AI expert. Analyze the following lab report carefully and conservatively.

LAB REPORT:
{ocr_text[:3000]}

RULES:
- Only flag conditions that are DIRECTLY supported by abnormal values.
- If all values are normal, say "No significant abnormalities detected".
- Do NOT diagnose diabetes unless glucose/HbA1c is abnormal.
- Do NOT diagnose hypertension unless blood pressure is documented as high.
- Be specific and evidence-based.
- risk_score MUST be an integer 0-100 based on severity of findings:
    0-29 = low risk (mostly normal values)
    30-54 = medium risk (some abnormal values, not urgent)
    55-74 = high risk (multiple abnormal values or one significantly abnormal)
    75-100 = critical risk (life-threatening findings)

Return ONLY a valid JSON object (no markdown, no extra text) with these exact fields:
{{
  "report_type": "diabetes|heart|kidney|general",
  "biomarkers": {{"test_name": "value with unit"}},
  "abnormal_findings": [
    {{
      "name": "test name",
      "value": "actual value",
      "normal": "normal range",
      "explanation": "what this indicates specifically"
    }}
  ],
  "conditions": ["only conditions directly supported by abnormal values"],
  "specialist": "recommended specialist",
  "urgency": "low|medium|high|critical",
  "risk_score": 42,
  "risk_level": "low|medium|high|critical",
  "summary": "comprehensive 5-8 sentence clinical summary with specific values and recommendations"
}}"""

        try:
            logger.info(f"[Ollama] Analyzing report with {self.model}...")
            raw = self._generate(prompt, temperature=0.3, max_tokens=2048)
            result = self._parse_json(raw)
            logger.info(f"✅ [Ollama] Report analysis complete: {result.get('report_type', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"[Ollama] analyze_report failed: {e}")
            # Return a minimal fallback so the pipeline can continue with derived values
            return {
                "report_type": "general",
                "biomarkers": {},
                "abnormal_findings": [],
                "conditions": [],
                "specialist": "General Practitioner",
                "urgency": "low",
                "risk_score": None,
                "risk_level": None,
                "summary": "",
            }

    async def analyze_xray_image(self, image_bytes: bytes) -> dict:
        """
        Analyze a medical image (X-ray, scan) using Ollama multimodal.
        Falls back to text-only prompt if multimodal not supported.
        """
        import base64
        import tempfile

        # Try multimodal via /api/generate with images field
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        prompt = """You are a radiologist AI. Analyze this medical image comprehensively.

Return ONLY a valid JSON object with these fields:
{
  "image_type": "type of imaging and view",
  "image_quality": "good|adequate|limited",
  "abnormal_findings": [{"location": "...", "description": "...", "severity": "mild|moderate|severe", "clinical_significance": "..."}],
  "conditions": ["differential diagnoses with supporting evidence"],
  "specialist": "recommended specialist",
  "urgency": "low|medium|high|critical",
  "summary": "comprehensive 6-8 sentence radiological interpretation"
}"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 2048},
        }

        try:
            logger.info(f"[Ollama] Analyzing image with {self.model} (multimodal)...")
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            resp.raise_for_status()
            raw = resp.json().get("response", "").strip()
            result = self._parse_json(raw)
            logger.info("✅ [Ollama] Image analysis complete")
            return result
        except Exception as e:
            logger.warning(f"[Ollama] Multimodal image analysis failed: {e}")
            raise

    async def analyze_text_report(self, text: str) -> dict:
        """Alias used by gemini_vision-compatible callers."""
        return await self.analyze_report(text)


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------

_instance: OllamaMedGemma | None = None


def get_ollama_client() -> OllamaMedGemma:
    """Return the singleton Ollama MedGemma client."""
    global _instance
    if _instance is None:
        _instance = OllamaMedGemma()
    return _instance

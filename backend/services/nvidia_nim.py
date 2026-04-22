import os
import requests
import logging
import json
import re
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')


class NVIDIANIMClient:
    """NVIDIA NIM API client using Meta Llama 3.1 8B for fast medical report analysis."""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY is not set in .env")
        
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.model = "meta/llama-3.1-8b-instruct"  # Fast 8B model
        
        logger.info(f"✅ NVIDIA API initialized with model: {self.model}")
    
    async def chat(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generic chat method for conversational AI.
        
        Args:
            prompt: The user's message/question
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            AI response as string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "top_p": 0.9,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return content.strip()
            
        except requests.exceptions.Timeout:
            logger.error("NVIDIA API timeout")
            raise Exception("AI service timeout - please try again")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"NVIDIA API error: {e}")
            raise Exception(f"AI service error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in chat: {e}")
            raise Exception(f"Chat error: {str(e)}")
    
    async def analyze_report(self, ocr_text: str) -> dict:
        """
        Extract structured data from OCR text and identify report type.
        Optimized for speed with Llama 3.1 8B model.
        
        Returns: {
            "report_type": "diabetes" | "heart" | "kidney" | "general",
            "biomarkers": {...},
            "conditions": [...],
            "abnormal_findings": [...],
            "specialist": "...",
            "urgency": "low|medium|high|critical",
            "summary": "..."
        }
        """
        prompt = f"""You are a medical AI analyzing a lab report. Be CONSERVATIVE and EVIDENCE-BASED.

LAB REPORT:
{ocr_text[:3000]}

CRITICAL RULES:
1. ONLY mention conditions if there are ABNORMAL values that directly support them
2. If all values are NORMAL, say "No significant abnormalities detected"
3. Focus on what the ABNORMAL findings indicate, not general possibilities
4. For elevated CRP/inflammation markers → focus on infection/inflammation, NOT chronic diseases
5. For elevated IgE → focus on allergic response, NOT chronic diseases
6. Do NOT diagnose diabetes unless glucose/HbA1c is abnormal
7. Do NOT diagnose hypertension unless blood pressure is documented as high
8. Do NOT diagnose heart disease unless cardiac markers (troponin, cholesterol, etc.) are abnormal

ANALYZE:
1. Report type (CBC, Lipid Profile, Comprehensive Metabolic, etc.)
2. List ONLY abnormal findings with values and normal ranges
3. What do these abnormal findings indicate? (be specific and conservative)
4. Recommended specialist based on findings
5. Urgency (low if minor, medium if concerning, high if serious, critical if life-threatening)

Respond as JSON:
{{
  "report_type": "diabetes|heart|kidney|general",
  "biomarkers": {{"test_name": "value with unit"}},
  "abnormal_findings": [
    {{
      "name": "test name",
      "value": "actual value",
      "normal": "normal range",
      "explanation": "what this indicates (be specific - e.g., 'suggests acute infection' not 'may indicate diabetes')"
    }}
  ],
  "conditions": ["ONLY if directly supported by abnormal values - e.g., 'acute infection', 'allergic response', NOT 'diabetes' unless glucose is high"],
  "specialist": "specialist type",
  "urgency": "low|medium|high|critical",
  "summary": "brief summary focusing on abnormal findings and their implications"
}}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 512,
            "stream": False
        }
        
        try:
            logger.info(f"Sending request to NVIDIA API (model: {self.model})...")
            
            # Use requests library with shorter timeout
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=15  # 15 second timeout
            )
            
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            logger.info("✅ NVIDIA API response received")
            
            # Parse JSON from response - handle multiple formats
            cleaned = re.sub(r"```json\n?|\n?```|```", "", content).strip()
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error: {e}, content: {json_str[:200]}")
            
            # Fallback: return safe defaults
            logger.warning(f"Could not parse JSON from response: {content[:200]}")
            return {
                "report_type": "general",
                "biomarkers": {},
                "conditions": [],
                "summary": "Analysis completed. Please review the report manually for detailed insights."
            }
            
        except requests.exceptions.Timeout:
            logger.error("NVIDIA API timeout after 15 seconds")
            raise Exception("NVIDIA API timeout - service is slow")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"NVIDIA API request error: {e}")
            raise Exception(f"NVIDIA API error: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Analysis error: {e}")


def get_nvidia_client() -> NVIDIANIMClient:
    """Get configured NVIDIA NIM client."""
    return NVIDIANIMClient()

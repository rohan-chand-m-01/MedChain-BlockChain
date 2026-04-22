"""
Gemini 2.5 Flash for Medical Analysis
Uses Gemini 2.5 Flash with multimodal vision capabilities
"""
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Load from root .env file
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / '.env')


class GeminiVision:
    """Gemini 2.5 Flash client for medical analysis with vision support"""
    
    def __init__(self):
        # Set API key as environment variable for genai.Client()
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set in .env")
            self.client = None
        else:
            try:
                self.client = genai.Client()
                logger.info("✓ Gemini 2.5 Flash client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None
    
    async def analyze_text_report(self, report_text: str) -> dict:
        """
        Analyze medical text report using Gemini
        
        Args:
            report_text: OCR extracted text from medical report
            
        Returns:
            dict: Analysis results with report_type, risk_score, abnormal_findings, conditions, etc.
        """
        if not self.is_available():
            raise Exception("Gemini client not initialized")
        
        try:
            logger.info("[Gemini] Analyzing text report")
            
            prompt = f"""You are a medical AI analyzing a lab report. Extract ALL data, calculate risk score, and return ONLY valid JSON.

LAB REPORT TEXT:
{report_text[:4000]}

INSTRUCTIONS:
1. Extract EVERY test name and value you see (e.g., "Glucose": "196 mg/dL", "HbA1c": "7.2%")
2. Identify which values are outside normal ranges
3. Calculate a risk_score (0-100) based on severity and number of abnormalities
4. Determine report type: "diabetes" (glucose/HbA1c high), "heart" (cholesterol/lipids high), "kidney" (creatinine/BUN high), or "general"
5. List specific medical conditions based on abnormal values
6. Write a detailed 8-10 sentence summary explaining the findings

RISK SCORE CALCULATION:
- 0-20: All values normal, no concerns
- 21-40: Minor abnormalities, routine follow-up
- 41-60: Moderate abnormalities, needs attention
- 61-80: Significant abnormalities, urgent care needed
- 81-100: Critical abnormalities, immediate medical intervention required

Calculate risk_score based on:
- Number and severity of abnormal findings
- How far values deviate from normal ranges (e.g., glucose 196 vs normal 100 = 96% above = high risk)
- Clinical significance of the abnormalities
- Potential for complications

Set risk_level as: "low" (<30), "medium" (30-60), "high" (61-80), "critical" (>80)

URGENCY CLASSIFICATION (must be one of these exact values):
- "low": Normal or minor findings, routine follow-up
- "medium": Concerning findings requiring prompt evaluation within 1-2 weeks
- "high": Significant abnormalities requiring medical attention within 48-72 hours
- "critical": Critical findings requiring immediate medical intervention

EXAMPLE OUTPUT:
{{
  "report_type": "diabetes",
  "risk_score": 78,
  "risk_level": "high",
  "biomarkers": {{
    "Glucose": "196 mg/dL",
    "HbA1c": "7.8%",
    "Cholesterol": "180 mg/dL"
  }},
  "abnormal_findings": [
    {{
      "name": "Fasting Glucose",
      "value": "196 mg/dL",
      "normal": "70-100 mg/dL",
      "severity": "severe",
      "explanation": "Fasting glucose of 196 mg/dL is significantly elevated, nearly double the upper limit of normal. This level is diagnostic of diabetes mellitus. The elevation indicates impaired insulin function and poor glucose regulation. This requires immediate medical attention."
    }}
  ],
  "conditions": [
    "Type 2 Diabetes Mellitus (fasting glucose 196 mg/dL, diagnostic threshold ≥126 mg/dL)"
  ],
  "specialist": "Endocrinologist",
  "urgency": "high",
  "summary": "This metabolic panel reveals significant abnormalities consistent with uncontrolled diabetes mellitus. Your fasting glucose is critically elevated at 196 mg/dL (normal: 70-100 mg/dL), which is 96% above the upper limit and meets diagnostic criteria for diabetes. HbA1c at 7.8% confirms poor long-term glucose control. These findings indicate your body is not effectively regulating blood sugar. Without treatment, sustained hyperglycemia can lead to serious complications including cardiovascular disease, kidney damage, nerve damage, and vision problems. The combination of elevated fasting glucose and HbA1c strongly suggests Type 2 Diabetes Mellitus requiring immediate medical intervention. I recommend urgent consultation with an endocrinologist within 48-72 hours to initiate treatment. Regular monitoring and follow-up will be essential to prevent long-term complications."
}}

NOW ANALYZE THE REPORT AND RETURN ONLY THE JSON OBJECT:"""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            result_text = response.text
            logger.info(f"[Gemini] Response: {len(result_text)} chars")
            
            parsed = json.loads(result_text)
            
            # Ensure risk_score and risk_level are present
            if "risk_score" not in parsed:
                logger.warning("[Gemini] No risk_score in response, defaulting to 50")
                parsed["risk_score"] = 50
            if "risk_level" not in parsed:
                parsed["risk_level"] = "medium"
            
            logger.info(f"✓ Gemini: type={parsed.get('report_type')}, risk={parsed.get('risk_score')}, biomarkers={len(parsed.get('biomarkers', {}))}")
            return parsed
                
        except Exception as e:
            logger.error(f"Gemini text analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    async def analyze_xray_image(self, image_bytes: bytes) -> dict:
        """
        Analyze medical image using Gemini 2.5 Flash vision capabilities
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            dict: Analysis results with report_type, risk_score, abnormal_findings, conditions, etc.
        """
        if not self.is_available():
            raise Exception("Gemini client not initialized")
        
        try:
            logger.info("[Gemini Vision] Analyzing medical image")
            
            prompt = """You are a medical AI analyzing a lab report image. Extract ALL visible data, calculate risk score, and return ONLY valid JSON.

INSTRUCTIONS:
1. Read ALL test names and values from the image (e.g., "Glucose": "196 mg/dL", "HbA1c": "7.2%")
2. Identify which values are outside normal ranges
3. Calculate a risk_score (0-100) based on severity and number of abnormalities
4. Determine report type: "diabetes" (glucose/HbA1c high), "heart" (cholesterol/lipids high), "kidney" (creatinine/BUN high), or "general"
5. List specific medical conditions based on abnormal values
6. Write a detailed 8-10 sentence summary explaining the findings

RISK SCORE CALCULATION:
- 0-20: All values normal, no concerns
- 21-40: Minor abnormalities, routine follow-up
- 41-60: Moderate abnormalities, needs attention
- 61-80: Significant abnormalities, urgent care needed
- 81-100: Critical abnormalities, immediate medical intervention required

Calculate risk_score based on:
- Number and severity of abnormal findings
- How far values deviate from normal ranges
- Clinical significance of the abnormalities
- Potential for complications

Set risk_level as: "low" (<30), "medium" (30-60), "high" (61-80), "critical" (>80)

URGENCY CLASSIFICATION (must be one of these exact values):
- "low": Normal or minor findings, routine follow-up
- "medium": Concerning findings requiring prompt evaluation within 1-2 weeks
- "high": Significant abnormalities requiring medical attention within 48-72 hours
- "critical": Critical findings requiring immediate medical intervention

EXAMPLE OUTPUT:
{
  "report_type": "diabetes",
  "risk_score": 78,
  "risk_level": "high",
  "biomarkers": {
    "Glucose": "196 mg/dL",
    "HbA1c": "7.8%"
  },
  "abnormal_findings": [
    {
      "name": "Fasting Glucose",
      "value": "196 mg/dL",
      "normal": "70-100 mg/dL",
      "severity": "severe",
      "explanation": "Fasting glucose of 196 mg/dL is significantly elevated, nearly double the upper limit of normal. This requires immediate medical attention."
    }
  ],
  "conditions": [
    "Type 2 Diabetes Mellitus (fasting glucose 196 mg/dL)"
  ],
  "specialist": "Endocrinologist",
  "urgency": "high",
  "summary": "This metabolic panel reveals significant abnormalities consistent with uncontrolled diabetes mellitus. Your fasting glucose is critically elevated at 196 mg/dL. HbA1c at 7.8% confirms poor long-term glucose control. These findings indicate your body is not effectively regulating blood sugar. Without treatment, sustained hyperglycemia can lead to serious complications. I recommend urgent consultation with an endocrinologist within 48-72 hours."
}

NOW ANALYZE THE IMAGE AND RETURN ONLY THE JSON OBJECT:"""
            
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            result_text = response.text
            logger.info(f"[Gemini Vision] Response: {len(result_text)} chars")
            
            parsed = json.loads(result_text)
            
            # Ensure risk_score and risk_level are present
            if "risk_score" not in parsed:
                logger.warning("[Gemini Vision] No risk_score in response, defaulting to 50")
                parsed["risk_score"] = 50
            if "risk_level" not in parsed:
                parsed["risk_level"] = "medium"
            
            logger.info(f"✓ Gemini Vision: type={parsed.get('report_type')}, risk={parsed.get('risk_score')}, biomarkers={len(parsed.get('biomarkers', {}))}")
            return parsed
                
        except Exception as e:
            logger.error(f"Gemini Vision analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


def get_gemini_vision():
    """Get Gemini Vision client"""
    return GeminiVision()

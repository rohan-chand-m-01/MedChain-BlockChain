"""
MedGemma 27B on Vertex AI - Using SDK instead of REST API
This version uses the Vertex AI SDK with explicit generation config
"""
import os
import json
import logging
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class MedGemmaVertexSDK:
    """MedGemma 27B client using Vertex AI SDK"""
    
    def __init__(self):
        # Load credentials
        creds_json = os.getenv("GCP_CREDENTIALS_JSON")
        self.credentials = None
        
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            except Exception as e:
                logger.warning(f"Failed to load GCP credentials: {e}")
        
        # Configuration
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "asia-southeast1")
        self.endpoint_id = os.getenv("MEDGEMMA_ENDPOINT_ID")
        
        # Initialize Vertex AI
        if self.project_id and self.credentials:
            try:
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=self.credentials
                )
                
                # Create model instance pointing to your deployed endpoint
                # Format: projects/{project}/locations/{location}/endpoints/{endpoint_id}
                endpoint_name = f"projects/{self.project_id}/locations/{self.location}/endpoints/{self.endpoint_id}"
                
                # Use GenerativeModel with the endpoint
                self.model = GenerativeModel(
                    model_name=endpoint_name,
                )
                
                logger.info(f"✓ MedGemma SDK initialized: {self.endpoint_id}")
                self.available = True
                
            except Exception as e:
                logger.warning(f"Failed to initialize MedGemma SDK: {e}")
                self.available = False
        else:
            self.available = False
            logger.warning("MedGemma SDK not configured")
    
    def is_available(self) -> bool:
        """Check if MedGemma SDK is configured and available"""
        return self.available
    
    async def analyze_report(self, report_text: str) -> dict:
        """
        Analyze medical report using MedGemma 27B via Vertex AI SDK
        
        Args:
            report_text: OCR extracted text from medical report
            
        Returns:
            dict: Analysis results with report_type, abnormal_findings, conditions, etc.
        """
        if not self.is_available():
            raise Exception("MedGemma SDK not configured")
        
        # Construct medical analysis prompt with proper Gemma IT chat template
        prompt = f"""<start_of_turn>user
You are a specialist in clinical pathology and laboratory medicine. Analyze this medical lab report and provide a detailed clinical interpretation.

LAB REPORT:
{report_text[:3000]}

Provide your analysis as a JSON object with these fields:
- report_type: "diabetes", "heart", "kidney", or "general"
- biomarkers: object with test names as keys and "value unit" as values
- abnormal_findings: array of objects with name, value, normal, severity, explanation
- conditions: array of specific medical conditions identified
- specialist: recommended specialist type
- urgency: "low", "medium", "high", or "critical"
- summary: detailed 5-7 sentence clinical summary with specific values and reasoning

Return ONLY valid JSON, no markdown or extra text.<end_of_turn>
<start_of_turn>model"""
        
        try:
            logger.info(f"[MedGemma SDK] Sending request")
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                max_output_tokens=1024,
                temperature=0.2,
                top_p=0.8,
                top_k=40,
            )
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            logger.info(f"[MedGemma SDK] Response received")
            
            # Extract text from response
            result_text = response.text
            logger.info(f"[MedGemma SDK] Response length: {len(result_text)} chars")
            logger.info(f"[MedGemma SDK] Response preview: {result_text[:200]}")
            
            # Check if echoing
            if (result_text.startswith("Prompt:") or 
                "LAB REPORT:" in result_text[:300] or 
                result_text.startswith("<start_of_turn>") or
                "You are a specialist in clinical pathology" in result_text[:300]):
                logger.error("MedGemma SDK is echoing the prompt")
                raise Exception("MedGemma model not generating responses - echoing prompt")
            
            # Try to parse JSON
            try:
                import re
                # Remove markdown code blocks
                cleaned = re.sub(r'```json\s*|\s*```', '', result_text).strip()
                
                # Find JSON object
                if not cleaned.startswith('{'):
                    start_idx = cleaned.find('{')
                    if start_idx != -1:
                        brace_count = 0
                        end_idx = start_idx
                        for i in range(start_idx, len(cleaned)):
                            if cleaned[i] == '{':
                                brace_count += 1
                            elif cleaned[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        
                        if end_idx > start_idx:
                            cleaned = cleaned[start_idx:end_idx]
                
                parsed = json.loads(cleaned)
                logger.info(f"✓ MedGemma SDK analysis complete: {parsed.get('report_type', 'unknown')}")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.warning(f"MedGemma SDK response not valid JSON: {e}")
                # Return wrapped response
                return {
                    "report_type": "general",
                    "abnormal_findings": [],
                    "conditions": [],
                    "specialist": "General Practitioner",
                    "urgency": "low",  # Changed from 'routine' to match DB constraint
                    "summary": str(result_text)[:2000],
                    "biomarkers": {}
                }
                
        except Exception as e:
            logger.error(f"MedGemma SDK analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


def get_medgemma_vertex_sdk():
    """Get MedGemma Vertex AI SDK client"""
    return MedGemmaVertexSDK()

"""
MedGemma 27B via Gradio API - Medical-specific AI model
Using the Hugging Face Gradio endpoint: warshanks/medgemma-27b-it
"""
import os
import json
import logging
import base64
from gradio_client import Client, handle_file
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from root .env file
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / '.env')


class MedGemmaGradio:
    """MedGemma 27B client using Gradio API with multi-account fallback"""
    
    def __init__(self):
        self.client = None
        self.current_account_index = 0
        self.system_prompt = "You are a helpful medical expert."
        self.max_tokens = 2048
        
        # Load Hugging Face tokens from environment (comma-separated for multiple accounts)
        hf_tokens_str = os.getenv("HUGGINGFACE_TOKENS", "")
        self.hf_tokens = [token.strip() for token in hf_tokens_str.split(",") if token.strip()]
        
        # If no tokens provided, try without authentication (public access)
        if not self.hf_tokens:
            logger.info("No HUGGINGFACE_TOKENS found, using public access")
            self.hf_tokens = [None]  # None means no authentication
        else:
            logger.info(f"Loaded {len(self.hf_tokens)} Hugging Face account(s)")
        
        # Try to initialize with first available token
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gradio client with current token"""
        try:
            current_token = self.hf_tokens[self.current_account_index]
            
            if current_token:
                # Initialize with authentication (use 'token' parameter, not 'hf_token')
                self.client = Client("warshanks/medgemma-27b-it", token=current_token)
                logger.info(f"✓ MedGemma 27B Gradio client initialized with account #{self.current_account_index + 1}")
            else:
                # Initialize without authentication (public access)
                self.client = Client("warshanks/medgemma-27b-it")
                logger.info("✓ MedGemma 27B Gradio client initialized (public access)")
                
        except Exception as e:
            logger.warning(f"Failed to initialize MedGemma Gradio client with account #{self.current_account_index + 1}: {e}")
            self.client = None
    
    def _switch_account(self):
        """Switch to next available Hugging Face account"""
        if len(self.hf_tokens) <= 1:
            logger.warning("No additional accounts available to switch to")
            return False
        
        # Try next account
        self.current_account_index = (self.current_account_index + 1) % len(self.hf_tokens)
        logger.info(f"Switching to Hugging Face account #{self.current_account_index + 1}")
        
        self._initialize_client()
        return self.client is not None
    
    def _handle_api_error(self, error_msg: str):
        """Handle API errors and attempt account switching if needed"""
        # Check if error is related to rate limits or credits
        rate_limit_keywords = ["rate limit", "quota", "credits", "429", "too many requests"]
        
        if any(keyword in error_msg.lower() for keyword in rate_limit_keywords):
            logger.warning(f"Rate limit/quota error detected: {error_msg}")
            
            # Try switching to next account
            if self._switch_account():
                logger.info("Successfully switched to backup account")
                return True
            else:
                logger.error("All accounts exhausted or unavailable")
                return False
        
        return False
    
    def is_available(self) -> bool:
        """Check if MedGemma Gradio is available"""
        return self.client is not None
    
    async def analyze_report(self, report_text: str) -> dict:
        """
        Analyze medical report using MedGemma 27B via Gradio API
        
        Args:
            report_text: OCR extracted text from medical report
            
        Returns:
            dict: Analysis results with report_type, abnormal_findings, conditions, etc.
        """
        if not self.is_available():
            raise Exception("MedGemma Gradio client not initialized")
        
        prompt = f"""Analyze this medical lab report and provide a HIGHLY DETAILED, COMPREHENSIVE clinical interpretation.

LAB REPORT:
{report_text[:3000]}

CRITICAL REQUIREMENTS FOR MAXIMUM DETAIL:

1. COMPREHENSIVE BIOMARKER EXTRACTION:
   - Extract ALL test values with units (e.g., "Glucose": "196 mg/dL")
   - Include EVERY test from the report, even if normal
   - Capture reference ranges when provided

2. DETAILED ABNORMAL FINDINGS (BE EXTREMELY THOROUGH):
   - List EVERY abnormal value with its normal range
   - Provide 3-4 sentences explaining clinical significance of EACH abnormal finding
   - Describe what the deviation indicates (mild/moderate/severe) with specific medical reasoning
   - Connect related abnormal findings (e.g., high glucose + high HbA1c suggests diabetes)
   - Explain potential causes, mechanisms, and pathophysiology
   - Discuss clinical implications and what it means for the patient's health
   - Include relevant medical terminology with explanations

3. SPECIFIC CONDITIONS WITH EVIDENCE:
   - Only list conditions directly supported by abnormal values
   - Be specific: "Type 2 Diabetes Mellitus (fasting glucose 196 mg/dL, diagnostic threshold ≥126 mg/dL)" not just "diabetes"
   - Include severity indicators and supporting evidence
   - Explain WHY the data suggests this condition with medical reasoning

4. RICH, COMPREHENSIVE SUMMARY (MINIMUM 8-10 SENTENCES):
   - Start with report type and comprehensive overall assessment
   - Detail EACH significant abnormal finding with actual values and reference ranges
   - Explain clinical implications and interconnections between findings
   - Discuss potential causes, mechanisms, and pathophysiology
   - Mention trends or patterns across multiple markers
   - Provide context about what these findings mean for overall health
   - Include recommendations for follow-up testing or monitoring
   - Discuss potential complications if left untreated
   - Use medical terminology but explain it clearly for patient understanding
   - Provide actionable next steps and lifestyle recommendations

5. REPORT TYPE CLASSIFICATION:
   - "diabetes" if glucose/HbA1c/insulin abnormal
   - "heart" if cholesterol/triglycerides/cardiac markers abnormal
   - "kidney" if creatinine/BUN/GFR abnormal
   - "general" otherwise

Provide your analysis as a JSON object with these fields:
- report_type: "diabetes", "heart", "kidney", or "general"
- biomarkers: object with test names as keys and "value unit" as values
- abnormal_findings: array of objects with name, value, normal, severity, explanation (3-4 sentences each)
- conditions: array of specific medical conditions with detailed context
- specialist: recommended specialist type
- urgency: "low", "medium", "high", or "critical"
- summary: COMPREHENSIVE 8-10 sentence clinical summary with specific values, medical reasoning, and actionable recommendations

Return ONLY valid JSON, no markdown or extra text."""
        
        try:
            logger.info("[MedGemma Gradio] Sending text analysis request")
            
            # Call Gradio API with text-only message
            result = self.client.predict(
                message={"text": prompt, "files": []},
                param_2=self.system_prompt,
                param_3=self.max_tokens,
                api_name="/chat"
            )
            
            logger.info(f"[MedGemma Gradio] Response received: {type(result)}")
            
            # Parse the response
            result_text = str(result) if not isinstance(result, str) else result
            logger.info(f"[MedGemma Gradio] Response length: {len(result_text)} chars")
            logger.info(f"[MedGemma Gradio] Response preview: {result_text[:200]}")
            
            # Try to parse JSON from response
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
                logger.info(f"✓ MedGemma 27B Gradio analysis complete: {parsed.get('report_type', 'unknown')}")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.warning(f"MedGemma Gradio response not valid JSON: {e}")
                logger.warning(f"Response text: {result_text[:1000]}")
                
                # Fallback: wrap the text response
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
            error_msg = str(e)
            logger.error(f"MedGemma Gradio analysis failed: {error_msg}")
            
            # Try to switch accounts if it's a rate limit error
            if self._handle_api_error(error_msg):
                logger.info("Retrying with new account...")
                # Retry once with new account
                try:
                    result = self.client.predict(
                        message={"text": prompt, "files": []},
                        param_2=self.system_prompt,
                        param_3=self.max_tokens,
                        api_name="/chat"
                    )
                    
                    result_text = str(result) if not isinstance(result, str) else result
                    
                    # Parse JSON
                    import re
                    cleaned = re.sub(r'```json\s*|\s*```', '', result_text).strip()
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
                    logger.info(f"✓ Retry successful with account #{self.current_account_index + 1}")
                    return parsed
                    
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
            
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    async def analyze_xray_image(self, image_bytes: bytes) -> dict:
        """
        Analyze X-ray/medical image using MedGemma 27B multimodal capabilities via Gradio
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            dict: Analysis results with findings, conditions, urgency, etc.
        """
        if not self.is_available():
            raise Exception("MedGemma Gradio client not initialized")
        
        # Save image temporarily for Gradio
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name
        
        try:
            logger.info("[MedGemma Gradio] Sending multimodal image analysis request")
            
            prompt = """Analyze this medical X-ray/scan image and provide a COMPREHENSIVE radiological interpretation.

CRITICAL REQUIREMENTS FOR DETAILED ANALYSIS:

1. IMAGE TYPE IDENTIFICATION:
   - Identify the type of imaging (Chest X-ray, Abdominal X-ray, CT, MRI, etc.)
   - Specify the view/projection (AP, PA, Lateral, etc.)
   - Note image quality and any technical limitations

2. ANATOMICAL STRUCTURES:
   - Systematically describe visible anatomical structures
   - Note normal findings for context
   - Identify any anatomical variants

3. DETAILED ABNORMAL FINDINGS (BE EXTREMELY THOROUGH):
   - Describe EVERY abnormality with precise location and characteristics
   - Use standard radiological terminology (e.g., "opacity", "consolidation", "infiltrate")
   - Specify size, shape, density, margins, and distribution
   - Compare with expected normal appearance
   - Rate severity (mild/moderate/severe) with specific reasoning
   - Explain clinical significance of each finding (3-4 sentences each)

4. DIFFERENTIAL DIAGNOSIS:
   - List possible conditions based on imaging findings
   - Rank by likelihood with supporting evidence
   - Be specific: "Right lower lobe pneumonia with air bronchograms" not just "infection"
   - Include relevant medical context and pathophysiology

5. COMPREHENSIVE SUMMARY (MINIMUM 8-10 SENTENCES):
   - Start with image type and overall quality assessment
   - Systematically review all anatomical regions
   - Detail EACH significant finding with location and characteristics
   - Explain clinical implications and potential causes
   - Discuss urgency and recommended follow-up
   - Mention any incidental findings
   - Provide actionable recommendations for clinicians
   - Include differential diagnoses with reasoning
   - Suggest additional imaging or tests if needed
   - Use medical terminology with clear explanations

Provide your analysis as a JSON object with these fields:
- image_type: type of imaging and view (e.g., "Chest X-ray PA view")
- image_quality: "good", "adequate", or "limited" with explanation
- anatomical_structures: array of visible structures with status
- abnormal_findings: array of objects with location, description, severity, clinical_significance (3-4 sentences each)
- conditions: array of specific differential diagnoses with supporting evidence
- specialist: recommended specialist type
- urgency: "low", "medium", "high", or "critical"
- summary: COMPREHENSIVE 8-10 sentence radiological interpretation with specific findings, medical reasoning, and recommendations

Return ONLY valid JSON, no markdown or extra text."""
            
            # Call Gradio API with image
            result = self.client.predict(
                message={"text": prompt, "files": [handle_file(tmp_path)]},
                param_2=self.system_prompt,
                param_3=self.max_tokens,
                api_name="/chat"
            )
            
            logger.info(f"[MedGemma Gradio] Image analysis response received")
            
            # Parse the response
            result_text = str(result) if not isinstance(result, str) else result
            logger.info(f"[MedGemma Gradio] Response length: {len(result_text)} chars")
            logger.info(f"[MedGemma Gradio] Response preview: {result_text[:300]}")
            
            # Try to parse JSON from response
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
                logger.info(f"✓ MedGemma 27B Gradio image analysis complete: {parsed.get('image_type', 'unknown')}")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.warning(f"MedGemma Gradio image response not valid JSON: {e}")
                logger.warning(f"Cleaned text: {cleaned[:500]}")
                
                # Fallback: wrap the text response
                return {
                    "image_type": "Medical imaging",
                    "image_quality": "unknown",
                    "anatomical_structures": [],
                    "abnormal_findings": [],
                    "conditions": [],
                    "specialist": "Radiologist",
                    "urgency": "medium",
                    "summary": str(result_text)[:2000]
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"MedGemma Gradio image analysis failed: {error_msg}")
            
            # Try to switch accounts if it's a rate limit error
            if self._handle_api_error(error_msg):
                logger.info("Retrying image analysis with new account...")
                # Retry once with new account
                try:
                    result = self.client.predict(
                        message={"text": prompt, "files": [handle_file(tmp_path)]},
                        param_2=self.system_prompt,
                        param_3=self.max_tokens,
                        api_name="/chat"
                    )
                    
                    result_text = str(result) if not isinstance(result, str) else result
                    
                    # Parse JSON
                    import re
                    cleaned = re.sub(r'```json\s*|\s*```', '', result_text).strip()
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
                    logger.info(f"✓ Image retry successful with account #{self.current_account_index + 1}")
                    return parsed
                    
                except Exception as retry_error:
                    logger.error(f"Image retry also failed: {retry_error}")
            
            import traceback
            logger.error(traceback.format_exc())
            raise
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass


def get_medgemma_gradio():
    """Get MedGemma Gradio client"""
    return MedGemmaGradio()

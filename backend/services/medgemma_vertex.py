"""
MedGemma 27B on Vertex AI - Medical-specific AI model
"""
import os
import re
import json
import logging
import requests
from google.cloud import aiplatform
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class MedGemmaVertex:
    """MedGemma 27B client for Vertex AI"""
    
    def __init__(self):
        # Load credentials
        creds_json = os.getenv("GCP_CREDENTIALS_JSON")
        self.credentials = None
        self.access_token = None
        
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                # Get access token
                self.credentials.refresh(Request())
                self.access_token = self.credentials.token
            except Exception as e:
                logger.warning(f"Failed to load GCP credentials: {e}")
        
        # Configuration
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "asia-southeast1")
        self.endpoint_id = os.getenv("MEDGEMMA_ENDPOINT_ID")
        
        # Build REST API URL (more reliable than SDK)
        if self.endpoint_id and self.project_id and self.access_token:
            # Use the direct predict URL format
            self.predict_url = f"https://{self.endpoint_id}.{self.location}-626609130804.prediction.vertexai.goog/v1/projects/{self.project_id}/locations/{self.location}/endpoints/{self.endpoint_id}:predict"
            logger.info(f"✓ MedGemma 27B endpoint configured: {self.endpoint_id}")
        else:
            self.predict_url = None
            logger.warning("MedGemma endpoint not configured")
    
    def is_available(self) -> bool:
        """Check if MedGemma is configured and available"""
        return self.predict_url is not None and self.access_token is not None
    
    async def analyze_report(self, report_text: str) -> dict:
        """
        Analyze medical report using MedGemma 27B via REST API with Chat Completions format
        
        Args:
            report_text: OCR extracted text from medical report
            
        Returns:
            dict: Analysis results with report_type, abnormal_findings, conditions, etc.
        """
        if not self.is_available():
            raise Exception("MedGemma endpoint not configured")
        
        # Refresh token if needed
        if self.credentials:
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token
        
        # Construct medical analysis using Chat Completions format (OpenAI-compatible)
        # This is the format MedGemma on Vertex AI expects
        try:
            logger.info(f"[MedGemma] Sending Chat Completions request")
            
            # Prepare request payload with Chat Completions format
            payload = {
                "instances": [{
                    "@requestFormat": "chatCompletions",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a specialist in clinical pathology and laboratory medicine. Analyze medical lab reports and provide detailed clinical interpretations in JSON format."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze this medical lab report and provide a HIGHLY DETAILED, COMPREHENSIVE clinical interpretation.

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

EXAMPLE OF EXCELLENT DETAILED SUMMARY:
"This comprehensive metabolic panel reveals significantly elevated fasting plasma glucose at 196 mg/dL, which is 96% above the upper limit of normal (70-100 mg/dL) and well exceeds the diagnostic threshold for diabetes mellitus (≥126 mg/dL) as defined by the American Diabetes Association 2023 guidelines. The post-prandial glucose level of 317 mg/dL further confirms poor glycemic control, indicating the body's inability to effectively regulate blood sugar levels after meals. These findings strongly suggest Type 2 Diabetes Mellitus, a chronic metabolic disorder characterized by insulin resistance and/or insufficient insulin production by the pancreatic beta cells. Untreated or poorly controlled diabetes can lead to serious long-term complications including cardiovascular disease, nephropathy (kidney damage), retinopathy (vision loss), neuropathy (nerve damage), and increased risk of infections. The elevated glucose levels indicate that glucose molecules are accumulating in the bloodstream rather than being transported into cells for energy, which can cause cellular damage through glycation of proteins and oxidative stress. Immediate medical attention is recommended to initiate or adjust diabetes management, which typically includes lifestyle modifications (dietary changes, regular exercise, weight management), oral hypoglycemic medications (such as metformin), and potentially insulin therapy depending on disease severity. Additional testing should include HbA1c (glycated hemoglobin) to assess average blood glucose control over the past 2-3 months, lipid panel to evaluate cardiovascular risk, kidney function tests (creatinine, eGFR), and comprehensive metabolic panel. Regular monitoring with an endocrinologist is essential to prevent complications and achieve target glucose levels (fasting <130 mg/dL, post-prandial <180 mg/dL). Early intervention and consistent management can significantly reduce the risk of complications and improve long-term health outcomes."

Return ONLY valid JSON, no markdown or extra text."""
                        }
                    ],
                    "max_tokens": 2048
                }],
                "parameters": {
                    "temperature": 0.3,
                    "topP": 0.9,
                    "topK": 40,
                    "maxOutputTokens": 2048
                }
            }
            
            # Make REST API request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.predict_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            logger.info(f"[MedGemma] Response received")
            logger.info(f"[MedGemma] Response structure: {list(result.keys())}")
            
            # Extract prediction from Chat Completions format
            # The response structure is: {"predictions": {...}} not {"predictions": [{...}]}
            if 'predictions' in result:
                prediction = result['predictions']
                logger.info(f"[MedGemma] Prediction type: {type(prediction)}")
                
                # Chat Completions format returns: {"choices": [{"message": {"content": "..."}}]}
                if isinstance(prediction, dict) and 'choices' in prediction:
                    choices = prediction.get('choices', [])
                    if choices and len(choices) > 0:
                        message = choices[0].get('message', {})
                        result_text = message.get('content', '')
                        
                        logger.info(f"[MedGemma] Chat Completions response length: {len(result_text)} chars")
                        logger.info(f"[MedGemma] Response preview: {result_text[:200]}")
                        
                        # Check if echoing (shouldn't happen with Chat Completions format)
                        if (result_text.startswith("Prompt:") or 
                            "LAB REPORT:" in result_text[:300] or 
                            "You are a specialist in clinical pathology" in result_text[:300]):
                            logger.error("MedGemma is echoing the prompt")
                            raise Exception("MedGemma model not generating responses - echoing prompt")
                        
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
                            logger.info(f"✓ MedGemma 27B analysis complete: {parsed.get('report_type', 'unknown')}")
                            return parsed
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"MedGemma response not valid JSON: {e}")
                            logger.warning(f"Response text: {result_text[:1000]}")
                            
                            # Last resort: wrap the text response
                            return {
                                "report_type": "general",
                                "abnormal_findings": [],
                                "conditions": [],
                                "specialist": "General Practitioner",
                                "urgency": "low",  # Changed from 'routine' to match DB constraint
                                "summary": str(result_text)[:2000],
                                "biomarkers": {}
                            }
            
            raise Exception("No predictions in response")
                
        except Exception as e:
            logger.error(f"MedGemma 27B analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


    async def analyze_xray_image(self, image_bytes: bytes) -> dict:
        """
        Analyze X-ray/medical image using MedGemma 27B multimodal capabilities
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            dict: Analysis results with findings, conditions, urgency, etc.
        """
        if not self.is_available():
            raise Exception("MedGemma endpoint not configured")
        
        # Refresh token if needed
        if self.credentials:
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token
        
        # Convert image to base64
        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        try:
            logger.info(f"[MedGemma] Sending multimodal X-ray analysis request")
            
            # Prepare request payload with Chat Completions format + image
            payload = {
                "instances": [{
                    "@requestFormat": "chatCompletions",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a specialist radiologist with expertise in interpreting medical imaging including X-rays, CT scans, and MRI. Analyze medical images and provide detailed clinical interpretations in JSON format."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Analyze this medical X-ray/scan image and provide a COMPREHENSIVE radiological interpretation.

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

6. URGENCY CLASSIFICATION (must be one of these exact values):
   - "low" - normal or minor findings, routine follow-up
   - "medium" - concerning findings requiring prompt evaluation within 1-2 weeks
   - "high" - significant abnormalities requiring medical attention within 48-72 hours
   - "critical" - critical findings requiring immediate medical intervention

Provide your analysis as a JSON object with these fields:
- image_type: type of imaging and view (e.g., "Chest X-ray PA view")
- image_quality: "good", "adequate", or "limited" with explanation
- anatomical_structures: array of visible structures with status
- abnormal_findings: array of objects with location, description, severity, clinical_significance (3-4 sentences each)
- conditions: array of specific differential diagnoses with supporting evidence
- specialist: recommended specialist type
- urgency: "low", "medium", "high", or "critical"
- summary: COMPREHENSIVE 8-10 sentence radiological interpretation with specific findings, medical reasoning, and recommendations

EXAMPLE OF EXCELLENT DETAILED SUMMARY:
"This posteroanterior (PA) chest radiograph demonstrates adequate inspiratory effort with 9 posterior ribs visible, indicating proper technique for diagnostic interpretation. The cardiac silhouette appears enlarged with a cardiothoracic ratio of approximately 0.55 (normal <0.50), suggesting cardiomegaly which may indicate chronic heart failure, hypertensive heart disease, or valvular pathology. There is a focal area of increased opacity in the right lower lobe measuring approximately 4x3 cm with irregular margins and air bronchograms visible within the consolidation, highly suggestive of bacterial pneumonia, most commonly caused by Streptococcus pneumoniae or Haemophilus influenzae. The presence of air bronchograms (air-filled bronchi visible against the consolidated lung tissue) is a classic radiological sign that helps differentiate pneumonia from other causes of lung opacity such as pleural effusion or atelectasis. The left lung fields appear clear with normal vascular markings and no evidence of infiltrates, masses, or pleural effusion. The costophrenic angles are sharp bilaterally, ruling out significant pleural fluid accumulation. The mediastinal contours are within normal limits with no evidence of lymphadenopathy or mass effect. Bony structures including the ribs, clavicles, and visible spine show no acute fractures or lytic lesions. Given the combination of consolidation with air bronchograms in the right lower lobe and cardiomegaly, this patient likely has community-acquired pneumonia with underlying cardiac disease, requiring prompt antibiotic therapy (typically a beta-lactam plus macrolide or respiratory fluoroquinolone) and cardiac evaluation. Immediate medical attention is recommended with follow-up chest X-ray in 4-6 weeks after treatment to ensure resolution and rule out underlying malignancy. Additional testing should include complete blood count, inflammatory markers (CRP, procalcitonin), blood cultures if febrile, and echocardiography to assess cardiac function and ejection fraction."

Return ONLY valid JSON, no markdown or extra text."""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 2048
                }],
                "parameters": {
                    "temperature": 0.3,
                    "topP": 0.9,
                    "topK": 40,
                    "maxOutputTokens": 2048
                }
            }
            
            # Make REST API request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.predict_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            logger.info(f"[MedGemma] X-ray analysis response received")
            logger.info(f"[MedGemma] Response keys: {list(result.keys())}")
            logger.info(f"[MedGemma] Full response structure: {json.dumps(result, indent=2)[:500]}")
            
            # Extract prediction from Chat Completions format
            if 'predictions' in result:
                prediction = result['predictions']
                logger.info(f"[MedGemma] Prediction type: {type(prediction)}")
                
                # Handle both dict and list formats
                if isinstance(prediction, list) and len(prediction) > 0:
                    prediction = prediction[0]
                
                if isinstance(prediction, dict) and 'choices' in prediction:
                    choices = prediction.get('choices', [])
                    if choices and len(choices) > 0:
                        message = choices[0].get('message', {})
                        result_text = message.get('content', '')
                        
                        logger.info(f"[MedGemma] X-ray response length: {len(result_text)} chars")
                        logger.info(f"[MedGemma] Response preview: {result_text[:300]}")
                        
                        # Parse JSON from response
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
                            logger.info(f"✓ MedGemma 27B X-ray analysis complete: {parsed.get('image_type', 'unknown')}")
                            return parsed
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"MedGemma X-ray response not valid JSON: {e}")
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
                else:
                    logger.error(f"[MedGemma] Unexpected prediction format: {type(prediction)}")
                    logger.error(f"[MedGemma] Prediction content: {str(prediction)[:500]}")
            else:
                logger.error(f"[MedGemma] No 'predictions' key in response")
            
            raise Exception(f"No predictions in response. Response keys: {list(result.keys())}")
                
        except Exception as e:
            logger.error(f"MedGemma 27B X-ray analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


def get_medgemma_vertex():
    """Get MedGemma Vertex AI client"""
    return MedGemmaVertex()

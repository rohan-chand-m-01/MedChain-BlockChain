"""
Local ClinicalBERT using pattern-based extraction
Fast, reliable, no external dependencies
"""

import re
from typing import List, Dict


class LocalClinicalBERT:
    """
    Pattern-based medical NER.
    Fast and reliable without transformer dependencies.
    """
    
    def __init__(self):
        # Medical entity patterns
        self.patterns = {
            "DISEASE": [
                r'\b(diabetes|hypertension|kidney disease|heart disease|cancer|stroke|asthma|copd|ckd)\b',
                r'\b(diabetic|hypertensive|renal failure|cardiac arrest|myocardial infarction)\b',
                r'\b(type 2 diabetes|type 1 diabetes|coronary artery disease|chronic kidney disease)\b',
            ],
            "TEST": [
                r'\b(glucose|hba1c|cholesterol|creatinine|bun|gfr|hemoglobin|albumin)\b',
                r'\b(blood pressure|bp|heart rate|bmi|ecg|ekg|x-ray|mri|ct scan)\b',
                r'\b(fasting blood sugar|postprandial|ldl|hdl|triglycerides)\b',
            ],
            "MEDICATION": [
                r'\b(metformin|insulin|aspirin|statin|ace inhibitor|beta blocker)\b',
                r'\b(lisinopril|atorvastatin|metoprolol|amlodipine|losartan)\b',
            ],
            "SYMPTOM": [
                r'\b(pain|fever|nausea|fatigue|dizziness|shortness of breath|chest pain)\b',
                r'\b(headache|cough|weakness|swelling|numbness|dyspnea)\b',
            ],
            "MEASUREMENT": [
                r'\b\d+\s*mg/dl\b',
                r'\b\d+/\d+\s*mmhg\b',
                r'\b\d+\.?\d*\s*%\b',
            ]
        }
    
    async def extract_entities(self, text: str) -> dict:
        """
        Extract medical entities from text using patterns.
        """
        entities = self._extract_with_patterns(text)
        
        # Deduplicate
        seen = set()
        filtered = []
        for entity in entities:
            key = (entity["text"].lower(), entity["label"])
            if key not in seen:
                seen.add(key)
                filtered.append(entity)
        
        return {
            "entities": filtered[:15],
            "method": "pattern-based",
            "count": len(filtered)
        }
    
    def _extract_with_patterns(self, text: str) -> List[Dict]:
        """Extract entities using regex patterns."""
        text_lower = text.lower()
        entities = []
        
        for label, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    # Get original case from text
                    start = match.start()
                    end = match.end()
                    original_text = text[start:end]
                    
                    entities.append({
                        "text": original_text,
                        "label": label,
                        "score": 0.90
                    })
        
        return entities


def get_clinical_bert_client():
    """Get clinical BERT client."""
    return LocalClinicalBERT()

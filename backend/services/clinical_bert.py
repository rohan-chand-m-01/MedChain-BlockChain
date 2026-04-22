"""
Clinical NER Service
Uses pattern-based extraction (reliable and fast)
"""

# Use simple pattern-based extraction
from services.clinical_bert_local import LocalClinicalBERT

def get_clinical_bert_client():
    """Get clinical BERT client (pattern-based)."""
    return LocalClinicalBERT()

__all__ = ['get_clinical_bert_client']

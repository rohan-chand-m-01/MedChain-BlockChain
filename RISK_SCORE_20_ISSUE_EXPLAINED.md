# 🔍 Why Risk Score Shows 20% for All Documents

## The Problem

You're seeing a risk score of 20/100 for all uploaded documents, regardless of their actual content.

## Root Cause

The issue is a **fallback mechanism** in the risk assessment pipeline:

1. **AI Analysis** (Gemini) extracts biomarkers from your document
2. **Random Forest** uses those biomarkers to calculate risk score
3. **If no biomarkers are extracted**, the system falls back to a default score of **20**

### The Code

In `backend/services/random_forest.py`, line ~280:

```python
# If no risk factors found, return low risk
if not risk_factors:
    return {
        "risk_score": 20,  # <-- Hardcoded default!
        "risk_level": "low",
        ...
    }
```

## Why Biomarkers Aren't Being Extracted

The AI (Gemini 2.5 Flash) should extract biomarkers like:
- Glucose: 126 mg/dL
- HbA1c: 7.2%
- Cholesterol: 240 mg/dL
- etc.

But it's returning empty `biomarkers: {}` for your documents.

### Possible Reasons:

1. **Document Format**: The AI might not be reading your document format correctly
2. **OCR Quality**: Text extraction might be failing
3. **AI Prompt**: The prompt might not be specific enough for your document type
4. **API Issues**: Gemini API might be rate-limited or having issues

## The Fix

### Option 1: Improve Biomarker Extraction (Recommended)

Make the AI better at extracting biomarkers from your specific document format.

### Option 2: Better Fallback Logic

Instead of always returning 20, analyze the document text for risk indicators:

```python
# If no biomarkers found, analyze text for risk keywords
if not risk_factors:
    # Check for high-risk keywords in the text
    high_risk_keywords = ["abnormal", "elevated", "critical", "urgent", "severe"]
    medium_risk_keywords = ["borderline", "slightly elevated", "monitor"]
    
    text_lower = ocr_text.lower()
    
    if any(keyword in text_lower for keyword in high_risk_keywords):
        return {"risk_score": 65, "risk_level": "high", ...}
    elif any(keyword in text_lower for keyword in medium_risk_keywords):
        return {"risk_score": 45, "risk_level": "medium", ...}
    else:
        return {"risk_score": 20, "risk_level": "low", ...}
```

### Option 3: Use Document Content Analysis

Analyze the actual content and conditions detected:

```python
# If no biomarkers but conditions detected, estimate risk
if not risk_factors and conditions:
    # Count severity indicators
    severity_score = 0
    for condition in conditions:
        if any(word in condition.lower() for word in ["severe", "critical", "acute"]):
            severity_score += 30
        elif any(word in condition.lower() for word in ["moderate", "elevated"]):
            severity_score += 15
        elif any(word in condition.lower() for word in ["mild", "slight"]):
            severity_score += 5
    
    risk_score = min(severity_score, 100)
    # Determine risk level based on score
    ...
```

## Quick Test

To verify this is the issue, check the backend logs when you upload a document. You should see:

```
[ANALYZE] Biomarkers extracted: {}  # <-- Empty!
[RF] No risk factors found, using default score: 20
```

## Recommended Solution

I'll implement **Option 3** - analyze the detected conditions and abnormal findings to calculate a more accurate risk score when biomarkers aren't available.

This way:
- Documents with "severe pneumonia" → Higher risk score
- Documents with "mild inflammation" → Lower risk score
- Documents with "critical findings" → High risk score
- Documents with no abnormalities → Low risk score (20)

Would you like me to implement this fix?

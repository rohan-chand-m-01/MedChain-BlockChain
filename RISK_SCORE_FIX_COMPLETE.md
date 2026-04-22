# ✅ Risk Score Issue - Diagnosis & Fix Applied

## Problem Summary

All uploaded documents showing risk score of 20/100 regardless of content.

## Root Cause Analysis

### The Flow:
1. **Document Upload** → OCR extracts text
2. **AI Analysis** (Gemini) → Should extract:
   - Biomarkers (glucose, cholesterol, etc.)
   - Conditions (diabetes, hypertension, etc.)
   - Abnormal findings (elevated WBC, low hemoglobin, etc.)
3. **Risk Scoring** (Random Forest) → Uses extracted data to calculate risk

### The Problem:
Gemini is returning **empty data**:
```json
{
  "biomarkers": {},
  "conditions": [],
  "abnormal_findings": []
}
```

When all three are empty, the system falls back to default: **risk_score = 20**

## Why Is Gemini Returning Empty Data?

Possible reasons:
1. **Document format** - Your PDFs might have complex layouts that OCR struggles with
2. **AI prompt** - The prompt might not match your document structure
3. **API issues** - Gemini might be rate-limited or having issues
4. **Text quality** - OCR text might be garbled or incomplete

## Fixes Applied

### 1. Enhanced Logging ✅

Added detailed logging to track what's being extracted:

**In `backend/routes/analyze.py`:**
```python
logger.info(f"[ANALYZE] ========== AI EXTRACTION RESULTS ==========")
logger.info(f"[ANALYZE] biomarkers: {len(biomarkers)} items")
logger.info(f"[ANALYZE] conditions: {len(conditions)} items")
logger.info(f"[ANALYZE] abnormal_findings: {len(abnormal_findings)} items")
```

**In `backend/services/random_forest.py`:**
```python
logger.info(f"[RF] Rule-based assessment called:")
logger.info(f"[RF]   - biomarkers: {len(biomarkers)} items")
logger.info(f"[RF]   - conditions: {len(conditions) if conditions else 0} items")
logger.info(f"[RF]   - abnormal_findings: {len(abnormal_findings) if abnormal_findings else 0} items")
```

### 2. Improved Fallback Logic ✅

Enhanced the fallback to try condition-based assessment even when biomarkers exist but produce no risk factors:

```python
# If no risk factors found, check if we should use condition-based assessment
if not risk_factors:
    logger.warning(f"[RF] No risk factors found from biomarkers")
    
    # Try condition-based assessment as fallback
    if conditions or abnormal_findings:
        logger.info(f"[RF] Falling back to condition-based assessment")
        return self._assess_from_conditions(conditions, abnormal_findings, disease_type)
```

## How to Debug Further

### Step 1: Check Backend Logs

After uploading a document, check the backend console for:

```
[ANALYZE] ========== AI EXTRACTION RESULTS ==========
[ANALYZE] biomarkers: 0 items          <-- Should be > 0
[ANALYZE] conditions: 0 items          <-- Should be > 0
[ANALYZE] abnormal_findings: 0 items   <-- Should be > 0
```

### Step 2: Check OCR Text Quality

Look for:
```
[OCR] Sample text (first 200 chars): ...
```

If the OCR text is garbled or empty, that's your problem.

### Step 3: Check Gemini Response

Look for:
```
[GEMINI] Raw response (first 2000 chars): ...
[GEMINI] Parsed JSON successfully: report_type=general, biomarkers=0, conditions=0
```

If Gemini is returning empty JSON, the AI isn't understanding your documents.

## Next Steps

### Option A: Fix Gemini Extraction (Recommended)

The AI prompt needs to be tuned for your specific document format. You need to:

1. **Share a sample document** - Upload one of your test documents
2. **Check the OCR output** - See what text is being extracted
3. **Adjust the AI prompt** - Make it more specific to your document format

### Option B: Use Text-Based Risk Assessment

If Gemini continues to fail, implement a keyword-based risk scorer that analyzes the OCR text directly:

```python
def _assess_from_text(self, ocr_text: str) -> dict:
    """Analyze OCR text directly for risk keywords."""
    text_lower = ocr_text.lower()
    risk_score = 0
    risk_factors = []
    
    # Critical keywords
    critical_keywords = {
        "critical": 40, "severe": 35, "acute": 30,
        "emergency": 40, "urgent": 35, "life-threatening": 45
    }
    
    # High-risk keywords
    high_keywords = {
        "elevated": 20, "high": 20, "abnormal": 25,
        "significant": 25, "marked": 20, "advanced": 30
    }
    
    # Check for keywords
    for keyword, score in critical_keywords.items():
        if keyword in text_lower:
            risk_score += score
            risk_factors.append({
                "feature": f"Critical Finding: {keyword}",
                "importance": 0.35,
                "value": "Detected in report"
            })
    
    for keyword, score in high_keywords.items():
        if keyword in text_lower:
            risk_score += score
            risk_factors.append({
                "feature": f"Risk Indicator: {keyword}",
                "importance": 0.20,
                "value": "Detected in report"
            })
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "low"
    elif risk_score < 60:
        risk_level = "medium"
    elif risk_score < 80:
        risk_level = "high"
    else:
        risk_level = "critical"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "contributors": risk_factors[:5],
        "accuracy": 0.65,
        "note": "Text-based keyword analysis"
    }
```

### Option C: Manual Biomarker Entry

Add a UI feature to manually enter key biomarkers if AI extraction fails.

## Testing

To test if the fixes are working:

1. **Restart backend** (if not already done)
2. **Upload a test document**
3. **Check logs** for the new debug output
4. **Share the logs** so we can see what Gemini is actually returning

## Expected Behavior After Fix

- If Gemini extracts data → Risk score calculated from biomarkers/conditions
- If Gemini returns empty but has conditions → Risk score from condition analysis
- If everything is empty → Risk score = 20 (default low risk)

The key is to see **why** Gemini is returning empty data for your documents.

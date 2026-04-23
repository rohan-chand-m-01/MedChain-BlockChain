# MedGemma 27B Gradio API Integration

## Overview

This project now uses the **MedGemma 27B** model via the Gradio API for AI-powered medical report analysis. MedGemma is a specialized medical AI model that provides comprehensive clinical interpretations of lab reports and medical images.

## What Changed

### Previous System
- Used MedGemma 27B via Google Vertex AI (required GCP credentials and endpoint setup)
- Required complex authentication and configuration
- Limited to specific GCP regions

### New System
- Uses MedGemma 27B via Hugging Face Gradio API
- Simpler integration with no authentication required
- Publicly accessible endpoint: `warshanks/medgemma-27b-it`
- Supports both text and multimodal (image) analysis

## Architecture

### Analysis Pipeline

1. **Image Detection**
   - If the uploaded file is an image (JPG, PNG, etc.), the system attempts multimodal analysis first
   - MedGemma analyzes the image directly without OCR

2. **Text Analysis Fallback**
   - If multimodal fails or the file is a PDF, OCR extracts text
   - MedGemma analyzes the extracted text

3. **Fallback Chain**
   - MedGemma Gradio (primary, medical-specific)
   - BioGPT (local, pattern-based)
   - NVIDIA Llama 3.1 8B (fallback)

## Files Modified

### New Files
- `backend/services/medgemma_gradio.py` - Gradio API client implementation
- `backend/test_medgemma_gradio.py` - Test script for the integration
- `MEDGEMMA_GRADIO_INTEGRATION.md` - This documentation

### Modified Files
- `backend/routes/analyze.py` - Updated to use Gradio client instead of Vertex AI
- `backend/requirements.txt` - Added `gradio_client>=1.0.0` dependency

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install the `gradio_client` package along with other dependencies.

### 2. Configure Multiple Accounts (Optional but Recommended)

For uninterrupted service, configure multiple Hugging Face accounts:

```bash
# Edit backend/.env
HUGGINGFACE_TOKENS=hf_token1,hf_token2,hf_token3
```

**Benefits:**
- Automatic fallback when one account runs out of credits
- Higher combined rate limits
- Zero downtime during high usage

**See:** `MULTI_ACCOUNT_SETUP.md` for detailed instructions

### 3. No Other Configuration Required

Unlike the Vertex AI version, no API keys or credentials are required if you use public access (leave `HUGGINGFACE_TOKENS` empty).

## Usage

### Programmatic Usage

```python
from services.medgemma_gradio import get_medgemma_gradio

# Initialize client
client = get_medgemma_gradio()

# Check availability
if client.is_available():
    # Analyze text report
    result = await client.analyze_report(report_text)
    
    # Analyze medical image
    with open("xray.jpg", "rb") as f:
        image_bytes = f.read()
    result = await client.analyze_xray_image(image_bytes)
```

### API Endpoint

The existing `/analyze-report` endpoint automatically uses MedGemma Gradio:

```bash
POST /analyze-report
{
  "file_base64": "base64_encoded_file",
  "file_type": "image/jpeg",
  "patient_wallet": "0x...",
  "file_name": "lab_report.jpg"
}
```

## Testing

Run the test script to verify the integration:

```bash
cd backend
python test_medgemma_gradio.py
```

Expected output:
```
=== Testing MedGemma Gradio Text Analysis ===

✓ MedGemma Gradio client initialized

Analyzing sample report...

=== Analysis Results ===
Report Type: diabetes
Urgency: moderate
Specialist: Endocrinologist

Biomarkers Found: 6
Conditions: ['Type 2 Diabetes Mellitus', ...]
Abnormal Findings: 5

Summary:
This comprehensive metabolic panel reveals significantly elevated fasting plasma glucose...

✅ Text analysis test completed successfully!
```

## API Response Format

MedGemma returns structured JSON with comprehensive clinical analysis:

```json
{
  "report_type": "diabetes|heart|kidney|general",
  "biomarkers": {
    "Glucose": "196 mg/dL",
    "HbA1c": "7.8%"
  },
  "abnormal_findings": [
    {
      "name": "Fasting Glucose",
      "value": "196 mg/dL",
      "normal": "70-100 mg/dL",
      "severity": "moderate",
      "explanation": "Detailed clinical explanation..."
    }
  ],
  "conditions": [
    "Type 2 Diabetes Mellitus (fasting glucose 196 mg/dL)"
  ],
  "specialist": "Endocrinologist",
  "urgency": "moderate",
  "summary": "Comprehensive 8-10 sentence clinical summary..."
}
```

## Features

### Multi-Account Support
- Configure multiple Hugging Face tokens for automatic fallback
- System detects rate limits and switches accounts seamlessly
- Logs show which account is currently active
- See `MULTI_ACCOUNT_SETUP.md` for configuration

### Text Analysis
- Extracts all biomarkers with values and units
- Identifies abnormal findings with detailed explanations
- Provides evidence-based condition diagnoses
- Recommends appropriate specialists
- Generates comprehensive clinical summaries (8-10 sentences)

### Image Analysis (Multimodal)
- Analyzes X-rays, CT scans, MRI, and lab report images
- Identifies anatomical structures
- Detects abnormalities with precise descriptions
- Provides differential diagnoses
- Generates radiological interpretations

## Advantages Over Previous System

1. **Simplicity**: No GCP credentials or endpoint configuration needed
2. **Accessibility**: Publicly available API, no authentication required
3. **Reliability**: Hosted on Hugging Face infrastructure
4. **Cost**: Free to use (subject to Gradio API limits)
5. **Maintenance**: No need to manage GCP resources or endpoints

## Limitations

1. **Rate Limits**: Gradio API may have usage limits (not documented)
2. **Latency**: May be slower than dedicated Vertex AI endpoints
3. **Availability**: Depends on Hugging Face/Gradio uptime
4. **Privacy**: Data is sent to external API (consider for sensitive data)

## Fallback Strategy

If MedGemma Gradio is unavailable, the system automatically falls back to:

1. **BioGPT** (local, privacy-focused)
2. **NVIDIA Llama 3.1 8B** (cloud, fast)

This ensures the analysis pipeline remains operational even if the primary service is down.

## Troubleshooting

### Client Not Available
```python
client = get_medgemma_gradio()
if not client.is_available():
    print("MedGemma Gradio client failed to initialize")
```

**Possible causes:**
- Network connectivity issues
- Gradio API is down
- `gradio_client` package not installed

**Solution:**
```bash
pip install gradio_client --upgrade
```

### Analysis Timeout
If analysis takes too long, the Gradio client has a 60-second timeout. The system will automatically fall back to alternative AI services.

### JSON Parsing Errors
MedGemma is prompted to return valid JSON. If parsing fails, the system wraps the text response in a safe default structure.

## Future Enhancements

1. **Caching**: Cache results for identical reports to reduce API calls
2. **Batch Processing**: Support multiple reports in a single request
3. **Custom Prompts**: Allow users to customize analysis prompts
4. **Local Deployment**: Option to run MedGemma locally for privacy-sensitive use cases

## References

- Gradio API: https://www.gradio.app/docs/python-client/introduction
- MedGemma Model: https://huggingface.co/spaces/warshanks/medgemma-27b-it
- Original Gradio API Documentation: https://www.gradio.app/guides/getting-started-with-the-python-client

## Support

For issues or questions:
1. Check the logs in `backend/main.py` for detailed error messages
2. Run the test script to verify the integration
3. Review the Gradio API documentation for API-specific issues

# Quick Setup Guide: MedGemma Gradio Integration

## Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install gradio_client
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Multiple Accounts (Recommended)

For production use, configure multiple Hugging Face accounts in `backend/.env`:

```bash
# Multiple accounts for automatic fallback
HUGGINGFACE_TOKENS=hf_token1,hf_token2,hf_token3

# Or leave empty for public access (rate limited)
HUGGINGFACE_TOKENS=
```

**How to get tokens:**
1. Create accounts at https://huggingface.co/join
2. Go to Settings → Access Tokens
3. Generate tokens with "Read" permission
4. Add to `.env` (comma-separated)

**See:** `MULTI_ACCOUNT_SETUP.md` for detailed instructions

### 3. Verify Installation

Run the test script:

```bash
python test_medgemma_gradio.py
```

Expected output:
```
=== Testing MedGemma Gradio Text Analysis ===

✓ MedGemma Gradio client initialized
Analyzing sample report...

=== Analysis Results ===
Report Type: diabetes
...
✅ Text analysis test completed successfully!
```

### Step 3: Start the Backend

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
Loaded 3 Hugging Face account(s)
✓ MedGemma 27B Gradio client initialized with account #1
```

### Step 4: Test the API

```bash
curl -X POST http://localhost:8000/analyze-report \
  -H "Content-Type: application/json" \
  -d '{
    "file_base64": "...",
    "file_type": "image/jpeg",
    "patient_wallet": "0x123...",
    "file_name": "lab_report.jpg"
  }'
```

## No Configuration Required!

Unlike the previous Vertex AI setup, the Gradio API requires:
- ❌ No API keys
- ❌ No GCP credentials
- ❌ No endpoint configuration
- ❌ No authentication

Just install the package and it works!

## What's Different?

### Before (Vertex AI)
```python
# Required environment variables
GCP_PROJECT_ID=your-project
GCP_LOCATION=asia-southeast1
MEDGEMMA_ENDPOINT_ID=your-endpoint-id
GCP_CREDENTIALS_JSON={"type":"service_account",...}
```

### After (Gradio)
```python
# No environment variables needed!
# Just import and use
from services.medgemma_gradio import get_medgemma_gradio

client = get_medgemma_gradio()
result = await client.analyze_report(text)
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'gradio_client'`

**Solution:**
```bash
pip install gradio_client
```

### Issue: Client not available

**Check:**
1. Internet connection
2. Gradio API status: https://status.huggingface.co/

**Fallback:**
The system automatically falls back to BioGPT or NVIDIA if MedGemma is unavailable.

### Issue: Slow response times

**Explanation:**
Gradio API may have variable latency depending on server load. The system has a 60-second timeout and will fall back to faster alternatives if needed.

## Testing with Sample Data

Create a test file `test_report.txt`:

```
LABORATORY REPORT

GLUCOSE, FASTING: 196 mg/dL (Normal: 70-100 mg/dL) HIGH
HbA1c: 7.8% (Normal: <5.7%) HIGH
CHOLESTEROL, TOTAL: 245 mg/dL (Normal: <200 mg/dL) HIGH
```

Then test:

```python
import asyncio
from services.medgemma_gradio import get_medgemma_gradio

async def test():
    with open("test_report.txt", "r") as f:
        text = f.read()
    
    client = get_medgemma_gradio()
    result = await client.analyze_report(text)
    print(result)

asyncio.run(test())
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Run test script
3. ✅ Start backend server
4. ✅ Test with sample data
5. 🚀 Deploy to production

## Support

- Documentation: See `MEDGEMMA_GRADIO_INTEGRATION.md`
- Test Script: `backend/test_medgemma_gradio.py`
- Source Code: `backend/services/medgemma_gradio.py`

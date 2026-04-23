# MedGemma Gradio - Quick Reference

## Environment Setup

```bash
# backend/.env

# Single account (basic)
HUGGINGFACE_TOKENS=hf_YourTokenHere

# Multiple accounts (recommended for production)
HUGGINGFACE_TOKENS=hf_token1,hf_token2,hf_token3

# No authentication (public, rate limited)
HUGGINGFACE_TOKENS=
```

## Installation

```bash
cd backend
pip install gradio_client
python test_medgemma_gradio.py  # Test
uvicorn main:app --reload        # Start server
```

## Account Switching

### Automatic
System automatically switches when detecting:
- Rate limit errors (429)
- Quota exceeded
- Credit exhausted

### Logs
```
✓ MedGemma 27B Gradio client initialized with account #1
⚠️ Rate limit/quota error detected
→ Switching to Hugging Face account #2
✓ Retry successful with account #2
```

## API Usage

### Text Analysis
```python
from services.medgemma_gradio import get_medgemma_gradio

client = get_medgemma_gradio()
result = await client.analyze_report(text)
```

### Image Analysis
```python
with open("xray.jpg", "rb") as f:
    image_bytes = f.read()

result = await client.analyze_xray_image(image_bytes)
```

## Rate Limits

| Account Type | Requests/Hour | Requests/Day |
|--------------|---------------|--------------|
| Free (no auth) | ~60 | ~1,000 |
| Authenticated | ~300 | ~5,000 |
| Pro | ~1,000 | ~20,000 |

## Fallback Chain

1. **MedGemma Gradio** (primary, medical-specific)
2. **BioGPT** (local, privacy-focused)
3. **NVIDIA Llama 3.1 8B** (cloud, fast)

## Common Issues

### "No module named 'gradio_client'"
```bash
pip install gradio_client
```

### "All accounts exhausted"
- Wait 1 hour for rate limits to reset
- Add more accounts to `.env`
- System falls back to BioGPT/NVIDIA

### Account not switching
Check error message matches keywords:
- "rate limit"
- "quota"
- "credits"
- "429"
- "too many requests"

## Monitoring

```bash
# Check current account
grep "initialized with account" logs/*.log

# Track switching
grep "Switching to" logs/*.log

# View errors
grep "Rate limit" logs/*.log
```

## Security

```bash
# ✅ Good
export HUGGINGFACE_TOKENS="hf_token1,hf_token2"

# ❌ Bad - never commit
git add .env  # Should fail
```

## Documentation

- **Setup**: `SETUP_MEDGEMMA.md`
- **Multi-Account**: `MULTI_ACCOUNT_SETUP.md`
- **Integration**: `MEDGEMMA_GRADIO_INTEGRATION.md`
- **Migration**: `MIGRATION_SUMMARY.md`

## Support

```python
# Check availability
client = get_medgemma_gradio()
print(f"Available: {client.is_available()}")
print(f"Accounts: {len(client.hf_tokens)}")
print(f"Current: #{client.current_account_index + 1}")
```

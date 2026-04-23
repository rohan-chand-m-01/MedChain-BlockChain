# Multi-Account Setup for MedGemma Gradio

## Overview

The MedGemma Gradio integration supports **automatic account switching** when one account runs out of credits or hits rate limits. This ensures uninterrupted service.

## How It Works

1. **Multiple Tokens**: Configure multiple Hugging Face tokens in `.env`
2. **Automatic Detection**: System detects rate limit/quota errors
3. **Seamless Switching**: Automatically switches to next available account
4. **Retry Logic**: Retries the failed request with new account
5. **Logging**: Tracks which account is currently active

## Setup Instructions

### Step 1: Get Hugging Face Tokens

You need to create multiple Hugging Face accounts and get their tokens:

1. **Create Hugging Face Accounts**
   - Go to https://huggingface.co/join
   - Create 2-3 accounts (use different emails)
   - Verify each account

2. **Generate Access Tokens**
   - Log into each account
   - Go to Settings → Access Tokens
   - Click "New token"
   - Name it (e.g., "MediChain API")
   - Select "Read" permission
   - Copy the token (starts with `hf_...`)

### Step 2: Configure Environment Variables

Edit `backend/.env`:

```bash
# Single account (basic)
HUGGINGFACE_TOKENS=hf_YourFirstTokenHere

# Multiple accounts (recommended)
HUGGINGFACE_TOKENS=hf_FirstToken,hf_SecondToken,hf_ThirdToken

# No authentication (public access, rate limited)
HUGGINGFACE_TOKENS=
```

**Example with 3 accounts:**
```bash
HUGGINGFACE_TOKENS=hf_abc123def456,hf_xyz789ghi012,hf_mno345pqr678
```

### Step 3: Test the Setup

Run the test script:

```bash
cd backend
python test_medgemma_gradio.py
```

Expected output:
```
Loaded 3 Hugging Face account(s)
✓ MedGemma 27B Gradio client initialized with account #1
...
✅ Text analysis test completed successfully!
```

## Account Switching Behavior

### Automatic Switching

The system automatically switches accounts when it detects:

- **Rate limit errors**: "429 Too Many Requests"
- **Quota exceeded**: "quota", "credits"
- **API limits**: "rate limit", "too many requests"

### Manual Testing

You can test account switching by simulating a rate limit:

```python
from services.medgemma_gradio import get_medgemma_gradio

client = get_medgemma_gradio()
print(f"Current account: #{client.current_account_index + 1}")

# Simulate rate limit error
client._handle_api_error("Rate limit exceeded")
print(f"Switched to account: #{client.current_account_index + 1}")
```

## Monitoring

### Check Current Account

The logs show which account is active:

```
[INFO] ✓ MedGemma 27B Gradio client initialized with account #1
[INFO] Analyzing report...
[WARNING] Rate limit/quota error detected: 429 Too Many Requests
[INFO] Switching to Hugging Face account #2
[INFO] ✓ Retry successful with account #2
```

### Account Rotation

Accounts rotate in order:
1. Account #1 (primary)
2. Account #2 (backup)
3. Account #3 (backup)
4. Back to Account #1 (if all exhausted)

## Best Practices

### 1. Use 2-3 Accounts

```bash
# Recommended: 3 accounts for redundancy
HUGGINGFACE_TOKENS=hf_primary,hf_backup1,hf_backup2
```

**Why?**
- Primary account handles most traffic
- Backup accounts kick in during high usage
- 3 accounts provide good balance between redundancy and management

### 2. Monitor Usage

Track which accounts are being used:

```bash
# Check logs for account switching
grep "Switching to Hugging Face account" backend/logs/*.log
```

### 3. Rotate Tokens Regularly

- Generate new tokens every 3-6 months
- Update `.env` with new tokens
- Restart backend server

### 4. Keep Tokens Secure

```bash
# ❌ NEVER commit tokens to git
git add .env  # This should fail if .gitignore is correct

# ✅ Use environment variables in production
export HUGGINGFACE_TOKENS="hf_token1,hf_token2"
```

## Troubleshooting

### Issue: "No additional accounts available to switch to"

**Cause**: Only one token configured or all accounts exhausted

**Solution:**
```bash
# Add more tokens
HUGGINGFACE_TOKENS=hf_token1,hf_token2,hf_token3
```

### Issue: "All accounts exhausted or unavailable"

**Cause**: All configured accounts hit rate limits

**Solution:**
1. Wait for rate limits to reset (usually 1 hour)
2. Add more accounts
3. System will automatically fall back to BioGPT or NVIDIA

### Issue: Tokens not being recognized

**Cause**: Incorrect format or invalid tokens

**Solution:**
```bash
# Check token format (should start with hf_)
echo $HUGGINGFACE_TOKENS

# Verify tokens are valid
curl -H "Authorization: Bearer hf_YourToken" \
  https://huggingface.co/api/whoami
```

### Issue: Account switching not working

**Cause**: Error message doesn't match rate limit keywords

**Solution:**
Check logs for actual error message and update keywords in `_handle_api_error()`:

```python
rate_limit_keywords = ["rate limit", "quota", "credits", "429", "too many requests"]
```

## Rate Limits

### Hugging Face Gradio API Limits

| Account Type | Requests/Hour | Requests/Day |
|--------------|---------------|--------------|
| Free (no auth) | ~60 | ~1,000 |
| Authenticated | ~300 | ~5,000 |
| Pro | ~1,000 | ~20,000 |

**Note**: These are estimates. Actual limits may vary.

### Calculating Your Needs

```
Daily requests = Users × Reports per user × Days
Example: 100 users × 5 reports × 1 day = 500 requests/day

Accounts needed = Daily requests / Requests per account
Example: 500 / 300 = 2 accounts (round up to 3 for safety)
```

## Advanced Configuration

### Custom Retry Logic

Edit `backend/services/medgemma_gradio.py`:

```python
def _handle_api_error(self, error_msg: str):
    # Add custom error detection
    custom_keywords = ["your_custom_error", "another_error"]
    
    if any(keyword in error_msg.lower() for keyword in custom_keywords):
        return self._switch_account()
    
    return False
```

### Account Priority

Accounts are used in order. To prioritize certain accounts:

```bash
# Put high-quota accounts first
HUGGINGFACE_TOKENS=hf_pro_account,hf_free_account1,hf_free_account2
```

### Disable Account Switching

To use only one account without fallback:

```bash
# Single token, no fallback
HUGGINGFACE_TOKENS=hf_single_token
```

## Production Deployment

### Environment Variables

```bash
# Docker
docker run -e HUGGINGFACE_TOKENS="hf_token1,hf_token2" ...

# Kubernetes
kubectl create secret generic hf-tokens \
  --from-literal=HUGGINGFACE_TOKENS="hf_token1,hf_token2"

# Heroku
heroku config:set HUGGINGFACE_TOKENS="hf_token1,hf_token2"
```

### Health Checks

Monitor account health:

```python
# Add to your monitoring
from services.medgemma_gradio import get_medgemma_gradio

client = get_medgemma_gradio()
health = {
    "total_accounts": len(client.hf_tokens),
    "current_account": client.current_account_index + 1,
    "is_available": client.is_available()
}
```

## Cost Optimization

### Free Tier Strategy

1. **Use 3 free accounts**: 900 requests/hour combined
2. **Implement caching**: Reduce duplicate requests
3. **Rate limiting**: Prevent abuse

### Paid Tier Strategy

1. **1 Pro account**: 1,000 requests/hour
2. **2 free backups**: Emergency fallback
3. **Cost**: ~$9/month for Pro

## Security

### Token Management

```bash
# ✅ Good: Environment variables
export HUGGINGFACE_TOKENS="hf_token1,hf_token2"

# ✅ Good: Secret management
aws secretsmanager get-secret-value --secret-id hf-tokens

# ❌ Bad: Hardcoded in code
HUGGINGFACE_TOKENS = "hf_abc123..."  # NEVER DO THIS
```

### Token Rotation

```bash
# 1. Generate new tokens
# 2. Add to .env (keep old ones)
HUGGINGFACE_TOKENS=hf_new1,hf_new2,hf_old1,hf_old2

# 3. Deploy and verify
# 4. Remove old tokens
HUGGINGFACE_TOKENS=hf_new1,hf_new2
```

## FAQ

**Q: How many accounts do I need?**
A: Start with 2-3. Add more if you hit rate limits frequently.

**Q: Can I mix free and paid accounts?**
A: Yes! Put paid accounts first for better performance.

**Q: What happens if all accounts fail?**
A: System falls back to BioGPT (local) or NVIDIA (cloud).

**Q: Do I need to restart after adding tokens?**
A: Yes, restart the backend server to load new tokens.

**Q: Can I use the same token multiple times?**
A: No, each token should be unique from different accounts.

## Support

- Documentation: `MEDGEMMA_GRADIO_INTEGRATION.md`
- Setup Guide: `SETUP_MEDGEMMA.md`
- Source Code: `backend/services/medgemma_gradio.py`

# MedGemma Multi-Account Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                    (Next.js + React)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ POST /analyze-report
                         │ {file_base64, file_type, ...}
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API Server                            │
│                   (FastAPI + Python)                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           routes/analyze.py                              │   │
│  │  • Detect file type (image/PDF)                          │   │
│  │  • Extract text via OCR (if needed)                      │   │
│  │  • Call AI analysis service                              │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                           │
│                       │ get_medgemma_gradio()                    │
│                       ▼                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │      services/medgemma_gradio.py                         │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  MedGemmaGradio Class                            │   │   │
│  │  │                                                   │   │   │
│  │  │  • hf_tokens = [token1, token2, token3]         │   │   │
│  │  │  • current_account_index = 0                     │   │   │
│  │  │  • client = Gradio Client                        │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                           │   │
│  │  Methods:                                                │   │
│  │  • analyze_report(text) → dict                          │   │
│  │  • analyze_xray_image(bytes) → dict                     │   │
│  │  • _switch_account() → bool                             │   │
│  │  • _handle_api_error(error) → bool                      │   │
│  └────────────────────┬────────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         │ Gradio API Call
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Hugging Face Gradio API                         │
│              (warshanks/medgemma-27b-it)                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Account #1  │  │  Account #2  │  │  Account #3  │          │
│  │  (Primary)   │  │  (Backup)    │  │  (Backup)    │          │
│  │              │  │              │  │              │          │
│  │ hf_token1    │  │ hf_token2    │  │ hf_token3    │          │
│  │ 300 req/hr   │  │ 300 req/hr   │  │ 300 req/hr   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  Total Capacity: 900 requests/hour                               │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow - Normal Operation

```
1. Request arrives
   ↓
2. Initialize with Account #1
   ↓
3. Call Gradio API
   ↓
4. Success! ✓
   ↓
5. Return analysis result
```

## Request Flow - Rate Limit Detected

```
1. Request arrives
   ↓
2. Call Gradio API with Account #1
   ↓
3. Error: "429 Rate Limit Exceeded"
   ↓
4. _handle_api_error() detects rate limit
   ↓
5. _switch_account() → Account #2
   ↓
6. Retry with Account #2
   ↓
7. Success! ✓
   ↓
8. Return analysis result
```

## Request Flow - All Accounts Exhausted

```
1. Request arrives
   ↓
2. Try Account #1 → Rate Limit
   ↓
3. Try Account #2 → Rate Limit
   ↓
4. Try Account #3 → Rate Limit
   ↓
5. All accounts exhausted
   ↓
6. Fallback to BioGPT (local)
   ↓
7. If BioGPT fails → NVIDIA Llama
   ↓
8. Return analysis result
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                     Analysis Pipeline                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Layer 1: OCR Extraction                                   │  │
│  │ • PDF → Text (PyPDF2 + Tesseract)                        │  │
│  │ • Image → Text (Tesseract)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Layer 2: Medical Entity Extraction                        │  │
│  │ • ClinicalBERT (diseases, tests, medications)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Layer 3: AI Analysis (with Multi-Account)                │  │
│  │                                                            │  │
│  │  Priority 1: MedGemma Gradio (medical-specific)          │  │
│  │  ├─ Account #1 (primary)                                 │  │
│  │  ├─ Account #2 (backup)                                  │  │
│  │  └─ Account #3 (backup)                                  │  │
│  │                                                            │  │
│  │  Priority 2: BioGPT (local, privacy-focused)             │  │
│  │                                                            │  │
│  │  Priority 3: NVIDIA Llama 3.1 8B (cloud, fast)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Layer 4: Risk Prediction                                  │  │
│  │ • Random Forest (disease-specific models)                │  │
│  │ • 73-92% accuracy                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Output: Comprehensive Analysis                            │  │
│  │ • Risk score, conditions, biomarkers                      │  │
│  │ • Specialist recommendation                               │  │
│  │ • Improvement plan                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Account Switching Logic

```python
def _handle_api_error(error_msg):
    """
    Detect rate limit errors and switch accounts
    """
    
    # Check for rate limit keywords
    rate_limit_keywords = [
        "rate limit",
        "quota",
        "credits",
        "429",
        "too many requests"
    ]
    
    if any(keyword in error_msg.lower() for keyword in rate_limit_keywords):
        # Switch to next account
        current_account_index = (current_account_index + 1) % len(hf_tokens)
        
        # Reinitialize client with new token
        client = Client("warshanks/medgemma-27b-it", 
                       hf_token=hf_tokens[current_account_index])
        
        return True  # Retry with new account
    
    return False  # Don't retry
```

## State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                  MedGemmaGradio Instance                         │
│                                                                   │
│  State Variables:                                                │
│  • hf_tokens: ["hf_token1", "hf_token2", "hf_token3"]          │
│  • current_account_index: 0 → 1 → 2 → 0 (circular)             │
│  • client: Gradio Client instance                               │
│  • system_prompt: "You are a helpful medical expert."          │
│  • max_tokens: 2048                                             │
│                                                                   │
│  Account Rotation:                                               │
│  Account #1 (index 0) ──rate limit──> Account #2 (index 1)     │
│                                              │                    │
│                                              │ rate limit         │
│                                              ▼                    │
│  Account #3 (index 2) <──────────────────────                   │
│         │                                                         │
│         │ rate limit                                             │
│         ▼                                                         │
│  Back to Account #1 (index 0)                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Error Handling                              │
│                                                                   │
│  API Call                                                        │
│     ↓                                                             │
│  Try with current account                                        │
│     ↓                                                             │
│  ┌─────────────────────────────────────────┐                    │
│  │ Success?                                 │                    │
│  └─────────────────────────────────────────┘                    │
│     │                    │                                        │
│     │ Yes                │ No                                     │
│     ▼                    ▼                                        │
│  Return result    Check error type                               │
│                         ↓                                         │
│                   ┌─────────────────────────────────────┐       │
│                   │ Rate limit error?                    │       │
│                   └─────────────────────────────────────┘       │
│                         │                    │                    │
│                         │ Yes                │ No                 │
│                         ▼                    ▼                    │
│                   Switch account      Raise exception            │
│                         ↓                                         │
│                   Retry once                                      │
│                         ↓                                         │
│                   ┌─────────────────────────────────────┐       │
│                   │ Success?                             │       │
│                   └─────────────────────────────────────┘       │
│                         │                    │                    │
│                         │ Yes                │ No                 │
│                         ▼                    ▼                    │
│                   Return result      Raise exception             │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Loading                         │
│                                                                   │
│  1. Read .env file                                               │
│     ↓                                                             │
│  2. Load HUGGINGFACE_TOKENS                                      │
│     ↓                                                             │
│  3. Split by comma                                               │
│     ↓                                                             │
│  4. Validate tokens (start with "hf_")                          │
│     ↓                                                             │
│  5. Store in hf_tokens array                                     │
│     ↓                                                             │
│  6. Initialize with first token                                  │
│     ↓                                                             │
│  7. Ready to handle requests                                     │
│                                                                   │
│  Example:                                                        │
│  HUGGINGFACE_TOKENS="hf_abc,hf_def,hf_ghi"                      │
│         ↓                                                         │
│  hf_tokens = ["hf_abc", "hf_def", "hf_ghi"]                     │
│         ↓                                                         │
│  current_account_index = 0                                       │
│         ↓                                                         │
│  client = Client(..., hf_token="hf_abc")                        │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Production Setup                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Environment Variables (Kubernetes/Docker)                 │  │
│  │                                                            │  │
│  │ HUGGINGFACE_TOKENS=hf_prod1,hf_prod2,hf_prod3            │  │
│  │ NVIDIA_API_KEY=nvapi_...                                  │  │
│  │ INSFORGE_BASE_URL=https://...                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Backend Container                                         │  │
│  │                                                            │  │
│  │ • Load environment variables                              │  │
│  │ • Initialize MedGemmaGradio with 3 accounts              │  │
│  │ • Start FastAPI server                                    │  │
│  │ • Handle requests with auto-failover                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Monitoring & Logging                                      │  │
│  │                                                            │  │
│  │ • Track account usage                                     │  │
│  │ • Alert on rate limits                                    │  │
│  │ • Monitor switching frequency                             │  │
│  │ • Log all API calls                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Scalability

```
┌─────────────────────────────────────────────────────────────────┐
│                    Horizontal Scaling                            │
│                                                                   │
│  Load Balancer                                                   │
│       ↓                                                           │
│  ┌─────────────┬─────────────┬─────────────┐                   │
│  │ Backend #1  │ Backend #2  │ Backend #3  │                   │
│  │             │             │             │                   │
│  │ 3 accounts  │ 3 accounts  │ 3 accounts  │                   │
│  │ 900 req/hr  │ 900 req/hr  │ 900 req/hr  │                   │
│  └─────────────┴─────────────┴─────────────┘                   │
│                                                                   │
│  Total: 2,700 requests/hour                                      │
│                                                                   │
│  Note: Each backend instance has its own set of 3 accounts      │
│        for independent failover                                  │
└─────────────────────────────────────────────────────────────────┘
```

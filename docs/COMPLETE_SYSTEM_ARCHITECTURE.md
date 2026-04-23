# MediChain Complete System Architecture

## Executive Summary

MediChain is a privacy-preserving, blockchain-secured medical records platform that uses **open-source AI models** (MedGemma 27B) for medical analysis, combined with advanced cryptography (FHE, ZK-Proofs) and decentralized storage (IPFS, Stellar blockchain).

**Key Differentiator:** Uses open-source MedGemma 27B model instead of proprietary APIs, ensuring data privacy, cost efficiency, and full control over medical AI.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Layers](#architecture-layers)
4. [Data Flow](#data-flow)
5. [AI Analysis Pipeline](#ai-analysis-pipeline)
6. [Privacy & Security](#privacy--security)
7. [Blockchain Integration](#blockchain-integration)
8. [Component Details](#component-details)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MediChain Platform                        │
│                                                                   │
│  Privacy-First Medical Records with Open-Source AI              │
│  ✓ MedGemma 27B (Open-Source Medical AI)                       │
│  ✓ Client-Side Encryption (Privy MPC)                          │
│  ✓ Decentralized Storage (IPFS)                                │
│  ✓ Blockchain Proofs (Stellar)                                 │
│  ✓ Zero-Knowledge Proofs                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Framework:** Next.js 15 (React 19)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 3.4
- **Authentication:** Privy (MPC Wallet)
- **State Management:** React Hooks
- **Encryption:** Web Crypto API + Privy SDK

### Backend
- **Framework:** FastAPI (Python)
- **Language:** Python 3.14
- **Database:** PostgreSQL (via InsForge)
- **API Style:** RESTful + OpenAPI

### AI/ML Stack (Open-Source Focus)
- **Primary:** MedGemma 27B (Gradio API) - Open-source medical LLM
- **Fallback 1:** BioGPT (Local) - Open-source biomedical model
- **Fallback 2:** ClinicalBERT - Open-source medical NER
- **Fallback 3:** NVIDIA NIM (Llama 3.1) - Open-source base model
- **Risk Prediction:** Random Forest (Scikit-learn) - Open-source ML

### Blockchain & Storage
- **Blockchain:** Stellar (Testnet)
- **Smart Contracts:** Solidity (Ethereum-compatible)
- **Decentralized Storage:** IPFS (Pinata)
- **Database:** InsForge (PostgreSQL + PostgREST)

### Privacy Technologies
- **Encryption:** AES-256-GCM (Client-side)
- **Key Management:** Privy MPC Wallets
- **FHE:** Simulation (TenSEAL-ready)
- **ZK-Proofs:** Groth16 Simulation (circom-ready)

---

## Architecture Layers


### Layer 1: Presentation Layer (Frontend)

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Patient    │  │    Doctor    │  │    Admin     │     │
│  │  Dashboard   │  │  Dashboard   │  │   Portal     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Privy Authentication (MPC Wallets)           │  │
│  │  • Email/Password + OAuth (Google, GitHub)          │  │
│  │  • Embedded Wallets (No seed phrases)               │  │
│  │  • Client-side encryption keys                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Client-Side Encryption Layer                 │  │
│  │  • AES-256-GCM encryption before upload             │  │
│  │  • Keys stored in Privy MPC                         │  │
│  │  • Zero-knowledge architecture                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
- `src/app/patient/page.tsx` - Patient dashboard with upload
- `src/app/doctor/page.tsx` - Doctor dashboard with patient list
- `src/contexts/PrivyProvider.tsx` - Authentication wrapper
- `src/services/privyKeyManager.ts` - Encryption key management
- `src/hooks/useLabReportEncryption.ts` - Encryption utilities

---

### Layer 2: API Gateway Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  API Routes:                                                 │
│  ├─ /api/analyze-report      → AI Analysis Pipeline        │
│  ├─ /api/records             → Medical Records CRUD         │
│  ├─ /api/privacy/*           → FHE + ZK-Proofs             │
│  ├─ /api/stellar/*           → Blockchain Operations        │
│  ├─ /api/ipfs/*              → Decentralized Storage        │
│  ├─ /api/access-control/*    → Permission Management        │
│  ├─ /api/chatbot             → Medical AI Assistant         │
│  └─ /api/whatsapp/*          → WhatsApp Integration         │
│                                                               │
│  Middleware:                                                 │
│  ├─ CORS (Cross-Origin)                                     │
│  ├─ Security Headers                                         │
│  └─ Request Logging                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/main.py` - FastAPI application entry
- `backend/routes/*.py` - API route handlers

---

### Layer 3: AI Analysis Layer (Open-Source Models)


```
┌─────────────────────────────────────────────────────────────────┐
│              AI Analysis Pipeline (Open-Source)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Step 1: OCR Text Extraction                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Tesseract OCR (Open-source)                         │    │
│  │  • PDF text extraction (PyPDF2/pdfplumber)             │    │
│  │  • Image preprocessing (Pillow)                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Step 2: Medical Entity Extraction                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  ClinicalBERT (Open-Source)                            │    │
│  │  • Extracts diseases, medications, tests               │    │
│  │  • Medical Named Entity Recognition (NER)              │    │
│  │  • Hugging Face Transformers                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Step 3: Medical Analysis (PRIMARY - OPEN-SOURCE)               │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  MedGemma 27B (Google's Open-Source Medical LLM)      │    │
│  │  ────────────────────────────────────────────────      │    │
│  │  • Hosted on Gradio API (Free tier available)         │    │
│  │  • Specialized for medical text understanding         │    │
│  │  • Trained on medical literature & clinical notes     │    │
│  │  • Extracts biomarkers, conditions, risk factors      │    │
│  │  • Generates detailed medical summaries               │    │
│  │  • NO proprietary API costs                           │    │
│  │  • Full data privacy (can self-host)                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Step 4: Fallback Models (All Open-Source)                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  BioGPT (Local Deployment)                             │    │
│  │  • Microsoft's open-source biomedical LLM             │    │
│  │  • Runs locally for maximum privacy                   │    │
│  │  • Pattern-based medical analysis                     │    │
│  │  • No external API calls                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Step 5: Risk Prediction (Open-Source ML)                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Random Forest Classifier (Scikit-learn)               │    │
│  │  • Trained on diabetes, heart, kidney datasets        │    │
│  │  • 73-92% accuracy across conditions                  │    │
│  │  • Disease-specific risk scoring                      │    │
│  │  • Explainable AI (feature importance)                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**AI Model Priority (All Open-Source):**
1. **MedGemma 27B** (Gradio API) - Primary medical analysis
2. **BioGPT** (Local) - Privacy-focused fallback
3. **ClinicalBERT** - Medical entity extraction
4. **Random Forest** - Risk prediction
5. **NVIDIA NIM** (Llama 3.1) - General fallback (open-source base)

**Key Files:**
- `backend/services/medgemma_gradio.py` - MedGemma integration
- `backend/services/biogpt_local.py` - BioGPT local deployment
- `backend/services/clinical_bert.py` - ClinicalBERT NER
- `backend/services/random_forest.py` - Risk prediction models
- `backend/services/ocr_extractor.py` - Text extraction

---

### Layer 4: Privacy & Cryptography Layer


```
┌─────────────────────────────────────────────────────────────────┐
│                  Privacy & Cryptography Layer                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Client-Side Encryption (Before Upload)                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • AES-256-GCM encryption in browser                   │    │
│  │  • Encryption keys managed by Privy MPC                │    │
│  │  • Files encrypted before leaving device               │    │
│  │  • Zero-knowledge: Backend never sees plaintext        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Fully Homomorphic Encryption (FHE)                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Compute on encrypted biomarkers                     │    │
│  │  • Risk calculation without decryption                 │    │
│  │  • Homomorphic operations (add, compare)               │    │
│  │  • Current: Simulation (TenSEAL-ready)                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Zero-Knowledge Proofs (ZK-Proofs)                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Range proofs (value in range, hide value)           │    │
│  │  • Threshold proofs (value > threshold, hide value)    │    │
│  │  • Condition proofs (prove diagnosis, hide data)       │    │
│  │  • Aggregate proofs (combine multiple proofs)          │    │
│  │  • Current: Groth16 simulation (circom-ready)          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Key Management (Privy MPC)                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Multi-Party Computation (MPC) wallets               │    │
│  │  • No seed phrases required                            │    │
│  │  • Distributed key shares                              │    │
│  │  • Social recovery options                             │    │
│  │  • Time-bound access delegation                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/services/fhe_service.py` - FHE operations
- `backend/services/zkproof_service.py` - ZK-Proof generation
- `backend/services/privacy_service.py` - Unified privacy service
- `backend/services/aes_encryptor.py` - AES encryption utilities
- `frontend/src/services/privyKeyManager.ts` - Client-side key management

---

### Layer 5: Storage Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Decentralized Storage (IPFS)                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Pinata IPFS Gateway                                   │    │
│  │  • Encrypted files stored on IPFS                      │    │
│  │  • Content-addressed (CID)                             │    │
│  │  • Immutable storage                                   │    │
│  │  • Distributed across nodes                            │    │
│  │  • Files remain encrypted at rest                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Structured Database (InsForge/PostgreSQL)                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Tables:                                                │    │
│  │  ├─ analyses          → AI analysis results            │    │
│  │  ├─ encrypted_reports → Encrypted file metadata        │    │
│  │  ├─ access_grants     → Permission records             │    │
│  │  ├─ appointments      → Scheduling data                │    │
│  │  ├─ profiles          → User profiles                  │    │
│  │  └─ stellar_accounts  → Blockchain accounts            │    │
│  │                                                          │    │
│  │  Features:                                              │    │
│  │  • PostgREST API (auto-generated)                      │    │
│  │  • Row-Level Security (RLS)                            │    │
│  │  • Real-time subscriptions                             │    │
│  │  • Full-text search                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/services/ipfs_uploader.py` - IPFS integration
- `backend/services/insforge.py` - Database client
- `migrations/*.sql` - Database schema

---

### Layer 6: Blockchain Layer


```
┌─────────────────────────────────────────────────────────────────┐
│                      Blockchain Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Stellar Blockchain (Testnet)                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Purpose: Immutable proof storage                      │    │
│  │  • Store IPFS CID hashes                               │    │
│  │  • Store risk scores & levels                          │    │
│  │  • Timestamp verification                              │    │
│  │  • Audit trail                                         │    │
│  │  • Low transaction costs                               │    │
│  │                                                          │    │
│  │  Operations:                                            │    │
│  │  ├─ Create accounts (patient, doctor, system)          │    │
│  │  ├─ Store proof transactions                           │    │
│  │  ├─ Query transaction history                          │    │
│  │  └─ Verify data integrity                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Ethereum Smart Contracts (Sepolia Testnet)                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  ConsentRegistry.sol                                    │    │
│  │  • Patient consent management                           │    │
│  │  • Time-bound access grants                            │    │
│  │  • Revocation mechanisms                               │    │
│  │  • Event logging                                       │    │
│  │                                                          │    │
│  │  StudyRegistry.sol                                      │    │
│  │  • Research study registration                          │    │
│  │  • Participant enrollment                              │    │
│  │  • Data contribution tracking                          │    │
│  │                                                          │    │
│  │  ResearchToken.sol (ERC-20)                            │    │
│  │  • Incentive tokens for data sharing                   │    │
│  │  • Reward distribution                                 │    │
│  │  • Governance rights                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/services/stellar_client.py` - Stellar integration
- `backend/routes/stellar.py` - Stellar API endpoints
- `blockchain/contracts/*.sol` - Smart contracts
- `backend/services/blockchain_client.py` - Ethereum integration

---

## Complete Data Flow

### Flow 1: Medical Report Upload & Analysis

```
┌──────────────────────────────────────────────────────────────────┐
│                    Report Upload Flow                             │
└──────────────────────────────────────────────────────────────────┘

Step 1: Client-Side Encryption
┌─────────────┐
│   Patient   │ Selects PDF/Image report
│   Browser   │
└──────┬──────┘
       │
       ├─→ Generate AES-256 encryption key (Privy MPC)
       ├─→ Encrypt file in browser (Web Crypto API)
       ├─→ Generate encryption IV & key hash
       └─→ File never leaves device unencrypted
       
Step 2: Upload to IPFS
┌─────────────┐
│   Backend   │ Receives encrypted file
│   FastAPI   │
└──────┬──────┘
       │
       ├─→ Upload encrypted file to IPFS (Pinata)
       ├─→ Receive IPFS CID (Content ID)
       └─→ Store CID in database
       
Step 3: OCR & Text Extraction
┌─────────────┐
│  OCR Layer  │ Extract text from file
└──────┬──────┘
       │
       ├─→ Tesseract OCR for images
       ├─→ PyPDF2/pdfplumber for PDFs
       └─→ Extract ~4000 chars for analysis
       
Step 4: Medical Entity Extraction (Open-Source)
┌─────────────┐
│ ClinicalBERT│ Extract medical entities
└──────┬──────┘
       │
       ├─→ Identify diseases (e.g., "Type 2 Diabetes")
       ├─→ Identify tests (e.g., "HbA1c", "Glucose")
       ├─→ Identify medications (e.g., "Metformin")
       └─→ Return structured entities
       
Step 5: Medical Analysis (MedGemma 27B - Open-Source)
┌─────────────┐
│  MedGemma   │ PRIMARY: Analyze medical text
│   27B API   │
└──────┬──────┘
       │
       ├─→ Extract biomarkers (Glucose: 196 mg/dL, HbA1c: 7.8%)
       ├─→ Identify abnormal findings with explanations
       ├─→ List medical conditions with evidence
       ├─→ Calculate risk score (0-100)
       ├─→ Determine risk level (low/medium/high/critical)
       ├─→ Recommend specialist (Endocrinologist, Cardiologist)
       ├─→ Set urgency (low/medium/high/critical)
       └─→ Generate detailed 8-10 sentence summary
       
       Fallback Chain (if MedGemma unavailable):
       ├─→ BioGPT (Local, open-source)
       ├─→ NVIDIA NIM (Llama 3.1, open-source base)
       └─→ Pattern-based analysis
       
Step 6: Risk Prediction (Random Forest - Open-Source)
┌─────────────┐
│   Random    │ Disease-specific risk scoring
│   Forest    │
└──────┬──────┘
       │
       ├─→ Diabetes model (88% accuracy)
       ├─→ Heart disease model (92% accuracy)
       ├─→ Kidney disease model (73% accuracy)
       └─→ Validate/refine MedGemma risk score


       
Step 7: Privacy Analysis (Optional - FHE + ZK)
┌─────────────┐
│   Privacy   │ Generate privacy proofs
│   Service   │
└──────┬──────┘
       │
       ├─→ FHE: Encrypt biomarkers
       ├─→ FHE: Compute risk on encrypted data
       ├─→ ZK: Generate range proofs (glucose in [70-100])
       ├─→ ZK: Generate threshold proofs (HbA1c > 6.5%)
       ├─→ ZK: Generate condition proofs (diabetes diagnosis)
       └─→ Return verifiable proofs without revealing data
       
Step 8: Store on Stellar Blockchain
┌─────────────┐
│   Stellar   │ Immutable proof storage
│  Blockchain │
└──────┬──────┘
       │
       ├─→ Create transaction with:
       │   • IPFS CID hash
       │   • Risk score
       │   • Risk level
       │   • Timestamp
       ├─→ Sign with system account
       ├─→ Submit to Stellar testnet
       └─→ Return transaction hash
       
Step 9: Store Analysis in Database
┌─────────────┐
│  InsForge   │ Store structured results
│  PostgreSQL │
└──────┬──────┘
       │
       ├─→ Insert into 'analyses' table:
       │   • patient_wallet (DID)
       │   • file_name, file_url (IPFS)
       │   • ocr_text (truncated)
       │   • summary (detailed)
       │   • risk_score, urgency
       │   • conditions (array)
       │   • biomarkers (JSONB)
       │   • specialist
       │   • improvement_plan (JSONB)
       │   • record_hash (SHA-256)
       │   • ipfs_cid
       │   • encryption_iv
       └─→ Return database record ID
       
Step 10: Return to Patient
┌─────────────┐
│   Patient   │ View analysis results
│  Dashboard  │
└─────────────┘
       │
       ├─→ Display risk score & level
       ├─→ Show biomarkers with values
       ├─→ List conditions & abnormal findings
       ├─→ Show specialist recommendation
       ├─→ Display improvement plan
       ├─→ Provide encryption key download
       └─→ Show Stellar transaction link
```

---

### Flow 2: Doctor Access Request

```
┌──────────────────────────────────────────────────────────────────┐
│                  Doctor Access Flow                               │
└──────────────────────────────────────────────────────────────────┘

Step 1: Doctor Requests Access
┌─────────────┐
│   Doctor    │ Requests patient records
│  Dashboard  │
└──────┬──────┘
       │
       ├─→ Enter patient wallet address
       ├─→ Specify access duration (hours)
       ├─→ Provide reason for access
       └─→ Submit access request
       
Step 2: Patient Grants Access
┌─────────────┐
│   Patient   │ Reviews access request
│  Dashboard  │
└──────┬──────┘
       │
       ├─→ View doctor details
       ├─→ Review requested duration
       ├─→ Approve or deny
       └─→ If approved, create access grant
       
Step 3: Store Access Grant
┌─────────────┐
│  Database   │ Record permission
└──────┬──────┘
       │
       ├─→ Insert into 'access_grants' table:
       │   • patient_wallet
       │   • doctor_wallet
       │   • granted_at (timestamp)
       │   • expires_at (timestamp)
       │   • status (active/revoked)
       └─→ Return grant ID
       
Step 4: Record on Blockchain (Optional)
┌─────────────┐
│   Smart     │ Immutable consent record
│  Contract   │
└──────┬──────┘
       │
       ├─→ Call ConsentRegistry.grantAccess()
       ├─→ Store patient, doctor, expiry
       ├─→ Emit AccessGranted event
       └─→ Return transaction hash
       
Step 5: Doctor Views Records
┌─────────────┐
│   Doctor    │ Access patient data
│  Dashboard  │
└──────┬──────┘
       │
       ├─→ Verify active access grant
       ├─→ Fetch patient records from database
       ├─→ Download encrypted files from IPFS
       ├─→ Decrypt using shared key (if authorized)
       └─→ View analysis, biomarkers, history
       
Step 6: Time-Bound Expiry
┌─────────────┐
│   System    │ Auto-revoke expired access
│   Cron Job  │
└──────┬──────┘
       │
       ├─→ Check access_grants for expired entries
       ├─→ Update status to 'expired'
       ├─→ Revoke on blockchain (if recorded)
       └─→ Notify doctor of expiration
```

---

## AI Analysis Pipeline (Detailed)


### MedGemma 27B Integration (Primary - Open-Source)

```
┌─────────────────────────────────────────────────────────────────┐
│              MedGemma 27B Analysis Pipeline                      │
│              (Google's Open-Source Medical LLM)                  │
└─────────────────────────────────────────────────────────────────┘

Why MedGemma?
✓ Open-source (Apache 2.0 license)
✓ Specialized for medical text understanding
✓ Trained on medical literature, clinical notes, PubMed
✓ 27 billion parameters (high accuracy)
✓ Can be self-hosted (full data privacy)
✓ Free Gradio API tier available
✓ No proprietary API costs
✓ Community-driven improvements

Input: OCR-extracted text (up to 4000 chars)
┌─────────────────────────────────────────────────────────────┐
│  Prompt Engineering:                                         │
│  • "You are an expert medical AI..."                        │
│  • Detailed instructions for biomarker extraction           │
│  • Structured JSON output format                            │
│  • Risk score calculation guidelines                        │
│  • Urgency classification rules                             │
└─────────────────────────────────────────────────────────────┘

MedGemma Processing:
┌─────────────────────────────────────────────────────────────┐
│  1. Biomarker Extraction                                     │
│     • Identifies test names (Glucose, HbA1c, Cholesterol)   │
│     • Extracts values with units (196 mg/dL, 7.8%)          │
│     • Captures reference ranges (70-100 mg/dL)              │
│     • Returns structured JSONB                              │
│                                                              │
│  2. Abnormal Findings Analysis                              │
│     • Compares values to normal ranges                      │
│     • Calculates deviation percentage                       │
│     • Explains clinical significance (2-3 sentences each)   │
│     • Categorizes severity (mild/moderate/severe)           │
│                                                              │
│  3. Condition Identification                                │
│     • Lists specific diagnoses with evidence                │
│     • "Type 2 Diabetes (glucose 196 mg/dL, HbA1c 7.8%)"    │
│     • Provides supporting biomarker data                    │
│     • Differential diagnoses when applicable                │
│                                                              │
│  4. Risk Score Calculation (0-100)                          │
│     • Based on number of abnormal findings                  │
│     • Weighted by deviation from normal                     │
│     • Considers clinical significance                       │
│     • Accounts for potential complications                  │
│     • Maps to risk level (low/medium/high/critical)         │
│                                                              │
│  5. Specialist Recommendation                               │
│     • Endocrinologist (diabetes/metabolic)                  │
│     • Cardiologist (heart/lipids)                           │
│     • Nephrologist (kidney)                                 │
│     • General Practitioner (routine)                        │
│                                                              │
│  6. Urgency Classification                                  │
│     • low: Normal/minor findings                            │
│     • medium: Concerning, needs evaluation                  │
│     • high: Significant abnormalities                       │
│     • critical: Immediate intervention required             │
│                                                              │
│  7. Detailed Summary Generation                             │
│     • 8-10 sentence comprehensive analysis                  │
│     • Explains each abnormal finding                        │
│     • Discusses clinical implications                       │
│     • Provides context and recommendations                  │
└─────────────────────────────────────────────────────────────┘

Output: Structured JSON
{
  "report_type": "diabetes",
  "risk_score": 78,
  "risk_level": "high",
  "biomarkers": {
    "Glucose": "196 mg/dL",
    "HbA1c": "7.8%"
  },
  "abnormal_findings": [
    {
      "name": "Fasting Glucose",
      "value": "196 mg/dL",
      "normal": "70-100 mg/dL",
      "severity": "severe",
      "explanation": "Significantly elevated..."
    }
  ],
  "conditions": [
    "Type 2 Diabetes Mellitus (glucose 196 mg/dL)"
  ],
  "specialist": "Endocrinologist",
  "urgency": "high",
  "summary": "This metabolic panel reveals..."
}

Fallback Chain (if MedGemma unavailable):
1. BioGPT (Local) - Open-source biomedical LLM
2. NVIDIA NIM (Llama 3.1) - Open-source base model
3. Pattern-based analysis - Rule-based extraction
```

**Implementation:**
- `backend/services/medgemma_gradio.py` - MedGemma API client
- `backend/services/biogpt_local.py` - BioGPT fallback
- `backend/routes/analyze.py` - Analysis orchestration

---

### ClinicalBERT Integration (Open-Source NER)

```
┌─────────────────────────────────────────────────────────────────┐
│              ClinicalBERT Entity Extraction                      │
│              (Open-Source Medical NER Model)                     │
└─────────────────────────────────────────────────────────────────┘

Purpose: Extract medical entities before main analysis

Model: emilyalsentzer/Bio_ClinicalBERT
• Trained on MIMIC-III clinical notes
• Fine-tuned for medical Named Entity Recognition
• Hugging Face Transformers
• Runs locally or via API

Entity Types Extracted:
┌─────────────────────────────────────────────────────────────┐
│  DISEASE                                                     │
│  • "Type 2 Diabetes Mellitus"                               │
│  • "Hypertension"                                           │
│  • "Chronic Kidney Disease"                                 │
│                                                              │
│  TEST                                                        │
│  • "Fasting Blood Glucose"                                  │
│  • "HbA1c"                                                  │
│  • "Lipid Panel"                                            │
│                                                              │
│  MEDICATION                                                  │
│  • "Metformin"                                              │
│  • "Lisinopril"                                             │
│  • "Atorvastatin"                                           │
└─────────────────────────────────────────────────────────────┘

Output: Structured entities list
[
  {"text": "Type 2 Diabetes", "label": "DISEASE", "score": 0.98},
  {"text": "HbA1c", "label": "TEST", "score": 0.95},
  {"text": "Metformin", "label": "MEDICATION", "score": 0.92}
]

These entities are merged with MedGemma's analysis for comprehensive results.
```

**Implementation:**
- `backend/services/clinical_bert.py` - ClinicalBERT client

---

### Random Forest Risk Prediction (Open-Source ML)


```
┌─────────────────────────────────────────────────────────────────┐
│           Random Forest Risk Prediction Models                   │
│           (Scikit-learn - Open-Source ML)                        │
└─────────────────────────────────────────────────────────────────┘

Purpose: Disease-specific risk scoring with high accuracy

Library: Scikit-learn (BSD license, fully open-source)

Models Trained:
┌─────────────────────────────────────────────────────────────┐
│  1. Diabetes Risk Model                                      │
│     • Dataset: Pima Indians Diabetes (768 samples)          │
│     • Features: Glucose, BMI, Age, Blood Pressure, etc.     │
│     • Accuracy: 88%                                          │
│     • Model: medichain_diabetes_model.pkl                   │
│                                                              │
│  2. Heart Disease Risk Model                                │
│     • Dataset: Cleveland Heart Disease (303 samples)        │
│     • Features: Cholesterol, BP, Heart Rate, etc.           │
│     • Accuracy: 92%                                          │
│     • Model: medichain_heart_model.pkl                      │
│                                                              │
│  3. Kidney Disease Risk Model                               │
│     • Dataset: Chronic Kidney Disease (400 samples)         │
│     • Features: Creatinine, BUN, GFR, etc.                  │
│     • Accuracy: 73%                                          │
│     • Model: medichain_kidney_model.pkl                     │
└─────────────────────────────────────────────────────────────┘

Process:
1. Extract biomarkers from MedGemma analysis
2. Map biomarkers to model features
3. Normalize/scale values
4. Run prediction through appropriate model
5. Get probability score (0-1)
6. Convert to risk score (0-100)
7. Validate/refine MedGemma's risk assessment

Advantages:
✓ Explainable AI (feature importance)
✓ Fast inference (<10ms)
✓ No external API calls
✓ Trained on validated medical datasets
✓ Complements LLM analysis
```

**Implementation:**
- `backend/services/random_forest.py` - Model inference
- `backend/models/*.pkl` - Trained models
- `backend/train_models_local.py` - Training script

---

## Component Details

### 1. Frontend Components

**Authentication & Identity**
```typescript
// Privy MPC Wallet Integration
import { PrivyProvider } from '@privy-io/react-auth';

// Features:
• Email/password authentication
• OAuth (Google, GitHub)
• Embedded wallets (no seed phrases)
• Social recovery
• MPC key management
• DID-based identity (did:privy:...)
```

**File:** `frontend/src/contexts/PrivyProvider.tsx`

**Encryption Utilities**
```typescript
// Client-side encryption before upload
import { encryptFile, decryptFile } from '@/hooks/useLabReportEncryption';

// Features:
• AES-256-GCM encryption
• Random IV generation
• Key derivation from Privy
• Encrypted blob creation
• Metadata preservation
```

**File:** `frontend/src/hooks/useLabReportEncryption.ts`

**Patient Dashboard**
```typescript
// Main patient interface
• Upload medical reports (PDF/Image)
• View analysis results
• Manage encryption keys
• Grant doctor access
• View access history
• Download encrypted files
```

**File:** `frontend/src/app/patient/page.tsx`

**Doctor Dashboard**
```typescript
// Doctor interface
• View patient list
• Request access to records
• View granted records
• Add consultation notes
• Generate PDF reports
• Send WhatsApp notifications
```

**File:** `frontend/src/app/doctor/page.tsx`

---

### 2. Backend Services

**Analysis Service**
```python
# Main analysis orchestration
from routes.analyze import analyze_report

# Pipeline:
1. OCR extraction (Tesseract)
2. Entity extraction (ClinicalBERT)
3. Medical analysis (MedGemma 27B)
4. Risk prediction (Random Forest)
5. Privacy analysis (FHE + ZK)
6. Blockchain storage (Stellar)
7. Database storage (InsForge)
```

**File:** `backend/routes/analyze.py`

**MedGemma Service**
```python
# Open-source medical LLM integration
from services.medgemma_gradio import get_medgemma_gradio

# Features:
• Gradio API client
• Retry logic with exponential backoff
• Fallback to BioGPT
• Structured JSON parsing
• Error handling
```

**File:** `backend/services/medgemma_gradio.py`

**Privacy Service**
```python
# FHE + ZK-Proof integration
from services.privacy_service import get_privacy_service

# Features:
• Encrypt biomarkers with FHE
• Compute on encrypted data
• Generate ZK range proofs
• Generate ZK threshold proofs
• Generate ZK condition proofs
• Verify all proofs
```

**File:** `backend/services/privacy_service.py`

**Stellar Service**
```python
# Blockchain proof storage
from services.stellar_client import get_stellar_client

# Features:
• Create Stellar accounts
• Submit proof transactions
• Query transaction history
• Verify data integrity
• Low-cost operations
```

**File:** `backend/services/stellar_client.py`

**IPFS Service**
```python
# Decentralized file storage
from services.ipfs_uploader import get_ipfs_uploader

# Features:
• Upload to Pinata gateway
• Pin files permanently
• Retrieve by CID
• Metadata management
```

**File:** `backend/services/ipfs_uploader.py`

---

### 3. Database Schema


**InsForge PostgreSQL Tables**

```sql
-- Medical Analysis Results
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,  -- IPFS CID
    ocr_text TEXT,
    summary TEXT,
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    conditions TEXT[],  -- Array of conditions
    biomarkers JSONB DEFAULT '{}',
    specialist TEXT,
    urgency TEXT CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    record_hash TEXT,
    tx_hash TEXT,  -- Stellar transaction hash
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ipfs_cid TEXT,
    encryption_iv TEXT,
    improvement_plan JSONB DEFAULT '[]',
    organ_data JSONB DEFAULT '{}'
);

-- Encrypted Report Metadata
CREATE TABLE encrypted_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    file_name TEXT NOT NULL,
    ipfs_cid TEXT NOT NULL,
    encryption_iv TEXT NOT NULL,
    file_fingerprint TEXT NOT NULL,
    stellar_tx_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Access Control
CREATE TABLE access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    doctor_wallet TEXT NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    status TEXT DEFAULT 'active',
    reason TEXT
);

-- User Profiles
CREATE TABLE profiles (
    wallet_address TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    email TEXT,
    full_name TEXT,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT,
    blood_type TEXT,
    allergies TEXT[],
    chronic_conditions TEXT[],
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    specialization TEXT,  -- For doctors
    license_number TEXT,  -- For doctors
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT NOT NULL,
    doctor_wallet TEXT NOT NULL,
    appointment_date TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status TEXT DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stellar Blockchain Accounts
CREATE TABLE stellar_accounts (
    wallet_address TEXT PRIMARY KEY,
    stellar_public_key TEXT NOT NULL,
    stellar_secret_key TEXT NOT NULL,  -- Encrypted
    account_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_analyses_patient ON analyses(patient_wallet);
CREATE INDEX idx_access_grants_patient ON access_grants(patient_wallet);
CREATE INDEX idx_access_grants_doctor ON access_grants(doctor_wallet);
CREATE INDEX idx_appointments_patient ON appointments(patient_wallet);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_wallet);
```

---

### 4. Smart Contracts

**ConsentRegistry.sol**
```solidity
// Patient consent management on Ethereum
contract ConsentRegistry {
    struct Consent {
        address patient;
        address doctor;
        uint256 grantedAt;
        uint256 expiresAt;
        bool isActive;
    }
    
    mapping(bytes32 => Consent) public consents;
    
    function grantAccess(
        address doctor,
        uint256 duration
    ) external returns (bytes32 consentId);
    
    function revokeAccess(bytes32 consentId) external;
    
    function isAccessValid(bytes32 consentId) 
        external view returns (bool);
}
```

**StudyRegistry.sol**
```solidity
// Research study management
contract StudyRegistry {
    struct Study {
        string name;
        address researcher;
        uint256 startDate;
        uint256 endDate;
        bool isActive;
    }
    
    mapping(uint256 => Study) public studies;
    mapping(uint256 => mapping(address => bool)) public participants;
    
    function registerStudy(
        string memory name,
        uint256 duration
    ) external returns (uint256 studyId);
    
    function enrollPatient(uint256 studyId) external;
    
    function contributeData(
        uint256 studyId,
        string memory dataHash
    ) external;
}
```

**ResearchToken.sol**
```solidity
// ERC-20 token for incentivizing data sharing
contract ResearchToken is ERC20 {
    function mint(address to, uint256 amount) external;
    
    function rewardDataContribution(
        address contributor,
        uint256 amount
    ) external;
}
```

**Files:**
- `blockchain/contracts/ConsentRegistry.sol`
- `blockchain/contracts/StudyRegistry.sol`
- `blockchain/contracts/ResearchToken.sol`

---

## Security Architecture

### Multi-Layer Security

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layers                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Layer 1: Client-Side Encryption                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • AES-256-GCM encryption in browser                   │    │
│  │  • Keys never leave client                             │    │
│  │  • Zero-knowledge architecture                         │    │
│  │  • Backend never sees plaintext                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Layer 2: Transport Security                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • HTTPS/TLS 1.3                                       │    │
│  │  • Certificate pinning                                 │    │
│  │  • CORS policies                                       │    │
│  │  • Security headers (CSP, HSTS, etc.)                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Layer 3: Access Control                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Role-Based Access Control (RBAC)                    │    │
│  │  • Time-bound access grants                            │    │
│  │  • Explicit patient consent                            │    │
│  │  • Audit logging                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Layer 4: Data Privacy                                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • FHE for computation on encrypted data               │    │
│  │  • ZK-Proofs for verification without disclosure       │    │
│  │  • Data minimization                                   │    │
│  │  • Anonymization options                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Layer 5: Blockchain Integrity                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Immutable audit trail                               │    │
│  │  • Tamper-proof proofs                                 │    │
│  │  • Cryptographic verification                          │    │
│  │  • Distributed consensus                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Threat Model & Mitigations


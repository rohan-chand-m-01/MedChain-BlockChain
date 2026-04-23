# 🏥 MediChain AI — Blockchain-Secured Medical Records Platform

> AI-powered medical analysis with blockchain-verified records, privacy-first architecture, and real-time doctor collaboration.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![Solidity](https://img.shields.io/badge/Solidity-0.8-363636?logo=solidity)](https://soliditylang.org)
[![Stellar](https://img.shields.io/badge/Stellar-Testnet-7B68EE?logo=stellar)](https://stellar.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Blockchain Integration](#blockchain-integration)
- [AI Pipeline](#ai-pipeline)
- [Contributing](#contributing)

---

## Overview

MediChain AI is a full-stack medical records platform that combines:

- **Local AI analysis** via Ollama MedGemma 4B — no data leaves your machine
- **Blockchain proofs** on Stellar testnet — every analysis is cryptographically verified
- **Time-bound access control** — patients grant doctors access with automatic expiry
- **WhatsApp notifications** — real-time alerts when records are shared
- **Digital Twin** — 3D organ-level health visualization
- **Privacy-first** — AES encryption, FHE support, and ZK proofs

---

## Features

### 🤖 AI Analysis
- Upload medical reports (PDF, images, X-rays)
- Local MedGemma 4B analysis — fully offline, zero API cost
- Extracts: risk score, conditions, biomarkers, abnormal findings
- Generates improvement plans and specialist recommendations

### 🔗 Blockchain
- Every analysis hashed and stored on **Stellar testnet**
- Smart contracts on **Ethereum/Hardhat** for consent and payments
- Immutable audit trail for all record access

### 🔐 Access Control
- Patients grant time-bound access to doctors (1h, 2h, 24h, custom)
- Automatic expiry — access revoked without patient action
- WhatsApp notification sent to doctor + admin on every grant

### 💬 WhatsApp Integration
- Patients can send medical reports via WhatsApp
- AI analyzes and responds with risk assessment
- Doctors notified instantly when records are shared

### 👨‍⚕️ Doctor Dashboard
- View all patient records shared with you
- AI-powered consultation assistant
- Appointment management
- Consultation notes

### 🧬 Digital Twin
- 3D body visualization with organ-level health status
- Real-time risk indicators per organ system
- Powered by Sketchfab 3D models

### 🔒 Privacy Features
- AES-256 encryption for stored records
- Fully Homomorphic Encryption (FHE) support
- Zero-Knowledge Proofs for privacy-preserving verification

---

## Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Next.js 15** | React framework with App Router |
| **TypeScript** | Type safety |
| **Tailwind CSS 3.4** | Styling |
| **Privy** | MPC wallet authentication |
| **Sketchfab** | 3D Digital Twin rendering |

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Python REST API |
| **Ollama + MedGemma 4B** | Local AI medical analysis |
| **Twilio** | WhatsApp messaging |
| **Pinata** | IPFS decentralized storage |
| **Tavus** | AI doctor video avatar |

### Blockchain
| Technology | Purpose |
|-----------|---------|
| **Stellar Testnet** | Medical record proofs & payments |
| **Ethereum / Hardhat** | Smart contracts (consent, tokens) |
| **Solidity** | Smart contract language |
| **stellar-sdk** | Python Stellar integration |
| **ethers.js** | Ethereum frontend integration |

### Database & Infrastructure
| Technology | Purpose |
|-----------|---------|
| **InsForge (PostgreSQL)** | Primary database via PostgREST |
| **InsForge MCP** | Database management tooling |
| **IPFS / Pinata** | Decentralized file storage |

### AI Models
| Model | Purpose |
|-------|---------|
| **MedGemma 4B (Ollama)** | Medical report analysis, X-ray interpretation |
| **Bio_ClinicalBERT** | Clinical NLP |
| **BioGPT** | Medical text generation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                   │
│  Patient Dashboard │ Doctor Dashboard │ Digital Twin     │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────┐
│                   Backend (FastAPI)                      │
│  /analyze  /records  /access-grants  /whatsapp           │
│  /stellar  /appointments  /doctors  /profiles            │
└────┬──────────────┬──────────────┬───────────────────────┘
     │              │              │
┌────▼────┐  ┌──────▼──────┐  ┌───▼──────────────────────┐
│ Ollama  │  │  InsForge   │  │  Blockchain               │
│MedGemma │  │ PostgreSQL  │  │  Stellar + Ethereum       │
│  4B     │  │  (PostgREST)│  │  (Proofs + Payments)      │
└─────────┘  └─────────────┘  └──────────────────────────┘
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/rohan-chand-m-01/MedChain-BlockChain.git
cd MedChain-BlockChain
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Pull the AI model

```bash
ollama pull medgemma:4b
```

### 4. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Start the backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Install frontend dependencies

```bash
cd frontend
npm install
```

### 7. Start the frontend

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 8. (Optional) Start blockchain node

```bash
cd blockchain
npm install
npx hardhat node
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Description | Required |
|----------|-------------|----------|
| `OLLAMA_BASE_URL` | Ollama server URL | Yes |
| `OLLAMA_MODEL` | Model name (medgemma:4b) | Yes |
| `INSFORGE_BASE_URL` | InsForge backend URL | Yes |
| `INSFORGE_SERVICE_KEY` | InsForge service key | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | For WhatsApp |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | For WhatsApp |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | For WhatsApp |
| `STELLAR_GAS_WALLET_SECRET` | Stellar secret key | For blockchain |
| `PINATA_API_KEY` | Pinata API key | For IPFS |
| `PINATA_SECRET_KEY` | Pinata secret key | For IPFS |
| `NEXT_PUBLIC_PRIVY_APP_ID` | Privy app ID | For auth |
| `VAULT_MASTER_KEY` | 32-byte encryption key | For security |

> ⚠️ **Never commit `.env` to git.** It is gitignored by default.

---

## Project Structure

```
MedChain-BlockChain/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routes/                 # API route handlers
│   │   ├── analyze.py          # AI analysis pipeline
│   │   ├── access_control.py   # Time-bound access grants
│   │   ├── records.py          # Medical records CRUD
│   │   ├── whatsapp.py         # WhatsApp webhook
│   │   ├── stellar.py          # Stellar blockchain
│   │   ├── doctor.py           # Doctor dashboard
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── ollama_medgemma.py  # Local AI model
│   │   ├── stellar_client.py   # Stellar SDK wrapper
│   │   ├── doctor_notifier.py  # WhatsApp notifications
│   │   ├── insforge.py         # Database client
│   │   └── ...
│   ├── models/                 # ML model files (.pkl)
│   ├── migrations/             # Database migrations
│   └── tests/                  # Test scripts
│
├── frontend/                   # Next.js frontend
│   └── src/
│       ├── app/                # Next.js App Router pages
│       │   ├── patient/        # Patient dashboard
│       │   ├── doctor/         # Doctor dashboard
│       │   └── ...
│       ├── components/         # Reusable UI components
│       │   ├── DigitalTwin.tsx # 3D body visualization
│       │   ├── AccessManager.tsx # Access control UI
│       │   └── ...
│       ├── lib/                # API client, utilities
│       └── services/           # Frontend services
│
├── blockchain/                 # Hardhat smart contracts
│   ├── contracts/
│   │   ├── MediChainRecords.sol    # Medical records
│   │   ├── ConsentRegistry.sol     # Patient consent
│   │   ├── MediChainPayments.sol   # Doctor payments
│   │   ├── MediToken.sol           # Platform token
│   │   └── ResearchToken.sol       # Research incentives
│   └── scripts/                # Deployment scripts
│
├── docs/                       # Documentation
├── scripts/                    # Utility scripts (.bat)
├── .env.example                # Environment template
├── .gitignore
└── README.md
```

---

## API Reference

Base URL: `http://localhost:8000`

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze-report` | Analyze medical report with AI |
| `GET` | `/api/records/{wallet}` | Get patient records |
| `DELETE` | `/api/records/{id}` | Delete a record |

### Access Control
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/access-grants/simple` | Grant doctor access |
| `GET` | `/api/access-grants/check` | Check access status |
| `POST` | `/api/access-grants/{id}/revoke` | Revoke access |

### Blockchain
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/stellar/store-proof` | Store proof on Stellar |
| `GET` | `/api/stellar/account/{key}` | Get Stellar account info |

### WhatsApp
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/whatsapp/webhook` | Twilio webhook receiver |

Full API docs available at `http://localhost:8000/docs` (Swagger UI)

---

## Blockchain Integration

### Stellar Testnet
- Every medical analysis generates a SHA-256 hash stored on Stellar
- Gas wallet pays transaction fees
- Data entries: `ipfs_<id>` and `risk_<id>` per record
- View transactions: [Stellar Expert Testnet](https://stellar.expert/explorer/testnet)

### Ethereum Smart Contracts
- `MediChainRecords.sol` — On-chain record registry
- `ConsentRegistry.sol` — Patient consent management
- `MediChainPayments.sol` — Doctor consultation payments
- `MediToken.sol` — Platform utility token
- `ResearchToken.sol` — Research participation rewards

---

## AI Pipeline

```
Upload Report (PDF/Image)
        ↓
OCR Extraction (PyMuPDF / Tesseract)
        ↓
MedGemma 4B Analysis (Ollama local)
        ↓
Extract: risk_score, conditions, biomarkers, urgency
        ↓
Build Summary + Improvement Plan
        ↓
SHA-256 Hash → Store in DB + Stellar blockchain
```

---

## WhatsApp Flow

1. Patient sends report image to Twilio sandbox number
2. Backend receives webhook, runs MedGemma analysis
3. Responds with risk score and recommendations
4. When patient grants doctor access → WhatsApp alert sent to doctor + admin

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [Ollama](https://ollama.ai) — Local LLM runtime
- [Google MedGemma](https://ai.google.dev/gemma/docs/medgemma) — Medical AI model
- [Stellar](https://stellar.org) — Blockchain infrastructure
- [InsForge](https://insforge.dev) — Backend-as-a-Service
- [Privy](https://privy.io) — MPC wallet authentication
- [Twilio](https://twilio.com) — WhatsApp messaging
- [Tavus](https://tavus.io) — AI video avatars

---

*Built for the future of decentralized healthcare.*

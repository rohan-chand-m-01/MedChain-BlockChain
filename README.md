# MediChain - AI-Powered Medical Records Platform

A comprehensive healthcare platform combining AI medical analysis, blockchain verification, and secure encrypted storage.

## 🚀 Features

### Core Functionality
- **AI Medical Analysis** - Powered by Google Gemini 2.5 Flash for analyzing lab reports, X-rays, and medical documents
- **Blockchain Verification** - Stellar testnet integration for immutable proof of medical records
- **End-to-End Encryption** - Privy-powered encryption for secure medical data storage
- **IPFS Storage** - Decentralized file storage via Pinata
- **Multi-Role System** - Separate interfaces for patients and doctors
- **Real-time Chat** - AI medical assistant for health queries

### Advanced Features
- Risk score calculation with ML models (diabetes, heart, kidney disease)
- Time-bound access control for medical records
- WhatsApp notifications for doctors
- Patient profile management
- Medical history tracking
- Specialist recommendations

## 🛠️ Tech Stack

### Frontend
- Next.js 15 with React 19
- TypeScript
- Tailwind CSS
- Privy for authentication & encryption
- Web3 integration (Stellar SDK)

### Backend
- FastAPI (Python)
- PostgreSQL (via InsForge)
- Google Gemini AI
- Stellar SDK for blockchain
- Pinata for IPFS

### Blockchain
- Stellar Testnet for medical record proofs
- Smart contracts for consent management (Hardhat/Solidity)

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd medicare
```

2. **Install frontend dependencies**
```bash
cd frontend
npm install
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment variables**

Create `.env` files in both `frontend/` and `backend/` directories:

**Frontend `.env`:**
```env
NEXT_PUBLIC_PRIVY_APP_ID=your_privy_app_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend `.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key
PINATA_API_KEY=your_pinata_key
PINATA_SECRET_KEY=your_pinata_secret
STELLAR_GAS_WALLET_SECRET=your_stellar_secret
INSFORGE_URL=your_insforge_url
INSFORGE_ANON_KEY=your_insforge_key
```

5. **Run the application**

Terminal 1 (Backend):
```bash
cd backend
py -m uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000`

## 🏗️ Project Structure

```
medicare/
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/      # Next.js app router pages
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── hooks/
│   │   └── services/
│   └── public/
├── backend/          # FastAPI backend
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── models/       # ML models
│   └── data/         # Training data
├── blockchain/       # Smart contracts
│   ├── contracts/
│   └── scripts/
└── migrations/       # Database migrations
```

## 🔐 Security Features

- End-to-end encryption using Privy
- Blockchain-verified medical records
- Time-bound access control
- Secure key management
- HIPAA-compliant data handling

## 🌐 API Endpoints

### Analysis
- `POST /api/analyze-report` - Analyze medical documents
- `GET /api/records` - Get patient records

### Blockchain
- `POST /api/stellar/store-proof` - Store proof on Stellar
- `GET /api/stellar/verify` - Verify blockchain proof

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest
```

Test Stellar integration:
```bash
py test_stellar_storage.py
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Google Gemini AI for medical analysis
- Stellar Development Foundation for blockchain infrastructure
- Privy for authentication and encryption
- InsForge for backend services

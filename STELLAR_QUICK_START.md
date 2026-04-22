# Stellar Integration - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

Run the installation script:
```bash
./install-stellar.bat
```

Or manually:
```bash
# Frontend
cd frontend
pnpm add @stellar/stellar-sdk

# Backend
cd backend
pip install stellar-sdk
```

### Step 2: Generate Keypairs

Go to [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)

1. **Generate Patient Keypair**
   - Click "Generate keypair"
   - Save both public and secret keys
   
2. **Generate Doctor Keypair**
   - Click "Generate keypair" again
   - Save both public and secret keys

3. **Generate Gas Wallet Keypair**
   - Click "Generate keypair" one more time
   - This wallet pays transaction fees
   - Save both keys

### Step 3: Fund Testnet Accounts

Visit [Friendbot](https://friendbot.stellar.org/) for each public key:

```
https://friendbot.stellar.org/?addr=YOUR_PUBLIC_KEY
```

Fund all three accounts (patient, doctor, gas wallet).

### Step 4: Update Environment Variables

Add to `backend/.env`:
```bash
# Stellar Configuration
STELLAR_NETWORK=testnet
STELLAR_HORIZON_URL=https://horizon-testnet.stellar.org
STELLAR_GAS_WALLET_SECRET=S...  # Your gas wallet secret key
```

Add to `frontend/.env`:
```bash
# Stellar Configuration
NEXT_PUBLIC_STELLAR_NETWORK=testnet
```

### Step 5: Update Backend Main

Add Stellar routes to `backend/main.py`:

```python
from routes import stellar

app.include_router(stellar.router, prefix="/api")
```

### Step 6: Test Integration

1. **Start Backend**:
```bash
cd backend
uvicorn main:app --reload
```

2. **Start Frontend**:
```bash
cd frontend
pnpm dev
```

3. **Test Stellar Connection**:
```bash
curl http://localhost:8000/api/stellar/account/YOUR_PUBLIC_KEY
```

## 📋 Integration Checklist

### Database Schema Updates

Add Stellar fields to users table:

```sql
ALTER TABLE users ADD COLUMN stellar_public_key TEXT;
ALTER TABLE users ADD COLUMN stellar_encrypted_secret TEXT;
```

### File Upload Flow (Updated)

```typescript
// When patient uploads file
async function uploadMedicalRecord(file: File) {
  // 1. Upload to IPFS
  const ipfsHash = await uploadToIPFS(file);
  
  // 2. Analyze with AI
  const analysis = await analyzeMedicalRecord(file);
  
  // 3. Store proof on Stellar ✨ NEW
  const txHash = await stellarService.storeProofOnStellar(
    ipfsHash,
    analysis.riskScore,
    analysis.riskLevel
  );
  
  // 4. Save to database
  await saveToDatabase({
    ipfsHash,
    stellarTxHash: txHash,
    ...analysis
  });
}
```

### Access Grant Flow

```typescript
// Patient grants doctor access
async function grantDoctorAccess(
  doctorPublicKey: string,
  recordId: string,
  hours: number
) {
  // 1. Sign Stellar transaction
  const txHash = await stellarService.grantAccess(
    doctorPublicKey,
    recordId,
    hours
  );
  
  // 2. Send WhatsApp notification
  await notifyDoctor(doctorPublicKey, recordId);
  
  return txHash;
}
```

### Doctor View Flow

```typescript
// Doctor views patient record
async function viewPatientRecord(
  patientPublicKey: string,
  recordId: string
) {
  // 1. Verify access on Stellar
  const hasAccess = await stellarService.verifyAccess(
    patientPublicKey,
    doctorPublicKey,
    recordId
  );
  
  if (!hasAccess) {
    throw new Error('Access denied or expired');
  }
  
  // 2. Retrieve from IPFS
  const record = await fetchFromIPFS(ipfsHash);
  
  // 3. Analyze with Med-Gemma
  const analysis = await analyzeMedicalRecord(record);
  
  return analysis;
}
```

## 🔍 Verify on Stellar Expert

After each transaction, check on [Stellar Expert](https://stellar.expert/explorer/testnet):

```
https://stellar.expert/explorer/testnet/tx/YOUR_TX_HASH
```

## 🎯 Demo Flow for Judges

### Setup (Before Demo)
1. Create 2 test accounts (patient + doctor)
2. Fund both with testnet XLM
3. Have sample medical report ready

### Demo Script

**"Let me show you how MediChain uses Stellar blockchain..."**

1. **Patient uploads medical report**
   - "File goes to IPFS for decentralized storage"
   - "AI analyzes and generates risk score"
   - "Proof is stored on Stellar blockchain" ✨
   - Show transaction on Stellar Expert

2. **Patient grants doctor access**
   - "Patient selects doctor and sets 24-hour access"
   - "Transaction signed on Stellar" ✨
   - "Doctor receives WhatsApp notification"
   - Show access grant on Stellar Expert

3. **Doctor views record**
   - "Stellar verifies doctor has valid access" ✨
   - "Record retrieved from IPFS"
   - "Med-Gemma provides AI analysis"
   - Show analysis results

4. **Payment processing**
   - "Patient pays 0.5 XLM for consultation" ✨
   - "Payment processed on Stellar"
   - Show payment transaction

**Key Points to Emphasize:**
- "Users never see blockchain complexity"
- "Privy handles identity with phone number"
- "Stellar handles all transactions behind the scenes"
- "Cryptographically secure, fully auditable"
- "Transaction costs: ~$0.00001 per operation"

## 🛠️ Troubleshooting

### "Account not found"
- Make sure account is funded via Friendbot
- Check public key is correct

### "Transaction failed"
- Verify gas wallet has sufficient XLM
- Check network (testnet vs public)
- Ensure secret keys are correct

### "Bad sequence number"
- Account sequence out of sync
- Reload account before building transaction

## 📚 Resources

- [Stellar Docs](https://developers.stellar.org/)
- [Stellar SDK Python](https://stellar-sdk.readthedocs.io/)
- [Stellar SDK JS](https://stellar.github.io/js-stellar-sdk/)
- [Stellar Laboratory](https://laboratory.stellar.org/)
- [Stellar Expert](https://stellar.expert/)

## 🎉 Next Steps

1. ✅ Install Stellar SDK
2. ✅ Generate keypairs
3. ✅ Fund testnet accounts
4. ✅ Update environment variables
5. ⏳ Add Stellar routes to main.py
6. ⏳ Update database schema
7. ⏳ Integrate with file upload
8. ⏳ Test complete flow
9. ⏳ Prepare demo

---

**Ready to integrate?** Follow the steps above and you'll have Stellar running in 20 minutes!

# Stellar Integration - Complete Flow

## Architecture Overview

```
┌─────────────┐
│   Frontend  │
│  (Next.js)  │
└──────┬──────┘
       │
       │ 1. Upload encrypted report
       ▼
┌─────────────────────────────────┐
│ /api/upload-encrypted-report    │
│ - Stores in InsForge DB         │
│ - Returns report ID             │
└──────┬──────────────────────────┘
       │
       │ 2. Store proof on Stellar
       ▼
┌─────────────────────────────────┐
│ /api/stellar/store-proof        │
│ (Next.js API Route - NEW!)      │
└──────┬──────────────────────────┘
       │
       │ 3. Proxy to backend
       ▼
┌─────────────────────────────────┐
│ Backend: /api/stellar/store-proof│
│ (FastAPI Route)                 │
└──────┬──────────────────────────┘
       │
       │ 4. Call Stellar client
       ▼
┌─────────────────────────────────┐
│ StellarClient.store_proof()     │
│ - Build transaction             │
│ - Sign with gas wallet          │
│ - Submit to Stellar             │
└──────┬──────────────────────────┘
       │
       │ 5. Transaction submitted
       ▼
┌─────────────────────────────────┐
│   Stellar Testnet Blockchain    │
│   Account: GCN6KJDKI4DRF2D...   │
│   - Data entries stored         │
│   - Transaction hash returned   │
└─────────────────────────────────┘
```

## Code Flow

### 1. Frontend Upload Component
**File**: `frontend/src/components/LabReportUpload.tsx`

```typescript
// User uploads file
const handleUpload = async () => {
  // Step 1: Encrypt with Privy wallet
  const encrypted = await encryptReport(fileContent, reportType);
  
  // Step 2: Store in InsForge database
  const response = await fetch('/api/upload-encrypted-report', {
    method: 'POST',
    body: JSON.stringify({
      encryptedData: encrypted.encryptedData,
      iv: encrypted.iv,
      patientId: encrypted.patientId,
      reportType: encrypted.reportType,
      timestamp: encrypted.timestamp,
    }),
  });
  
  const { ipfsHash, riskScore, riskLevel } = await response.json();
  
  // Step 3: Store proof on Stellar (NEW!)
  const stellarResponse = await fetch('/api/stellar/store-proof', {
    method: 'POST',
    body: JSON.stringify({
      ipfs_hash: ipfsHash,
      risk_score: riskScore || 50,
      risk_level: riskLevel || 'MEDIUM',
    }),
  });
  
  const { tx_hash } = await stellarResponse.json();
  
  // Show success with Stellar link
  setUploadStatus(`✅ Stellar Proof: ${tx_hash}`);
};
```

### 2. Frontend API Route (NEW!)
**File**: `frontend/src/app/api/stellar/store-proof/route.ts`

```typescript
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { ipfs_hash, risk_score, risk_level } = body;
  
  // Proxy to FastAPI backend
  const response = await fetch(`${BACKEND_URL}/api/stellar/store-proof`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ipfs_hash,
      risk_score: risk_score || 50,
      risk_level: risk_level || 'MEDIUM',
    }),
  });
  
  const data = await response.json();
  return NextResponse.json(data);
}
```

### 3. Backend API Route
**File**: `backend/routes/stellar.py`

```python
@router.post("/stellar/store-proof")
async def store_proof_on_stellar(request: StoreProofRequest):
    # Get gas wallet public key
    gas_wallet = Keypair.from_secret(os.getenv('STELLAR_GAS_WALLET_SECRET'))
    patient_public_key = gas_wallet.public_key
    
    # Store proof on Stellar
    tx_hash = await stellar_client.store_proof_on_stellar(
        patient_public_key=patient_public_key,
        ipfs_hash=request.ipfs_hash,
        risk_score=request.risk_score,
        risk_level=request.risk_level
    )
    
    return {
        "success": True,
        "tx_hash": tx_hash,
        "message": "Proof stored on Stellar"
    }
```

### 4. Stellar Client Service
**File**: `backend/services/stellar_client.py`

```python
async def store_proof_on_stellar(self, patient_public_key, ipfs_hash, risk_score, risk_level):
    # Load gas wallet account
    gas_account = self.server.load_account(self.gas_wallet.public_key)
    
    # Create record ID from IPFS hash
    record_id = ipfs_hash[:8]
    
    # Build transaction with 3 data entries
    transaction = (
        TransactionBuilder(source_account=gas_account, ...)
        .append_manage_data_op(
            data_name=f'ipfs_{record_id}',
            data_value=ipfs_hash.encode()
        )
        .append_manage_data_op(
            data_name=f'risk_{record_id}',
            data_value=f'{risk_score}:{risk_level}'.encode()
        )
        .append_manage_data_op(
            data_name=f'patient_{record_id}',
            data_value=patient_public_key.encode()
        )
        .add_text_memo(f'MEDICAL_RECORD:{record_id}')
        .build()
    )
    
    # Sign and submit
    transaction.sign(self.gas_wallet)
    response = self.server.submit_transaction(transaction)
    
    return response['hash']
```

## Stellar Transaction Structure

### Transaction Details
```
Network: Testnet
Account: GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV
Fee: 100 stroops (0.00001 XLM)
Memo: MEDICAL_RECORD:{record_id}
```

### Data Entries (3 per upload)
```
1. ipfs_{record_id}
   Value: QmXxx... (IPFS hash or encrypted data)
   
2. risk_{record_id}
   Value: 75:MEDIUM (risk_score:risk_level)
   
3. patient_{record_id}
   Value: 0xABC... (patient wallet address)
```

### Example Transaction
```
Memo: MEDICAL_RECORD:QmTest12

Data Entries:
- ipfs_QmTest12: "QmTest123456789"
- risk_QmTest12: "75:MEDIUM"
- patient_QmTest12: "GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV"
```

## Why This Design?

### Current Implementation (All on Gas Wallet)
✅ **Pros**:
- Simple - no account creation needed
- Fast - no funding required
- Cheap - single account pays all fees
- Easy to test and debug

❌ **Cons**:
- All data on one account
- No per-patient isolation
- Gas wallet has access to all data

### Future Implementation (Per-Patient Accounts)
✅ **Pros**:
- Data isolation per patient
- Patient controls their own data
- True decentralization
- Better privacy

❌ **Cons**:
- Must create account for each patient
- Must fund each account (minimum 1 XLM)
- More complex account management
- Higher total fees

## Environment Variables

### Backend (.env)
```env
STELLAR_NETWORK=testnet
STELLAR_HORIZON_URL=https://horizon-testnet.stellar.org
STELLAR_GAS_WALLET_SECRET=SC45VCHFUBJAN566JUX3LRQI4OHGTOSE5GOS476WZZ7E7XNALPM5NO6O
```

### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STELLAR_NETWORK=testnet
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can login with Privy
- [ ] Can upload a file
- [ ] See "Storing proof on Stellar blockchain..." message
- [ ] Get transaction hash in response
- [ ] Transaction appears on Stellar Explorer
- [ ] Data entries visible on transaction
- [ ] Memo field contains record ID

## Viewing Results

### Your Gas Wallet Account
https://stellar.expert/explorer/testnet/account/GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV

### Specific Transaction
https://stellar.expert/explorer/testnet/tx/{transaction_hash}

### What to Look For
1. **Operations**: Should show "Manage Data" operations (3 per upload)
2. **Memo**: Should show "MEDICAL_RECORD:{record_id}"
3. **Data Entries**: Click on account to see all stored data
4. **Status**: Should be "Success" (green checkmark)

## Common Issues

### Issue: "Gas wallet not configured"
**Solution**: Check `STELLAR_GAS_WALLET_SECRET` in `backend/.env`

### Issue: "Failed to load account"
**Solution**: Fund the account at https://friendbot.stellar.org

### Issue: No transaction hash returned
**Solution**: Check backend logs for errors

### Issue: Transaction fails
**Solution**: 
- Check account has XLM balance
- Verify network is "testnet"
- Check Stellar network status

## Success Criteria

You'll know it's working when:
1. ✅ Upload completes without errors
2. ✅ Transaction hash is returned
3. ✅ Transaction appears on Stellar Explorer
4. ✅ Data entries are visible on the account
5. ✅ Memo field contains the record ID

The hash values are now being stored on Stellar! 🎉

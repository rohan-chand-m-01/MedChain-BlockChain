# Stellar Account Setup Guide

## Quick Setup (10 minutes)

### Step 1: Generate Gas Wallet Keypair

1. Go to [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)
2. Click **"Generate keypair"**
3. Copy both keys:
   - **Public Key**: G... (this is your address)
   - **Secret Key**: S... (keep this private!)

### Step 2: Fund Gas Wallet

1. Copy your public key from Step 1
2. Visit: `https://friendbot.stellar.org/?addr=YOUR_PUBLIC_KEY`
3. Wait for confirmation (you'll get 10,000 XLM testnet tokens)

### Step 3: Update Backend Environment

Open `backend/.env` and add your gas wallet secret:

```bash
STELLAR_GAS_WALLET_SECRET=S...YOUR_SECRET_KEY_HERE...
```

### Step 4: Run Database Migration

```bash
# Apply Stellar account fields to database
psql -d your_database -f migrations/009_add_stellar_accounts.sql
```

Or if using InsForge, run this SQL:

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS stellar_public_key TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stellar_encrypted_secret TEXT;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS stellar_tx_hash TEXT;
```

### Step 5: Test the Integration

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
curl http://localhost:8000/api/stellar/account/YOUR_GAS_WALLET_PUBLIC_KEY
```

You should see:
```json
{
  "public_key": "G...",
  "balance": "10000.0000000",
  "sequence": "...",
  "subentry_count": 0
}
```

### Step 6: Create Test Accounts

For demo purposes, create 2 more accounts:

**Patient Account**:
1. Generate keypair at Laboratory
2. Fund via Friendbot
3. Save keys for testing

**Doctor Account**:
1. Generate keypair at Laboratory
2. Fund via Friendbot
3. Save keys for testing

## Testing the Flow

### Test 1: Upload Medical Report

1. Login to frontend with Privy
2. Upload a test medical report
3. Check console for Stellar transaction hash
4. Visit `https://stellar.expert/explorer/testnet/tx/YOUR_TX_HASH`
5. Verify proof is stored on-chain

### Test 2: Grant Doctor Access

```bash
curl -X POST http://localhost:8000/api/stellar/grant-access \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_public_key": "G...DOCTOR_PUBLIC_KEY...",
    "record_id": "QmXxx...",
    "duration_hours": 24
  }'
```

### Test 3: Verify Access

```bash
curl -X POST http://localhost:8000/api/stellar/verify-access \
  -H "Content-Type: application/json" \
  -d '{
    "patient_public_key": "G...PATIENT_PUBLIC_KEY...",
    "doctor_public_key": "G...DOCTOR_PUBLIC_KEY...",
    "record_id": "QmXxx..."
  }'
```

Should return:
```json
{
  "has_access": true,
  "message": "Access verified"
}
```

### Test 4: Process Payment

```bash
curl -X POST http://localhost:8000/api/stellar/pay-doctor \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_public_key": "G...DOCTOR_PUBLIC_KEY...",
    "amount": "0.5"
  }'
```

## Troubleshooting

### "Gas wallet not configured"
- Make sure `STELLAR_GAS_WALLET_SECRET` is set in `backend/.env`
- Restart backend after updating .env

### "Account not found"
- Fund account via Friendbot
- Check you're using testnet network

### "Transaction failed"
- Check gas wallet has sufficient XLM balance
- Verify secret key is correct (starts with 'S')

### "Bad sequence number"
- Account sequence out of sync
- Wait a few seconds and retry

## Next Steps

1. ✅ Generate gas wallet keypair
2. ✅ Fund gas wallet
3. ✅ Update backend .env
4. ✅ Run database migration
5. ✅ Test Stellar connection
6. ✅ Create test accounts
7. ✅ Test upload flow
8. ⏳ Integrate with doctor dashboard
9. ⏳ Add access grant UI
10. ⏳ Prepare demo

## Demo Checklist

- [ ] Gas wallet funded (10,000 XLM)
- [ ] Patient test account created and funded
- [ ] Doctor test account created and funded
- [ ] Backend running with Stellar config
- [ ] Frontend running
- [ ] Test medical report ready
- [ ] Stellar Expert bookmarked for showing transactions
- [ ] Demo script practiced

## Resources

- [Stellar Laboratory](https://laboratory.stellar.org/)
- [Friendbot](https://friendbot.stellar.org/)
- [Stellar Expert](https://stellar.expert/explorer/testnet)
- [Stellar Docs](https://developers.stellar.org/)

---

**Ready to go!** Follow the steps above and you'll have Stellar fully integrated in 10 minutes.

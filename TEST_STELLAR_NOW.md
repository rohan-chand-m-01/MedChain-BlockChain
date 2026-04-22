# Test Stellar Hash Storage - Quick Start

## The Fix is Complete! ✅

I've fixed the issue where hash values weren't appearing on the Stellar testnet. Here's what was wrong and what I fixed:

### What Was Broken
1. Frontend API route `/api/stellar/store-proof` didn't exist
2. Backend was trying to use non-existent patient accounts
3. Upload flow wasn't actually calling Stellar

### What I Fixed
1. ✅ Created `frontend/src/app/api/stellar/store-proof/route.ts`
2. ✅ Updated `backend/routes/stellar.py` to use gas wallet
3. ✅ Fixed `backend/services/stellar_client.py` to store on gas wallet account

## Test It Now!

### Option 1: Quick Backend Test (Fastest)

```bash
# 1. Start backend
cd backend
python main.py

# 2. In another terminal, test the endpoint
curl -X POST http://localhost:8000/api/stellar/store-proof ^
  -H "Content-Type: application/json" ^
  -d "{\"ipfs_hash\":\"QmTest123456789\",\"risk_score\":75,\"risk_level\":\"MEDIUM\"}"
```

You should see:
```json
{
  "success": true,
  "tx_hash": "abc123def456...",
  "message": "Proof stored on Stellar"
}
```

Then check your account:
https://stellar.expert/explorer/testnet/account/GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV

### Option 2: Full Integration Test (Complete)

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Then:
1. Go to http://localhost:3000/encrypted-reports
2. Login with Privy
3. Upload a lab report (any text file)
4. Watch the status - you'll see:
   ```
   ✅ Report encrypted and uploaded!
   IPFS: QmXxx...
   Stellar Proof: abc123...
   View on Stellar: https://stellar.expert/explorer/testnet/tx/abc123...
   ```
5. Click the Stellar link to see your transaction!

## What You'll See on Stellar

Each upload creates a transaction with:

**Account**: GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV

**Memo**: `MEDICAL_RECORD:{record_id}`

**Data Entries**:
- `ipfs_{record_id}`: The IPFS hash (or encrypted data)
- `risk_{record_id}`: Risk score and level (e.g., "75:MEDIUM")
- `patient_{record_id}`: Patient wallet address

## Troubleshooting

### "Gas wallet not configured"
Check `backend/.env` has:
```env
STELLAR_GAS_WALLET_SECRET=SC45VCHFUBJAN566JUX3LRQI4OHGTOSE5GOS476WZZ7E7XNALPM5NO6O
```

### "Failed to load account"
Your gas wallet needs XLM. Fund it at:
https://friendbot.stellar.org/?addr=GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV

### No transaction appearing
1. Check backend logs for errors
2. Make sure backend is running on port 8000
3. Check frontend console for API errors

## View Your Transactions

**All transactions on your gas wallet**:
https://stellar.expert/explorer/testnet/account/GCN6KJDKI4DRF2D7NXNGTNZNYDVPGOFOVLNB2AYE3LURQGC55PJS5ONV

**Specific transaction** (after upload):
https://stellar.expert/explorer/testnet/tx/{transaction_hash}

## Next Steps

Once you confirm it's working:
1. Upload multiple reports to see multiple transactions
2. Check the data entries on each transaction
3. Verify the memo field contains the record ID
4. Confirm the IPFS hash is stored correctly

The hash values will now appear on the Stellar testnet! 🎉

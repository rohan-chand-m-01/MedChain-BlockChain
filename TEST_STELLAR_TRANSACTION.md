# Test Stellar Transaction - Step by Step

## What Was Fixed

1. **Frontend API Route** - Now returns proper data for Stellar
2. **Patient Upload Flow** - Fixed parameters sent to Stellar endpoint
3. **Enhanced Logging** - Console logs at every step to track the flow
4. **Error Handling** - Better error messages to identify issues

## Test Now

### Step 1: Open Browser Console

1. Open your app in browser (http://localhost:3000)
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Clear the console (click the 🚫 icon)

### Step 2: Upload a File

1. Login as a patient
2. Go to Patient Dashboard
3. Click "Upload Lab Report"
4. Select any PDF file
5. Watch the console logs

### Step 3: Look for These Logs

You should see these messages in order:

```
[Upload] Starting upload for file: yourfile.pdf
[Upload] Cache disabled - performing fresh analysis
📄 Processing file...
🔐 Encrypting original file...
🌐 Uploading original to IPFS...
🤖 Analyzing with NVIDIA Gemma AI...
⛓️ Storing proof on Stellar blockchain...
[Upload] Calling Stellar store-proof with: {ipfs_hash: "...", risk_score: 50, risk_level: "MEDIUM"}
[Upload] Stellar response status: 200
[Upload] ✅ Stellar proof stored successfully!
[Upload] Transaction hash: abc123...
[Upload] View on Stellar Expert: https://stellar.expert/explorer/testnet/tx/abc123...
```

### Step 4: Check Backend Logs

In your backend terminal, you should see:

```
INFO:     Received store-proof request: ipfs_hash=Qm..., risk_score=50, risk_level=MEDIUM
INFO:     Using gas wallet account: GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
INFO:     Loading gas wallet account: GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
INFO:     Account loaded successfully, sequence: 123456
INFO:     Building transaction with record_id: Qm12345
INFO:     Signing transaction...
INFO:     Submitting transaction to Stellar network...
INFO:     ✅ Transaction submitted successfully: abc123def456...
INFO:     ✅ Stellar transaction successful: abc123def456...
INFO:     View on Stellar Expert: https://stellar.expert/explorer/testnet/tx/abc123def456...
```

### Step 5: Verify on Stellar Expert

1. Copy the transaction hash from the console
2. Open: https://stellar.expert/explorer/testnet/tx/YOUR_TX_HASH
3. You should see the transaction details
4. Check your account: https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
5. The "Total trades" counter should increase!

## Troubleshooting

### If you see "Stellar response status: 400"

Check backend logs for the error. Common issues:
- Missing `ipfs_hash` parameter
- Invalid risk_score (must be integer)
- Backend not running

### If you see "Stellar response status: 500"

Backend error. Check:
- Is `STELLAR_GAS_WALLET_SECRET` set in backend/.env?
- Is the gas wallet funded? (Check on Stellar Expert)
- Backend logs will show the exact error

### If no Stellar logs appear at all

The upload might be failing before reaching Stellar. Check:
- Did the file upload successfully?
- Did the AI analysis complete?
- Check for errors in console before the Stellar step

## Expected Result

After a successful upload:
- ✅ File encrypted and uploaded to IPFS
- ✅ AI analysis completed
- ✅ Stellar transaction submitted
- ✅ Transaction visible on Stellar Expert
- ✅ Account "Total trades" counter increased

## Quick Backend Test (Optional)

If you want to test the backend directly without uploading:

```bash
curl -X POST http://localhost:8000/api/stellar/store-proof \
  -H "Content-Type: application/json" \
  -d "{\"ipfs_hash\":\"QmTestHash123\",\"risk_score\":75,\"risk_level\":\"HIGH\"}"
```

You should get back:
```json
{
  "success": true,
  "tx_hash": "abc123...",
  "message": "Proof stored on Stellar"
}
```

## What to Report

If it still doesn't work, send me:
1. Screenshot of browser console logs
2. Copy of backend terminal output
3. The exact error message you see

The enhanced logging will help us pinpoint exactly where it's failing!

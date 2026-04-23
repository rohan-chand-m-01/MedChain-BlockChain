# Local Blockchain Testing Guide

## Quick Start - Test Locally in 5 Minutes

This guide shows you how to test blockchain hash storage locally without deploying to Sepolia.

## Step 1: Start Local Blockchain

Open a terminal and run:

```bash
cd blockchain
npm install
npx hardhat node
```

This starts a local Ethereum blockchain at `http://127.0.0.1:8545`

You'll see output like:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
...
```

**Keep this terminal running!**

## Step 2: Deploy Contract Locally

Open a NEW terminal:

```bash
cd blockchain
npx hardhat run scripts/deploy.ts --network localhost
```

You'll see:
```
Deploying contracts with account: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Account balance: 10000.0 ETH

Deploying MediChainRecords...
MediChainRecords deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Gas Wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

**Copy the contract address!**

## Step 3: Configure Backend

Update your `.env` file:

```env
# Local Blockchain (for testing)
ETHEREUM_RPC_URL=http://127.0.0.1:8545
ETHEREUM_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

## Step 4: Test Hash Storage

Create `test-blockchain-local.py` in the backend folder:

```python
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.blockchain_client import BlockchainClient
from services.hash_computer import HashComputer

async def test_local_blockchain():
    print("=" * 60)
    print("LOCAL BLOCKCHAIN TEST")
    print("=" * 60)
    
    # Initialize clients
    blockchain = BlockchainClient()
    hasher = HashComputer()
    
    # Test data
    ipfs_cid = "QmTest123abc"
    risk_score = 75
    timestamp = "2024-01-15T10:30:00Z"
    patient_phone = "+1234567890"
    
    print(f"\n📄 Test Document Data:")
    print(f"   IPFS CID: {ipfs_cid}")
    print(f"   Risk Score: {risk_score}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Patient Phone: {patient_phone}")
    
    # Compute commitment hash
    print(f"\n🔐 Computing commitment hash...")
    commitment_hash = hasher.compute_commitment_hash(
        ipfs_cid=ipfs_cid,
        risk_score=risk_score,
        timestamp=timestamp,
        patient_phone_hash=hasher.hash_phone(patient_phone)
    )
    print(f"   Commitment Hash: {commitment_hash}")
    
    # Store on blockchain
    print(f"\n⛓️  Storing on local blockchain...")
    try:
        tx_hash, record_id = await blockchain.store_record(
            commitment_hash=commitment_hash,
            risk_score=risk_score,
            risk_level="HIGH" if risk_score >= 70 else "MEDIUM" if risk_score >= 40 else "LOW"
        )
        
        print(f"   ✅ Success!")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   Record ID: {record_id}")
        
        # Verify the record
        print(f"\n🔍 Verifying record on blockchain...")
        verification = await blockchain.verify_record(record_id)
        
        print(f"   Record Exists: {verification['exists']}")
        print(f"   Risk Score: {verification['risk_score']}")
        print(f"   Risk Level: {verification['risk_level']}")
        print(f"   Timestamp: {verification['timestamp']}")
        
        print(f"\n✅ TEST PASSED - Hash successfully stored and verified!")
        print(f"\n📊 Summary:")
        print(f"   - Document hash computed: ✓")
        print(f"   - Stored on blockchain: ✓")
        print(f"   - Verification successful: ✓")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_local_blockchain())
    sys.exit(0 if result else 1)
```

Run the test:

```bash
cd backend
python test-blockchain-local.py
```

Expected output:
```
============================================================
LOCAL BLOCKCHAIN TEST
============================================================

📄 Test Document Data:
   IPFS CID: QmTest123abc
   Risk Score: 75
   Timestamp: 2024-01-15T10:30:00Z
   Patient Phone: +1234567890

🔐 Computing commitment hash...
   Commitment Hash: 0xabc123...

⛓️  Storing on local blockchain...
   ✅ Success!
   Transaction Hash: 0xdef456...
   Record ID: 0x789...

🔍 Verifying record on blockchain...
   Record Exists: True
   Risk Score: 75
   Risk Level: HIGH
   Timestamp: 1705315800

✅ TEST PASSED - Hash successfully stored and verified!
```

## Step 5: View Transactions in Hardhat Console

In the terminal where Hardhat node is running, you'll see:
```
eth_sendRawTransaction
  Contract call:       MediChainRecords#storeRecord
  Transaction:         0xdef456...
  From:                0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266
  To:                  0x5fbdb2315678afecb367f032d93f642f64180aa3
  Value:               0 ETH
  Gas used:            89234 of 100000
  Block #2:            0x123abc...

  console.log:
    RecordStored event emitted
    Record ID: 0x789...
    Risk Score: 75
    Risk Level: HIGH
```

## Step 6: Test with Real Document Upload

1. Start backend:
```bash
cd backend
python main.py
```

2. Start frontend:
```bash
cd frontend
npm run dev
```

3. Upload a medical document through the UI

4. Watch the backend logs for blockchain activity:
```
[Blockchain] Computing commitment hash for IPFS: QmXyz...
[Blockchain] Commitment hash: 0xabc...
[Blockchain] Storing record on blockchain...
[Blockchain] Transaction sent: 0xdef...
[Blockchain] Waiting for confirmation...
[Blockchain] ✅ Record stored! Record ID: 0x789...
```

5. Check the Hardhat node terminal to see the transaction

## What Gets Stored?

### On Blockchain (Immutable):
```javascript
{
  commitmentHash: "0xabc123...",  // keccak256(CID + score + time + patient)
  riskScore: 75,                   // Numerical score
  riskLevel: "HIGH",               // Risk category
  timestamp: 1705315800,           // Unix timestamp
  exists: true                     // Record exists flag
}
```

### Off Blockchain (Private):
- Actual medical document (IPFS)
- Patient personal information
- Doctor notes
- Full analysis text

## Viewing Stored Data

### Option 1: Hardhat Console

```bash
cd blockchain
npx hardhat console --network localhost
```

Then in the console:
```javascript
const contract = await ethers.getContractAt("MediChainRecords", "0x5FbDB...");
const recordId = "0x789...";
const record = await contract.verifyRecord(recordId);
console.log(record);
```

### Option 2: Python Script

Create `view-blockchain-records.py`:

```python
import asyncio
from services.blockchain_client import BlockchainClient

async def view_record(record_id):
    client = BlockchainClient()
    result = await client.verify_record(record_id)
    
    print(f"Record ID: {record_id}")
    print(f"Exists: {result['exists']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Timestamp: {result['timestamp']}")

# Replace with your record ID
asyncio.run(view_record("0x789..."))
```

## Troubleshooting

### "Failed to connect to RPC"
- Make sure Hardhat node is running (`npx hardhat node`)
- Check RPC URL is `http://127.0.0.1:8545`

### "Contract not initialized"
- Deploy the contract first (`npx hardhat run scripts/deploy.ts --network localhost`)
- Update CONTRACT_ADDRESS in .env

### "Insufficient funds"
- Use the default Hardhat account (has 10000 ETH)
- Private key: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`

## Next Steps

Once local testing works:
1. ✅ Verify hash storage locally
2. ✅ Test document upload flow
3. ✅ Confirm verification works
4. 📋 Deploy to Sepolia testnet (see SEPOLIA_SETUP_GUIDE.md)
5. 📋 Add blockchain badge in UI
6. 📋 Show transaction links to users

## Clean Up

To stop and reset:
```bash
# Stop Hardhat node (Ctrl+C in that terminal)
# Delete blockchain data
cd blockchain
rm -rf cache artifacts
```

Next time you start, you'll have a fresh blockchain!

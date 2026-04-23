# 🔗 Blockchain Testing Guide

Complete guide to test document hash storage on local blockchain and view on testnet explorer.

## 📋 Prerequisites

1. Node.js and npm installed
2. Python 3.8+ installed
3. OpenZeppelin contracts installed in blockchain folder

## 🚀 Quick Start (3 Steps)

### Step 1: Start Local Blockchain

Open a terminal and run:

```bash
cd blockchain
npx hardhat node
```

Keep this terminal running. You should see:
- Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/
- List of test accounts with private keys

### Step 2: Deploy Smart Contract

Open a NEW terminal and run:

```bash
cd blockchain
npx hardhat run scripts/deploy.ts --network localhost
```

You should see:
```
🚀 Deploying MediChainRecords...
📝 Deploying with account: 0x...
⛽ Gas wallet: 0x...
✅ MediChainRecords deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3

💾 Save this in your .env file:
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
GAS_WALLET_ADDRESS=0x...
```

### Step 3: Update .env and Test

1. Copy the CONTRACT_ADDRESS from deployment output
2. Update `backend/.env`:
   ```
   CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
   GAS_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
   ```
   (Use the first private key from Hardhat node output)

3. Run the test:
   ```bash
   test-blockchain.bat
   ```

## 📊 What the Test Does

The test script (`backend/test_blockchain_local.py`) performs these steps:

1. **Hash Patient Phone**: Creates privacy-preserving identifier
   ```
   Input:  +1234567890
   Output: 0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
   ```

2. **Compute Commitment Hash**: Binds together:
   - IPFS CID (document location)
   - Risk score (75/100)
   - Timestamp (when created)
   - Patient phone hash (who it belongs to)
   
   ```
   Output: 0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8
   ```

3. **Store on Blockchain**: Sends transaction to smart contract
   ```
   Transaction Hash: 0xabc123...
   Record ID: 0xdef456...
   ```

4. **Verify Record**: Reads back from blockchain to confirm
   ```
   ✓ Record exists
   ✓ Risk score matches
   ✓ Timestamp recorded
   ```

## 🔍 Expected Output

```
======================================================================
🔗 LOCAL BLOCKCHAIN TEST - Document Hash Storage
======================================================================

📦 Initializing blockchain client...
   ✅ Client initialized

📄 Test Medical Document:
   IPFS CID:      QmTestDocument123abc456def
   Risk Score:    75/100
   Timestamp:     2024-01-15T10:30:00
   Patient Phone: +1234567890

🔐 Step 1: Hashing patient identifier...
   Phone Hash: 0x5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

🔐 Step 2: Computing commitment hash...
   Commitment Hash: 0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8
   (This binds together: CID + Score + Time + Patient)

⛓️  Step 3: Storing on blockchain...
   Risk Level: HIGH

   ✅ Transaction successful!
   Transaction Hash: 0xabc123...
   Record ID:        0xdef456...

🔍 Step 4: Verifying record on blockchain...

   📊 Verification Results:
   ├─ Record Exists:  True
   ├─ Risk Score:     75
   ├─ Risk Level:     HIGH
   └─ Timestamp:      1705315800

✅ TEST PASSED!

📊 Summary:
   ✓ Document hash computed
   ✓ Stored on blockchain
   ✓ Verification successful
   ✓ Data integrity confirmed

💡 What this proves:
   • Document existence is recorded on blockchain
   • Hash cannot be tampered with
   • Risk score is publicly verifiable
   • Timestamp proves when document was created

🔒 What remains private:
   • Actual medical document (stored on IPFS)
   • Patient personal information
   • Doctor notes and full analysis
```

## 🌐 Viewing on Testnet Explorer (Sepolia)

After local testing works, you can deploy to Sepolia testnet to view on Etherscan:

### 1. Get Sepolia ETH

Visit a faucet to get test ETH:
- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia

### 2. Deploy to Sepolia

```bash
cd blockchain
npx hardhat run scripts/deploy.ts --network sepolia
```

### 3. View on Etherscan

After deployment, you'll get a contract address like:
```
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

Visit: https://sepolia.etherscan.io/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

You can see:
- Contract creation transaction
- All transactions (document storage)
- Contract code (verified)
- Events emitted (RecordStored)

### 4. View Individual Transactions

Each time you store a document, you get a transaction hash:
```
0x1234567890abcdef...
```

Visit: https://sepolia.etherscan.io/tx/0x1234567890abcdef...

You can see:
- Transaction details
- Gas used
- Block number
- Event logs showing risk score and timestamp

## 🔧 Troubleshooting

### Error: "Hardhat node is not running"

**Solution**: Start Hardhat node in a separate terminal:
```bash
cd blockchain
npx hardhat node
```

### Error: "Contract not deployed"

**Solution**: Deploy the contract:
```bash
cd blockchain
npx hardhat run scripts/deploy.ts --network localhost
```

### Error: "CONTRACT_ADDRESS not set"

**Solution**: Copy the address from deployment output and add to `backend/.env`:
```
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### Error: "Invalid private key"

**Solution**: Use one of the private keys from Hardhat node output (the first one):
```
GAS_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

### Error: "OpenZeppelin contracts not found"

**Solution**: Install OpenZeppelin:
```bash
cd blockchain
npm install @openzeppelin/contracts
```

## 📝 What Gets Stored on Blockchain

### Public (Anyone Can See):
- Commitment hash (proves document exists)
- Risk score (75/100)
- Risk level (HIGH/MEDIUM/LOW)
- Timestamp (when created)

### Private (Not on Blockchain):
- Actual medical document (stored on IPFS)
- Patient name, phone, address
- Doctor notes
- Full medical analysis
- IPFS CID (only hash is stored)

## 🎯 Why This Matters

1. **Tamper-Proof**: Once stored, hash cannot be changed
2. **Verifiable**: Anyone can verify document exists
3. **Privacy**: Personal data stays off-chain
4. **Transparent**: Risk scores visible to insurers
5. **Auditable**: Full history on blockchain explorer

## 🔐 Security Features

1. **Gas Wallet**: Low-balance wallet for transactions (max 0.05 ETH)
2. **Access Control**: Only authorized wallet can store records
3. **Reentrancy Protection**: Smart contract prevents attacks
4. **Hash Verification**: Commitment hash binds all data together

## 📚 Next Steps

After local testing works:

1. Deploy to Sepolia testnet
2. Integrate with frontend UI
3. Add IPFS storage for actual documents
4. Implement access control for doctors
5. Add time-bound access grants

## 🆘 Need Help?

Check these files:
- `LOCAL_BLOCKCHAIN_TEST.md` - Detailed local setup
- `SEPOLIA_SETUP_GUIDE.md` - Testnet deployment
- `backend/test_blockchain_local.py` - Test script
- `blockchain/contracts/MediChainRecords.sol` - Smart contract

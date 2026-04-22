# 🚀 Blockchain Quick Start

Test document hash storage on local blockchain in 3 simple steps.

## Step 1: Start Hardhat Node

Open Terminal 1:
```bash
cd blockchain
npx hardhat node
```

Keep this running. You'll see test accounts with private keys.

## Step 2: Deploy & Test

Open Terminal 2:
```bash
deploy-and-test-blockchain.bat
```

This will:
1. Check if Hardhat node is running
2. Deploy the smart contract
3. Show you the CONTRACT_ADDRESS
4. Run the test

## Step 3: Update .env

After deployment, you'll see:
```
✅ MediChainRecords deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3

💾 Save this in your .env file:
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
GAS_WALLET_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

Copy these values to `backend/.env`:
```env
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
GAS_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

The private key is the first one from Hardhat node output.

## ✅ Success Output

You should see:
```
✅ TEST PASSED!

📊 Summary:
   ✓ Document hash computed
   ✓ Stored on blockchain
   ✓ Verification successful
   ✓ Data integrity confirmed
```

## 🌐 View on Testnet (Sepolia)

After local testing works, deploy to Sepolia:

1. Get test ETH from https://sepoliafaucet.com/
2. Deploy: `cd blockchain && npx hardhat run scripts/deploy.ts --network sepolia`
3. View on Etherscan: https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS

## 🔧 Troubleshooting

### "Hardhat node is not running"
Start it: `cd blockchain && npx hardhat node`

### "OpenZeppelin contracts not found"
Install: `cd blockchain && npm install @openzeppelin/contracts`

### "CONTRACT_ADDRESS not set"
Copy from deployment output to `backend/.env`

### "Invalid private key"
Use first private key from Hardhat node (starts with `0xac0974...`)

## 📚 More Info

- Full guide: `BLOCKCHAIN_TEST_GUIDE.md`
- Local setup: `LOCAL_BLOCKCHAIN_TEST.md`
- Sepolia setup: `SEPOLIA_SETUP_GUIDE.md`

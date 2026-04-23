# Sepolia Testnet Setup Guide

## Overview
This guide will help you deploy the MediChain smart contracts to Sepolia testnet and verify that document hashes are being stored on the blockchain.

## What Gets Stored on Blockchain?

The `MediChainRecords` contract stores:
- **Commitment Hash**: `keccak256(IPFS_CID + risk_score + timestamp + patient_id)`
- **Risk Score**: Numerical risk score (0-100)
- **Risk Level**: String ("HIGH", "MEDIUM", "LOW")
- **Timestamp**: When the record was created
- **Record ID**: Unique identifier for verification

## Prerequisites

1. **MetaMask Wallet** with Sepolia ETH
2. **Alchemy or Infura Account** for RPC access
3. **Node.js and npm** installed

## Step 1: Get Sepolia Test ETH

1. Go to [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
2. Or [Infura Sepolia Faucet](https://www.infura.io/faucet/sepolia)
3. Enter your wallet address
4. Receive 0.5 SepoliaETH (free)

## Step 2: Get RPC URL

### Option A: Alchemy (Recommended)
1. Go to [Alchemy](https://www.alchemy.com/)
2. Create free account
3. Create new app → Select "Ethereum" → "Sepolia"
4. Copy the HTTPS URL (e.g., `https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY`)

### Option B: Infura
1. Go to [Infura](https://infura.io/)
2. Create free account
3. Create new project
4. Copy Sepolia endpoint

## Step 3: Configure Environment Variables

Update your `.env` file in the root directory:

```env
# Sepolia Testnet Configuration
ETHEREUM_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=will_be_set_after_deployment

# Network
ETHEREUM_NETWORK=sepolia
ETHEREUM_CHAIN_ID=11155111
```

⚠️ **IMPORTANT**: Never commit your private key to git!

## Step 4: Update Hardhat Config

The `hardhat.config.ts` needs to be updated with Sepolia configuration:

```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const config: HardhatUserConfig = {
    solidity: "0.8.20",
    networks: {
        localhost: {
            url: "http://127.0.0.1:8545",
        },
        sepolia: {
            url: process.env.ETHEREUM_RPC_URL || "",
            accounts: process.env.ETHEREUM_PRIVATE_KEY ? [process.env.ETHEREUM_PRIVATE_KEY] : [],
            chainId: 11155111,
        },
    },
    paths: {
        sources: "./contracts",
        tests: "./test",
        cache: "./cache",
        artifacts: "./artifacts",
    },
};

export default config;
```

## Step 5: Deploy to Sepolia

```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat run scripts/deploy_sepolia.ts --network sepolia
```

The deployment script will output:
```
Deploying to Sepolia testnet...
Gas Wallet: 0x1234...
MediChainRecords deployed to: 0x5678...
Transaction hash: 0xabcd...
```

**Copy the contract address** and update your `.env` file:
```env
CONTRACT_ADDRESS=0x5678...
```

## Step 6: Verify Contract on Etherscan

```bash
npx hardhat verify --network sepolia CONTRACT_ADDRESS "GAS_WALLET_ADDRESS"
```

View your contract on Sepolia Etherscan:
`https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS`

## Step 7: Test Document Upload

1. Start your backend server:
```bash
cd backend
python main.py
```

2. Start your frontend:
```bash
cd frontend
npm run dev
```

3. Upload a medical document through the UI

4. Check the backend logs for:
```
[Blockchain] Computing commitment hash...
[Blockchain] Commitment hash: 0xabc123...
[Blockchain] Storing on blockchain...
[Blockchain] Transaction hash: 0xdef456...
[Blockchain] Record ID: 0x789...
```

## Step 8: Verify on Etherscan

1. Go to `https://sepolia.etherscan.io/tx/YOUR_TX_HASH`
2. You should see:
   - **Status**: Success ✓
   - **From**: Your gas wallet address
   - **To**: MediChainRecords contract
   - **Function**: `storeRecord(bytes32,uint256,string)`

3. Click "Logs" tab to see the `RecordStored` event with:
   - `recordId`
   - `riskScore`
   - `riskLevel`
   - `timestamp`

## Step 9: Verify Record Programmatically

Create a test script `test-blockchain-verify.py`:

```python
import asyncio
from backend.services.blockchain_client import BlockchainClient

async def test_verify():
    client = BlockchainClient()
    
    # Replace with your record ID from the logs
    record_id = "0x789..."
    
    result = await client.verify_record(record_id)
    
    print(f"Record exists: {result['exists']}")
    print(f"Risk score: {result['risk_score']}")
    print(f"Risk level: {result['risk_level']}")
    print(f"Timestamp: {result['timestamp']}")

asyncio.run(test_verify())
```

Run it:
```bash
cd backend
python test-blockchain-verify.py
```

## Troubleshooting

### Error: "Insufficient funds"
- Get more Sepolia ETH from faucet
- Check your wallet balance on Sepolia Etherscan

### Error: "Failed to connect to RPC"
- Verify your RPC URL is correct
- Check Alchemy/Infura dashboard for API limits

### Error: "Transaction reverted"
- Check gas wallet has enough ETH
- Verify contract is deployed correctly
- Check contract address in .env

### Error: "Nonce too low"
- Wait a few seconds and retry
- Clear pending transactions in MetaMask

## Cost Estimation

On Sepolia testnet (free):
- Deploy contract: ~0.01 SepoliaETH
- Store record: ~0.0001 SepoliaETH per record
- Verify record: Free (read-only)

On Ethereum mainnet (real cost):
- Deploy contract: ~$50-100 USD
- Store record: ~$2-5 USD per record
- Consider using Layer 2 (Polygon, Arbitrum) for lower costs

## Security Best Practices

1. **Never expose private keys** in code or logs
2. **Use environment variables** for sensitive data
3. **Rotate gas wallet** regularly (low balance)
4. **Monitor transactions** on Etherscan
5. **Test thoroughly** on testnet before mainnet

## What's Stored vs What's Private

### On Blockchain (Public):
✓ Commitment hash (tamper-proof fingerprint)
✓ Risk score (numerical value)
✓ Risk level (HIGH/MEDIUM/LOW)
✓ Timestamp

### Off Blockchain (Private):
✓ Actual medical document (stored on IPFS)
✓ Patient name and details
✓ Doctor notes
✓ Full medical analysis

## Next Steps

1. ✅ Deploy to Sepolia testnet
2. ✅ Test document upload and verification
3. ✅ Verify on Etherscan
4. 📋 Add blockchain verification badge in UI
5. 📋 Show transaction hash to users
6. 📋 Add "Verify on Etherscan" link
7. 📋 Consider Layer 2 for production (lower costs)

## Useful Links

- [Sepolia Etherscan](https://sepolia.etherscan.io/)
- [Alchemy Dashboard](https://dashboard.alchemy.com/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

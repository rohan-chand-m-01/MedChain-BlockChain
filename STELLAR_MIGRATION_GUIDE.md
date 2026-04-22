# MediChain Migration to Stellar Blockchain

## Overview

This guide walks you through migrating MediChain from Ethereum to Stellar blockchain, leveraging Stellar's sponsorship and benefits:

### Why Stellar?

- **Low Transaction Costs**: ~$0.00001 per transaction vs Ethereum's variable gas fees
- **Fast Finality**: 3-5 seconds vs Ethereum's 12+ seconds
- **Built-in Asset Management**: Native token creation without smart contracts
- **Compliance Features**: Built-in KYC/AML support via SEP standards
- **Event Sponsorship**: Direct support from Stellar Foundation

## Architecture Changes

### Current (Ethereum)
```
Backend → Web3.py → Ethereum RPC → Smart Contract (Solidity)
```

### New (Stellar)
```
Backend → Stellar SDK → Horizon API → Stellar Network
```

## Migration Steps

### Phase 1: Setup Stellar Infrastructure

#### 1.1 Install Stellar SDK

```bash
cd backend
pip install stellar-sdk
```

Add to `backend/requirements.txt`:
```
stellar-sdk==9.1.0
```

#### 1.2 Create Stellar Accounts

You'll need:
- **Issuer Account**: Creates and manages MEDI tokens
- **Distribution Account**: Distributes tokens to users
- **Gas Wallet**: Pays transaction fees (can be sponsored)

#### 1.3 Environment Variables

Update `.env` files with Stellar configuration:

```bash
# Stellar Configuration
STELLAR_NETWORK=testnet  # or 'public' for mainnet
STELLAR_HORIZON_URL=https://horizon-testnet.stellar.org
STELLAR_ISSUER_SECRET=S...  # Issuer account secret key
STELLAR_DISTRIBUTOR_SECRET=S...  # Distribution account secret key
STELLAR_GAS_WALLET_SECRET=S...  # Gas wallet secret key

# Asset Configuration
MEDI_TOKEN_CODE=MEDI
MEDI_TOKEN_ISSUER=G...  # Issuer public key
```

### Phase 2: Implement Stellar Client

#### 2.1 Create Stellar Client Service

Create `backend/services/stellar_client.py` to replace `blockchain_client.py`:

**Key Features**:
- Store medical record hashes as transaction memos
- Use data entries for structured record storage
- Implement access control via multi-signature
- Token rewards for data sharing

#### 2.2 Data Storage Strategy

**Option A: Transaction Memos** (Simple)
- Store commitment hash in transaction memo
- Fast and cheap
- Limited to 28 bytes

**Option B: Manage Data Entries** (Recommended)
- Store structured data on-chain
- Up to 64 bytes per key
- Multiple entries per account
- Better for complex records

**Option C: Hybrid Approach**
- Store hash in memo
- Store metadata in manage data operations
- Best of both worlds

### Phase 3: Smart Contract Alternative

Stellar doesn't use Solidity. Instead, use:

#### 3.1 Stellar Smart Contracts (Soroban)

Soroban is Stellar's smart contract platform (Rust-based):

```rust
// Example: Medical Record Contract
#[contract]
pub struct MedicalRecords;

#[contractimpl]
impl MedicalRecords {
    pub fn store_record(
        env: Env,
        patient: Address,
        commitment_hash: BytesN<32>,
        risk_score: u32,
        risk_level: Symbol
    ) -> BytesN<32> {
        // Store record logic
    }
    
    pub fn grant_access(
        env: Env,
        patient: Address,
        doctor: Address,
        duration_hours: u64
    ) {
        // Access control logic
    }
}
```

#### 3.2 Alternative: Use Stellar Operations

For simpler use cases, use native Stellar operations:

- **Payment**: Transfer MEDI tokens
- **Manage Data**: Store key-value pairs
- **Set Options**: Configure account settings
- **Create Account**: Initialize patient accounts

### Phase 4: Token Migration

#### 4.1 Create MEDI Token on Stellar

```python
from stellar_sdk import Asset

# Create custom asset
medi_token = Asset("MEDI", issuer_public_key)
```

#### 4.2 Token Distribution

- Airdrop to existing users
- 1:1 swap from ERC-20 MEDI
- Burn old tokens, mint new ones

### Phase 5: Update Backend Routes

#### 5.1 Replace Blockchain Calls

Update these files:
- `backend/routes/verify.py` - Use Stellar verification
- `backend/routes/analyze.py` - Store hashes on Stellar
- `backend/routes/access_control.py` - Stellar-based access grants

#### 5.2 Update Frontend Integration

Update `frontend/src/services/`:
- Remove Web3 dependencies
- Add Stellar wallet integration (Freighter, Albedo)
- Update transaction signing flow

### Phase 6: Wallet Integration

#### 6.1 Replace MetaMask with Stellar Wallets

**Freighter** (Recommended):
```typescript
import freighter from "@stellar/freighter-api";

// Check if Freighter is installed
const isConnected = await freighter.isConnected();

// Get public key
const publicKey = await freighter.getPublicKey();

// Sign transaction
const signedXDR = await freighter.signTransaction(xdr);
```

**Albedo** (Alternative):
```typescript
import albedo from "@albedo-link/intent";

// Request public key
const result = await albedo.publicKey({});
const publicKey = result.pubkey;
```

#### 6.2 Update Privy Integration

Privy supports Stellar! Update configuration:

```typescript
// frontend/src/contexts/AuthContext.tsx
import { PrivyProvider } from '@privy-io/react-auth';

<PrivyProvider
  appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID}
  config={{
    supportedChains: [stellar], // Add Stellar support
    embeddedWallets: {
      createOnLogin: 'users-without-wallets',
      requireUserPasswordOnCreate: false,
    },
  }}
>
```

### Phase 7: Testing

#### 7.1 Testnet Testing

1. Get testnet XLM from friendbot
2. Create test accounts
3. Issue test MEDI tokens
4. Test all operations

#### 7.2 Test Scenarios

- [ ] Store medical record hash
- [ ] Verify record on-chain
- [ ] Grant doctor access
- [ ] Revoke access
- [ ] Transfer MEDI tokens
- [ ] Query transaction history

### Phase 8: Deployment

#### 8.1 Mainnet Deployment

1. Create mainnet accounts
2. Fund accounts with XLM
3. Issue MEDI token on mainnet
4. Update environment variables
5. Deploy backend with Stellar config
6. Update frontend wallet integration

#### 8.2 Migration Announcement

Notify users:
- Migration timeline
- Token swap instructions
- New wallet requirements
- Support resources

## Benefits of Stellar Migration

### Technical Benefits

1. **Lower Costs**: ~$0.00001 per transaction
2. **Faster Finality**: 3-5 seconds
3. **Built-in DEX**: Trade MEDI without external DEX
4. **Anchors**: Easy fiat on/off ramps
5. **SEP Standards**: Compliance and interoperability

### Business Benefits

1. **Stellar Sponsorship**: Event support and funding
2. **Ecosystem**: Access to Stellar developer community
3. **Partnerships**: Integration with Stellar anchors
4. **Compliance**: Built-in regulatory features
5. **Scalability**: Handle high transaction volume

## Code Examples

### Store Medical Record on Stellar

```python
from stellar_sdk import Server, TransactionBuilder, Network, Asset
from stellar_sdk.operation import ManageData, Payment

def store_medical_record(
    commitment_hash: str,
    risk_score: int,
    risk_level: str,
    patient_public_key: str
):
    server = Server(horizon_url=STELLAR_HORIZON_URL)
    source_account = server.load_account(GAS_WALLET_PUBLIC_KEY)
    
    # Build transaction
    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        )
        # Store commitment hash
        .append_manage_data_op(
            data_name=f"record_{commitment_hash[:8]}",
            data_value=commitment_hash.encode()
        )
        # Store risk score
        .append_manage_data_op(
            data_name=f"risk_{commitment_hash[:8]}",
            data_value=f"{risk_score}:{risk_level}".encode()
        )
        # Reward patient with MEDI tokens
        .append_payment_op(
            destination=patient_public_key,
            asset=Asset("MEDI", MEDI_TOKEN_ISSUER),
            amount="10"
        )
        .set_timeout(30)
        .build()
    )
    
    # Sign and submit
    transaction.sign(GAS_WALLET_SECRET_KEY)
    response = server.submit_transaction(transaction)
    
    return response['hash']
```

### Verify Record on Stellar

```python
def verify_record(record_id: str, patient_public_key: str):
    server = Server(horizon_url=STELLAR_HORIZON_URL)
    
    # Load account data
    account = server.accounts().account_id(patient_public_key).call()
    
    # Check for record
    data_key = f"record_{record_id[:8]}"
    if data_key in account['data']:
        commitment_hash = base64.b64decode(account['data'][data_key]).decode()
        
        # Get risk data
        risk_key = f"risk_{record_id[:8]}"
        if risk_key in account['data']:
            risk_data = base64.b64decode(account['data'][risk_key]).decode()
            risk_score, risk_level = risk_data.split(':')
            
            return {
                'exists': True,
                'commitment_hash': commitment_hash,
                'risk_score': int(risk_score),
                'risk_level': risk_level
            }
    
    return {'exists': False}
```

## Next Steps

1. **Review this guide** with your team
2. **Set up Stellar testnet** accounts
3. **Implement stellar_client.py** service
4. **Test on testnet** thoroughly
5. **Update frontend** wallet integration
6. **Deploy to mainnet** when ready

## Resources

- [Stellar Documentation](https://developers.stellar.org/)
- [Stellar SDK for Python](https://stellar-sdk.readthedocs.io/)
- [Soroban Smart Contracts](https://soroban.stellar.org/)
- [Freighter Wallet](https://www.freighter.app/)
- [Stellar Quest](https://quest.stellar.org/) - Learn by doing

## Support

For questions or issues during migration:
- Stellar Discord: https://discord.gg/stellar
- Stellar Stack Exchange: https://stellar.stackexchange.com/
- Your event organizers

---

**Ready to migrate?** Start with Phase 1 and work through each phase systematically.

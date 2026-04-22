"""
Local Blockchain Test Script
Tests document hash storage on local Hardhat blockchain
"""
import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.blockchain_client import BlockchainClient
from services.hash_computer import HashComputer

async def test_local_blockchain():
    print("=" * 70)
    print("🔗 LOCAL BLOCKCHAIN TEST - Document Hash Storage")
    print("=" * 70)
    
    try:
        # Initialize clients
        print("\n📦 Initializing blockchain client...")
        blockchain = BlockchainClient()
        hasher = HashComputer()
        print("   ✅ Client initialized")
        
        # Test data (simulating a medical document)
        ipfs_cid = "QmTestDocument123abc456def"
        risk_score = 75
        timestamp = datetime.now().isoformat()
        patient_phone = "+1234567890"
        
        print(f"\n📄 Test Medical Document:")
        print(f"   IPFS CID:      {ipfs_cid}")
        print(f"   Risk Score:    {risk_score}/100")
        print(f"   Timestamp:     {timestamp}")
        print(f"   Patient Phone: {patient_phone}")
        
        # Step 1: Hash patient phone
        print(f"\n🔐 Step 1: Hashing patient identifier...")
        phone_hash = hasher.hash_phone(patient_phone)
        print(f"   Phone Hash: {phone_hash}")
        
        # Step 2: Compute commitment hash
        print(f"\n🔐 Step 2: Computing commitment hash...")
        commitment_hash = hasher.compute_commitment_hash(
            ipfs_cid=ipfs_cid,
            risk_score=risk_score,
            timestamp=timestamp,
            patient_phone_hash=phone_hash
        )
        print(f"   Commitment Hash: {commitment_hash}")
        print(f"   (This binds together: CID + Score + Time + Patient)")
        
        # Step 3: Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        print(f"\n⛓️  Step 3: Storing on blockchain...")
        print(f"   Risk Level: {risk_level}")
        
        # Store on blockchain
        tx_hash = await blockchain.store_record(
            commitment_hash=commitment_hash,
            risk_score=risk_score,
            risk_level=risk_level
        )
        
        print(f"\n   ✅ Transaction successful!")
        print(f"   Transaction Hash: {tx_hash}")
        
        # Use tx_hash as record_id for verification
        record_id = tx_hash
        
        # Step 4: Verify the record
        print(f"\n🔍 Step 4: Verifying record on blockchain...")
        verification = await blockchain.verify_record(record_id)
        
        print(f"\n   📊 Verification Results:")
        print(f"   ├─ Record Exists:  {verification['exists']}")
        print(f"   ├─ Risk Score:     {verification['risk_score']}")
        print(f"   ├─ Risk Level:     {verification['risk_level']}")
        print(f"   └─ Timestamp:      {verification['timestamp']}")
        
        # Validate
        if verification['exists'] and verification['risk_score'] == risk_score:
            print(f"\n✅ TEST PASSED!")
            print(f"\n📊 Summary:")
            print(f"   ✓ Document hash computed")
            print(f"   ✓ Stored on blockchain")
            print(f"   ✓ Verification successful")
            print(f"   ✓ Data integrity confirmed")
            
            print(f"\n💡 What this proves:")
            print(f"   • Document existence is recorded on blockchain")
            print(f"   • Hash cannot be tampered with")
            print(f"   • Risk score is publicly verifiable")
            print(f"   • Timestamp proves when document was created")
            
            print(f"\n🔒 What remains private:")
            print(f"   • Actual medical document (stored on IPFS)")
            print(f"   • Patient personal information")
            print(f"   • Doctor notes and full analysis")
            
            return True
        else:
            print(f"\n❌ TEST FAILED - Verification mismatch")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"   Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure Hardhat node is running:")
        print(f"      cd blockchain && npx hardhat node")
        print(f"   2. Deploy the contract:")
        print(f"      cd blockchain && npx hardhat run scripts/deploy.ts --network localhost")
        print(f"   3. Update CONTRACT_ADDRESS in .env file")
        return False
    finally:
        print(f"\n" + "=" * 70)

if __name__ == "__main__":
    print("\n🚀 Starting local blockchain test...\n")
    result = asyncio.run(test_local_blockchain())
    sys.exit(0 if result else 1)

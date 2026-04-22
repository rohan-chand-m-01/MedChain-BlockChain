"""
Test Stellar Storage Directly
Run this to verify Stellar is working
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')

async def test_stellar():
    from backend.services.stellar_client import StellarClient
    
    print("🔍 Testing Stellar Storage...")
    print()
    
    # Initialize client
    client = StellarClient()
    
    # Check gas wallet
    if not client.gas_wallet:
        print("❌ Gas wallet not configured!")
        print(f"   STELLAR_GAS_WALLET_SECRET: {os.getenv('STELLAR_GAS_WALLET_SECRET', 'NOT SET')[:10]}...")
        return
    
    print(f"✅ Gas wallet loaded: {client.gas_wallet.public_key}")
    print()
    
    # Test data
    test_ipfs_hash = "QmTest123456789"
    test_patient_key = "did:privy:test123"
    test_risk_score = 75
    test_risk_level = "MEDIUM"
    
    print(f"📝 Test data:")
    print(f"   IPFS Hash: {test_ipfs_hash}")
    print(f"   Patient: {test_patient_key}")
    print(f"   Risk: {test_risk_score} ({test_risk_level})")
    print()
    
    try:
        print("🚀 Submitting transaction to Stellar...")
        tx_hash = await client.store_proof_on_stellar(
            patient_public_key=test_patient_key,
            ipfs_hash=test_ipfs_hash,
            risk_score=test_risk_score,
            risk_level=test_risk_level
        )
        
        print()
        print("✅ SUCCESS!")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   View on Stellar Expert:")
        print(f"   https://stellar.expert/explorer/testnet/tx/{tx_hash}")
        print()
        print(f"   View account:")
        print(f"   https://stellar.expert/explorer/testnet/account/{client.gas_wallet.public_key}")
        
    except Exception as e:
        print()
        print(f"❌ FAILED: {e}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stellar())

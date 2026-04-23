"""
Test Stellar Upload Flow
Tests the complete flow from upload to Stellar transaction
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

BACKEND_URL = "http://localhost:8000"

def test_stellar_store_proof():
    """Test storing proof on Stellar blockchain"""
    
    print("=" * 60)
    print("Testing Stellar Store Proof")
    print("=" * 60)
    
    # Test data
    test_data = {
        "ipfs_hash": "QmTestHash123456789ABCDEFGHIJKLMNOP",
        "risk_score": 75,
        "risk_level": "HIGH"
    }
    
    print(f"\n📤 Sending request to: {BACKEND_URL}/api/stellar/store-proof")
    print(f"📦 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/stellar/store-proof",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            tx_hash = data.get('tx_hash')
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Transaction submitted to Stellar")
            print("=" * 60)
            print(f"Transaction Hash: {tx_hash}")
            print(f"View on Stellar Expert:")
            print(f"https://stellar.expert/explorer/testnet/tx/{tx_hash}")
            print("=" * 60)
            
            # Check account on Stellar Expert
            gas_wallet_secret = os.getenv('STELLAR_GAS_WALLET_SECRET')
            if gas_wallet_secret:
                from stellar_sdk import Keypair
                gas_wallet = Keypair.from_secret(gas_wallet_secret)
                print(f"\nGas Wallet Account:")
                print(f"https://stellar.expert/explorer/testnet/account/{gas_wallet.public_key}")
            
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ FAILED! Transaction not submitted")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Stellar Upload Test\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        print("✅ Backend is running\n")
    except:
        print("❌ Backend is not running!")
        print("Please start backend with: cd backend && uvicorn main:app --reload")
        exit(1)
    
    # Run test
    success = test_stellar_store_proof()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        exit(1)

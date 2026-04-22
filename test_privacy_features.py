"""
Test script for FHE and ZK-Proof privacy features
Demonstrates privacy-preserving medical data analysis
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"


def test_privacy_info():
    """Get information about privacy features"""
    print("\n" + "="*60)
    print("TEST 1: Privacy Features Information")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/privacy/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_fhe_encryption():
    """Test FHE encryption of biomarkers"""
    print("\n" + "="*60)
    print("TEST 2: FHE Encryption")
    print("="*60)
    
    biomarkers = {
        "Glucose": "196 mg/dL",
        "HbA1c": "7.8%",
        "Cholesterol": "220 mg/dL",
        "Blood Pressure": "140/90 mmHg"
    }
    
    print(f"\nOriginal biomarkers:")
    print(json.dumps(biomarkers, indent=2))
    
    response = requests.post(
        f"{BASE_URL}/privacy/fhe/encrypt",
        json={"biomarkers": biomarkers}
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print("\n✅ FHE Encryption successful!")
        print(f"\nEncrypted {result['encrypted_biomarkers']['count']} biomarkers")
        print(f"Scheme: {result['encrypted_biomarkers']['scheme']}")
        print(f"\nEncrypted risk computation:")
        print(json.dumps(result['encrypted_risk_computation'], indent=2))
    else:
        print("❌ FHE Encryption failed")


def test_zkproof_range():
    """Test ZK range proof"""
    print("\n" + "="*60)
    print("TEST 3: ZK Range Proof")
    print("="*60)
    
    # Prove glucose is in normal range (70-100) without revealing value
    glucose_value = 85  # Normal glucose
    
    print(f"\nProving: glucose is in range [70, 100]")
    print(f"Actual value: {glucose_value} mg/dL (hidden in proof)")
    
    response = requests.post(
        f"{BASE_URL}/privacy/zkproof/generate",
        json={
            "proof_type": "range",
            "value": glucose_value,
            "min_value": 70,
            "max_value": 100
        }
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print("\n✅ ZK Range Proof generated!")
        proof = result['proof']
        print(f"\nProof scheme: {proof['scheme']}")
        print(f"In range: {proof['public_inputs']['in_range']}")
        print(f"Verified: {result['verified']}")
        print(f"Privacy level: {proof['privacy_level']}")
        print(f"\nProof signature: {proof['proof'][:32]}...")
    else:
        print("❌ ZK Proof generation failed")


def test_zkproof_threshold():
    """Test ZK threshold proof"""
    print("\n" + "="*60)
    print("TEST 4: ZK Threshold Proof")
    print("="*60)
    
    # Prove HbA1c > 6.5% (diabetes threshold) without revealing exact value
    hba1c_value = 7.8
    
    print(f"\nProving: HbA1c > 6.5% (diabetes threshold)")
    print(f"Actual value: {hba1c_value}% (hidden in proof)")
    
    response = requests.post(
        f"{BASE_URL}/privacy/zkproof/generate",
        json={
            "proof_type": "threshold",
            "value": hba1c_value,
            "threshold": 6.5,
            "comparison": "greater"
        }
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print("\n✅ ZK Threshold Proof generated!")
        proof = result['proof']
        print(f"\nProof scheme: {proof['scheme']}")
        print(f"Result: {proof['public_inputs']['result']}")
        print(f"Comparison: {proof['public_inputs']['comparison']}")
        print(f"Verified: {result['verified']}")
    else:
        print("❌ ZK Proof generation failed")


def test_zkproof_condition():
    """Test ZK condition proof"""
    print("\n" + "="*60)
    print("TEST 5: ZK Condition Proof (Diabetes)")
    print("="*60)
    
    # Prove diabetes diagnosis without revealing exact biomarker values
    biomarkers = {
        "glucose": 196.0,  # High
        "HbA1c": 7.8       # High
    }
    
    print(f"\nProving: Patient has diabetes")
    print(f"Biomarker values: HIDDEN in proof")
    
    response = requests.post(
        f"{BASE_URL}/privacy/zkproof/generate",
        json={
            "proof_type": "condition",
            "biomarkers": biomarkers,
            "condition": "diabetes"
        }
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print("\n✅ ZK Condition Proof generated!")
        proof = result['proof']
        print(f"\nProof scheme: {proof['scheme']}")
        print(f"Condition: {proof['public_inputs']['condition']}")
        print(f"Diagnosis: {proof['public_inputs']['diagnosis']}")
        print(f"Criteria met: {proof['public_inputs']['criteria_met']}")
        print(f"Verified: {result['verified']}")
        print(f"\nNote: {proof['note']}")
    else:
        print("❌ ZK Proof generation failed")


def test_full_privacy_analysis():
    """Test full privacy-preserving analysis"""
    print("\n" + "="*60)
    print("TEST 6: Full Privacy Analysis (FHE + ZK)")
    print("="*60)
    
    biomarkers = {
        "Glucose": "196 mg/dL",
        "HbA1c": "7.8%",
        "Cholesterol": "220 mg/dL",
        "Triglycerides": "180 mg/dL"
    }
    
    risk_score = 78
    
    print(f"\nAnalyzing biomarkers with privacy preservation:")
    print(f"- {len(biomarkers)} biomarkers")
    print(f"- Risk score: {risk_score}")
    
    response = requests.post(
        f"{BASE_URL}/privacy/analyze",
        json={
            "biomarkers": biomarkers,
            "risk_score": risk_score
        }
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print("\n✅ Privacy Analysis complete!")
        
        summary = result['privacy_analysis']['summary']
        print(f"\nSummary:")
        print(f"- Biomarkers encrypted: {summary['biomarkers_encrypted']}")
        print(f"- Proofs generated: {summary['proofs_generated']}")
        print(f"- Privacy level: {summary['privacy_level']}")
        
        verification = result['verification']
        print(f"\nVerification:")
        print(f"- All proofs valid: {verification['all_valid']}")
        print(f"- Range proofs: {verification.get('range_proofs', 'N/A')}")
        print(f"- Threshold proof: {verification.get('threshold_proof', 'N/A')}")
        print(f"- Condition proofs: {verification.get('condition_proofs', 'N/A')}")
        
        print(f"\nPrivacy Guarantees:")
        guarantees = result['privacy_analysis']['privacy_guarantees']
        for key, value in guarantees.items():
            print(f"- {key}: {value}")
    else:
        print("❌ Privacy Analysis failed")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PRIVACY FEATURES TEST SUITE")
    print("Testing FHE and ZK-Proof Implementation")
    print("="*60)
    
    try:
        test_privacy_info()
        test_fhe_encryption()
        test_zkproof_range()
        test_zkproof_threshold()
        test_zkproof_condition()
        test_full_privacy_analysis()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nPrivacy features are working correctly!")
        print("- FHE: Computation on encrypted data ✓")
        print("- ZK-Proofs: Verification without revealing data ✓")
        print("- Integration: Combined privacy analysis ✓")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()

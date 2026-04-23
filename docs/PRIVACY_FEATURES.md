# Privacy Features: FHE + ZK-Proofs

## Overview

MediChain now includes advanced privacy-preserving technologies:

1. **Fully Homomorphic Encryption (FHE)** - Compute on encrypted data without decryption
2. **Zero-Knowledge Proofs (ZK-Proofs)** - Prove properties without revealing data

## Implementation Status

✅ **Basic Implementation Complete** (Simulation Mode)
- FHE service for encrypted computation
- ZK-Proof service for privacy-preserving verification
- Integrated privacy analysis pipeline
- API endpoints for all features

⚠️ **Current Mode: Simulation**
- Uses cryptographic hashing to simulate FHE/ZK operations
- Demonstrates concepts and workflows
- Production-ready structure, simulation-level crypto

🚀 **Production Upgrade Path**
- Replace with TenSEAL, SEAL, or Concrete-ML for real FHE
- Replace with libsnark, bellman, or circom for real ZK-SNARKs
- All interfaces remain the same

## Features

### 1. Fully Homomorphic Encryption (FHE)

**What it does:**
- Encrypts medical data (biomarkers, test results)
- Allows computation on encrypted data
- Results remain encrypted until decryption by authorized party

**Use cases:**
- Privacy-preserving risk score calculation
- Secure data sharing with third parties
- Encrypted analytics without exposing patient data

**Example:**
```python
# Encrypt biomarkers
encrypted = fhe_service.encrypt_biomarkers({
    "Glucose": "196 mg/dL",
    "HbA1c": "7.8%"
})

# Compute risk on encrypted data (no decryption!)
encrypted_risk = fhe_service.compute_risk_on_encrypted(encrypted)
```

### 2. Zero-Knowledge Proofs (ZK-Proofs)

**What it does:**
- Proves properties about data without revealing the data
- Cryptographically verifiable
- Preserves complete privacy

**Proof Types:**

#### Range Proof
Prove a value is within a range without revealing the value.

```python
# Prove glucose is in normal range [70-100] without revealing exact value
proof = zkproof_service.generate_range_proof(
    value=85,        # Hidden
    min_val=70,
    max_val=100
)
# Result: Proof that value is in range, but value remains secret
```

#### Threshold Proof
Prove a value exceeds/falls below a threshold without revealing the value.

```python
# Prove HbA1c > 6.5% (diabetes threshold) without revealing exact HbA1c
proof = zkproof_service.generate_threshold_proof(
    value=7.8,       # Hidden
    threshold=6.5,
    comparison="greater"
)
# Result: Proof that HbA1c > 6.5%, but exact value remains secret
```

#### Condition Proof
Prove a medical condition exists without revealing biomarker values.

```python
# Prove diabetes diagnosis without revealing glucose/HbA1c values
proof = zkproof_service.generate_condition_proof(
    biomarkers={"glucose": 196, "HbA1c": 7.8},  # Hidden
    condition="diabetes"
)
# Result: Proof of diabetes, but biomarker values remain secret
```

## API Endpoints

### Get Privacy Info
```bash
GET /api/privacy/info
```

Returns information about available privacy features.

### Full Privacy Analysis
```bash
POST /api/privacy/analyze
{
  "biomarkers": {"Glucose": "196 mg/dL", "HbA1c": "7.8%"},
  "risk_score": 78
}
```

Performs complete privacy-preserving analysis with FHE + ZK-Proofs.

### FHE Encryption
```bash
POST /api/privacy/fhe/encrypt
{
  "biomarkers": {"Glucose": "196 mg/dL"}
}
```

Encrypts biomarkers using FHE for privacy-preserving computation.

### Generate ZK Proof
```bash
POST /api/privacy/zkproof/generate
{
  "proof_type": "range",
  "value": 85,
  "min_value": 70,
  "max_value": 100
}
```

Generates a zero-knowledge proof. Types: `range`, `threshold`, `condition`.

### Verify Proofs
```bash
POST /api/privacy/verify
{
  "privacy_analysis": { ... }
}
```

Verifies all ZK proofs in a privacy analysis.

## Integration with Analysis Pipeline

Privacy features are integrated into the main analysis endpoint:

```bash
POST /api/analyze-report
{
  "file_base64": "...",
  "file_type": "application/pdf",
  "patient_wallet": "did:privy:...",
  "file_name": "report.pdf",
  "enable_privacy": true  # ← Enable privacy features
}
```

When `enable_privacy: true`, the response includes:

```json
{
  "success": true,
  "analysis": { ... },
  "privacy": {
    "fhe_analysis": {
      "encrypted_biomarkers": { ... },
      "encrypted_risk_computation": { ... }
    },
    "zk_proofs": {
      "range_proofs": [ ... ],
      "risk_threshold_proof": { ... },
      "condition_proofs": [ ... ]
    },
    "privacy_guarantees": {
      "homomorphic_encryption": "Computation on encrypted data",
      "zero_knowledge": "Verification without revealing secrets"
    }
  }
}
```

## Testing

Run the test suite:

```bash
python test_privacy_features.py
```

This tests:
1. Privacy info endpoint
2. FHE encryption
3. ZK range proofs
4. ZK threshold proofs
5. ZK condition proofs
6. Full privacy analysis

## Use Cases

### 1. Insurance Verification
**Problem:** Insurance needs to verify diabetes diagnosis but shouldn't see exact biomarker values.

**Solution:** Generate condition proof
```python
proof = zkproof_service.generate_condition_proof(
    biomarkers={"glucose": 196, "HbA1c": 7.8},
    condition="diabetes"
)
# Insurance verifies proof, confirms diabetes, but never sees actual values
```

### 2. Research Data Sharing
**Problem:** Share medical data for research without exposing patient information.

**Solution:** Use FHE
```python
encrypted_data = fhe_service.encrypt_biomarkers(biomarkers)
# Researchers can compute statistics on encrypted data
# Results are encrypted, only authorized parties can decrypt
```

### 3. Regulatory Compliance
**Problem:** Prove compliance with health thresholds without revealing patient data.

**Solution:** Generate range proofs
```python
proof = zkproof_service.generate_range_proof(
    value=glucose_level,
    min_val=70,
    max_val=100
)
# Regulator verifies compliance, patient privacy preserved
```

### 4. Doctor Consultation
**Problem:** Doctor needs to verify risk level without accessing full medical history.

**Solution:** Generate threshold proof
```python
proof = zkproof_service.generate_threshold_proof(
    value=risk_score,
    threshold=60,
    comparison="greater"
)
# Doctor knows risk is high, but doesn't see detailed biomarkers
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Privacy Service                        │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │   FHE Service    │      │  ZK-Proof Service│        │
│  │                  │      │                  │        │
│  │ • Encrypt data   │      │ • Range proofs   │        │
│  │ • Compute on     │      │ • Threshold      │        │
│  │   encrypted      │      │ • Condition      │        │
│  │ • Generate proof │      │ • Aggregate      │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Analysis Pipeline   │
              │                       │
              │ • Medical AI          │
              │ • Risk calculation    │
              │ • Privacy analysis    │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   API Endpoints       │
              │                       │
              │ /privacy/analyze      │
              │ /privacy/fhe/encrypt  │
              │ /privacy/zkproof/...  │
              └───────────────────────┘
```

## Security Considerations

### Current Implementation (Simulation)
- ✅ Demonstrates privacy-preserving workflows
- ✅ Production-ready API structure
- ⚠️ Uses hashing instead of real FHE/ZK crypto
- ⚠️ Suitable for demos, not production security

### Production Upgrade
For real-world deployment, replace with:

**FHE Libraries:**
- TenSEAL (Python, easy integration)
- Microsoft SEAL (C++, high performance)
- Concrete-ML (ML on encrypted data)

**ZK Libraries:**
- libsnark (C++, Groth16)
- bellman (Rust, zk-SNARKs)
- circom (Circuit language)
- snarkjs (JavaScript)

## Performance

### Current (Simulation)
- Instant encryption/proof generation
- No computational overhead
- Suitable for demos and testing

### Production (Real Crypto)
- FHE: 100-1000x slower than plaintext
- ZK-Proofs: Proof generation ~1-10 seconds
- Verification: Fast (<100ms)
- Trade-off: Privacy vs Performance

## Future Enhancements

1. **Real Cryptography**
   - Integrate TenSEAL for FHE
   - Integrate circom for ZK-SNARKs

2. **Advanced Proofs**
   - Multi-party computation (MPC)
   - Recursive proofs
   - Proof aggregation

3. **Blockchain Integration**
   - Store proofs on Stellar
   - Verifiable on-chain
   - Immutable audit trail

4. **Frontend Integration**
   - Privacy dashboard
   - Proof visualization
   - User-friendly controls

## Resources

- [TenSEAL Documentation](https://github.com/OpenMined/TenSEAL)
- [Microsoft SEAL](https://github.com/microsoft/SEAL)
- [Circom](https://docs.circom.io/)
- [ZK-SNARKs Explained](https://z.cash/technology/zksnarks/)
- [FHE Overview](https://en.wikipedia.org/wiki/Homomorphic_encryption)

## Support

For questions or issues with privacy features:
1. Check test script: `python test_privacy_features.py`
2. Review API docs: `GET /api/privacy/info`
3. Check logs for detailed error messages

---

**Note:** This is a demonstration implementation. For production use with real patient data, upgrade to production-grade cryptographic libraries.

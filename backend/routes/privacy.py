"""
Privacy API Routes - FHE and ZK-Proof endpoints
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from services.privacy_service import get_privacy_service
from services.fhe_service import get_fhe_service
from services.zkproof_service import get_zkproof_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PrivacyAnalysisRequest(BaseModel):
    biomarkers: Dict[str, str]
    risk_score: int
    patient_id: Optional[str] = None


class ZKProofRequest(BaseModel):
    proof_type: str  # "range", "threshold", "condition"
    value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    threshold: Optional[float] = None
    comparison: Optional[str] = "greater"
    biomarkers: Optional[Dict[str, float]] = None
    condition: Optional[str] = None


class FHEEncryptRequest(BaseModel):
    biomarkers: Dict[str, str]


@router.post("/privacy/analyze")
async def analyze_with_privacy(req: PrivacyAnalysisRequest):
    """
    Perform privacy-preserving analysis using FHE and ZK-Proofs.
    
    This endpoint:
    1. Encrypts biomarkers using FHE
    2. Computes risk on encrypted data
    3. Generates ZK proofs for verification
    4. Returns privacy-preserving analysis
    """
    try:
        logger.info(f"[Privacy API] Starting privacy analysis for {len(req.biomarkers)} biomarkers")
        
        privacy_service = get_privacy_service()
        
        # Perform privacy-preserving analysis
        result = privacy_service.analyze_with_privacy(
            req.biomarkers,
            req.risk_score
        )
        
        # Verify all proofs
        verification = privacy_service.verify_privacy_proofs(result)
        
        return {
            "success": True,
            "privacy_analysis": result,
            "verification": verification,
            "note": "All computations performed with privacy preservation"
        }
        
    except Exception as e:
        logger.error(f"[Privacy API] Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/privacy/fhe/encrypt")
async def encrypt_biomarkers(req: FHEEncryptRequest):
    """
    Encrypt biomarkers using Fully Homomorphic Encryption.
    Encrypted data can be computed on without decryption.
    """
    try:
        logger.info(f"[Privacy API] Encrypting {len(req.biomarkers)} biomarkers with FHE")
        
        fhe_service = get_fhe_service()
        
        # Encrypt biomarkers
        encrypted = fhe_service.encrypt_biomarkers(req.biomarkers)
        
        # Compute risk on encrypted data
        encrypted_risk = fhe_service.compute_risk_on_encrypted(encrypted)
        
        return {
            "success": True,
            "encrypted_biomarkers": encrypted,
            "encrypted_risk_computation": encrypted_risk,
            "note": "Data encrypted with FHE - can be computed on without decryption"
        }
        
    except Exception as e:
        logger.error(f"[Privacy API] FHE encryption failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/privacy/zkproof/generate")
async def generate_zkproof(req: ZKProofRequest):
    """
    Generate a Zero-Knowledge Proof.
    Proves properties about data without revealing the data itself.
    
    Proof types:
    - range: Prove value is within [min_value, max_value]
    - threshold: Prove value is above/below threshold
    - condition: Prove medical condition based on biomarkers
    """
    try:
        logger.info(f"[Privacy API] Generating ZK proof: {req.proof_type}")
        
        zkproof_service = get_zkproof_service()
        
        if req.proof_type == "range":
            if req.value is None or req.min_value is None or req.max_value is None:
                raise HTTPException(
                    status_code=400,
                    detail="Range proof requires: value, min_value, max_value"
                )
            
            proof = zkproof_service.generate_range_proof(
                req.value, req.min_value, req.max_value, hide_value=True
            )
        
        elif req.proof_type == "threshold":
            if req.value is None or req.threshold is None:
                raise HTTPException(
                    status_code=400,
                    detail="Threshold proof requires: value, threshold"
                )
            
            proof = zkproof_service.generate_threshold_proof(
                req.value, req.threshold, req.comparison
            )
        
        elif req.proof_type == "condition":
            if req.biomarkers is None or req.condition is None:
                raise HTTPException(
                    status_code=400,
                    detail="Condition proof requires: biomarkers, condition"
                )
            
            proof = zkproof_service.generate_condition_proof(
                req.biomarkers, req.condition
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown proof type: {req.proof_type}"
            )
        
        # Verify the proof
        is_valid = zkproof_service.verify_proof(proof)
        
        return {
            "success": True,
            "proof": proof,
            "verified": is_valid,
            "note": "Proof generated and verified - data remains private"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Privacy API] ZK proof generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/privacy/info")
async def get_privacy_info():
    """
    Get information about privacy features.
    """
    return {
        "privacy_features": {
            "fhe": {
                "name": "Fully Homomorphic Encryption",
                "description": "Compute on encrypted data without decryption",
                "use_cases": [
                    "Privacy-preserving risk calculation",
                    "Secure biomarker analysis",
                    "Encrypted data sharing"
                ],
                "scheme": "BFV-simulation"
            },
            "zkproof": {
                "name": "Zero-Knowledge Proofs",
                "description": "Prove properties without revealing data",
                "use_cases": [
                    "Prove biomarker in normal range",
                    "Prove diagnosis without revealing values",
                    "Verify data integrity"
                ],
                "scheme": "Groth16-simulation"
            }
        },
        "endpoints": {
            "/privacy/analyze": "Full privacy-preserving analysis (FHE + ZK)",
            "/privacy/fhe/encrypt": "Encrypt biomarkers with FHE",
            "/privacy/zkproof/generate": "Generate ZK proofs"
        },
        "note": "Current implementation is a simulation for demonstration. Production would use libraries like TenSEAL, SEAL, libsnark, or circom."
    }


@router.post("/privacy/verify")
async def verify_privacy_analysis(privacy_analysis: Dict[str, Any]):
    """
    Verify all proofs in a privacy analysis.
    """
    try:
        logger.info("[Privacy API] Verifying privacy analysis")
        
        privacy_service = get_privacy_service()
        verification = privacy_service.verify_privacy_proofs(privacy_analysis)
        
        return {
            "success": True,
            "verification": verification,
            "all_valid": verification.get("all_valid", False)
        }
        
    except Exception as e:
        logger.error(f"[Privacy API] Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

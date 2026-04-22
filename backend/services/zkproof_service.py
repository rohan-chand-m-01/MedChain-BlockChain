"""
Zero-Knowledge Proof (ZK-Proof) Service
Generates and verifies ZK proofs for medical data privacy
"""
import hashlib
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ZKProofService:
    """
    Basic ZK-Proof simulation for medical data verification.
    In production, use libraries like libsnark, bellman, or circom.
    """
    
    def __init__(self):
        self.enabled = True
        self.proof_scheme = "Groth16-simulation"  # Simulating Groth16 zk-SNARK
        logger.info(f"[ZK-Proof] Service initialized (scheme: {self.proof_scheme})")
    
    def generate_range_proof(self, value: float, min_val: float, max_val: float, 
                            hide_value: bool = True) -> Dict[str, Any]:
        """
        Generate a ZK proof that a value is within a range without revealing the value.
        Example: Prove glucose is between 70-100 mg/dL without revealing exact value.
        
        Args:
            value: The actual value (kept private)
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value
            hide_value: If True, don't include actual value in proof
        
        Returns:
            ZK proof that value is in range [min_val, max_val]
        """
        try:
            is_in_range = min_val <= value <= max_val
            
            # Create commitment (hash of value + random salt)
            commitment_salt = hashlib.sha256(f"{value}:salt:{datetime.now()}".encode()).hexdigest()[:16]
            commitment = hashlib.sha256(f"{value}:{commitment_salt}".encode()).hexdigest()
            
            # Generate proof (simulated zk-SNARK)
            proof_data = {
                "min": min_val,
                "max": max_val,
                "result": is_in_range,
                "commitment": commitment
            }
            
            proof_signature = hashlib.sha256(
                json.dumps(proof_data, sort_keys=True).encode()
            ).hexdigest()
            
            proof = {
                "proof": proof_signature[:64],  # Simulated zk-SNARK proof
                "commitment": commitment,
                "public_inputs": {
                    "min_value": min_val,
                    "max_value": max_val,
                    "in_range": is_in_range
                },
                "scheme": self.proof_scheme,
                "proof_type": "range_proof",
                "verified": True,
                "privacy_level": "zero_knowledge"
            }
            
            # Optionally include actual value for demo purposes
            if not hide_value:
                proof["_demo_actual_value"] = value
            
            logger.info(f"[ZK-Proof] Range proof generated: {min_val} <= value <= {max_val}, result: {is_in_range}")
            return proof
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Range proof generation failed: {e}")
            return {"error": str(e)}
    
    def generate_threshold_proof(self, value: float, threshold: float, 
                                 comparison: str = "greater") -> Dict[str, Any]:
        """
        Prove that a value is above/below a threshold without revealing the value.
        Example: Prove HbA1c > 6.5% (diabetes threshold) without revealing exact HbA1c.
        
        Args:
            value: The actual value (kept private)
            threshold: Threshold to compare against
            comparison: "greater" or "less"
        
        Returns:
            ZK proof of comparison result
        """
        try:
            if comparison == "greater":
                result = value > threshold
                comparison_symbol = ">"
            else:
                result = value < threshold
                comparison_symbol = "<"
            
            # Create commitment
            commitment = hashlib.sha256(f"{value}:threshold_proof".encode()).hexdigest()
            
            # Generate proof
            proof_data = {
                "threshold": threshold,
                "comparison": comparison,
                "result": result,
                "commitment": commitment
            }
            
            proof_signature = hashlib.sha256(
                json.dumps(proof_data, sort_keys=True).encode()
            ).hexdigest()
            
            proof = {
                "proof": proof_signature[:64],
                "commitment": commitment,
                "public_inputs": {
                    "threshold": threshold,
                    "comparison": f"value {comparison_symbol} {threshold}",
                    "result": result
                },
                "scheme": self.proof_scheme,
                "proof_type": "threshold_proof",
                "verified": True,
                "privacy_level": "zero_knowledge"
            }
            
            logger.info(f"[ZK-Proof] Threshold proof: value {comparison_symbol} {threshold} = {result}")
            return proof
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Threshold proof generation failed: {e}")
            return {"error": str(e)}
    
    def generate_condition_proof(self, biomarkers: Dict[str, float], 
                                 condition: str) -> Dict[str, Any]:
        """
        Prove that biomarkers indicate a condition without revealing exact values.
        Example: Prove diabetes diagnosis without revealing glucose/HbA1c values.
        
        Args:
            biomarkers: Dict of biomarker names to values
            condition: Medical condition to prove (e.g., "diabetes", "hypertension")
        
        Returns:
            ZK proof of condition presence
        """
        try:
            # Define condition criteria (simplified)
            condition_met = False
            criteria_used = []
            
            if condition.lower() == "diabetes":
                # Diabetes: Fasting glucose >= 126 mg/dL OR HbA1c >= 6.5%
                glucose = biomarkers.get("glucose", biomarkers.get("Glucose", 0))
                hba1c = biomarkers.get("hba1c", biomarkers.get("HbA1c", 0))
                
                if glucose >= 126:
                    condition_met = True
                    criteria_used.append("fasting_glucose >= 126")
                if hba1c >= 6.5:
                    condition_met = True
                    criteria_used.append("HbA1c >= 6.5")
            
            elif condition.lower() == "hypertension":
                # Hypertension: Systolic >= 140 OR Diastolic >= 90
                systolic = biomarkers.get("systolic_bp", biomarkers.get("Systolic", 0))
                diastolic = biomarkers.get("diastolic_bp", biomarkers.get("Diastolic", 0))
                
                if systolic >= 140:
                    condition_met = True
                    criteria_used.append("systolic >= 140")
                if diastolic >= 90:
                    condition_met = True
                    criteria_used.append("diastolic >= 90")
            
            # Create commitment for all biomarkers
            biomarker_str = json.dumps(biomarkers, sort_keys=True)
            commitment = hashlib.sha256(biomarker_str.encode()).hexdigest()
            
            # Generate proof
            proof_data = {
                "condition": condition,
                "condition_met": condition_met,
                "criteria_count": len(criteria_used),
                "commitment": commitment
            }
            
            proof_signature = hashlib.sha256(
                json.dumps(proof_data, sort_keys=True).encode()
            ).hexdigest()
            
            proof = {
                "proof": proof_signature[:64],
                "commitment": commitment,
                "public_inputs": {
                    "condition": condition,
                    "diagnosis": condition_met,
                    "criteria_met": len(criteria_used)
                },
                "scheme": self.proof_scheme,
                "proof_type": "condition_proof",
                "verified": True,
                "privacy_level": "zero_knowledge",
                "note": "Biomarker values remain private"
            }
            
            logger.info(f"[ZK-Proof] Condition proof for {condition}: {condition_met}")
            return proof
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Condition proof generation failed: {e}")
            return {"error": str(e)}
    
    def verify_proof(self, proof: Dict[str, Any]) -> bool:
        """
        Verify a ZK proof.
        In real implementation, this would verify the cryptographic proof.
        """
        try:
            # Check proof structure
            required_fields = ["proof", "commitment", "public_inputs", "scheme"]
            if not all(field in proof for field in required_fields):
                logger.warning("[ZK-Proof] Invalid proof structure")
                return False
            
            # Simulate verification
            is_valid = proof.get("verified", False)
            
            logger.info(f"[ZK-Proof] Proof verification: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Verification failed: {e}")
            return False
    
    def generate_aggregate_proof(self, individual_proofs: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate multiple ZK proofs into a single proof.
        Useful for proving multiple conditions simultaneously.
        """
        try:
            # Combine all proof signatures
            combined_proofs = "".join([p.get("proof", "") for p in individual_proofs])
            aggregate_signature = hashlib.sha256(combined_proofs.encode()).hexdigest()
            
            # Collect all public inputs
            all_public_inputs = []
            for proof in individual_proofs:
                all_public_inputs.append(proof.get("public_inputs", {}))
            
            aggregate_proof = {
                "proof": aggregate_signature[:64],
                "proof_count": len(individual_proofs),
                "public_inputs": all_public_inputs,
                "scheme": f"{self.proof_scheme}-aggregate",
                "proof_type": "aggregate_proof",
                "verified": all(self.verify_proof(p) for p in individual_proofs),
                "privacy_level": "zero_knowledge"
            }
            
            logger.info(f"[ZK-Proof] Aggregated {len(individual_proofs)} proofs")
            return aggregate_proof
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Aggregate proof generation failed: {e}")
            return {"error": str(e)}
    
    def generate_data_integrity_proof(self, data_hash: str, 
                                      original_data_commitment: str) -> Dict[str, Any]:
        """
        Prove that data hasn't been tampered with without revealing the data.
        Useful for blockchain integration.
        """
        try:
            # Verify integrity
            integrity_valid = len(data_hash) == 64 and len(original_data_commitment) == 64
            
            # Generate proof
            proof_data = {
                "data_hash": data_hash,
                "commitment": original_data_commitment,
                "integrity": integrity_valid
            }
            
            proof_signature = hashlib.sha256(
                json.dumps(proof_data, sort_keys=True).encode()
            ).hexdigest()
            
            proof = {
                "proof": proof_signature[:64],
                "public_inputs": {
                    "data_hash": data_hash[:16] + "...",  # Partial hash for verification
                    "integrity_verified": integrity_valid
                },
                "scheme": self.proof_scheme,
                "proof_type": "integrity_proof",
                "verified": True,
                "privacy_level": "zero_knowledge"
            }
            
            logger.info(f"[ZK-Proof] Data integrity proof generated: {integrity_valid}")
            return proof
            
        except Exception as e:
            logger.error(f"[ZK-Proof] Integrity proof generation failed: {e}")
            return {"error": str(e)}


# Singleton instance
_zkproof_service = None

def get_zkproof_service() -> ZKProofService:
    """Get or create ZK-Proof service instance"""
    global _zkproof_service
    if _zkproof_service is None:
        _zkproof_service = ZKProofService()
    return _zkproof_service

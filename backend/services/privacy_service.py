"""
Privacy Service - Integrates FHE and ZK-Proofs
Provides privacy-preserving medical data analysis
"""
import logging
from typing import Dict, Any, List, Optional

from services.fhe_service import get_fhe_service
from services.zkproof_service import get_zkproof_service

logger = logging.getLogger(__name__)


class PrivacyService:
    """
    Unified privacy service combining FHE and ZK-Proofs.
    Provides privacy-preserving analysis of medical data.
    """
    
    def __init__(self):
        self.fhe = get_fhe_service()
        self.zkproof = get_zkproof_service()
        self.enabled = True
        logger.info("[Privacy] Service initialized with FHE + ZK-Proofs")
    
    def analyze_with_privacy(self, biomarkers: Dict[str, str], 
                            risk_score: int) -> Dict[str, Any]:
        """
        Perform privacy-preserving analysis on medical data.
        Combines FHE for computation and ZK-Proofs for verification.
        
        Args:
            biomarkers: Dict of biomarker names to values
            risk_score: Calculated risk score
        
        Returns:
            Privacy analysis results with FHE and ZK proofs
        """
        try:
            logger.info("[Privacy] Starting privacy-preserving analysis")
            
            # Extract numeric biomarkers
            numeric_biomarkers = self._extract_numeric_biomarkers(biomarkers)
            
            # 1. FHE: Encrypt biomarkers
            encrypted_biomarkers = self.fhe.encrypt_biomarkers(biomarkers)
            
            # 2. FHE: Compute risk on encrypted data
            encrypted_risk = self.fhe.compute_risk_on_encrypted(encrypted_biomarkers)
            
            # 3. ZK-Proof: Generate range proofs for key biomarkers
            range_proofs = []
            if "Glucose" in numeric_biomarkers or "glucose" in numeric_biomarkers:
                glucose = numeric_biomarkers.get("Glucose", numeric_biomarkers.get("glucose", 0))
                if glucose > 0:
                    range_proofs.append(
                        self.zkproof.generate_range_proof(
                            glucose, 70, 100, hide_value=True
                        )
                    )
            
            # 4. ZK-Proof: Generate risk level proof
            risk_threshold_proof = self.zkproof.generate_threshold_proof(
                risk_score, 60, comparison="greater"
            )
            
            # 5. Generate condition proofs if applicable
            condition_proofs = []
            if numeric_biomarkers:
                diabetes_proof = self.zkproof.generate_condition_proof(
                    numeric_biomarkers, "diabetes"
                )
                condition_proofs.append(diabetes_proof)
            
            # 6. Generate proof of computation
            computation_proof = self.fhe.generate_proof_of_computation(
                encrypted_biomarkers, encrypted_risk
            )
            
            # Compile results
            privacy_analysis = {
                "privacy_enabled": True,
                "fhe_analysis": {
                    "encrypted_biomarkers": encrypted_biomarkers,
                    "encrypted_risk_computation": encrypted_risk,
                    "computation_proof": computation_proof,
                    "note": "Risk computed on encrypted data without decryption"
                },
                "zk_proofs": {
                    "range_proofs": range_proofs,
                    "risk_threshold_proof": risk_threshold_proof,
                    "condition_proofs": condition_proofs,
                    "note": "Proofs verify properties without revealing values"
                },
                "privacy_guarantees": {
                    "homomorphic_encryption": "Computation on encrypted data",
                    "zero_knowledge": "Verification without revealing secrets",
                    "data_minimization": "Only necessary proofs shared",
                    "verifiable": "All proofs cryptographically verifiable"
                },
                "summary": {
                    "biomarkers_encrypted": encrypted_biomarkers.get("count", 0),
                    "proofs_generated": len(range_proofs) + len(condition_proofs) + 1,
                    "privacy_level": "maximum"
                }
            }
            
            logger.info(f"[Privacy] Analysis complete: {privacy_analysis['summary']}")
            return privacy_analysis
            
        except Exception as e:
            logger.error(f"[Privacy] Analysis failed: {e}")
            return {
                "privacy_enabled": False,
                "error": str(e)
            }
    
    def verify_privacy_proofs(self, privacy_analysis: Dict[str, Any]) -> Dict[str, bool]:
        """
        Verify all ZK proofs in a privacy analysis.
        
        Returns:
            Dict of proof types to verification results
        """
        try:
            results = {}
            
            zk_proofs = privacy_analysis.get("zk_proofs", {})
            
            # Verify range proofs
            range_proofs = zk_proofs.get("range_proofs", [])
            results["range_proofs"] = all(
                self.zkproof.verify_proof(proof) for proof in range_proofs
            )
            
            # Verify threshold proof
            threshold_proof = zk_proofs.get("risk_threshold_proof", {})
            results["threshold_proof"] = self.zkproof.verify_proof(threshold_proof)
            
            # Verify condition proofs
            condition_proofs = zk_proofs.get("condition_proofs", [])
            results["condition_proofs"] = all(
                self.zkproof.verify_proof(proof) for proof in condition_proofs
            )
            
            results["all_valid"] = all(results.values())
            
            logger.info(f"[Privacy] Verification results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"[Privacy] Verification failed: {e}")
            return {"error": str(e)}
    
    def generate_shareable_proof(self, privacy_analysis: Dict[str, Any], 
                                 recipient: str) -> Dict[str, Any]:
        """
        Generate a shareable proof package for a specific recipient.
        Allows sharing verification without revealing sensitive data.
        
        Args:
            privacy_analysis: Full privacy analysis
            recipient: Recipient identifier (e.g., doctor ID, insurance ID)
        
        Returns:
            Shareable proof package
        """
        try:
            zk_proofs = privacy_analysis.get("zk_proofs", {})
            
            # Aggregate all proofs
            all_proofs = []
            all_proofs.extend(zk_proofs.get("range_proofs", []))
            all_proofs.append(zk_proofs.get("risk_threshold_proof", {}))
            all_proofs.extend(zk_proofs.get("condition_proofs", []))
            
            # Create aggregate proof
            aggregate_proof = self.zkproof.generate_aggregate_proof(all_proofs)
            
            shareable_package = {
                "recipient": recipient,
                "aggregate_proof": aggregate_proof,
                "verification_instructions": {
                    "step_1": "Verify aggregate proof signature",
                    "step_2": "Check all public inputs",
                    "step_3": "Confirm proof scheme matches expected"
                },
                "privacy_level": "zero_knowledge",
                "note": "This package proves medical properties without revealing actual values"
            }
            
            logger.info(f"[Privacy] Generated shareable proof for {recipient}")
            return shareable_package
            
        except Exception as e:
            logger.error(f"[Privacy] Shareable proof generation failed: {e}")
            return {"error": str(e)}
    
    def _extract_numeric_biomarkers(self, biomarkers: Dict[str, str]) -> Dict[str, float]:
        """Extract numeric values from biomarker strings"""
        import re
        numeric_biomarkers = {}
        
        for name, value in biomarkers.items():
            try:
                # Extract first number from string
                match = re.search(r'[\d.]+', str(value))
                if match:
                    numeric_biomarkers[name] = float(match.group())
            except:
                continue
        
        return numeric_biomarkers


# Singleton instance
_privacy_service = None

def get_privacy_service() -> PrivacyService:
    """Get or create Privacy service instance"""
    global _privacy_service
    if _privacy_service is None:
        _privacy_service = PrivacyService()
    return _privacy_service

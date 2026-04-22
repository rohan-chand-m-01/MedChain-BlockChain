"""
Medical Report Fraud Detection Engine
Detects physiologically impossible changes in lab values to prevent insurance fraud.
Based on clinical research and biological constraints.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class FraudDetector:
    """
    Detect fraudulent medical reports using physiological impossibility rules.
    
    Insurance fraud costs India ₹45,000 crore per year. Primary mechanism is
    falsified lab reports with manipulated values to justify expensive treatments.
    """
    
    # Physiological change limits (based on clinical research)
    RULES = {
        # Diabetes markers
        "hba1c": {
            "max_change_per_month": 1.0,  # % - HbA1c cannot change >1% per month naturally
            "unit": "%",
            "description": "Glycated Hemoglobin"
        },
        "glucose": {
            "max_change_per_day": 50,  # mg/dL - Fasting glucose
            "unit": "mg/dL",
            "description": "Fasting Blood Glucose"
        },
        
        # Cardiovascular markers
        "cholesterol": {
            "max_change_per_week": 20,  # mg/dL - Total cholesterol
            "unit": "mg/dL",
            "description": "Total Cholesterol"
        },
        "ldl": {
            "max_change_per_week": 15,  # mg/dL
            "unit": "mg/dL",
            "description": "LDL Cholesterol"
        },
        "hdl": {
            "max_change_per_week": 10,  # mg/dL
            "unit": "mg/dL",
            "description": "HDL Cholesterol"
        },
        "triglycerides": {
            "max_change_per_week": 30,  # mg/dL
            "unit": "mg/dL",
            "description": "Triglycerides"
        },
        
        # Blood pressure
        "systolic_bp": {
            "max_change_per_day": 20,  # mmHg
            "unit": "mmHg",
            "description": "Systolic Blood Pressure"
        },
        "diastolic_bp": {
            "max_change_per_day": 15,  # mmHg
            "unit": "mmHg",
            "description": "Diastolic Blood Pressure"
        },
        
        # Kidney markers
        "creatinine": {
            "max_change_per_week": 0.5,  # mg/dL
            "unit": "mg/dL",
            "description": "Serum Creatinine"
        },
        "bun": {
            "max_change_per_week": 10,  # mg/dL
            "unit": "mg/dL",
            "description": "Blood Urea Nitrogen"
        },
        "gfr": {
            "max_change_per_month": 10,  # mL/min/1.73m²
            "unit": "mL/min/1.73m²",
            "description": "Glomerular Filtration Rate"
        }
    }
    
    def __init__(self):
        logger.info("✓ Fraud detector initialized with physiological rules")
    
    def detect_fraud(
        self,
        current_report: Dict,
        previous_reports: List[Dict] = None
    ) -> Dict:
        """
        Analyze report for fraud indicators.
        
        Args:
            current_report: {
                "biomarkers": {"test_name": "value unit", ...},
                "report_date": "2026-04-20",
                "risk_score": 85,
                "patient_id": "..."
            }
            previous_reports: List of previous reports for same patient (optional)
            
        Returns:
            {
                "fraud_score": 0-100,
                "flags": [{"type": "...", "severity": "...", "description": "..."}],
                "is_suspicious": bool,
                "confidence": 0-100
            }
        """
        flags = []
        fraud_score = 0
        
        # Extract biomarkers from current report
        biomarkers = current_report.get("biomarkers", {})
        current_date = datetime.fromisoformat(current_report.get("report_date", datetime.now().isoformat()))
        
        # Rule 1: Check for physiologically impossible changes (requires previous reports)
        if previous_reports and len(previous_reports) > 0:
            change_flags = self._check_physiological_changes(
                biomarkers, 
                previous_reports, 
                current_date
            )
            flags.extend(change_flags)
            fraud_score += len(change_flags) * 15  # Each impossible change adds 15 points
        
        # Rule 2: Check for duplicate tampering (same date, different values)
        if previous_reports:
            duplicate_flags = self._check_duplicate_tampering(
                biomarkers,
                previous_reports,
                current_date
            )
            flags.extend(duplicate_flags)
            fraud_score += len(duplicate_flags) * 30  # Duplicates are highly suspicious
        
        # Rule 3: Check for anomalous risk score (>50% above patient baseline)
        if previous_reports and len(previous_reports) >= 2:
            baseline_risk = sum(r.get("risk_score", 50) for r in previous_reports[-3:]) / min(len(previous_reports), 3)
            current_risk = current_report.get("risk_score", 50)
            
            if current_risk > baseline_risk * 1.5:
                flags.append({
                    "type": "anomalous_risk",
                    "severity": "medium",
                    "description": f"Risk score {current_risk} is {int((current_risk/baseline_risk - 1)*100)}% above patient baseline ({int(baseline_risk)})",
                    "impact": 10
                })
                fraud_score += 10
        
        # Rule 4: Check for impossible value combinations
        combination_flags = self._check_impossible_combinations(biomarkers)
        flags.extend(combination_flags)
        fraud_score += len(combination_flags) * 20
        
        # Cap fraud score at 100
        fraud_score = min(fraud_score, 100)
        
        # Determine if suspicious (threshold: 40)
        is_suspicious = fraud_score >= 40
        
        # Calculate confidence based on number of data points
        confidence = min(100, 50 + (len(previous_reports) * 10 if previous_reports else 0))
        
        logger.info(f"Fraud detection: score={fraud_score}, flags={len(flags)}, suspicious={is_suspicious}")
        
        return {
            "fraud_score": fraud_score,
            "flags": flags,
            "is_suspicious": is_suspicious,
            "confidence": confidence,
            "total_flags": len(flags)
        }
    
    def _check_physiological_changes(
        self,
        current_biomarkers: Dict,
        previous_reports: List[Dict],
        current_date: datetime
    ) -> List[Dict]:
        """Check if biomarker changes exceed physiological limits"""
        flags = []
        
        # Get most recent previous report
        if not previous_reports:
            return flags
        
        # Sort by date
        sorted_reports = sorted(
            previous_reports,
            key=lambda r: datetime.fromisoformat(r.get("report_date", "2000-01-01")),
            reverse=True
        )
        
        previous_report = sorted_reports[0]
        previous_biomarkers = previous_report.get("biomarkers", {})
        previous_date = datetime.fromisoformat(previous_report.get("report_date", "2000-01-01"))
        
        # Calculate time difference
        time_diff = current_date - previous_date
        days_diff = time_diff.days
        
        if days_diff <= 0:
            return flags  # Same day or future date - skip
        
        # Check each biomarker
        for marker_key, rule in self.RULES.items():
            # Try to find marker in current and previous reports
            current_value = self._extract_value(current_biomarkers, marker_key)
            previous_value = self._extract_value(previous_biomarkers, marker_key)
            
            if current_value is None or previous_value is None:
                continue  # Marker not found in both reports
            
            # Calculate change
            change = abs(current_value - previous_value)
            
            # Determine time period and max allowed change
            if "max_change_per_day" in rule:
                max_change = rule["max_change_per_day"] * days_diff
                period = f"{days_diff} day(s)"
            elif "max_change_per_week" in rule:
                weeks = days_diff / 7
                max_change = rule["max_change_per_week"] * weeks
                period = f"{weeks:.1f} week(s)"
            elif "max_change_per_month" in rule:
                months = days_diff / 30
                max_change = rule["max_change_per_month"] * months
                period = f"{months:.1f} month(s)"
            else:
                continue
            
            # Check if change exceeds limit
            if change > max_change:
                flags.append({
                    "type": "impossible_change",
                    "severity": "high",
                    "marker": rule["description"],
                    "description": f"{rule['description']} changed by {change:.1f} {rule['unit']} in {period} (max: {max_change:.1f} {rule['unit']})",
                    "previous_value": f"{previous_value:.1f} {rule['unit']}",
                    "current_value": f"{current_value:.1f} {rule['unit']}",
                    "days_apart": days_diff,
                    "impact": 15
                })
                logger.warning(f"⚠️ Impossible change detected: {rule['description']} changed {change:.1f} in {days_diff} days")
        
        return flags
    
    def _check_duplicate_tampering(
        self,
        current_biomarkers: Dict,
        previous_reports: List[Dict],
        current_date: datetime
    ) -> List[Dict]:
        """Check for same date with different values (duplicate tampering)"""
        flags = []
        
        for prev_report in previous_reports:
            prev_date = datetime.fromisoformat(prev_report.get("report_date", "2000-01-01"))
            
            # Same date?
            if prev_date.date() == current_date.date():
                prev_biomarkers = prev_report.get("biomarkers", {})
                
                # Check if any values differ
                for marker_key in self.RULES.keys():
                    current_value = self._extract_value(current_biomarkers, marker_key)
                    prev_value = self._extract_value(prev_biomarkers, marker_key)
                    
                    if current_value is not None and prev_value is not None:
                        if abs(current_value - prev_value) > 0.1:  # Different values
                            flags.append({
                                "type": "duplicate_tampering",
                                "severity": "critical",
                                "marker": self.RULES[marker_key]["description"],
                                "description": f"Two reports from same date ({current_date.date()}) show different {self.RULES[marker_key]['description']} values",
                                "previous_value": f"{prev_value:.1f}",
                                "current_value": f"{current_value:.1f}",
                                "impact": 30
                            })
                            logger.error(f"🚨 Duplicate tampering detected: Same date, different values for {marker_key}")
        
        return flags
    
    def _check_impossible_combinations(self, biomarkers: Dict) -> List[Dict]:
        """Check for medically impossible value combinations"""
        flags = []
        
        # Example: Very high HbA1c with normal glucose (impossible)
        hba1c = self._extract_value(biomarkers, "hba1c")
        glucose = self._extract_value(biomarkers, "glucose")
        
        if hba1c and glucose:
            if hba1c > 8.0 and glucose < 100:
                flags.append({
                    "type": "impossible_combination",
                    "severity": "high",
                    "description": f"HbA1c {hba1c:.1f}% indicates diabetes but fasting glucose {glucose:.0f} mg/dL is normal (medically inconsistent)",
                    "impact": 20
                })
        
        # Example: Very high LDL with very high HDL (rare combination)
        ldl = self._extract_value(biomarkers, "ldl")
        hdl = self._extract_value(biomarkers, "hdl")
        
        if ldl and hdl:
            if ldl > 160 and hdl > 80:
                flags.append({
                    "type": "unusual_combination",
                    "severity": "medium",
                    "description": f"High LDL ({ldl:.0f} mg/dL) with high HDL ({hdl:.0f} mg/dL) is statistically rare",
                    "impact": 10
                })
        
        return flags
    
    def _extract_value(self, biomarkers: Dict, marker_key: str) -> float:
        """
        Extract numeric value from biomarkers dict.
        Handles various formats: "126 mg/dL", "7.2%", "126", etc.
        """
        # Try exact key match
        if marker_key in biomarkers:
            return self._parse_value(biomarkers[marker_key])
        
        # Try fuzzy match (case-insensitive, partial match)
        marker_key_lower = marker_key.lower().replace("_", " ")
        
        for key, value in biomarkers.items():
            key_lower = key.lower()
            
            # Check for partial matches
            if marker_key_lower in key_lower or key_lower in marker_key_lower:
                return self._parse_value(value)
            
            # Check for common aliases
            aliases = {
                "hba1c": ["glycated", "hemoglobin a1c", "hba1c", "a1c"],
                "glucose": ["blood sugar", "fasting glucose", "fbs", "blood glucose"],
                "cholesterol": ["total cholesterol", "chol"],
                "ldl": ["ldl cholesterol", "ldl-c", "low density"],
                "hdl": ["hdl cholesterol", "hdl-c", "high density"],
                "creatinine": ["serum creatinine", "s.creatinine"],
                "bun": ["blood urea nitrogen", "urea"],
                "systolic_bp": ["systolic", "sbp"],
                "diastolic_bp": ["diastolic", "dbp"]
            }
            
            if marker_key in aliases:
                for alias in aliases[marker_key]:
                    if alias in key_lower:
                        return self._parse_value(value)
        
        return None
    
    def _parse_value(self, value_str: str) -> float:
        """Parse numeric value from string like '126 mg/dL' or '7.2%'"""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        if not isinstance(value_str, str):
            return None
        
        # Extract first number from string
        import re
        match = re.search(r'(\d+\.?\d*)', value_str)
        if match:
            return float(match.group(1))
        
        return None


def get_fraud_detector():
    """Get fraud detector instance"""
    return FraudDetector()

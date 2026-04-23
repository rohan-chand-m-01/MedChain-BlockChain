"""
Test script to verify Gemini is extracting data properly
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from services.gemini_vision import get_gemini_vision

# Sample lab report text
SAMPLE_REPORT = """
LABORATORY REPORT

Patient: Test Patient
Date: 2024-01-15

METABOLIC PANEL:
Glucose (Fasting): 196 mg/dL [Normal: 70-100 mg/dL] HIGH
HbA1c: 7.8% [Normal: <5.7%] HIGH
Cholesterol (Total): 240 mg/dL [Normal: <200 mg/dL] HIGH
LDL Cholesterol: 165 mg/dL [Normal: <100 mg/dL] HIGH
HDL Cholesterol: 38 mg/dL [Normal: >40 mg/dL] LOW
Triglycerides: 210 mg/dL [Normal: <150 mg/dL] HIGH

COMPLETE BLOOD COUNT:
WBC: 11.5 K/uL [Normal: 4.0-11.0 K/uL] HIGH
Hemoglobin: 13.2 g/dL [Normal: 13.5-17.5 g/dL] NORMAL
Platelets: 250 K/uL [Normal: 150-400 K/uL] NORMAL

KIDNEY FUNCTION:
Creatinine: 1.1 mg/dL [Normal: 0.7-1.3 mg/dL] NORMAL
BUN: 18 mg/dL [Normal: 7-20 mg/dL] NORMAL
GFR: 85 mL/min [Normal: >60 mL/min] NORMAL

INTERPRETATION:
Significantly elevated glucose and HbA1c consistent with uncontrolled diabetes mellitus.
Lipid panel shows dyslipidemia with elevated total cholesterol, LDL, and triglycerides.
Recommend urgent endocrinology consultation.
"""

async def test_gemini():
    print("Testing Gemini Vision text analysis...")
    print("=" * 60)
    
    gemini = get_gemini_vision()
    
    if not gemini.is_available():
        print("❌ Gemini not available - check GOOGLE_API_KEY in .env")
        return
    
    print("✓ Gemini client initialized")
    print()
    
    try:
        result = await gemini.analyze_text_report(SAMPLE_REPORT)
        
        print("RESULTS:")
        print("=" * 60)
        print(f"Report Type: {result.get('report_type')}")
        print()
        
        print(f"Biomarkers Extracted: {len(result.get('biomarkers', {}))}")
        for key, value in list(result.get('biomarkers', {}).items())[:5]:
            print(f"  - {key}: {value}")
        if len(result.get('biomarkers', {})) > 5:
            print(f"  ... and {len(result.get('biomarkers', {})) - 5} more")
        print()
        
        print(f"Abnormal Findings: {len(result.get('abnormal_findings', []))}")
        for finding in result.get('abnormal_findings', [])[:3]:
            print(f"  - {finding.get('name')}: {finding.get('value')} (normal: {finding.get('normal')})")
            print(f"    Severity: {finding.get('severity')}")
            print(f"    Explanation: {finding.get('explanation', '')[:100]}...")
        print()
        
        print(f"Conditions: {len(result.get('conditions', []))}")
        for condition in result.get('conditions', [])[:3]:
            print(f"  - {condition}")
        print()
        
        print(f"Specialist: {result.get('specialist')}")
        print(f"Urgency: {result.get('urgency')}")
        print()
        
        print(f"Summary Length: {len(result.get('summary', ''))} chars")
        print(f"Summary Preview: {result.get('summary', '')[:200]}...")
        print()
        
        # Check if data was actually extracted
        if len(result.get('biomarkers', {})) == 0:
            print("❌ FAILED: No biomarkers extracted!")
        elif len(result.get('abnormal_findings', [])) == 0:
            print("⚠️  WARNING: No abnormal findings extracted!")
        else:
            print("✅ SUCCESS: Data extracted properly!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())

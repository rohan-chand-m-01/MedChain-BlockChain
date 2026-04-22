"""
Test MedGemma Gradio API integration
"""
import asyncio
from services.medgemma_gradio import get_medgemma_gradio

async def test_text_analysis():
    """Test text-based medical report analysis"""
    print("=== Testing MedGemma Gradio Text Analysis ===\n")
    
    # Sample lab report text
    sample_report = """
    LABORATORY REPORT
    
    Patient: Test Patient
    Date: 2024-01-15
    
    GLUCOSE, FASTING: 196 mg/dL (Normal: 70-100 mg/dL) HIGH
    HbA1c: 7.8% (Normal: <5.7%) HIGH
    CHOLESTEROL, TOTAL: 245 mg/dL (Normal: <200 mg/dL) HIGH
    LDL CHOLESTEROL: 165 mg/dL (Normal: <100 mg/dL) HIGH
    HDL CHOLESTEROL: 38 mg/dL (Normal: >40 mg/dL) LOW
    TRIGLYCERIDES: 210 mg/dL (Normal: <150 mg/dL) HIGH
    """
    
    try:
        client = get_medgemma_gradio()
        
        if not client.is_available():
            print("❌ MedGemma Gradio client not available")
            return
        
        print("✓ MedGemma Gradio client initialized")
        print("\nAnalyzing sample report...")
        
        result = await client.analyze_report(sample_report)
        
        print("\n=== Analysis Results ===")
        print(f"Report Type: {result.get('report_type')}")
        print(f"Urgency: {result.get('urgency')}")
        print(f"Specialist: {result.get('specialist')}")
        print(f"\nBiomarkers Found: {len(result.get('biomarkers', {}))}")
        print(f"Conditions: {result.get('conditions', [])}")
        print(f"Abnormal Findings: {len(result.get('abnormal_findings', []))}")
        print(f"\nSummary:\n{result.get('summary', 'N/A')[:500]}...")
        
        print("\n✅ Text analysis test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_image_analysis():
    """Test image-based medical report analysis"""
    print("\n\n=== Testing MedGemma Gradio Image Analysis ===\n")
    
    # You would need to provide an actual image file for this test
    print("⚠️ Image analysis test requires an actual medical image file")
    print("Skipping image test for now...")
    
    # Example code for when you have an image:
    # with open("path/to/medical_image.jpg", "rb") as f:
    #     image_bytes = f.read()
    # 
    # client = get_medgemma_gradio()
    # result = await client.analyze_xray_image(image_bytes)
    # print(result)


if __name__ == "__main__":
    print("MedGemma Gradio API Integration Test\n")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_text_analysis())
    asyncio.run(test_image_analysis())
    
    print("\n" + "=" * 50)
    print("All tests completed!")

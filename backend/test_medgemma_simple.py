"""
Simple MedGemma endpoint test
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

print("=== MedGemma Configuration ===")
print(f"Project ID: {os.getenv('GCP_PROJECT_ID')}")
print(f"Location: {os.getenv('GCP_LOCATION')}")
print(f"Endpoint ID: {os.getenv('MEDGEMMA_ENDPOINT_ID')}")
print()

# Try to initialize
try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    
    creds_json = os.getenv("GCP_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION")
    endpoint_id = os.getenv("MEDGEMMA_ENDPOINT_ID")
    
    aiplatform.init(
        project=project_id,
        location=location,
        credentials=credentials
    )
    
    endpoint_name = f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}"
    endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
    
    print(f"✓ Endpoint object created")
    print(f"  Display name: {endpoint.display_name}")
    print(f"  Resource name: {endpoint.resource_name}")
    print()
    
    # Try to get the gca_resource which contains deployment info
    try:
        gca = endpoint.gca_resource
        print(f"✓ GCA resource accessible")
        print(f"  Deployed models count: {len(gca.deployed_models)}")
        
        if len(gca.deployed_models) == 0:
            print("\n⚠️  WARNING: No models deployed to this endpoint!")
            print("   You need to deploy a model to this endpoint first.")
            print("   Go to: Vertex AI > Model Registry > Select MedGemma model > Deploy")
        else:
            for model in gca.deployed_models:
                print(f"\n  Model: {model.display_name}")
                print(f"    Model ID: {model.id}")
                print(f"    Model path: {model.model}")
                
                # Check private endpoints
                if hasattr(model, 'private_endpoints') and model.private_endpoints:
                    pe = model.private_endpoints
                    if hasattr(pe, 'predict_http_uri') and pe.predict_http_uri:
                        print(f"    ✓ Predict URI: {pe.predict_http_uri}")
                    else:
                        print(f"    ✗ No predict URI (endpoint not ready)")
                else:
                    print(f"    ✗ No private endpoints configured")
    except Exception as e:
        print(f"✗ Error accessing GCA resource: {e}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

"""
Check MedGemma endpoint status on Vertex AI
"""
import os
import json
from google.cloud import aiplatform
from google.oauth2 import service_account

# Load credentials from .env
from dotenv import load_dotenv
load_dotenv()

creds_json = os.getenv("GCP_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)
credentials = service_account.Credentials.from_service_account_info(creds_dict)

# Initialize
project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_LOCATION", "asia-southeast1")
endpoint_id = os.getenv("MEDGEMMA_ENDPOINT_ID")

aiplatform.init(
    project=project_id,
    location=location,
    credentials=credentials
)

print(f"Project: {project_id}")
print(f"Location: {location}")
print(f"Endpoint ID: {endpoint_id}")
print()

# Get endpoint
try:
    endpoint_name = f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}"
    endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
    
    print(f"✓ Endpoint found: {endpoint.display_name}")
    print(f"  Resource name: {endpoint.resource_name}")
    print(f"  Create time: {endpoint.create_time}")
    print(f"  Update time: {endpoint.update_time}")
    print()
    
    # Check deployed models
    if hasattr(endpoint, 'gca_resource'):
        gca = endpoint.gca_resource
        print(f"  Deployed models: {len(gca.deployed_models)}")
        
        for i, model in enumerate(gca.deployed_models):
            print(f"\n  Model {i+1}:")
            print(f"    ID: {model.id}")
            print(f"    Model: {model.model}")
            print(f"    Display name: {model.display_name}")
            
            # Check if model has dedicated resources
            if hasattr(model, 'dedicated_resources'):
                dr = model.dedicated_resources
                print(f"    Machine type: {dr.machine_spec.machine_type}")
                print(f"    Min replicas: {dr.min_replica_count}")
                print(f"    Max replicas: {dr.max_replica_count}")
                
                # Check accelerator
                if hasattr(dr.machine_spec, 'accelerator_type') and dr.machine_spec.accelerator_type:
                    print(f"    Accelerator: {dr.machine_spec.accelerator_type}")
                    print(f"    Accelerator count: {dr.machine_spec.accelerator_count}")
            
            # Check private endpoints (this is what causes "DNS is empty" error)
            if hasattr(model, 'private_endpoints'):
                pe = model.private_endpoints
                print(f"    Private endpoints: {pe}")
                if hasattr(pe, 'predict_http_uri'):
                    print(f"    Predict URI: {pe.predict_http_uri}")
                if hasattr(pe, 'health_http_uri'):
                    print(f"    Health URI: {pe.health_http_uri}")
    
    print("\n✓ Endpoint is configured")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

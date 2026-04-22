"""
Test WhatsApp webhook locally
"""
import requests

# Test local backend
local_url = "http://localhost:8000/api/whatsapp/webhook"

# Simulate Twilio WhatsApp message
data = {
    "From": "whatsapp:+1234567890",
    "Body": "Hello test",
    "NumMedia": "0"
}

print("Testing local webhook...")
try:
    response = requests.post(local_url, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test via LocalTunnel
tunnel_url = "https://bitter-toys-relax.loca.lt/api/whatsapp/webhook"
print("\nTesting via LocalTunnel...")
try:
    response = requests.post(tunnel_url, data=data, headers={"Bypass-Tunnel-Reminder": "true"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

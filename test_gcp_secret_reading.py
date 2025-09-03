#!/usr/bin/env python3
"""
Test GCP secret reading to see if newlines are being added
"""

from google.cloud import secretmanager
import os

def test_secret_reading():
    """Test reading secrets from GCP"""
    print("🔍 Testing GCP Secret Reading")
    print("=" * 40)
    
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'romp-family-enterprises')
    
    secrets = ['weatherkit-key-id', 'weatherkit-team-id', 'weatherkit-service-id', 'weatherkit-private-key']
    
    for secret_name in secrets:
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        value = response.payload.data.decode("UTF-8")
        
        print(f"\n📋 Secret: {secret_name}")
        print(f"   Raw Value: '{value}'")
        print(f"   Length: {len(value)}")
        print(f"   Has newline: {'\\n' in value}")
        print(f"   Has carriage return: {'\\r' in value}")
        print(f"   Repr: {repr(value)}")

if __name__ == "__main__":
    test_secret_reading() 
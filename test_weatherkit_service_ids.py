#!/usr/bin/env python3
"""
Test different Service ID formats for WeatherKit
"""

import os
import base64
import jwt
import requests
from datetime import datetime, timedelta

def get_weatherkit_credentials_from_gcp():
    """Get WeatherKit credentials from GCP Secret Manager"""
    try:
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'romp-family-enterprises')
        
        secrets = {}
        secret_names = ['weatherkit-key-id', 'weatherkit-team-id', 'weatherkit-service-id', 'weatherkit-private-key']
        
        for secret_name in secret_names:
            name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secrets[secret_name] = response.payload.data.decode("UTF-8")
        
        return {
            'key_id': secrets['weatherkit-key-id'],
            'team_id': secrets['weatherkit-team-id'],
            'service_id': secrets['weatherkit-service-id'],
            'private_key': secrets['weatherkit-private-key']
        }
    except Exception as e:
        print(f"❌ Error getting WeatherKit credentials from GCP: {e}")
        return None

def test_service_id(credentials, service_id):
    """Test a specific Service ID"""
    try:
        # Decode the base64 private key
        private_key = base64.b64decode(credentials['private_key']).decode('utf-8')
        
        # Create JWT payload
        now = datetime.utcnow()
        payload = {
            'iss': credentials['team_id'],
            'iat': now,
            'exp': now + timedelta(hours=1),
            'sub': service_id
        }
        
        # Create JWT headers
        headers = {
            'kid': credentials['key_id'],
            'alg': 'ES256'
        }
        
        # Generate JWT token
        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        
        # Test WeatherKit API
        weather_url = "https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(weather_url, headers=headers)
        
        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_different_service_ids():
    """Test different Service ID formats"""
    print("🌤️  Testing Different Service ID Formats for WeatherKit")
    print("=" * 60)
    
    # Get credentials from GCP
    print("🔍 Reading credentials from GCP Secret Manager...")
    credentials = get_weatherkit_credentials_from_gcp()
    
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return
    
    print("✅ Successfully retrieved credentials from GCP")
    print(f"   Key ID: {credentials['key_id']}")
    print(f"   Team ID: {credentials['team_id']}")
    print(f"   Current Service ID: {credentials['service_id']}")
    
    # Test different Service ID formats
    service_ids_to_test = [
        credentials['service_id'],  # Current one
        f"{credentials['service_id']}.weatherkit",  # With .weatherkit suffix
        f"{credentials['service_id']}.weather",  # With .weather suffix
        "com.romp.its2hot.weatherkit",  # Explicit with .weatherkit
        "com.romp.its2hot.weather",  # Explicit with .weather
        "com.romp.its2hot",  # Just the bundle ID
    ]
    
    print("\n🧪 Testing different Service ID formats...")
    
    for service_id in service_ids_to_test:
        print(f"\nTesting: {service_id}")
        success, message = test_service_id(credentials, service_id)
        
        if success:
            print(f"✅ SUCCESS with Service ID: {service_id}")
            print("🎉 This is the correct Service ID format!")
            return service_id
        else:
            print(f"❌ Failed: {message}")
    
    print("\n❌ None of the Service ID formats worked.")
    print("This suggests the issue might be:")
    print("1. The key doesn't have WeatherKit capability enabled")
    print("2. The app doesn't have WeatherKit capability enabled")
    print("3. The Team ID might be incorrect")
    
    return None

if __name__ == "__main__":
    working_service_id = test_different_service_ids()
    if working_service_id:
        print(f"\n✅ Use this Service ID: {working_service_id}")
        print("Update your GCP secret with this value.") 
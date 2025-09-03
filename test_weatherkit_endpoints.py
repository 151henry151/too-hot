#!/usr/bin/env python3
"""
Test different WeatherKit endpoints to get more specific error messages
"""

import os
import base64
import jwt
import requests
import json
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
            # Strip newlines that the GCP client adds
            secrets[secret_name] = response.payload.data.decode("UTF-8").strip()
        
        return {
            'key_id': secrets['weatherkit-key-id'],
            'team_id': secrets['weatherkit-team-id'],
            'service_id': secrets['weatherkit-service-id'],
            'private_key': secrets['weatherkit-private-key']
        }
    except Exception as e:
        print(f"❌ Error getting WeatherKit credentials from GCP: {e}")
        return None

def test_weatherkit_endpoint(credentials, endpoint_url, description):
    """Test a specific WeatherKit endpoint"""
    try:
        # Decode private key
        private_key = base64.b64decode(credentials['private_key']).decode('utf-8')
        
        # Create JWT payload
        now = datetime.utcnow()
        payload = {
            'iss': credentials['team_id'],
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=1)).timestamp()),
            'sub': credentials['service_id']
        }
        
        # Create JWT headers
        headers = {
            'kid': credentials['key_id'],
            'alg': 'ES256',
            'typ': 'JWT'
        }
        
        # Generate JWT token
        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        
        # Test WeatherKit API
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'User-Agent': 'TooHotApp/1.0'
        }
        
        print(f"\n🌡️  Testing: {description}")
        print(f"   URL: {endpoint_url}")
        
        response = requests.get(endpoint_url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_weatherkit_endpoints():
    """Test various WeatherKit endpoints"""
    print("🔍 Testing Different WeatherKit Endpoints")
    print("=" * 50)
    
    # Get credentials
    credentials = get_weatherkit_credentials_from_gcp()
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return
    
    print(f"✅ Using Key ID: {credentials['key_id']}")
    print(f"✅ Using Team ID: {credentials['team_id']}")
    print(f"✅ Using Service ID: {credentials['service_id']}")
    
    # Test different endpoints
    endpoints = [
        ("https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060", "Daily Forecast (New York)"),
        ("https://weatherkit.apple.com/v1/weather/en/37.7749/-122.4194", "Daily Forecast (San Francisco)"),
        ("https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060/current", "Current Weather (New York)"),
        ("https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060/hourly", "Hourly Forecast (New York)"),
        ("https://weatherkit.apple.com/v1/availability", "Availability Check"),
    ]
    
    success_count = 0
    for endpoint_url, description in endpoints:
        if test_weatherkit_endpoint(credentials, endpoint_url, description):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(endpoints)} endpoints worked")
    
    if success_count == 0:
        print("\n💡 All endpoints failed. This suggests:")
        print("1. The key doesn't have WeatherKit capability")
        print("2. The app doesn't have WeatherKit capability")
        print("3. The Team ID is incorrect")
        print("4. There's a propagation delay (try again in a few minutes)")

if __name__ == "__main__":
    test_weatherkit_endpoints() 
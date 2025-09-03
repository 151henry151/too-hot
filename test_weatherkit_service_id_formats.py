#!/usr/bin/env python3
"""
Test different Service ID formats with WeatherKit
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

def test_service_id_format(credentials, service_id):
    """Test a specific Service ID format"""
    try:
        # Decode private key
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
            'Accept': 'application/json',
            'User-Agent': 'TooHotApp/1.0'
        }
        
        response = requests.get(weather_url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS with Service ID: {service_id}")
            return True
        else:
            print(f"❌ Failed with Service ID: {service_id} - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Service ID {service_id}: {e}")
        return False

def test_service_id_formats():
    """Test various Service ID formats"""
    print("🔍 Testing Different Service ID Formats")
    print("=" * 50)
    
    # Get base credentials
    credentials = get_weatherkit_credentials_from_gcp()
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return
    
    print(f"✅ Using Key ID: {credentials['key_id']}")
    print(f"✅ Using Team ID: {credentials['team_id']}")
    print(f"✅ Using Private Key Length: {len(credentials['private_key'])} characters")
    
    # Test different Service ID formats
    service_id_formats = [
        credentials['service_id'],  # Original: com.romp.its2hot
        f"{credentials['service_id']}.weatherkit",  # com.romp.its2hot.weatherkit
        f"{credentials['service_id']}.weather",  # com.romp.its2hot.weather
        credentials['service_id'].replace('.', ''),  # comrompits2hot
        credentials['team_id'],  # Use Team ID as Service ID
        f"{credentials['team_id']}.weatherkit",  # Team ID + .weatherkit
        f"{credentials['team_id']}.weather",  # Team ID + .weather
    ]
    
    print(f"\n🧪 Testing {len(service_id_formats)} Service ID formats...")
    
    success_count = 0
    for service_id in service_id_formats:
        if test_service_id_format(credentials, service_id):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(service_id_formats)} formats worked")
    
    if success_count == 0:
        print("\n💡 All Service ID formats failed. This suggests:")
        print("1. The Apple Developer Key doesn't have WeatherKit capability")
        print("2. The app doesn't have WeatherKit capability")
        print("3. The Team ID is incorrect")
        print("4. The private key is corrupted")

if __name__ == "__main__":
    test_service_id_formats() 
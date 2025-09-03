#!/usr/bin/env python3
"""
Test script to verify Apple WeatherKit credentials from GCP secrets
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

def test_weatherkit_credentials():
    """Test WeatherKit credentials from GCP secrets"""
    print("🌤️  Testing Apple WeatherKit Credentials from GCP Secrets")
    print("=" * 60)
    
    # Get credentials from GCP
    print("🔍 Reading credentials from GCP Secret Manager...")
    credentials = get_weatherkit_credentials_from_gcp()
    
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return False
    
    print("✅ Successfully retrieved credentials from GCP")
    print(f"   Key ID: {credentials['key_id']}")
    print(f"   Team ID: {credentials['team_id']}")
    print(f"   Service ID: {credentials['service_id']}")
    print(f"   Private Key: {credentials['private_key'][:8]}...{credentials['private_key'][-4:] if len(credentials['private_key']) > 12 else '***'}")
    
    # Validate base64
    try:
        private_key = base64.b64decode(credentials['private_key']).decode('utf-8')
        print("✅ Base64 validation successful")
    except Exception as e:
        print(f"❌ Invalid base64 encoding: {e}")
        return False
    
    # Test JWT generation
    try:
        print("\n🔐 Testing JWT generation...")
        
        # Create JWT payload
        now = datetime.utcnow()
        payload = {
            'iss': credentials['team_id'],
            'iat': now,
            'exp': now + timedelta(hours=1),
            'sub': credentials['service_id']
        }
        
        # Create JWT headers
        headers = {
            'kid': credentials['key_id'],
            'alg': 'ES256'
        }
        
        # Generate JWT token
        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        print("✅ JWT token generated successfully")
        
        # Test WeatherKit API
        print("\n🌡️  Testing WeatherKit API...")
        weather_url = "https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(weather_url, headers=headers)
        
        if response.status_code == 200:
            weather_data = response.json()
            print("✅ WeatherKit API successful!")
            print(f"Response status: {response.status_code}")
            
            # Check if we got weather data
            if 'forecastDaily' in weather_data:
                print("✅ Forecast data available")
                if 'days' in weather_data['forecastDaily'] and len(weather_data['forecastDaily']['days']) > 0:
                    today = weather_data['forecastDaily']['days'][0]
                    high_temp = today.get('temperatureMax', 'N/A')
                    print(f"✅ Today's high temperature: {high_temp}°F")
                    return True
                else:
                    print("⚠️  No daily forecast data found")
                    return False
            else:
                print("⚠️  No forecast data in response")
                return False
        else:
            print(f"❌ WeatherKit API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WeatherKit: {e}")
        return False

if __name__ == "__main__":
    success = test_weatherkit_credentials()
    if success:
        print("\n🎉 All WeatherKit credentials from GCP are working correctly!")
    else:
        print("\n❌ WeatherKit credentials from GCP need to be fixed.") 
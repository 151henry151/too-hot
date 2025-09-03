#!/usr/bin/env python3
"""
Test WeatherKit authentication using Apple's exact documentation format
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

def test_weatherkit_apple_format():
    """Test WeatherKit using Apple's exact documentation format"""
    print("🍎 Testing WeatherKit with Apple's Exact Format")
    print("=" * 55)
    
    # Get credentials
    credentials = get_weatherkit_credentials_from_gcp()
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return
    
    print(f"✅ Key ID: {credentials['key_id']}")
    print(f"✅ Team ID: {credentials['team_id']}")
    print(f"✅ Service ID: {credentials['service_id']}")
    print(f"✅ Private Key Length: {len(credentials['private_key'])} characters")
    
    try:
        # Decode private key
        private_key = base64.b64decode(credentials['private_key']).decode('utf-8')
        print(f"✅ Private Key Content Length: {len(private_key)} characters")
        print(f"✅ Private Key Starts With: {private_key[:50]}...")
        
        # Create JWT payload exactly as per Apple's documentation
        now = datetime.utcnow()
        payload = {
            'iss': credentials['team_id'],
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=1)).timestamp()),
            'sub': credentials['service_id']
        }
        
        # Create JWT headers exactly as per Apple's documentation
        headers = {
            'kid': credentials['key_id'],
            'alg': 'ES256',
            'typ': 'JWT'
        }
        
        print(f"\n🔐 JWT Payload: {json.dumps(payload, indent=2)}")
        print(f"🔐 JWT Headers: {json.dumps(headers, indent=2)}")
        
        # Generate JWT token
        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        print(f"✅ JWT Token Generated (Length: {len(token)} characters)")
        print(f"✅ JWT Token Starts With: {token[:50]}...")
        
        # Decode and verify the token structure
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"✅ Decoded Token Payload: {json.dumps(decoded, indent=2)}")
        
        # Test WeatherKit API with exact Apple format
        weather_url = "https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'User-Agent': 'TooHotApp/1.0'
        }
        
        print(f"\n🌡️  Testing WeatherKit API...")
        print(f"   URL: {weather_url}")
        print(f"   Authorization: Bearer {token[:50]}...")
        
        response = requests.get(weather_url, headers=headers)
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            weather_data = response.json()
            print("✅ WeatherKit API successful!")
            print(f"   Response Keys: {list(weather_data.keys())}")
            
            if 'forecastDaily' in weather_data:
                print("✅ Forecast data available")
                return True
            else:
                print("⚠️  No forecast data in response")
                print(f"   Response: {json.dumps(weather_data, indent=2)}")
                return False
        else:
            print(f"❌ WeatherKit API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to parse error response
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Error: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing WeatherKit API: {e}")
        return False

if __name__ == "__main__":
    success = test_weatherkit_apple_format()
    if success:
        print("\n🎉 WeatherKit authentication is working!")
    else:
        print("\n❌ WeatherKit authentication failed.")
        print("\n💡 Next steps:")
        print("1. Verify the key has WeatherKit capability in Apple Developer portal")
        print("2. Verify the app has WeatherKit capability in Apple Developer portal")
        print("3. Check if the Team ID is correct")
        print("4. Consider creating a new key if the issue persists") 
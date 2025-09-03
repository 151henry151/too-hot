#!/usr/bin/env python3
"""
Comprehensive WeatherKit setup verification
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

def verify_weatherkit_setup():
    """Comprehensive WeatherKit setup verification"""
    print("🔍 Comprehensive WeatherKit Setup Verification")
    print("=" * 60)
    
    # Step 1: Get credentials from GCP
    print("\n📋 Step 1: Reading credentials from GCP...")
    credentials = get_weatherkit_credentials_from_gcp()
    if not credentials:
        print("❌ Failed to get credentials from GCP")
        return False
    
    print("✅ Credentials retrieved successfully")
    print(f"   Key ID: {credentials['key_id']}")
    print(f"   Team ID: {credentials['team_id']}")
    print(f"   Service ID: {credentials['service_id']}")
    print(f"   Private Key Length: {len(credentials['private_key'])} characters")
    
    # Step 2: Verify private key format
    print("\n🔐 Step 2: Verifying private key format...")
    try:
        private_key = base64.b64decode(credentials['private_key']).decode('utf-8')
        print("✅ Base64 decoding successful")
        print(f"   Private Key Content Length: {len(private_key)} characters")
        print(f"   Private Key Starts With: {private_key[:50]}...")
        print(f"   Private Key Ends With: {private_key[-50:]}...")
        
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("❌ Private key doesn't start with expected header")
            return False
        if not private_key.endswith('-----END PRIVATE KEY-----'):
            print("❌ Private key doesn't end with expected footer")
            return False
        print("✅ Private key format is correct")
        
    except Exception as e:
        print(f"❌ Private key verification failed: {e}")
        return False
    
    # Step 3: Generate and verify JWT token
    print("\n🎫 Step 3: Generating and verifying JWT token...")
    try:
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
        
        print(f"   JWT Payload: {json.dumps(payload, indent=2)}")
        print(f"   JWT Headers: {json.dumps(headers, indent=2)}")
        
        # Generate JWT token
        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        print(f"✅ JWT token generated successfully")
        print(f"   Token Length: {len(token)} characters")
        print(f"   Token Starts With: {token[:50]}...")
        
        # Decode and verify the token structure
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"✅ JWT token structure is valid")
        print(f"   Decoded Payload: {json.dumps(decoded, indent=2)}")
        
        # Verify all required fields are present
        required_fields = ['iss', 'iat', 'exp', 'sub']
        for field in required_fields:
            if field not in decoded:
                print(f"❌ Missing required field: {field}")
                return False
        print("✅ All required JWT fields are present")
        
    except Exception as e:
        print(f"❌ JWT generation failed: {e}")
        return False
    
    # Step 4: Test WeatherKit API with detailed error analysis
    print("\n🌡️  Step 4: Testing WeatherKit API...")
    try:
        weather_url = "https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'User-Agent': 'TooHotApp/1.0'
        }
        
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
            
            # Additional error analysis
            if response.status_code == 401:
                print("\n🔍 401 Error Analysis:")
                print("   - This usually means authentication failed")
                print("   - Possible causes:")
                print("     1. Key doesn't have WeatherKit capability")
                print("     2. App doesn't have WeatherKit capability")
                print("     3. Team ID is incorrect")
                print("     4. Service ID is incorrect")
                print("     5. Private key is corrupted")
                print("     6. Changes haven't propagated yet")
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing WeatherKit API: {e}")
        return False

if __name__ == "__main__":
    success = verify_weatherkit_setup()
    if success:
        print("\n🎉 WeatherKit setup is working correctly!")
    else:
        print("\n❌ WeatherKit setup needs to be fixed.")
        print("\n💡 Next steps:")
        print("1. Double-check the key's WeatherKit capability in Apple Developer portal")
        print("2. Double-check the app's WeatherKit capability in Apple Developer portal")
        print("3. Verify the Team ID is correct")
        print("4. Consider creating a new key if the issue persists") 
#!/usr/bin/env python3
"""
Test script to verify Apple WeatherKit credentials
"""

import os
import base64
import jwt
import requests
from datetime import datetime, timedelta

def test_weatherkit_credentials():
    """Test WeatherKit credentials"""
    print("🌤️  Testing Apple WeatherKit Credentials")
    print("=" * 50)
    
    # Get credentials from user
    print("Please provide your WeatherKit credentials:")
    
    key_id = input("Key ID (e.g., S64QUPN2H9): ").strip()
    team_id = input("Team ID: ").strip()
    service_id = input("Service ID: ").strip()
    
    print("\n📄 Private Key:")
    print("If you have the .p8 file, convert it to base64:")
    print("   base64 -i AuthKey_S64QUPN2H9.p8 | tr -d '\n'")
    print()
    
    private_key_base64 = input("Base64 encoded private key: ").strip()
    
    if not all([key_id, team_id, service_id, private_key_base64]):
        print("❌ All credentials are required")
        return False
    
    # Validate base64
    try:
        private_key = base64.b64decode(private_key_base64).decode('utf-8')
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
            'iss': team_id,
            'iat': now,
            'exp': now + timedelta(hours=1),
            'sub': service_id
        }
        
        # Create JWT headers
        headers = {
            'kid': key_id,
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
        print("\n🎉 All WeatherKit credentials are working correctly!")
    else:
        print("\n❌ WeatherKit credentials need to be fixed.") 
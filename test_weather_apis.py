#!/usr/bin/env python3
"""
Test script for weather APIs
Tests both The Weather Company API and WeatherAPI.com
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_weatherkit_api():
    """Test Apple WeatherKit REST API (same source as iOS weather app)"""
    key_id = os.getenv('WEATHERKIT_KEY_ID')
    team_id = os.getenv('WEATHERKIT_TEAM_ID')
    service_id = os.getenv('WEATHERKIT_SERVICE_ID')
    private_key = os.getenv('WEATHERKIT_PRIVATE_KEY')
    
    if not all([key_id, team_id, service_id, private_key]):
        print("❌ WeatherKit credentials not configured")
        return False
    
    try:
        # Import the JWT generation function from app.py
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # We'll test JWT generation first
        print("🔐 Testing WeatherKit JWT generation...")
        
        # Test JWT generation
        import jwt
        import base64
        from datetime import datetime, timedelta
        
        # Decode the base64 private key
        private_key_decoded = base64.b64decode(private_key).decode('utf-8')
        
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
        token = jwt.encode(payload, private_key_decoded, algorithm='ES256', headers=headers)
        print("✅ JWT token generated successfully")
        
        # Test weather data retrieval
        print("🌡️  Testing WeatherKit API forecast...")
        weather_url = "https://weatherkit.apple.com/v1/weather/en/40.7128/-74.0060"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(weather_url, headers=headers)
        
        if response.status_code == 200:
            weather_data = response.json()
            if 'forecastDaily' in weather_data and 'days' in weather_data['forecastDaily']:
                today_forecast = weather_data['forecastDaily']['days'][0]
                high_temp = today_forecast.get('temperatureMax', 'N/A')
                print(f"✅ WeatherKit API successful: High temp {high_temp}°F")
                return True
            else:
                print("❌ No forecast data available")
                return False
        else:
            print(f"❌ WeatherKit API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WeatherKit API: {e}")
        return False

def test_weatherapi():
    """Test WeatherAPI.com (for historical data)"""
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("❌ WEATHER_API_KEY not configured")
        return False
    
    try:
        print("🌡️  Testing WeatherAPI.com forecast...")
        forecast_url = "http://api.weatherapi.com/v1/forecast.json"
        forecast_params = {
            'key': api_key,
            'q': 'New York',
            'days': 1,
            'aqi': 'no',
            'alerts': 'no'
        }
        
        response = requests.get(forecast_url, params=forecast_params)
        
        if response.status_code == 200:
            data = response.json()
            current_temp = data['forecast']['forecastday'][0]['day']['maxtemp_f']
            print(f"✅ WeatherAPI.com forecast successful: High temp {current_temp}°F")
            return True
        else:
            print(f"❌ WeatherAPI.com error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WeatherAPI.com: {e}")
        return False

def main():
    print("🌤️  Weather API Test Suite")
    print("=" * 40)
    
    # Test Apple WeatherKit REST API
    print("\n1. Testing Apple WeatherKit REST API (iOS weather app source)...")
    weatherkit_ok = test_weatherkit_api()
    
    # Test WeatherAPI.com
    print("\n2. Testing WeatherAPI.com (historical data)...")
    weatherapi_ok = test_weatherapi()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Apple WeatherKit API: {'✅ Working' if weatherkit_ok else '❌ Failed'}")
    print(f"   WeatherAPI.com: {'✅ Working' if weatherapi_ok else '❌ Failed'}")
    
    if weatherkit_ok and weatherapi_ok:
        print("\n🎉 All weather APIs are working correctly!")
        print("   - Forecast data will come from Apple WeatherKit REST API")
        print("   - Historical data will come from WeatherAPI.com")
    elif weatherapi_ok:
        print("\n⚠️  WeatherAPI.com is working, but Apple WeatherKit API failed.")
        print("   - Forecast data will fall back to WeatherAPI.com")
        print("   - Historical data will come from WeatherAPI.com")
    else:
        print("\n❌ Weather APIs are not working. Please check your configuration.")

if __name__ == "__main__":
    main() 
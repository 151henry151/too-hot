#!/usr/bin/env python3
"""
Simple script to set up Apple WeatherKit REST API credentials
"""

import os
import base64

def set_weatherkit_credentials():
    """Set up Apple WeatherKit REST API credentials in .env file"""
    print("🌤️  Apple WeatherKit REST API Setup (iOS Weather App Source)")
    print("=" * 70)
    print("This will configure the same data source as the iOS weather app.")
    print()
    print("📋 Prerequisites:")
    print("1. Apple Developer Account (https://developer.apple.com)")
    print("2. Access to Certificates, Identifiers & Profiles")
    print("3. WeatherKit capability enabled")
    print()
    print("🔑 Setup Steps:")
    print("1. Go to https://developer.apple.com/account/resources/authkeys/list")
    print("2. Click '+' to create a new key")
    print("3. Name it 'WeatherKit API' and enable WeatherKit capability")
    print("4. Download the .p8 file")
    print("5. Convert the .p8 file to base64 (see instructions below)")
    print()
    
    # Get credentials
    key_id = input("Enter your WeatherKit Key ID: ").strip()
    if not key_id:
        print("❌ Key ID is required")
        return
    
    team_id = input("Enter your Apple Team ID: ").strip()
    if not team_id:
        print("❌ Team ID is required")
        return
    
    service_id = input("Enter your WeatherKit Service ID: ").strip()
    if not service_id:
        print("❌ Service ID is required")
        return
    
    print("\n📄 Private Key Setup:")
    print("To convert your .p8 file to base64, run this command:")
    print("   base64 -i AuthKey_XXXXXXXXXX.p8 | tr -d '\n'")
    print("(Replace XXXXXXXX with your actual Key ID)")
    print()
    
    private_key = input("Enter your base64 encoded private key: ").strip()
    if not private_key:
        print("❌ Private key is required")
        return
    
    # Validate base64
    try:
        base64.b64decode(private_key)
    except Exception:
        print("❌ Invalid base64 encoding. Please check your private key.")
        return
    
    # Read existing .env file if it exists
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update or add the credentials
    lines = env_content.split('\n')
    updated_lines = []
    
    # Track which credentials we've updated
    updated = {'key_id': False, 'team_id': False, 'service_id': False, 'private_key': False}
    
    for line in lines:
        if line.startswith('WEATHERKIT_KEY_ID='):
            updated_lines.append(f'WEATHERKIT_KEY_ID={key_id}')
            updated['key_id'] = True
        elif line.startswith('WEATHERKIT_TEAM_ID='):
            updated_lines.append(f'WEATHERKIT_TEAM_ID={team_id}')
            updated['team_id'] = True
        elif line.startswith('WEATHERKIT_SERVICE_ID='):
            updated_lines.append(f'WEATHERKIT_SERVICE_ID={service_id}')
            updated['service_id'] = True
        elif line.startswith('WEATHERKIT_PRIVATE_KEY='):
            updated_lines.append(f'WEATHERKIT_PRIVATE_KEY={private_key}')
            updated['private_key'] = True
        else:
            updated_lines.append(line)
    
    # Add any missing credentials
    if not updated['key_id']:
        updated_lines.append(f'WEATHERKIT_KEY_ID={key_id}')
    if not updated['team_id']:
        updated_lines.append(f'WEATHERKIT_TEAM_ID={team_id}')
    if not updated['service_id']:
        updated_lines.append(f'WEATHERKIT_SERVICE_ID={service_id}')
    if not updated['private_key']:
        updated_lines.append(f'WEATHERKIT_PRIVATE_KEY={private_key}')
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ WeatherKit credentials saved to .env file")
    print(f"   Key ID: {key_id}")
    print(f"   Team ID: {team_id}")
    print(f"   Service ID: {service_id}")
    print(f"   Private Key: {private_key[:8]}...{private_key[-4:] if len(private_key) > 12 else '***'}")
    print()
    print("🚀 The app will now use Apple WeatherKit REST API for forecast data")
    print("   (exact same source as the iOS weather app)")
    print()
    print("📝 Note: Historical data will still use WeatherAPI.com")
    print()
    print("🧪 Test the setup:")
    print("   python test_weather_apis.py")

if __name__ == "__main__":
    set_weatherkit_credentials() 
#!/usr/bin/env python3
"""
Simple script to set the WeatherAPI key
"""

import os

def set_weather_api_key():
    """Set the WeatherAPI key in .env file"""
    print("🌤️  WeatherAPI.com API Key Setup")
    print("=" * 40)
    print("Get your free API key from: https://www.weatherapi.com/")
    print("1. Go to https://www.weatherapi.com/")
    print("2. Sign up for a free account")
    print("3. Copy your API key from the dashboard")
    print()
    
    api_key = input("Enter your WeatherAPI.com API key: ").strip()
    
    if not api_key:
        print("❌ API key is required")
        return
    
    # Read existing .env file if it exists
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update or add the API key
    lines = env_content.split('\n')
    updated_lines = []
    api_key_found = False
    
    for line in lines:
        if line.startswith('WEATHER_API_KEY='):
            updated_lines.append(f'WEATHER_API_KEY={api_key}')
            api_key_found = True
        else:
            updated_lines.append(line)
    
    if not api_key_found:
        updated_lines.append(f'WEATHER_API_KEY={api_key}')
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ WeatherAPI key saved to .env file")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    print()
    print("🚀 You can now start the application:")
    print("   source venv/bin/activate")
    print("   python app.py")

if __name__ == "__main__":
    set_weather_api_key() 
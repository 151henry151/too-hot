#!/usr/bin/env python3
"""
Setup script for Too Hot Temperature Alert Service
Helps configure environment variables
"""

import os
import getpass

def setup_environment():
    """Interactive setup for environment variables"""
    print("🌡️  Too Hot Temperature Alert Service - Environment Setup")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists. This will overwrite it.")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📧 Email Configuration (Gmail)")
    print("You'll need to:")
    print("1. Enable 2-factor authentication on your Google account")
    print("2. Generate an App Password at: https://myaccount.google.com/apppasswords")
    print("3. Use that App Password (not your regular password)")
    
    email = input("\nEnter your Gmail address: ").strip()
    if not email or '@' not in email:
        print("❌ Invalid email address")
        return
    
    password = getpass.getpass("Enter your Gmail App Password: ").strip()
    if not password:
        print("❌ Password is required")
        return
    
    print("\n🌤️  Weather API Configuration")
    print("Get your free API key from: https://www.weatherapi.com/")
    print("1. Sign up for a free account")
    print("2. Copy your API key")
    
    weather_key = input("\nEnter your Weather API key: ").strip()
    if not weather_key:
        print("⚠️  No weather API key provided. Temperature checking will be limited.")
        weather_key = "your-weather-api-key"
    
    # Generate a secret key
    import secrets
    secret_key = secrets.token_hex(32)
    
    # Create .env file
    env_content = f"""# Email Configuration (Gmail)
MAIL_USERNAME={email}
MAIL_PASSWORD={password}

# Weather API Configuration
WEATHER_API_KEY={weather_key}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# Database Configuration (for future use)
DATABASE_URL=sqlite:///too_hot.db
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ Environment configuration saved to .env")
        print("\n📋 Configuration Summary:")
        print(f"   Email: {email}")
        print(f"   Weather API: {'Configured' if weather_key != 'your-weather-api-key' else 'Not configured'}")
        print(f"   Secret Key: Generated")
        
        print("\n🚀 You can now start the application:")
        print("   source venv/bin/activate")
        print("   python app.py")
        
    except Exception as e:
        print(f"❌ Error saving .env file: {e}")

if __name__ == "__main__":
    setup_environment() 
#!/usr/bin/env python3
"""
Script to set up PayPal credentials for local development
"""

import os
import subprocess

def setup_local_paypal():
    """Set up PayPal credentials for local development"""
    
    print("🔧 Setting up PayPal credentials for local development...")
    print("\n📝 You need PayPal API credentials from the PayPal Developer Dashboard:")
    print("1. Go to https://developer.paypal.com/")
    print("2. Create a developer account if you don't have one")
    print("3. Create a new app to get Client ID and Client Secret")
    print("4. Use SANDBOX mode for testing (not live mode)")
    print("\n")
    
    # Get credentials from user
    client_id = input("Enter your PayPal Client ID: ").strip()
    client_secret = input("Enter your PayPal Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required.")
        return False
    
    # Create .env file if it doesn't exist
    env_file = ".env"
    env_content = f"""# PayPal Configuration (Local Development)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID={client_id}
PAYPAL_CLIENT_SECRET={client_secret}

# Other environment variables (if needed)
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ PayPal credentials saved to {env_file}")
    print("🔒 This file should be in your .gitignore (it already is)")
    print("\n📝 Next steps:")
    print("1. Restart your Flask app: python app.py")
    print("2. Test the payment flow in your local development environment")
    print("3. For production, use Google Cloud Secret Manager with live mode")
    
    return True

if __name__ == "__main__":
    setup_local_paypal() 
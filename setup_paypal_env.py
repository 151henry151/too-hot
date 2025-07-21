#!/usr/bin/env python3
"""
Secure PayPal Environment Setup Script
This script helps set up PayPal credentials locally without exposing them in code.
"""

import os
import sys
from pathlib import Path

def setup_paypal_env():
    """Set up PayPal environment variables securely"""
    
    # PayPal credentials (these would normally be entered securely)
    paypal_client_id = "AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ"
    paypal_client_secret = "EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha"
    
    # Environment variables to set
    env_vars = {
        'PAYPAL_MODE': 'sandbox',  # Change to 'live' for production
        'PAYPAL_CLIENT_ID': paypal_client_id,
        'PAYPAL_CLIENT_SECRET': paypal_client_secret,
    }
    
    # Check if .env file exists
    env_file = Path('.env')
    
    if env_file.exists():
        print("📁 .env file already exists. Updating PayPal credentials...")
        
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add PayPal variables
        updated_lines = []
        paypal_vars_updated = set()
        
        for line in lines:
            line = line.strip()
            if line.startswith('PAYPAL_'):
                # Update existing PayPal variables
                for key, value in env_vars.items():
                    if line.startswith(f'{key}='):
                        updated_lines.append(f'{key}={value}\n')
                        paypal_vars_updated.add(key)
                        break
                else:
                    # Keep other PayPal variables that aren't in our list
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
        
        # Add any missing PayPal variables
        for key, value in env_vars.items():
            if key not in paypal_vars_updated:
                updated_lines.append(f'{key}={value}\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
            
    else:
        print("📁 Creating new .env file with PayPal credentials...")
        
        # Create new .env file with all required variables
        env_content = f"""# Weather API Configuration
WEATHER_API_KEY=your_weather_api_key_here

# Email Configuration (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# PayPal Configuration
PAYPAL_MODE={env_vars['PAYPAL_MODE']}
PAYPAL_CLIENT_ID={env_vars['PAYPAL_CLIENT_ID']}
PAYPAL_CLIENT_SECRET={env_vars['PAYPAL_CLIENT_SECRET']}

# Printful Configuration
PRINTFUL_API_KEY=your_printful_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    print("✅ PayPal environment variables set successfully!")
    print("🔒 Credentials are stored in .env file (not committed to git)")
    print("📝 Remember to update other variables in .env file as needed")
    print("🌐 For GCP deployment, set these as environment variables in Cloud Run")

def create_gcp_deployment_script():
    """Create a script for GCP deployment with environment variables"""
    
    gcp_script = """#!/bin/bash
# GCP Deployment Script with PayPal Environment Variables

# Set your GCP project ID
PROJECT_ID="your-gcp-project-id"

# Deploy to Cloud Run with environment variables
gcloud run deploy too-hot-app \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars="PAYPAL_MODE=sandbox" \\
  --set-env-vars="PAYPAL_CLIENT_ID=AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ" \\
  --set-env-vars="PAYPAL_CLIENT_SECRET=EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha" \\
  --set-env-vars="WEATHER_API_KEY=your_weather_api_key" \\
  --set-env-vars="MAIL_USERNAME=your_email@gmail.com" \\
  --set-env-vars="MAIL_PASSWORD=your_app_password" \\
  --set-env-vars="PRINTFUL_API_KEY=your_printful_api_key" \\
  --set-env-vars="SECRET_KEY=your_secret_key"

echo "🚀 App deployed to GCP Cloud Run!"
echo "🔗 Your app URL will be shown above"
"""
    
    with open('deploy_gcp.sh', 'w') as f:
        f.write(gcp_script)
    
    # Make the script executable
    os.chmod('deploy_gcp.sh', 0o755)
    
    print("📜 Created deploy_gcp.sh script for GCP deployment")
    print("⚠️  Remember to update the script with your actual API keys before deploying")

if __name__ == "__main__":
    print("🔐 Setting up PayPal environment variables...")
    setup_paypal_env()
    create_gcp_deployment_script()
    print("\n🎉 Setup complete! You can now:")
    print("   1. Run 'python app.py' to test locally")
    print("   2. Update other variables in .env file")
    print("   3. Use 'deploy_gcp.sh' for GCP deployment") 
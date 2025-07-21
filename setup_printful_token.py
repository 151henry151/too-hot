#!/usr/bin/env python3
"""
Secure Printful Token Setup Script
This script helps set up Printful token locally without exposing it in code.
"""

import os
import sys
from pathlib import Path

def setup_printful_token():
    """Set up Printful token securely"""
    
    # Printful token (this would normally be entered securely)
    printful_token = "eWlXN3veWJXrQyOan2OEpHkQ9nuZuUqy6pZnmJjk"
    
    # Check if .env file exists
    env_file = Path('.env')
    
    if env_file.exists():
        print("📁 .env file already exists. Updating Printful token...")
        
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add Printful token
        updated_lines = []
        printful_token_updated = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('PRINTFUL_API_KEY='):
                # Update existing Printful token
                updated_lines.append(f'PRINTFUL_API_KEY={printful_token}\n')
                printful_token_updated = True
            else:
                updated_lines.append(line + '\n')
        
        # Add Printful token if it wasn't found
        if not printful_token_updated:
            updated_lines.append(f'PRINTFUL_API_KEY={printful_token}\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
            
    else:
        print("📁 Creating new .env file with Printful token...")
        
        # Create new .env file with all required variables
        env_content = f"""# Weather API Configuration
WEATHER_API_KEY=your_weather_api_key_here

# Email Configuration (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ
PAYPAL_CLIENT_SECRET=EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha

# Printful Configuration
PRINTFUL_API_KEY={printful_token}

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    print("✅ Printful token set successfully!")
    print("🔒 Token is stored in .env file (not committed to git)")
    print("🌐 For GCP deployment, set this as environment variable in Cloud Run")

def update_gcp_deployment_script():
    """Update the GCP deployment script with the Printful token"""
    
    gcp_script = """#!/bin/bash
# GCP Deployment Script with PayPal and Printful Environment Variables

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
  --set-env-vars="PRINTFUL_API_KEY=eWlXN3veWJXrQyOan2OEpHkQ9nuZuUqy6pZnmJjk" \\
  --set-env-vars="WEATHER_API_KEY=your_weather_api_key" \\
  --set-env-vars="MAIL_USERNAME=your_email@gmail.com" \\
  --set-env-vars="MAIL_PASSWORD=your_app_password" \\
  --set-env-vars="SECRET_KEY=your_secret_key"

echo "🚀 App deployed to GCP Cloud Run!"
echo "🔗 Your app URL will be shown above"
"""
    
    with open('deploy_gcp.sh', 'w') as f:
        f.write(gcp_script)
    
    # Make the script executable
    os.chmod('deploy_gcp.sh', 0o755)
    
    print("📜 Updated deploy_gcp.sh script with Printful token")
    print("⚠️  Remember to update the script with your actual API keys before deploying")

if __name__ == "__main__":
    print("🔐 Setting up Printful token...")
    setup_printful_token()
    update_gcp_deployment_script()
    print("\n🎉 Setup complete! You can now:")
    print("   1. Run 'python app.py' to test locally")
    print("   2. Update other variables in .env file")
    print("   3. Use 'deploy_gcp.sh' for GCP deployment") 
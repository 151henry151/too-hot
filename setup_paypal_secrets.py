#!/usr/bin/env python3
"""
Script to set up PayPal secrets in Google Cloud Secret Manager
"""

import subprocess
import sys

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_paypal_secrets():
    """Set up PayPal secrets in Google Cloud Secret Manager"""
    
    print("🔧 Setting up PayPal secrets in Google Cloud Secret Manager...")
    
    # Check if gcloud is installed
    if not run_command("which gcloud"):
        print("❌ gcloud CLI not found. Please install Google Cloud SDK first.")
        return False
    
    # Check if user is authenticated
    auth_status = run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'")
    if not auth_status:
        print("❌ Not authenticated with gcloud. Please run 'gcloud auth login' first.")
        return False
    
    print(f"✅ Authenticated as: {auth_status}")
    
    # Get project ID
    project_id = run_command("gcloud config get-value project")
    if not project_id:
        print("❌ No project ID set. Please run 'gcloud config set project YOUR_PROJECT_ID' first.")
        return False
    
    print(f"✅ Using project: {project_id}")
    
    # Enable Secret Manager API if not already enabled
    print("🔧 Enabling Secret Manager API...")
    run_command("gcloud services enable secretmanager.googleapis.com")
    
    # Create secrets
    secrets = [
        ("paypal-client-id", "PayPal Client ID (from PayPal Developer Dashboard)"),
        ("paypal-client-secret", "PayPal Client Secret (from PayPal Developer Dashboard)")
    ]
    
    for secret_name, description in secrets:
        print(f"\n🔧 Setting up {secret_name}...")
        print(f"Please enter your {description}:")
        
        # Check if secret already exists
        existing = run_command(f"gcloud secrets describe {secret_name} --format='value(name)' 2>/dev/null")
        
        if existing:
            print(f"⚠️  Secret '{secret_name}' already exists.")
            update = input("Do you want to update it? (y/N): ").lower().strip()
            if update != 'y':
                continue
        
        # Get the secret value
        secret_value = input(f"Enter {description}: ").strip()
        
        if not secret_value:
            print(f"⚠️  Skipping {secret_name} (empty value)")
            continue
        
        # Create or update the secret
        if existing:
            # Update existing secret
            run_command(f"echo '{secret_value}' | gcloud secrets versions add {secret_name} --data-file=-")
            print(f"✅ Updated {secret_name}")
        else:
            # Create new secret
            run_command(f"echo '{secret_value}' | gcloud secrets create {secret_name} --data-file=-")
            print(f"✅ Created {secret_name}")
    
    print("\n🎉 PayPal secrets setup complete!")
    print("\n📝 Next steps:")
    print("1. Make sure your PayPal app is in 'sandbox' mode for testing")
    print("2. Deploy your app with: ./deploy_gcp.sh")
    print("3. Test the payment flow in your deployed app")
    
    return True

if __name__ == "__main__":
    setup_paypal_secrets() 
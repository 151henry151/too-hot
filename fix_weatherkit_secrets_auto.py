#!/usr/bin/env python3
"""
Automatically fix WeatherKit secrets by reading the private key file
"""

import subprocess
import base64
import os

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def fix_weatherkit_secrets_auto():
    """Automatically fix WeatherKit secrets"""
    print("🔧 Automatically Fixing WeatherKit Secrets")
    print("=" * 50)
    
    # Check if gcloud is installed and authenticated
    print("🔍 Checking gcloud setup...")
    if not run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'"):
        print("❌ Not authenticated with gcloud. Please run: gcloud auth login")
        return False
    
    # Get project ID
    project_id = run_command("gcloud config get-value project")
    if not project_id:
        print("❌ No project ID set. Please run: gcloud config set project YOUR_PROJECT_ID")
        return False
    
    print(f"✅ Using project: {project_id}")
    
    # Get credentials from user
    key_id = input("Enter your WeatherKit Key ID: ").strip()
    if not key_id:
        print("❌ Key ID is required")
        return False
    
    team_id = input("Enter your Apple Team ID: ").strip()
    if not team_id:
        print("❌ Team ID is required")
        return False
    
    service_id = input("Enter your WeatherKit Service ID: ").strip()
    if not service_id:
        print("❌ Service ID is required")
        return False
    
    # Read the private key file and encode it
    private_key_path = input(f"Enter path to your AuthKey_{key_id}.p8 file: ").strip()
    if not private_key_path or not os.path.exists(private_key_path):
        print(f"❌ Private key file not found: {private_key_path}")
        return False
    
    print(f"📁 Reading private key from: {private_key_path}")
    with open(private_key_path, 'rb') as f:
        private_key_content = f.read()
    
    # Encode to base64 without newlines
    private_key_b64 = base64.b64encode(private_key_content).decode('utf-8')
    print(f"✅ Private key encoded (length: {len(private_key_b64)} characters)")
    
    # Define the clean secrets
    secrets_to_fix = {
        'weatherkit-key-id': key_id,
        'weatherkit-team-id': team_id,
        'weatherkit-service-id': service_id,
        'weatherkit-private-key': private_key_b64
    }
    
    # Update secrets in GCP
    print("\n🔐 Updating GCP secrets with clean values...")
    
    for secret_name, secret_value in secrets_to_fix.items():
        print(f"Updating secret: {secret_name}")
        
        # Add the secret version (this will create a new version)
        echo_result = run_command(f'echo "{secret_value}" | gcloud secrets versions add {secret_name} --data-file=-')
        if echo_result is None:
            print(f"❌ Failed to update secret {secret_name}")
            return False
        
        print(f"✅ Updated secret: {secret_name}")
    
    print("\n🎉 All WeatherKit secrets updated successfully!")
    print("\n📋 Updated Secret Summary:")
    for secret_name in secrets_to_fix.keys():
        print(f"   - {secret_name}")
    
    print("\n🧪 Test the fix:")
    print("   python test_weatherkit_gcp_secrets.py")
    
    return True

if __name__ == "__main__":
    fix_weatherkit_secrets_auto() 
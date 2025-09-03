#!/usr/bin/env python3
"""
Fix WeatherKit secrets by removing newline characters
"""

import subprocess

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def fix_weatherkit_secrets():
    """Fix WeatherKit secrets by removing newline characters"""
    print("🔧 Fixing WeatherKit Secrets")
    print("=" * 40)
    
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
    
    # Get current values and clean them
    secrets_to_fix = {
        'weatherkit-key-id': input("Enter your WeatherKit Key ID: ").strip(),
        'weatherkit-team-id': input("Enter your Apple Team ID (without newlines): ").strip(),
        'weatherkit-service-id': input("Enter your WeatherKit Service ID: ").strip(),
        'weatherkit-private-key': input("Enter your base64 encoded private key (without newlines): ").strip()
    }
    
    if not secrets_to_fix['weatherkit-team-id'] or not secrets_to_fix['weatherkit-private-key']:
        print("❌ Team ID and private key are required")
        return False
    
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
    fix_weatherkit_secrets() 
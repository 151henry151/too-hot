#!/usr/bin/env python3
"""
Create GCP secrets for Apple WeatherKit credentials directly
Uses the specific Key ID provided by the user
"""

import subprocess
import base64

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_weatherkit_secrets_direct():
    """Create GCP secrets for Apple WeatherKit credentials directly"""
    print("🌤️  Creating Apple WeatherKit GCP Secrets")
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
    
    # Get the remaining credentials from user
    print("\n📋 WeatherKit Credentials")
    print("Enter your WeatherKit Key ID:")
    
    key_id = input("Key ID: ").strip()
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
    
    print("\n📄 Private Key Setup:")
    print("Convert your .p8 file to base64:")
    print(f"   base64 -i AuthKey_{key_id}.p8 | tr -d '\n'")
    print()
    
    private_key = input("Enter your base64 encoded private key: ").strip()
    if not private_key:
        print("❌ Private key is required")
        return False
    
    # Validate base64
    try:
        base64.b64decode(private_key)
        print("✅ Base64 validation successful")
    except Exception:
        print("❌ Invalid base64 encoding. Please check your private key.")
        return False
    
    # Create secrets in GCP
    print("\n🔐 Creating GCP secrets...")
    
    secrets = {
        'weatherkit-key-id': key_id,
        'weatherkit-team-id': team_id,
        'weatherkit-service-id': service_id,
        'weatherkit-private-key': private_key
    }
    
    for secret_name, secret_value in secrets.items():
        print(f"Creating secret: {secret_name}")
        
        # Create the secret if it doesn't exist
        create_result = run_command(f"gcloud secrets create {secret_name} --replication-policy=automatic", check=False)
        if create_result is None and "already exists" not in subprocess.run(f"gcloud secrets create {secret_name} --replication-policy=automatic", shell=True, capture_output=True, text=True).stderr:
            print(f"❌ Failed to create secret {secret_name}")
            return False
        
        # Add the secret version
        echo_result = run_command(f'echo "{secret_value}" | gcloud secrets versions add {secret_name} --data-file=-')
        if echo_result is None:
            print(f"❌ Failed to add secret version for {secret_name}")
            return False
        
        print(f"✅ Created secret: {secret_name}")
    
    print("\n🎉 All WeatherKit secrets created successfully!")
    print("\n📋 Secret Summary:")
    for secret_name in secrets.keys():
        print(f"   - {secret_name}")
    
    print("\n🚀 Next steps:")
    print("1. Deploy your app to Cloud Run")
    print("2. Test the WeatherKit integration")
    print("3. Monitor the logs to ensure everything works correctly")
    
    return True

if __name__ == "__main__":
    create_weatherkit_secrets_direct() 
#!/usr/bin/env python3
"""
Set WeatherKit environment variable in Cloud Run
"""

import subprocess
import os

def set_weatherkit_env():
    """Set WeatherKit environment variable in Cloud Run"""
    print("🌤️ Setting WeatherKit environment variable in Cloud Run")
    print("=" * 60)
    
    # Check if gcloud is installed and authenticated
    print("🔍 Checking gcloud setup...")
    try:
        result = subprocess.run("gcloud auth list --filter=status:ACTIVE --format='value(account)'", 
                              shell=True, capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            print("❌ Not authenticated with gcloud. Please run: gcloud auth login")
            return False
        print(f"✅ Authenticated as: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ gcloud not found or not working. Please install and configure gcloud.")
        return False
    
    # Get project ID
    try:
        project_id = subprocess.run("gcloud config get-value project", 
                                  shell=True, capture_output=True, text=True, check=True)
        project_id = project_id.stdout.strip()
        if not project_id:
            print("❌ No project ID set. Please run: gcloud config set project YOUR_PROJECT_ID")
            return False
        print(f"✅ Using project: {project_id}")
    except subprocess.CalledProcessError:
        print("❌ Failed to get project ID")
        return False
    
    # Get service name
    service_name = input("Enter your Cloud Run service name (default: too-hot): ").strip()
    if not service_name:
        service_name = "too-hot"
    
    # Get region
    region = input("Enter your Cloud Run region (default: us-central1): ").strip()
    if not region:
        region = "us-central1"
    
    print(f"\n🔧 Updating Cloud Run service: {service_name} in {region}")
    
    # Update the service with WeatherKit enabled
    try:
        cmd = f"gcloud run services update {service_name} --region={region} --set-env-vars=WEATHERKIT_ENABLED=true"
        print(f"Running: {cmd}")
        
        result = subprocess.run(cmd, shell=True, check=True)
        print("✅ WeatherKit environment variable set successfully!")
        
        print("\n🚀 Next steps:")
        print("1. Test the WeatherKit integration:")
        print(f"   curl https://{service_name}-[hash]-{region}.a.run.app/api/weatherkit/test")
        print("2. The scheduler will now use WeatherKit for the 8 AM daily check")
        print("3. Monitor the logs to ensure everything works correctly")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update Cloud Run service: {e}")
        return False

if __name__ == "__main__":
    set_weatherkit_env() 
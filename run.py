#!/usr/bin/env python3
"""
Startup script for Too Hot Temperature Alert Service
Checks dependencies and starts the application
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors', 
        'flask_mail',
        'requests',
        'python_dotenv',
        'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Please activate the virtual environment and install requirements:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if environment file exists"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            print("⚠️  No .env file found. Please copy env.example to .env and configure it.")
            print("   cp env.example .env")
            print("   Then edit .env with your email and API settings.")
            return False
        else:
            print("❌ No environment configuration found")
            return False
    
    print("✅ Environment file found")
    return True

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Too Hot Temperature Alert Service...")
    print("📱 Web interface will be available at: http://localhost:5000")
    print("🔧 API endpoints will be available at: http://localhost:5000/api/")
    print("\n💡 To stop the application, press Ctrl+C")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🌡️  Too Hot Temperature Alert Service")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Check environment
    print("\n⚙️  Checking environment...")
    if not check_environment():
        print("\n💡 You can still run the app without full configuration for testing.")
        print("   The temperature checking will be limited without API keys.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Start the application
    return start_application()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
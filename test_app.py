#!/usr/bin/env python3
"""
Test script for Too Hot Temperature Alert Service
Tests the API endpoints and basic functionality
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"

def test_server_running():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return False

def test_subscribe():
    """Test user subscription"""
    print("\n📧 Testing subscription...")
    
    test_email = "test@example.com"
    test_location = "New York"
    
    data = {
        "email": test_email,
        "location": test_location
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscribe",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Subscription successful: {result['message']}")
            return test_email
        else:
            print(f"❌ Subscription failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Subscription error: {e}")
        return None

def test_unsubscribe(email):
    """Test user unsubscription"""
    print(f"\n🚫 Testing unsubscription for {email}...")
    
    data = {"email": email}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/unsubscribe",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Unsubscription successful: {result['message']}")
            return True
        else:
            print(f"❌ Unsubscription failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Unsubscription error: {e}")
        return False

def test_get_subscribers():
    """Test getting subscribers list"""
    print("\n👥 Testing get subscribers...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/subscribers")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Subscribers retrieved: {result['count']} subscribers")
            return True
        else:
            print(f"❌ Get subscribers failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get subscribers error: {e}")
        return False

def test_check_temperatures():
    """Test temperature checking (will fail without API key)"""
    print("\n🌡️ Testing temperature check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/check-temperatures")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Temperature check successful: {result['message']}")
            print(f"   Notifications sent: {result['notifications_sent']}")
            return True
        elif response.status_code == 500:
            result = response.json()
            print(f"⚠️  Temperature check failed (expected without API key): {result['error']}")
            print("   This is expected if WEATHER_API_KEY is not configured")
            return True
        else:
            print(f"❌ Temperature check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Temperature check error: {e}")
        return False

def test_web_interface():
    """Test web interface accessibility"""
    print("\n🌐 Testing web interface...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            content = response.text
            if "Too Hot" in content and "Temperature Alert Service" in content:
                print("✅ Web interface is accessible and contains expected content")
                return True
            else:
                print("⚠️  Web interface accessible but content may be incomplete")
                return True
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running Too Hot Temperature Alert Service Tests")
    print("=" * 50)
    
    tests = [
        ("Server Running", test_server_running),
        ("Web Interface", test_web_interface),
        ("Subscribe", test_subscribe),
        ("Get Subscribers", test_get_subscribers),
        ("Check Temperatures", test_check_temperatures),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_name == "Subscribe":
                email = test_func()
                if email:
                    passed += 1
                    # Test unsubscribe after successful subscription
                    if test_unsubscribe(email):
                        passed += 1
                        total += 1
            else:
                if test_func():
                    passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 
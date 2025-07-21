#!/usr/bin/env python3
"""
Test script for push notifications
This script tests the push notification setup and sends a test notification
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_push_notification_setup():
    """Test the push notification setup"""
    print("🧪 Testing Push Notification Setup...")
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"⚠️  Flask app returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app is not running: {e}")
        return False
    
    # Test 2: Check if service worker is accessible
    try:
        response = requests.get('http://127.0.0.1:5000/static/js/sw.js', timeout=5)
        if response.status_code == 200:
            print("✅ Service worker is accessible")
        else:
            print(f"❌ Service worker not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Service worker error: {e}")
    
    # Test 3: Check if push notification script is accessible
    try:
        response = requests.get('http://127.0.0.1:5000/static/js/push-notifications.js', timeout=5)
        if response.status_code == 200:
            print("✅ Push notification script is accessible")
        else:
            print(f"❌ Push notification script not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Push notification script error: {e}")
    
    # Test 4: Check if manifest is accessible
    try:
        response = requests.get('http://127.0.0.1:5000/static/manifest.json', timeout=5)
        if response.status_code == 200:
            print("✅ PWA manifest is accessible")
        else:
            print(f"❌ PWA manifest not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ PWA manifest error: {e}")
    
    # Test 5: Check if VAPID keys are loaded
    vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
    if vapid_private_key:
        print("✅ VAPID private key is loaded")
    else:
        print("❌ VAPID private key not found in environment")
    
    # Test 6: Check if subscriptions file exists
    if os.path.exists('push_subscriptions.json'):
        with open('push_subscriptions.json', 'r') as f:
            subscriptions = json.load(f)
        print(f"✅ Found {len(subscriptions)} push notification subscriptions")
    else:
        print("ℹ️  No push subscriptions file found yet (normal for new setup)")
    
    return True

def send_test_notification():
    """Send a test push notification"""
    print("\n📢 Sending Test Push Notification...")
    
    test_data = {
        'title': 'Test Climate Alert',
        'body': 'This is a test notification from the Too Hot climate awareness campaign!',
        'url': '/'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/send-push-notification',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test notification sent successfully!")
            print(f"   Message: {result.get('message', 'Unknown')}")
            print(f"   Successful sends: {result.get('successful_sends', 0)}")
            print(f"   Failed sends: {result.get('failed_sends', 0)}")
            print(f"   Total subscribers: {result.get('total_subscribers', 0)}")
        else:
            print(f"❌ Failed to send test notification: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending test notification: {e}")

def main():
    """Main test function"""
    print("🚀 Push Notification Test Suite")
    print("=" * 40)
    
    # Test the setup
    if test_push_notification_setup():
        print("\n" + "=" * 40)
        
        # Ask user if they want to send a test notification
        response = input("\nSend a test push notification? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            send_test_notification()
        else:
            print("⏭️  Skipping test notification")
    
    print("\n📝 Next Steps:")
    print("1. Visit http://127.0.0.1:5000 in your browser")
    print("2. Click 'Enable Push Notifications'")
    print("3. Grant permission when prompted")
    print("4. Run this test again to send a test notification")
    print("5. Check your device for the notification!")

if __name__ == '__main__':
    main() 
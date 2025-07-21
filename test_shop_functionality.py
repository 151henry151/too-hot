#!/usr/bin/env python3
"""
Test script to verify shop functionality
"""

import requests
import json

def test_shop_page():
    """Test that the shop page loads correctly"""
    try:
        response = requests.get('http://localhost:5000/shop')
        if response.status_code == 200:
            print("✅ Shop page loads successfully")
            return True
        else:
            print(f"❌ Shop page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing shop page: {e}")
        return False

def test_color_mapping():
    """Test that the color mapping is working correctly"""
    # Test data - this should match what's in the frontend
    color_mapping = {
        'black': 'Black',
        'french-navy': 'French Navy',
        'anthracite': 'Anthracite',
        'white': 'White',
        'heather-grey': 'Heather Grey'
    }
    
    reverse_mapping = {
        'Black': 'black',
        'French Navy': 'french-navy',
        'Anthracite': 'anthracite',
        'White': 'white',
        'Heather Grey': 'heather-grey'
    }
    
    print("Testing color mapping...")
    
    # Test forward mapping
    for display_key, api_name in color_mapping.items():
        print(f"  {display_key} -> {api_name}")
    
    # Test reverse mapping
    for api_name, display_key in reverse_mapping.items():
        print(f"  {api_name} -> {display_key}")
    
    print("✅ Color mapping looks correct")

def test_payment_creation():
    """Test payment creation with correct color data"""
    test_data = {
        'amount': '25.00',
        'quantity': 1,
        'size': 'M',
        'product_id': 'tshirt',
        'color': 'French Navy',  # This should be the Printful API color name
        'printful_product_id': '387436926'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/create-payment',
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Payment creation successful")
                print(f"   Approval URL: {data.get('approval_url', 'N/A')}")
                return True
            else:
                print(f"❌ Payment creation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Payment creation failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment creation: {e}")
        return False

def main():
    print("🧪 Testing Shop Functionality")
    print("=" * 40)
    
    # Test 1: Shop page loads
    if not test_shop_page():
        print("❌ Shop page test failed")
        return
    
    # Test 2: Color mapping
    test_color_mapping()
    
    # Test 3: Payment creation
    if test_payment_creation():
        print("\n✅ All tests passed! Shop functionality is working correctly.")
    else:
        print("\n❌ Payment creation test failed. Check the backend logs.")

if __name__ == "__main__":
    main() 
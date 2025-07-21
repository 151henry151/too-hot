#!/usr/bin/env python3
"""
Test script to check shop images
"""

import requests
import json

def test_shop_images():
    """Test the shop route to see what images are returned"""
    
    try:
        print("🔍 Testing shop route...")
        
        response = requests.get('http://127.0.0.1:5000/shop')
        
        if response.status_code == 200:
            print("✅ Shop page loaded successfully")
            
            # Look for image URLs in the response
            content = response.text
            
            # Check if we can find the product image references
            if 'product-image' in content:
                print("✅ Product image element found")
            else:
                print("❌ Product image element not found")
            
            # Check for static image fallback
            if '/static/img/tshirt.png' in content:
                print("✅ Static image fallback found")
            else:
                print("❌ Static image fallback not found")
                
        else:
            print(f"❌ Error loading shop page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_shop_images() 
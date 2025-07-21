#!/usr/bin/env python3
"""
Test script to fetch Printful product images
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_printful_images():
    """Test fetching product images from Printful"""
    
    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
    PRINTFUL_BASE_URL = 'https://api.printful.com'
    
    if not PRINTFUL_API_KEY:
        print("❌ Printful API key not found")
        return
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 Fetching product images from Printful...")
        
        # Get sync products
        response = requests.get(
            f'{PRINTFUL_BASE_URL}/sync/products',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('result', [])
            
            print(f"✅ Found {len(products)} sync products")
            
            for i, product in enumerate(products, 1):
                product_id = product.get('id')
                name = product.get('name', 'Unknown')
                
                print(f"\n{i}. Product ID: {product_id}")
                print(f"   Name: {name}")
                
                # Get detailed product info
                detail_response = requests.get(
                    f'{PRINTFUL_BASE_URL}/sync/products/{product_id}',
                    headers=headers
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    sync_product = detail_data.get('result', {})
                    
                    variants = sync_product.get('sync_variants', [])
                    print(f"   Variants: {len(variants)}")
                    
                    for j, variant in enumerate(variants):
                        files = variant.get('files', [])
                        print(f"   Variant {j+1} files: {len(files)}")
                        
                        for k, file in enumerate(files):
                            file_type = file.get('type', 'unknown')
                            file_url = file.get('url', 'no url')
                            print(f"     File {k+1}: {file_type} - {file_url}")
                            
                            # Test if image URL is accessible
                            if file_url and file_url != 'no url':
                                try:
                                    img_response = requests.head(file_url, timeout=5)
                                    if img_response.status_code == 200:
                                        print(f"       ✅ Image accessible")
                                    else:
                                        print(f"       ❌ Image not accessible (status: {img_response.status_code})")
                                except Exception as e:
                                    print(f"       ❌ Error accessing image: {str(e)}")
                else:
                    print(f"   ❌ Error getting product details: {detail_response.status_code}")
            
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_printful_images() 
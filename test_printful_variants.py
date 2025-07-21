#!/usr/bin/env python3
"""
Test script to debug Printful API variant structure
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_printful_variants():
    """Test Printful API to see actual variant structure"""
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
        # Get sync products
        print("🔍 Fetching sync products...")
        sync_response = requests.get(
            f'{PRINTFUL_BASE_URL}/sync/products',
            headers=headers
        )
        
        if sync_response.status_code == 200:
            sync_data = sync_response.json()
            sync_products = sync_data.get('result', [])
            
            print(f"📦 Found {len(sync_products)} sync products")
            
            for sync_product in sync_products:
                sync_product_id = sync_product.get('id')
                name = sync_product.get('name', '')
                
                print(f"\n🔍 Product: {name} (ID: {sync_product_id})")
                
                # Get detailed sync product info with variants
                detail_response = requests.get(
                    f'{PRINTFUL_BASE_URL}/sync/products/{sync_product_id}',
                    headers=headers
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    sync_product_detail = detail_data.get('result', {})
                    
                    # Get variants with their IDs
                    variants = sync_product_detail.get('sync_variants', [])
                    print(f"  📋 Found {len(variants)} variants:")
                    
                    for variant in variants:
                        variant_id = variant.get('id')
                        variant_name = variant.get('name', '')
                        retail_price = variant.get('retail_price', 'N/A')
                        
                        print(f"    - ID: {variant_id}")
                        print(f"      Name: {variant_name}")
                        print(f"      Price: {retail_price}")
                        
                        # Try to parse color and size
                        if '|' in variant_name:
                            color_size = variant_name.split('|')[1].strip()
                            print(f"      Color/Size: {color_size}")
                            
                            if '/' in color_size:
                                color = color_size.split('/')[0].strip()
                                size = color_size.split('/')[1].strip()
                                print(f"      Parsed - Color: '{color}', Size: '{size}'")
                        else:
                            print(f"      No color/size separator found")
                        print()
                else:
                    print(f"  ❌ Failed to get product details: {detail_response.status_code}")
        else:
            print(f"❌ API Error ({sync_response.status_code}): {sync_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_printful_variants() 
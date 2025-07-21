#!/usr/bin/env python3
"""
Printful Product Fetcher
This script fetches t-shirt products from your specific Printful store.
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def get_printful_store_products():
    """Fetch products from your specific Printful store"""
    
    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
    PRINTFUL_BASE_URL = 'https://api.printful.com'
    
    if not PRINTFUL_API_KEY:
        print("❌ Printful API key not found in environment variables")
        return
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 Fetching products from your Printful store...")
        
        # Get store products (not catalog products)
        response = requests.get(
            f'{PRINTFUL_BASE_URL}/store/products',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('result', [])
            
            print(f"✅ Found {len(products)} products in your store")
            
            # Filter for t-shirts
            tshirts = []
            for product in products:
                name = product.get('name', '').lower()
                if any(keyword in name for keyword in ['t-shirt', 'tshirt', 'shirt', 'tee', 'too hot']):
                    tshirts.append(product)
            
            print(f"👕 Found {len(tshirts)} t-shirt products:")
            print("=" * 80)
            
            for i, product in enumerate(tshirts, 1):
                product_id = product.get('id')
                name = product.get('name', 'Unknown')
                brand = product.get('brand', 'Unknown')
                
                print(f"{i:2d}. ID: {product_id}")
                print(f"    Name: {name}")
                print(f"    Brand: {brand}")
                print("-" * 40)
            
            # Save to file for easy reference
            with open('printful_tshirts.json', 'w') as f:
                json.dump(tshirts, f, indent=2)
            
            print(f"\n💾 Product details saved to 'printful_tshirts.json'")
            
            # Show IDs in a simple list for easy copying
            print("\n📋 Product IDs (for easy copying):")
            print("=" * 40)
            for product in tshirts:
                print(f"'{product.get('id')}',")
            
            return tshirts
            
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def get_sync_products():
    """Get sync products (your custom products)"""
    
    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
    PRINTFUL_BASE_URL = 'https://api.printful.com'
    
    if not PRINTFUL_API_KEY:
        print("❌ Printful API key not found in environment variables")
        return
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 Fetching sync products (your custom products)...")
        
        # Get sync products
        response = requests.get(
            f'{PRINTFUL_BASE_URL}/sync/products',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('result', [])
            
            print(f"✅ Found {len(products)} sync products")
            
            # Filter for t-shirts
            tshirts = []
            for product in products:
                name = product.get('name', '').lower()
                if any(keyword in name for keyword in ['t-shirt', 'tshirt', 'shirt', 'tee', 'too hot']):
                    tshirts.append(product)
            
            print(f"👕 Found {len(tshirts)} t-shirt sync products:")
            print("=" * 80)
            
            for i, product in enumerate(tshirts, 1):
                sync_product_id = product.get('id')
                name = product.get('name', 'Unknown')
                
                print(f"{i:2d}. Sync Product ID: {sync_product_id}")
                print(f"    Name: {name}")
                print("-" * 40)
            
            # Save to file for easy reference
            with open('printful_sync_tshirts.json', 'w') as f:
                json.dump(tshirts, f, indent=2)
            
            print(f"\n💾 Sync product details saved to 'printful_sync_tshirts.json'")
            
            # Show sync product IDs in a simple list for easy copying
            print("\n📋 Sync Product IDs (for easy copying):")
            print("=" * 40)
            for product in tshirts:
                print(f"'{product.get('id')}',")
            
            return tshirts
            
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("🛍️ Printful Store Product Fetcher")
    print("=" * 50)
    
    print("\n1️⃣ Checking store products...")
    store_products = get_printful_store_products()
    
    print("\n2️⃣ Checking sync products...")
    sync_products = get_sync_products()
    
    if store_products or sync_products:
        total_tshirts = len(store_products or []) + len(sync_products or [])
        print(f"\n🎯 Found {total_tshirts} t-shirt products total")
        print("Use the sync product IDs in your app.py file to replace the placeholder product ID.")
    else:
        print("❌ No t-shirt products found in your store")
        print("💡 Make sure you've created t-shirt products in your Printful store") 
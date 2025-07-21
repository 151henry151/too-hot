#!/usr/bin/env python3
"""
Generate VAPID keys for push notifications
Run this script to generate the required VAPID keys for web push notifications
"""

import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.serialization import PrivateFormat, NoEncryption

def generate_vapid_keys():
    """Generate VAPID key pair for push notifications"""
    # Generate private key
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # Get public key
    public_key = private_key.public_key()
    
    # Export public key in raw format
    public_key_raw = public_key.public_bytes(
        encoding=Encoding.X962,
        format=PublicFormat.UncompressedPoint
    )
    
    # Convert to base64 for VAPID
    public_key_b64 = base64.urlsafe_b64encode(public_key_raw).decode('utf-8').rstrip('=')
    
    # Export private key in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    ).decode('utf-8')
    
    return {
        'public_key': public_key_b64,
        'private_key': private_key_pem
    }

def main():
    """Generate and display VAPID keys"""
    print("🔑 Generating VAPID keys for push notifications...")
    
    try:
        keys = generate_vapid_keys()
        
        print("\n✅ VAPID keys generated successfully!")
        print("\n📋 Public Key (add to your JavaScript):")
        print(f"const vapidPublicKey = '{keys['public_key']}';")
        
        print("\n🔐 Private Key (keep secret, add to your server):")
        print(keys['private_key'])
        
        # Save to file
        with open('vapid_keys.json', 'w') as f:
            json.dump(keys, f, indent=2)
        
        print("\n💾 Keys saved to 'vapid_keys.json'")
        print("\n📝 Next steps:")
        print("1. Add the public key to your push-notifications.js file")
        print("2. Add the private key to your server environment variables")
        print("3. Use the private key to sign push notification payloads")
        
    except Exception as e:
        print(f"❌ Error generating VAPID keys: {e}")
        print("\n💡 Make sure you have the cryptography library installed:")
        print("pip install cryptography")

if __name__ == '__main__':
    main() 
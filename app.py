from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response, render_template_string
from flask_cors import CORS
from flask_mail import Mail, Message
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import paypalrestsdk
from functools import wraps
import base64
from flask_sqlalchemy import SQLAlchemy
import subprocess
import time
import re
from pytz import timezone
import threading
from sqlalchemy import and_
import atexit
import random

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure PayPal
paypal_mode = os.getenv('PAYPAL_MODE', 'sandbox')  # sandbox for local dev, live for production
paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET')

if paypal_client_id and paypal_client_secret:
    paypalrestsdk.configure({
        "mode": paypal_mode,
        "client_id": paypal_client_id,
        "client_secret": paypal_client_secret
    })
    print(f"✅ PayPal configured in {paypal_mode} mode")
else:
    print("⚠️  PayPal credentials not found. Payment functionality will not work.")
    print("   Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET environment variables.")
    print("   For local development, use sandbox mode.")
    print("   For production, use live mode with Google Cloud Secret Manager.")

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'mail.spacemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False  # SSL only
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'tendegrees@its2hot.org'

# Old Gmail config (commented out)
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Debug logging to see what environment variables are being read
print(f"DEBUG: MAIL_USERNAME = {os.getenv('MAIL_USERNAME', 'Not set')}")
print(f"DEBUG: MAIL_PASSWORD = {os.getenv('MAIL_PASSWORD', 'Not set')[:4]}..." if os.getenv('MAIL_PASSWORD') else "DEBUG: MAIL_PASSWORD = None")
print(f"DEBUG: WEATHER_API_KEY = {os.getenv('WEATHER_API_KEY', 'Not set')[:4]}..." if os.getenv('WEATHER_API_KEY') else "DEBUG: WEATHER_API_KEY = None")

mail = Mail(app)

# --- Database Setup ---
CLOUDSQL_CONNECTION_NAME = os.getenv('CLOUDSQL_CONNECTION_NAME', 'romp-family-enterprises:us-central1:too-hot-db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'TooHot2024!')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'too_hot')

if os.getenv('GAE_ENV', '').startswith('standard') or os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_ENV'):
    # Running on GCP (Cloud Run or App Engine)
    DB_SOCKET_DIR = os.getenv('DB_SOCKET_DIR', '/cloudsql')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@/{POSTGRES_DB}'
        f'?host={DB_SOCKET_DIR}/{CLOUDSQL_CONNECTION_NAME}'
    )
else:
    # Local dev fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///too_hot.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    location = db.Column(db.String(128), default='auto')
    subscribed_at = db.Column(db.String(64), nullable=False)

    def as_dict(self):
        return {
            'email': self.email,
            'location': self.location,
            'subscribed_at': self.subscribed_at
        }

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    push_token = db.Column(db.String(512), unique=True, nullable=False)
    platform = db.Column(db.String(32), nullable=False)  # 'expo', 'fcm', etc.
    device_type = db.Column(db.String(32), nullable=False)  # 'ios', 'android'
    location = db.Column(db.String(128), default='auto')  # Location for this device
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def as_dict(self):
        return {
            'id': self.id,
            'push_token': self.push_token,
            'platform': self.platform,
            'device_type': self.device_type,
            'location': self.location,
            'registered_at': self.registered_at.isoformat(),
            'is_active': self.is_active
        }

# --- New Models for Logging ---
class PushNotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, nullable=True)
    push_token = db.Column(db.String(512), nullable=True)
    platform = db.Column(db.String(32), nullable=True)
    device_type = db.Column(db.String(32), nullable=True)
    title = db.Column(db.String(256), nullable=True)
    body = db.Column(db.String(1024), nullable=True)
    data = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=True)  # success/failure
    error = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'push_token': self.push_token,
            'platform': self.platform,
            'device_type': self.device_type,
            'title': self.title,
            'body': self.body,
            'data': self.data,
            'status': self.status,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }

class DebugLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(64), nullable=True)  # 'android', 'ios', 'backend', etc.
    device_id = db.Column(db.String(128), nullable=True)  # Changed from Integer to String to handle device identifiers
    email = db.Column(db.String(256), nullable=True)
    message = db.Column(db.Text, nullable=False)
    context = db.Column(db.String(256), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'device_id': self.device_id,
            'email': self.email,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }

class SchedulerLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trigger_type = db.Column(db.String(32), nullable=False)  # 'manual', 'cloud_scheduler', 'test'
    locations_checked = db.Column(db.Text, nullable=True)  # JSON array of locations
    temperatures_found = db.Column(db.Text, nullable=True)  # JSON object with location:temp pairs
    alerts_triggered = db.Column(db.Integer, default=0)  # Number of alerts sent
    threshold_used = db.Column(db.Float, nullable=False)  # Temperature threshold used
    status = db.Column(db.String(32), nullable=False)  # 'success', 'error', 'partial'
    error_message = db.Column(db.Text, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)  # How long the check took
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            'id': self.id,
            'trigger_type': self.trigger_type,
            'locations_checked': self.locations_checked,
            'temperatures_found': self.temperatures_found,
            'alerts_triggered': self.alerts_triggered,
            'threshold_used': self.threshold_used,
            'status': self.status,
            'error_message': self.error_message,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat()
        }

class CommitInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), unique=True, nullable=False)  # Full commit hash
    commit_message = db.Column(db.Text, nullable=False)
    commit_date = db.Column(db.DateTime, nullable=False)
    lines_added = db.Column(db.Integer, nullable=True)
    lines_deleted = db.Column(db.Integer, nullable=True)
    lines_changed = db.Column(db.Integer, nullable=True)
    time_spent_minutes = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            'id': self.id,
            'commit_hash': self.commit_hash,
            'commit_message': self.commit_message,
            'commit_date': self.commit_date.isoformat(),
            'lines_added': self.lines_added,
            'lines_deleted': self.lines_deleted,
            'lines_changed': self.lines_changed,
            'time_spent_minutes': self.time_spent_minutes,
            'last_updated': self.last_updated.isoformat()
        }

# --- Initialize DB ---
# Remove the @app.before_first_request decorator and function
# Instead, use app.app_context() at startup
with app.app_context():
    db.create_all()

# Weather API configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_BASE_URL = "http://api.weatherapi.com/v1"
NWS_BASE_URL = "https://api.weather.gov"  # Free National Weather Service API

# Temperature threshold for climate alerts (configurable via admin)
TEMP_THRESHOLD = int(os.getenv('TEMP_THRESHOLD', '1'))  # degrees Fahrenheit above average
CHECK_FREQUENCY = os.getenv('CHECK_FREQUENCY', 'hourly')  # 'hourly' or 'daily'

# Printful API configuration
PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
PRINTFUL_BASE_URL = 'https://api.printful.com'

def test_printful_connection():
    """Test Printful API connection and get available products"""
    if not PRINTFUL_API_KEY:
        print("⚠️  Printful API key not found in environment variables")
        return False
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test connection by getting products
        response = requests.get(
            f'{PRINTFUL_BASE_URL}/products',
            headers=headers
        )
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Printful API connection successful!")
            print(f"📦 Found {len(products.get('result', []))} products")
            return True
        elif response.status_code == 401:
            print("❌ Printful API authentication failed. Check your token.")
            return False
        else:
            print(f"❌ Printful API error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Printful API: {str(e)}")
        return False

def get_printful_product_variants():
    """Fetch actual product variants from Printful API with variant IDs"""
    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
    PRINTFUL_BASE_URL = 'https://api.printful.com'
    
    if not PRINTFUL_API_KEY:
        print("❌ Printful API key not found")
        return {}
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get sync products
        sync_response = requests.get(
            f'{PRINTFUL_BASE_URL}/sync/products',
            headers=headers
        )
        
        if sync_response.status_code == 200:
            sync_data = sync_response.json()
            sync_products = sync_data.get('result', [])
            
            products_data = {}
            
            for sync_product in sync_products:
                sync_product_id = sync_product.get('id')
                name = sync_product.get('name', '')
                
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
                    
                    # Map variants by color and size
                    color_variants = {}
                    for variant in variants:
                        variant_id = variant.get('id')
                        variant_name = variant.get('name', '')
                        
                        # Extract color and size from variant name
                        # Format: "IT'S TOO HOT! White text on dark background / French Navy / S"
                        if ' / ' in variant_name:
                            # Split by ' / ' to get the parts
                            parts = variant_name.split(' / ')
                            if len(parts) >= 3:
                                # Last part is size, second to last is color
                                color = parts[-2].strip()
                                size = parts[-1].strip()
                                
                                if color not in color_variants:
                                    color_variants[color] = {}
                                
                                color_variants[color][size] = {
                                    'variant_id': variant_id,
                                    'name': variant_name,
                                    'retail_price': variant.get('retail_price', '25.00')
                                }
                    
                    # Determine product type based on name
                    if 'dark' in name.lower() or 'white text' in name.lower():
                        product_key = 'tshirt'  # Dark design
                        fallback_image = '/static/img/tshirt_text.png'
                    elif 'light' in name.lower() or 'black text' in name.lower():
                        product_key = 'tshirt_light'  # Light design
                        fallback_image = '/static/img/tshirt_text_black.png'
                    else:
                        product_key = 'tshirt'  # Default to dark
                        fallback_image = '/static/img/tshirt_text.png'
                    
                    products_data[product_key] = {
                        'sync_product_id': sync_product_id,
                        'name': name,
                        'image': fallback_image,
                        'variants': color_variants
                    }
            
            return products_data
            
        else:
            print(f"❌ API Error ({sync_response.status_code}): {sync_response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ Error fetching product variants: {str(e)}")
        return {}

def get_printful_product_images():
    """Fetch product images from Printful API"""
    PRINTFUL_API_KEY = os.getenv('PRINTFUL_API_KEY')
    PRINTFUL_BASE_URL = 'https://api.printful.com'
    
    if not PRINTFUL_API_KEY:
        print("❌ Printful API key not found")
        return {}
    
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get catalog products to find the base product IDs
        response = requests.get(
            f'{PRINTFUL_BASE_URL}/products',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            catalog_products = data.get('result', [])
            
            # Find t-shirt products
            tshirt_products = {}
            for product in catalog_products:
                name = product.get('title', '').lower()
                if 't-shirt' in name or 'tshirt' in name:
                    product_id = product.get('id')
                    tshirt_products[product_id] = {
                        'name': product.get('title', ''),
                        'image': product.get('image', '')
                    }
            
            # Now get sync products and map them to catalog images
            sync_response = requests.get(
                f'{PRINTFUL_BASE_URL}/sync/products',
                headers=headers
            )
            
            if sync_response.status_code == 200:
                sync_data = sync_response.json()
                sync_products = sync_data.get('result', [])
                
                product_images = {}
                for sync_product in sync_products:
                    sync_product_id = sync_product.get('id')
                    name = sync_product.get('name', '')
                    
                    # Get detailed sync product info
                    detail_response = requests.get(
                        f'{PRINTFUL_BASE_URL}/sync/products/{sync_product_id}',
                        headers=headers
                    )
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        sync_product_detail = detail_data.get('result', {})
                        
                        # Get the catalog product ID from the first variant
                        variants = sync_product_detail.get('sync_variants', [])
                        if variants:
                            first_variant = variants[0]
                            catalog_product_id = first_variant.get('product_id')
                            
                            # Use catalog product image if available
                            if catalog_product_id in tshirt_products:
                                product_images[sync_product_id] = {
                                    'url': tshirt_products[catalog_product_id]['image'],
                                    'name': name
                                }
                            else:
                                # Use different static images based on product name
                                if 'dark' in name.lower() or 'white text' in name.lower():
                                    fallback_image = '/static/img/tshirt_text.png'  # White text on dark
                                elif 'light' in name.lower() or 'black text' in name.lower():
                                    fallback_image = '/static/img/tshirt_text_black.png'  # Black text on light
                                else:
                                    fallback_image = '/static/img/tshirt.png'  # Default
                                
                                product_images[sync_product_id] = {
                                    'url': fallback_image,
                                    'name': name
                                }
                
                return product_images
            
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ Error fetching product images: {str(e)}")
        return {}

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Serve the privacy policy page"""
    return render_template('privacy_policy.html')

@app.route('/shop')
def shop():
    # Get actual product variants from Printful
    product_variants = get_printful_product_variants()
    
    # Product details with actual variants and mockup images
    products = {
        'tshirt': {
            'name': 'IT\'S TOO HOT! T-Shirt (Dark)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with white text on dark background',
            'printful_product_id': product_variants.get('tshirt', {}).get('sync_product_id', '387436926'),
            'image': product_variants.get('tshirt', {}).get('image', url_for('static', filename='img/tshirt_text.png')),
            'variants': product_variants.get('tshirt', {}).get('variants', {}),
            'colors': {
                'black': {
                    'name': 'Black',
                    'front': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-black-front-687da1fc27008.png'),
                    'back': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-black-back-687da1fc275a7.png')
                },
                'french-navy': {
                    'name': 'French Navy',
                    'front': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-french-navy-front-687da1fc26147.png'),
                    'back': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-french-navy-back-687da1fc26cdc.png')
                },
                'anthracite': {
                    'name': 'Anthracite',
                    'front': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-anthracite-front-687da1fc279c8.png'),
                    'back': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-anthracite-back-687da1fc28199.png')
                }
            }
        },
        'tshirt_light': {
            'name': 'IT\'S TOO HOT! T-Shirt (Light)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with black text on light background',
            'printful_product_id': product_variants.get('tshirt_light', {}).get('sync_product_id', '387436861'),
            'image': product_variants.get('tshirt_light', {}).get('image', url_for('static', filename='img/tshirt_text_black.png')),
            'variants': product_variants.get('tshirt_light', {}).get('variants', {}),
            'colors': {
                'white': {
                    'name': 'White',
                    'front': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-white-front-687da29871c60.png'),
                    'back': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-white-back-687da2987241c.png')
                },
                'heather-grey': {
                    'name': 'Heather Grey',
                    'front': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-heather-grey-front-687da298707b3.png'),
                    'back': url_for('static', filename='img/mockups/unisex-organic-mid-light-t-shirt-heather-grey-back-687da298712d1.png')
                }
            }
        }
    }
    
    # Debug: Print what variants we found
    print("🔍 Product variants found:")
    for product_key, product_data in product_variants.items():
        print(f"  {product_key}: {product_data.get('name', 'Unknown')}")
        for color, sizes in product_data.get('variants', {}).items():
            print(f"    {color}: {list(sizes.keys())}")
    
    return render_template('shop.html', products=products)

@app.route('/checkout')
def checkout():
    # Get product details from session or query parameters
    product_id = request.args.get('product_id', 'tshirt')
    quantity = int(request.args.get('quantity', 1))
    
    # Product details (you can customize these)
    products = {
        'tshirt': {
            'name': 'IT\'S TOO HOT! T-Shirt (Dark)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with white text on dark background',
            'image': url_for('static', filename='img/tshirt.png'),
            'printful_product_id': '387436926'  # White text on dark background
        },
        'tshirt_light': {
            'name': 'IT\'S TOO HOT! T-Shirt (Light)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with black text on light background',
            'image': url_for('static', filename='img/tshirt.png'),
            'printful_product_id': '387436861'  # Black text on light background
        }
    }
    
    product = products.get(product_id, products['tshirt'])
    total = product['price'] * quantity
    
    return render_template('checkout.html', 
                         product=product, 
                         quantity=quantity, 
                         total=total)

@app.route('/create-payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        amount = data['amount']
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.host_url + "payment-success",
                "cancel_url": request.host_url + "payment-cancelled"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "IT'S TOO HOT! T-Shirt",
                        "sku": "TSHIRT001",
                        "price": str(amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": "Climate awareness t-shirt purchase"
            }]
        })
        
        if payment.create():
            # Store payment info in session for later use
            session['payment_id'] = payment.id
            session['order_data'] = data
            
            # Get approval URL
            for link in payment.links:
                if link.rel == "approval_url":
                    return jsonify({
                        'success': True,
                        'approval_url': link.href
                    })
        else:
            return jsonify({'error': payment.error}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/payment-success')
def payment_success():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    
    if payment_id and payer_id:
        # Execute the payment
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Get order data from session
            order_data = session.get('order_data', {})
            
            try:
                # Create order in Printful
                printful_order = create_printful_order(order_data)
                
                # Send confirmation email
                send_order_confirmation(order_data)
                
                return render_template('payment_success.html', 
                                     order_id=printful_order.get('id'))
            except Exception as e:
                return render_template('payment_error.html', error=str(e))
        else:
            return render_template('payment_error.html', error="Payment execution failed")
    
    return render_template('payment_error.html', error="Invalid payment data")

@app.route('/payment-cancelled')
def payment_cancelled():
    return render_template('payment_cancelled.html')

def create_printful_order(order_data):
    """Create order in Printful using newer API with correct variant ID"""
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get the correct variant ID based on product, color, and size
    product_variants = get_printful_product_variants()
    product_key = order_data.get('product_id', 'tshirt')
    color = order_data.get('color', 'black')
    size = order_data.get('size', 'M')
    
    # Find the correct variant ID
    variant_id = None
    if product_key in product_variants:
        product_data = product_variants[product_key]
        variants = product_data.get('variants', {})
        
        # Try to find the exact color/size combination
        if color in variants and size in variants[color]:
            variant_id = variants[color][size]['variant_id']
        else:
            # Fallback: use the first available variant for this color
            if color in variants:
                first_size = list(variants[color].keys())[0]
                variant_id = variants[color][first_size]['variant_id']
    
    if not variant_id:
        raise Exception(f'Variant not found for {product_key}, color: {color}, size: {size}')
    
    # Prepare order data for Printful (newer API format)
    printful_order = {
        'recipient': {
            'name': order_data['customer_name'],
            'address1': order_data['address']['line1'],
            'city': order_data['address']['city'],
            'state_code': order_data['address']['state'],
            'country_code': 'US',
            'zip': order_data['address']['postal_code']
        },
        'items': [{
            'sync_variant_id': variant_id,  # Use the specific variant ID
            'quantity': order_data['quantity']
        }],
        'retail_costs': {
            'currency': 'USD',
            'subtotal': str(order_data['total']),
            'shipping': '5.00',
            'tax': '0.00',
            'total': str(float(order_data['total']) + 5.00)
        }
    }
    
    try:
        response = requests.post(
            f'{PRINTFUL_BASE_URL}/orders',
            headers=headers,
            json=printful_order
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception('Printful API authentication failed. Check your token.')
        elif response.status_code == 404:
            raise Exception('Product not found. Check your product ID.')
        else:
            raise Exception(f'Printful API error ({response.status_code}): {response.text}')
            
    except requests.exceptions.RequestException as e:
        raise Exception(f'Network error connecting to Printful: {str(e)}')

def send_order_confirmation(order_data):
    """Send order confirmation email"""
    try:
        msg = Message(
            'Order Confirmation - IT\'S TOO HOT! T-Shirt',
            sender=app.config['MAIL_USERNAME'],
            recipients=[order_data['email']]
        )
        
        msg.body = f"""
        Thank you for your order!
        
        Order Details:
        - Product: {order_data['product_name']}
        - Quantity: {order_data['quantity']}
        - Total: ${order_data['total']}
        
        Your order will be shipped to:
        {order_data['customer_name']}
        {order_data['address']['line1']}
        {order_data['address']['city']}, {order_data['address']['state']} {order_data['address']['postal_code']}
        
        You'll receive tracking information once your order ships.
        
        Thank you for supporting climate awareness!
        """
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

def send_welcome_email(email, location):
    """Send welcome email to new subscriber (HTML + plain text fallback)"""
    try:
        subject = "🌍 Welcome to the Climate Movement - IT'S TOO HOT!"
        # Plain text fallback
        body = f"""
        Welcome to the Climate Movement!
        
        Thank you for joining the "IT'S TOO HOT!" climate awareness campaign. 
        You're now part of a growing community of activists working to raise 
        awareness about climate change.
        
        What happens next:
        - We'll monitor temperatures in your area ({location})
        - When temperatures are {TEMP_THRESHOLD}°F+ hotter than historical averages, you'll get an alert
        - Wear your "IT'S TOO HOT!" shirt on those days to raise awareness
        - Start conversations about climate change with friends and family
        
        Your "IT'S TOO HOT!" shirt is your climate activism uniform. When you wear it 
        on climate anomaly days, you're showing the world that climate change is real 
        and happening now.
        
        Ready to make a difference? Share this campaign with your friends:
        https://its2hot.org
        
        Together, we can raise awareness and drive climate action!
        
        #TooHot #ClimateAction #ClimateChange
        
        ---
        To unsubscribe, reply to this email with "unsubscribe"
        """
        # HTML body using new template
        html_body = render_template('welcome_email.html', location=location)
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=body,
            html=html_body
        )
        mail.send(msg)
        print(f"Welcome email sent to {email}")
    except Exception as e:
        print(f"Failed to send welcome email to {email}: {e}")

# --- Update /api/subscribe to use DB ---
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    email = data['email'].strip()
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    if Subscriber.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already subscribed'}), 409
    location = data.get('location', 'auto')
    subscriber = Subscriber(
        email=email,
        location=location,
        subscribed_at=datetime.now().isoformat()
    )
    db.session.add(subscriber)
    db.session.commit()
    try:
        send_welcome_email(email, location)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    return jsonify({
        'message': 'Successfully subscribed to temperature notifications',
        'email': email
    }), 201

# --- Update /api/unsubscribe to use DB ---
@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    email = data['email'].strip()
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        db.session.delete(subscriber)
        db.session.commit()
    return jsonify({
        'message': 'Successfully unsubscribed from temperature notifications',
        'email': email
    }), 200

@app.route('/api/register-device', methods=['POST'])
def register_device():
    data = request.get_json()
    push_token = data.get('push_token')
    platform = data.get('platform', 'expo')
    device_type = data.get('device_type', 'unknown')
    location = data.get('location', 'auto')  # Get location from request
    
    if not push_token:
        return jsonify({'error': 'Push token is required'}), 400
    
    try:
        # Check if device already exists
        existing_device = Device.query.filter_by(push_token=push_token).first()
        
        if existing_device:
            # Update existing device
            existing_device.platform = platform
            existing_device.device_type = device_type
            existing_device.location = location  # Update location
            existing_device.is_active = True
            existing_device.registered_at = datetime.utcnow()
        else:
            # Create new device
            new_device = Device(
                push_token=push_token,
                platform=platform,
                device_type=device_type,
                location=location  # Set location
            )
            db.session.add(new_device)
        
        db.session.commit()
        
        print(f"✅ Device registered: {platform} {device_type} at {location} - {push_token[:20]}...")
        
        return jsonify({
            'message': 'Device registered successfully',
            'device_id': existing_device.id if existing_device else new_device.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error registering device: {e}")
        return jsonify({'error': 'Failed to register device'}), 500

@app.route('/api/unregister-device', methods=['POST'])
def unregister_device():
    data = request.get_json()
    push_token = data.get('push_token')
    if not push_token:
        return jsonify({'error': 'Push token is required'}), 400
    device = Device.query.filter_by(push_token=push_token).first()
    if device:
        device.is_active = False
        db.session.commit()
        print(f"✅ Device unregistered: {device.platform} {device.device_type} - {push_token[:20]}...")
        # Add log entry for unregistration
        log = PushNotificationLog(
            device_id=device.id,
            push_token=device.push_token,
            platform=device.platform,
            device_type=device.device_type,
            title='Push notifications disabled',
            body='User disabled push notifications',
            data=None,
            status='unregistered',
            error=None
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Device unregistered successfully'})
    print(f"❌ Device not found for unregistration: {push_token[:20]}...")
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/check-temperatures', methods=['GET'])
def check_temperatures():
    """Check forecasted high temperatures and send notifications if conditions are met"""
    if not WEATHER_API_KEY:
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    notifications_sent = []
    processed_locations = set()  # Track locations to avoid duplicate push notifications
    
    for subscriber in Subscriber.query.all():
        try:
            location = subscriber.location
            if location == 'auto':
                location = 'New York'
            
            # Get forecasted high temperature for today
            forecast_url = f"{WEATHER_BASE_URL}/forecast.json"
            forecast_params = {
                'key': WEATHER_API_KEY,
                'q': location,
                'days': 1,
                'aqi': 'no',
                'alerts': 'no'
            }
            forecast_response = requests.get(forecast_url, params=forecast_params)
            if forecast_response.status_code != 200:
                print(f"Failed to get forecast for {location}: {forecast_response.status_code}")
                continue
            
            forecast_data = forecast_response.json()
            current_temp = forecast_data['forecast']['forecastday'][0]['day']['maxtemp_f']
            
            # Get historical data for today's date (last 30 years)
            today = datetime.now()
            historical_url = f"{WEATHER_BASE_URL}/history.json"
            
            # Calculate average temperature from historical data
            historical_temps = []
            for year in range(1, 31):  # Last 30 years
                try:
                    historical_date = today.replace(year=today.year - year)
                    historical_params = {
                        'key': WEATHER_API_KEY,
                        'q': location,
                        'dt': historical_date.strftime('%Y-%m-%d')
                    }
                    historical_response = requests.get(historical_url, params=historical_params)
                    
                    if historical_response.status_code == 200:
                        historical_data = historical_response.json()
                        if 'forecast' in historical_data and historical_data['forecast']['forecastday']:
                            historical_temp = historical_data['forecast']['forecastday'][0]['day']['maxtemp_f']
                            historical_temps.append(historical_temp)
                except Exception as e:
                    print(f"Error fetching historical data for {location} year {year}: {e}")
                    continue
            
            # Calculate average temperature
            if historical_temps:
                avg_temp = sum(historical_temps) / len(historical_temps)
                print(f"{location}: Current temp {current_temp}°F, Avg temp {avg_temp:.1f}°F, Diff {current_temp - avg_temp:.1f}°F")
            else:
                # Fallback to hardcoded average if historical data fails
                avg_temp = 85
                print(f"{location}: Using fallback avg temp {avg_temp}°F")
            
            # Check if temperature exceeds threshold
            if current_temp >= avg_temp + TEMP_THRESHOLD:
                print(f"🌡️ TEMPERATURE ALERT: {location} is {current_temp - avg_temp:.1f}°F hotter than average!")
                
                # Send email notification
                send_notification(subscriber.email, location, current_temp, avg_temp)
                notifications_sent.append({
                    'email': subscriber.email,
                    'location': location,
                    'current_temp': current_temp,
                    'avg_temp': avg_temp,
                    'threshold': TEMP_THRESHOLD
                })
                
                # Send push notification (only once per location)
                if location not in processed_locations:
                    send_push_notification(location, current_temp, avg_temp)
                    processed_locations.add(location)
            else:
                print(f"No alert for {location}: {current_temp}°F vs {avg_temp:.1f}°F avg (threshold: {TEMP_THRESHOLD}°F)")
                
        except Exception as e:
            print(f"Error processing subscriber {subscriber.email}: {e}")
            continue
    
    return jsonify({
        'message': f'Processed {len(Subscriber.query.all())} subscribers',
        'notifications_sent': len(notifications_sent),
        'threshold': TEMP_THRESHOLD,
        'details': notifications_sent
    })

def send_notification(email, location, current_temp, avg_temp, years=30):
    """Send climate alert notification to subscriber (HTML email)"""
    try:
        temp_diff = round(current_temp - avg_temp, 1)
        subject = f"🌡️ Climate Alert - {location} - IT'S TOO HOT!"
        html_body = render_template(
            'alert_email.html',
            location=location,
            current_temp=current_temp,
            avg_temp=avg_temp,
            temp_diff=temp_diff,
            years=years
        )
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
        print(f"Notification sent to {email}")
    except Exception as e:
        print(f"Failed to send notification to {email}: {e}")

def send_push_notification(location, current_temp, avg_temp, years=30):
    """Send push notification to devices in the specific location"""
    try:
        temp_diff = round(current_temp - avg_temp, 1)
        
        # Get active devices for this specific location
        devices = Device.query.filter_by(is_active=True, location=location).all()
        
        if not devices:
            print(f"No active devices found for location: {location}")
            return
        
        # For Expo push notifications, we need to send to Expo's servers
        # This is a simplified version - in production you'd use Expo's SDK
        expo_tokens = [device.push_token for device in devices if device.platform == 'expo']
        
        if expo_tokens:
            # Send to Expo push service
            expo_url = "https://exp.host/--/api/v2/push/send"
            
            messages = []
            for token in expo_tokens:
                messages.append({
                    "to": token,
                    "title": f"🌡️ IT'S TOO HOT! - {location}",
                    "body": f"Temperature is {temp_diff}°F hotter than average. Wear your shirt!",
                    "data": {
                        "location": location,
                        "current_temp": current_temp,
                        "avg_temp": avg_temp,
                        "temp_diff": temp_diff
                    },
                    "sound": "default",
                    "priority": "high"
                })
            
            # Send in batches of 100 (Expo limit)
            batch_size = 100
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                response = requests.post(expo_url, json=batch, headers={
                    'Content-Type': 'application/json'
                })
                
                if response.status_code == 200:
                    print(f"✅ Push notifications sent to {len(batch)} devices in {location}")
                else:
                    print(f"❌ Failed to send push notifications to {location}: {response.text}")
        else:
            print(f"No Expo devices found for location: {location}")
        
    except Exception as e:
        print(f"Failed to send push notifications for {location}: {e}")

# --- Update /api/subscribers to use DB ---
@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    subs = Subscriber.query.all()
    return jsonify({
        'subscribers': [s.as_dict() for s in subs],
        'count': len(subs)
    })

@app.route('/api/push-subscribers', methods=['GET'])
def get_push_subscribers():
    """Return all active push notification subscribers (Device table)"""
    devices = Device.query.filter_by(is_active=True).all()
    return jsonify({
        'subscribers': [d.as_dict() for d in devices],
        'count': len(devices)
    })

@app.route('/api/test-printful', methods=['GET'])
def test_printful_api():
    """Test Printful API connection"""
    try:
        success = test_printful_connection()
        return jsonify({
            'success': success,
            'message': 'Printful API connection test completed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/log-error', methods=['POST'])
def log_error():
    data = request.get_json()
    email = data.get('email', 'tendegrees@its2hot.org')
    error_message = data.get('error', 'No error message provided')
    context = data.get('context', 'No context provided')
    try:
        subject = f"[ITS2HOT] Mobile App Error Log - {context}"
        body = f"Error reported from mobile app:\n\nContext: {context}\nError: {error_message}\n\nFull data: {data}"
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            body=body
        )
        mail.send(msg)
        print(f"Error log email sent to {email}")
        return jsonify({'success': True, 'message': 'Error log sent via email'})
    except Exception as e:
        print(f"Failed to send error log email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Admin Auth Decorator ---
def check_auth(username, password):
    return username == 'admin' and password == 'evergreen'

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Utility: Load/Save JSON ---
def load_json_file(filename, default=None):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# --- Logging ---
def log_event(filename, event):
    logs = load_json_file(filename, default=[])
    logs.append(event)
    save_json_file(filename, logs)

# --- Expo Android Build URL Helper ---
EXPO_PROJECT_ID = "cd9501a1-6d26-4451-ab0a-54631514d4fe"
EXPO_BUILD_CACHE = {"url": None, "timestamp": 0}
EXPO_BUILD_CACHE_TTL = 300  # 5 minutes

def get_latest_expo_apk_url():
    now = time.time()
    if EXPO_BUILD_CACHE["url"] and now - EXPO_BUILD_CACHE["timestamp"] < EXPO_BUILD_CACHE_TTL:
        return EXPO_BUILD_CACHE["url"], None
    try:
        expo_token = os.getenv('EXPO_TOKEN')
        if not expo_token:
            return None, "EXPO_TOKEN environment variable is not set."
        
        print(f"🔍 Fetching Android builds with token: {expo_token[:10]}...")
        
        # Use the new EAS API endpoint
        endpoint = f"https://expo.dev/api/v2/projects/{EXPO_PROJECT_ID}/builds"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {expo_token}"
        }
        
        # Get builds for Android platform
        params = {
            "platform": "android",
            "limit": 1,
            "status": "finished"  # Only get completed builds
        }
        
        print(f"🔍 Trying endpoint: {endpoint}")
        resp = requests.get(endpoint, headers=headers, params=params)
        print(f"📱 Android API response status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            builds = data.get("data", [])
            print(f"📱 Found {len(builds)} Android builds")
            
            if builds:
                build = builds[0]
                print(f"📱 Latest build status: {build.get('status')}")
                print(f"📱 Latest build artifacts: {build.get('artifacts', {})}")
                
                # Try different artifact field names
                artifacts = build.get("artifacts", {})
                apk_url = (
                    artifacts.get("applicationArchiveUrl") or 
                    artifacts.get("url") or 
                    build.get("url")
                )
                
                if apk_url:
                    print(f"📱 APK URL found: {apk_url}")
                    EXPO_BUILD_CACHE["url"] = apk_url
                    EXPO_BUILD_CACHE["timestamp"] = now
                    return apk_url, None
                else:
                    print("❌ No APK artifact found in latest build")
                    print(f"❌ Build data: {build}")
                    return None, "No APK artifact found in latest build."
            else:
                print("❌ No builds found for this project")
                return None, "No builds found for this project."
        elif resp.status_code == 401:
            print("❌ Unauthorized - check your EXPO_TOKEN")
            return None, "Unauthorized - check your EXPO_TOKEN."
        elif resp.status_code == 404:
            print("❌ Project not found or access denied")
            return None, "Project not found or access denied."
        else:
            print(f"❌ Expo API returned status {resp.status_code}")
            print(f"❌ Response text: {resp.text[:200]}...")
            return None, f"Expo API error: {resp.status_code}"
        
    except Exception as e:
        print(f"❌ Failed to fetch Expo build: {e}")
        return None, f"Failed to fetch Expo build: {e}"

EXPO_IOS_BUILD_CACHE = {"url": None, "timestamp": 0}
EXPO_IOS_BUILD_CACHE_TTL = 300  # 5 minutes

def get_latest_expo_ios_url():
    now = time.time()
    if EXPO_IOS_BUILD_CACHE["url"] and now - EXPO_IOS_BUILD_CACHE["timestamp"] < EXPO_IOS_BUILD_CACHE_TTL:
        return EXPO_IOS_BUILD_CACHE["url"], None
    try:
        expo_token = os.getenv('EXPO_TOKEN')
        if not expo_token:
            return None, "EXPO_TOKEN environment variable is not set."
        
        print(f"🍎 Fetching iOS builds with token: {expo_token[:10]}...")
        
        # Use the new EAS API endpoint
        endpoint = f"https://expo.dev/api/v2/projects/{EXPO_PROJECT_ID}/builds"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {expo_token}"
        }
        
        # Get builds for iOS platform
        params = {
            "platform": "ios",
            "limit": 1,
            "status": "finished"  # Only get completed builds
        }
        
        print(f"🍎 Trying endpoint: {endpoint}")
        resp = requests.get(endpoint, headers=headers, params=params)
        print(f"🍎 iOS API response status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            builds = data.get("data", [])
            print(f"🍎 Found {len(builds)} iOS builds")
            
            if builds:
                build = builds[0]
                print(f"🍎 Latest build status: {build.get('status')}")
                print(f"🍎 Latest build artifacts: {build.get('artifacts', {})}")
                
                # Try different artifact field names
                artifacts = build.get("artifacts", {})
                ios_url = (
                    artifacts.get("applicationArchiveUrl") or 
                    artifacts.get("url") or 
                    build.get("url")
                )
                
                if ios_url:
                    print(f"🍎 iOS URL found: {ios_url}")
                    EXPO_IOS_BUILD_CACHE["url"] = ios_url
                    EXPO_IOS_BUILD_CACHE["timestamp"] = now
                    return ios_url, None
                else:
                    print("❌ No iOS artifact found in latest build")
                    print(f"❌ Build data: {build}")
                    return None, "No iOS artifact found in latest build."
            else:
                print("❌ No builds found for this project")
                return None, "No builds found for this project."
        elif resp.status_code == 401:
            print("❌ Unauthorized - check your EXPO_TOKEN")
            return None, "Unauthorized - check your EXPO_TOKEN."
        elif resp.status_code == 404:
            print("❌ Project not found or access denied")
            return None, "Project not found or access denied."
        else:
            print(f"❌ Expo API returned status {resp.status_code}")
            print(f"❌ Response text: {resp.text[:200]}...")
            return None, f"Expo API error: {resp.status_code}"
        
    except Exception as e:
        print(f"❌ Failed to fetch Expo build: {e}")
        return None, f"Failed to fetch Expo build: {e}"

# --- Admin Dashboard ---
@app.route('/admin', methods=['GET'])
@requires_auth
def admin_dashboard():
    email_subs = [s.as_dict() for s in Subscriber.query.all()]
    notif_log = load_json_file('notification_log.json', default=[])
    trigger_log = load_json_file('trigger_log.json', default=[])
    expo_apk_url, expo_apk_error = get_latest_expo_apk_url()
    expo_ios_url, expo_ios_error = get_latest_expo_ios_url()
    
    # Calculate total temperature alerts sent
    total_alerts = db.session.query(db.func.sum(SchedulerLog.alerts_triggered)).filter(
        SchedulerLog.status == 'success',
        SchedulerLog.alerts_triggered > 0
    ).scalar() or 0
    
    return render_template('admin.html',
        email_subs=email_subs,
        notif_log=notif_log,
        trigger_log=trigger_log,
        expo_apk_url=expo_apk_url,
        expo_apk_error=expo_apk_error,
        expo_ios_url=expo_ios_url,
        expo_ios_error=expo_ios_error,
        total_alerts=total_alerts)

# --- Resend Welcome Email ---
@app.route('/admin/resend-welcome', methods=['POST'])
@requires_auth
def admin_resend_welcome():
    data = request.get_json()
    email = data.get('email')
    location = data.get('location', 'auto')
    try:
        send_welcome_email(email, location)
        log_event('notification_log.json', {
            'type': 'welcome_email', 'email': email, 'timestamp': datetime.now().isoformat()
        })
        return jsonify({'success': True, 'message': f'Resent welcome email to {email}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Send Test Trigger Email ---
@app.route('/admin/send-test-email', methods=['POST'])
@requires_auth
def admin_send_test_email():
    data = request.get_json()
    email = data.get('email')
    try:
        # Use placeholder values for test
        html_body = render_template(
            'alert_email.html',
            location='New York',
            current_temp=104,
            avg_temp=87,
            temp_diff=17,
            years=30
        )
        msg = Message(
            'Test Climate Alert from IT\'S TOO HOT!',
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
        log_event('notification_log.json', {
            'type': 'test_email', 'email': email, 'timestamp': datetime.now().isoformat()
        })
        return jsonify({'success': True, 'message': f'Test alert email sent to {email}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Send Test Push Notification ---
@app.route('/admin/send-test-notification', methods=['POST'])
@requires_auth
def admin_send_test_notification():
    data = request.get_json()
    endpoint = data.get('endpoint')
    # You would implement your push notification logic here
    # For now, just log the attempt
    log_event('notification_log.json', {
        'type': 'test_push', 'endpoint': endpoint, 'timestamp': datetime.now().isoformat()
    })
    return jsonify({'success': True, 'message': f'Test push notification sent to {endpoint}'})

# --- Log App Trigger Event ---
def log_trigger_event(event):
    log_event('trigger_log.json', event)

# --- Log Scheduler Activity ---
def log_scheduler_activity(trigger_type, locations_checked, temperatures_found, alerts_triggered, 
                          threshold_used, status, error_message=None, duration_ms=None):
    """Log scheduler activity to database"""
    try:
        log = SchedulerLog(
            trigger_type=trigger_type,
            locations_checked=json.dumps(locations_checked) if locations_checked else None,
            temperatures_found=json.dumps(temperatures_found) if temperatures_found else None,
            alerts_triggered=alerts_triggered,
            threshold_used=threshold_used,
            status=status,
            error_message=error_message,
            duration_ms=duration_ms
        )
        db.session.add(log)
        db.session.commit()
        print(f"📊 Scheduler log: {trigger_type} - {status} - {alerts_triggered} alerts")
    except Exception as e:
        print(f"❌ Failed to log scheduler activity: {e}")

def get_cloud_scheduler_job_info(job_name):
    """Get information about a Cloud Scheduler job including next run time"""
    try:
        # Get project ID from environment or metadata
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            # Try to get from metadata service
            try:
                metadata_response = requests.get('http://metadata.google.internal/computeMetadata/v1/project/project-id', 
                                              headers={'Metadata-Flavor': 'Google'}, timeout=2)
                if metadata_response.status_code == 200:
                    project_id = metadata_response.text
                    print(f"🔍 Got project ID from metadata: {project_id}")
                else:
                    print(f"❌ Metadata service returned {metadata_response.status_code}")
            except Exception as e:
                print(f"❌ Error getting project ID from metadata: {e}")
                pass
        
        if not project_id:
            print(f"❌ Could not determine Google Cloud project ID for job {job_name}")
            return None
        
        print(f"🔍 Using project ID: {project_id}")
        
        # Get authentication token
        try:
            auth_response = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token', 
                                       headers={'Metadata-Flavor': 'Google'}, timeout=2)
            if auth_response.status_code != 200:
                print(f"❌ Failed to get auth token for job {job_name}: HTTP {auth_response.status_code}")
                return None
            token = auth_response.json()['access_token']
            print(f"🔍 Got auth token successfully")
        except Exception as e:
            print(f"❌ Failed to get auth token for job {job_name}: {e}")
            return None
        
        # Query Cloud Scheduler API
        base_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/us-central1"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        job_url = f"{base_url}/jobs/{job_name}"
        print(f"🔍 Querying Cloud Scheduler API: {job_url}")
        response = requests.get(job_url, headers=headers, timeout=10)
        
        print(f"🔍 Cloud Scheduler API response: HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"🔍 Response body: {response.text}")
        
        if response.status_code == 200:
            job_data = response.json()
            print(f"🔍 Job data: {job_data}")
            return {
                'name': job_data.get('name'),
                'state': job_data.get('state'),
                'schedule': job_data.get('schedule'),
                'timeZone': job_data.get('timeZone'),
                'lastAttemptTime': job_data.get('lastAttemptTime'),
                'nextRunTime': job_data.get('nextRunTime')
            }
        else:
            print(f"❌ Failed to get job info for {job_name}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting Cloud Scheduler job info for {job_name}: {e}")
        return None

# --- API to get logs (for dashboard AJAX) ---
@app.route('/admin/logs', methods=['GET'])
@requires_auth
def admin_get_logs():
    notif_log = load_json_file('notification_log.json', default=[])
    trigger_log = load_json_file('trigger_log.json', default=[])
    return jsonify({'notification_log': notif_log, 'trigger_log': trigger_log})

# --- Expo Push Receipt Fetcher ---
RECEIPT_FETCH_INTERVAL = 900  # 15 minutes
RECEIPT_LOOKBACK_MINUTES = 30  # How far back to look for tickets

def fetch_and_update_push_receipts():
    with app.app_context():
        # Find logs with ticket_id and status 'success' but not yet updated with receipt
        cutoff = datetime.utcnow() - timedelta(minutes=RECEIPT_LOOKBACK_MINUTES)
        logs = PushNotificationLog.query.filter(
            and_(
                PushNotificationLog.status == 'success',
                PushNotificationLog.timestamp >= cutoff,
                PushNotificationLog.data != None
            )
        ).all()
        ticket_id_map = {}
        for log in logs:
            try:
                data = json.loads(log.data)
                ticket_id = data.get('ticket_id')
                if ticket_id:
                    ticket_id_map[ticket_id] = log
            except Exception:
                continue
        if not ticket_id_map:
            return
        # Query Expo receipts in batches of 1000
        ticket_ids = list(ticket_id_map.keys())
        batch_size = 1000
        for i in range(0, len(ticket_ids), batch_size):
            batch = ticket_ids[i:i+batch_size]
            try:
                resp = requests.post(
                    'https://exp.host/--/api/v2/push/getReceipts',
                    headers={'Content-Type': 'application/json'},
                    json={'ids': batch}
                )
                if resp.status_code == 200:
                    data = resp.json().get('data', {})
                    for tid, receipt in data.items():
                        log = ticket_id_map.get(tid)
                        if log:
                            # Update log with receipt status and details
                            log.data = json.dumps({**json.loads(log.data), 'receipt': receipt})
                            if receipt.get('status') == 'ok':
                                log.status = 'delivered'
                                log.error = None
                            else:
                                log.status = 'delivery_error'
                                log.error = json.dumps(receipt)
                    db.session.commit()
            except Exception as e:
                print(f"[ERROR] Failed to fetch push receipts: {e}")

def start_receipt_fetcher():
    def run():
        while True:
            try:
                fetch_and_update_push_receipts()
            except Exception as e:
                print(f"[ERROR] in receipt fetcher: {e}")
            time.sleep(RECEIPT_FETCH_INTERVAL)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    atexit.register(lambda: t.join(timeout=1))

start_receipt_fetcher()

# --- Update /api/send-push-notification to log ticket info ---
@app.route('/api/send-push-notification', methods=['POST'])
def api_send_push_notification():
    data = request.get_json()
    title = data.get('title', "🌡️ IT'S TOO HOT! - " + (data.get('location') or ''))
    body = data.get('body', 'Temperature alert!')
    url = data.get('url', '/')
    location = data.get('location')
    current_temp = data.get('current_temp')
    avg_temp = data.get('avg_temp')
    
    devices = Device.query.filter_by(is_active=True).all()
    expo_tokens = [device.push_token for device in devices if device.platform == 'expo']
    if not expo_tokens:
        # Log the attempt
        log = PushNotificationLog(
            device_id=None,
            push_token=None,
            platform='expo',
            device_type=None,
            title=title,
            body=body,
            data=json.dumps({'url': url, 'location': location, 'current_temp': current_temp, 'avg_temp': avg_temp}),
            status='failure',
            error='No Expo push tokens registered'
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': False, 'message': 'No Expo push tokens registered', 'total_subscribers': 0}), 200
    
    expo_url = "https://exp.host/--/api/v2/push/send"
    messages = []
    device_map = {}
    for device in devices:
        if device.platform == 'expo':
            msg = {
                "to": device.push_token,
                "title": title,
                "body": body,
                "data": {
                    "url": url,
                    "location": location,
                    "current_temp": current_temp,
                    "avg_temp": avg_temp
                },
                "sound": "default",
                "priority": "high"
            }
            messages.append(msg)
            device_map[device.push_token] = device
    batch_size = 100
    successful_sends = 0
    failed_sends = 0
    errors = []
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        tokens = [msg['to'] for msg in batch]
        try:
            response = requests.post(expo_url, json=batch, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                resp_data = response.json()
                tickets = resp_data.get('data', [])
                for idx, ticket in enumerate(tickets):
                    msg = batch[idx]
                    device = device_map.get(msg['to'])
                    ticket_id = ticket.get('id')
                    log_data = {
                        'url': url,
                        'ticket_id': ticket_id,
                        'ticket_status': ticket.get('status'),
                        'ticket_message': ticket.get('message'),
                        'ticket_details': ticket.get('details')
                    }
                    if ticket.get('status') == 'ok':
                        successful_sends += 1
                        log = PushNotificationLog(
                            device_id=device.id if device else None,
                            push_token=msg['to'],
                            platform='expo',
                            device_type=device.device_type if device else None,
                            title=title,
                            body=body,
                            data=json.dumps(log_data),
                            status='success',
                            error=None
                        )
                    else:
                        failed_sends += 1
                        errors.append(ticket.get('message'))
                        log = PushNotificationLog(
                            device_id=device.id if device else None,
                            push_token=msg['to'],
                            platform='expo',
                            device_type=device.device_type if device else None,
                            title=title,
                            body=body,
                            data=json.dumps(log_data),
                            status='ticket_error',
                            error=json.dumps(ticket)
                        )
                    db.session.add(log)
                db.session.commit()
            else:
                failed_sends += len(batch)
                errors.append(response.text)
                for msg in batch:
                    device = device_map.get(msg['to'])
                    log = PushNotificationLog(
                        device_id=device.id if device else None,
                        push_token=msg['to'],
                        platform='expo',
                        device_type=device.device_type if device else None,
                        title=title,
                        body=body,
                        data=json.dumps({'url': url}),
                        status='failure',
                        error=response.text
                    )
                    db.session.add(log)
                db.session.commit()
        except Exception as e:
            failed_sends += len(batch)
            errors.append(str(e))
            for msg in batch:
                device = device_map.get(msg['to'])
                log = PushNotificationLog(
                    device_id=device.id if device else None,
                    push_token=msg['to'],
                    platform='expo',
                    device_type=device.device_type if device else None,
                    title=title,
                    body=body,
                    data=json.dumps({'url': url}),
                    status='failure',
                    error=str(e)
                )
                db.session.add(log)
            db.session.commit()
    return jsonify({
        'success': failed_sends == 0,
        'message': 'Push notifications sent' if failed_sends == 0 else 'Some notifications failed',
        'successful_sends': successful_sends,
        'failed_sends': failed_sends,
        'total_subscribers': len(expo_tokens),
        'errors': errors
    })

# --- API: Log Push Notification Attempt ---
@app.route('/api/log-push', methods=['POST'])
def log_push():
    data = request.get_json()
    log = PushNotificationLog(
        device_id=data.get('device_id'),
        push_token=data.get('push_token'),
        platform=data.get('platform'),
        device_type=data.get('device_type'),
        title=data.get('title'),
        body=data.get('body'),
        data=json.dumps(data.get('data')) if data.get('data') else None,
        status=data.get('status'),
        error=data.get('error')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True, 'log_id': log.id})

# --- API: Log Debug/Error Info ---
@app.route('/api/log-debug', methods=['POST'])
def log_debug():
    data = request.get_json()
    
    # Map mobile app fields to database fields
    source = data.get('platform') or data.get('source')  # Mobile app sends 'platform', backend expects 'source'
    device_id = data.get('deviceId') or data.get('device_id')
    email = data.get('email')
    message = data.get('message')
    context = data.get('context')
    
    # Add extra device info to context if available
    device_info = []
    if data.get('deviceName'):
        device_info.append(f"Device: {data.get('deviceName')}")
    if data.get('deviceModel'):
        device_info.append(f"Model: {data.get('deviceModel')}")
    if data.get('level'):
        device_info.append(f"Level: {data.get('level')}")
    
    if device_info:
        context = f"{context or ''} | {' | '.join(device_info)}"
    
    log = DebugLog(
        source=source,
        device_id=device_id,
        email=email,
        message=message,
        context=context
    )
    db.session.add(log)
    db.session.commit()
    
    print(f"📱 Mobile log saved: {source} - {message[:50]}...")
    return jsonify({'success': True, 'log_id': log.id})

# --- API: Fetch Logs ---
@app.route('/api/logs', methods=['GET'])
def get_logs():
    log_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 100))
    if log_type == 'push':
        logs = PushNotificationLog.query.order_by(PushNotificationLog.timestamp.desc()).limit(limit).all()
        return jsonify({'logs': [l.as_dict() for l in logs]})
    elif log_type == 'debug':
        logs = DebugLog.query.order_by(DebugLog.timestamp.desc()).limit(limit).all()
        return jsonify({'logs': [l.as_dict() for l in logs]})
    elif log_type == 'scheduler':
        logs = SchedulerLog.query.order_by(SchedulerLog.timestamp.desc()).limit(limit).all()
        return jsonify({'logs': [l.as_dict() for l in logs]})
    else:
        push_logs = PushNotificationLog.query.order_by(PushNotificationLog.timestamp.desc()).limit(limit).all()
        debug_logs = DebugLog.query.order_by(DebugLog.timestamp.desc()).limit(limit).all()
        scheduler_logs = SchedulerLog.query.order_by(SchedulerLog.timestamp.desc()).limit(limit).all()
        return jsonify({
            'push_logs': [l.as_dict() for l in push_logs],
            'debug_logs': [l.as_dict() for l in debug_logs],
            'scheduler_logs': [l.as_dict() for l in scheduler_logs]
        })

# --- API: Delete/Unsubscribe Push Subscriber ---
@app.route('/api/push-subscriber/<int:device_id>', methods=['DELETE'])
def delete_push_subscriber(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'success': False, 'error': 'Device not found'}), 404
    db.session.delete(device)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Device {device_id} deleted'})

# --- API: Test Temperature Alert (Custom or Real Data) ---
@app.route('/api/test-temperature-alert', methods=['POST'])
def test_temperature_alert():
    data = request.get_json()
    location = data.get('location', 'New York')
    use_real_data = data.get('use_real_data', False)
    test_threshold = data.get('threshold', TEMP_THRESHOLD)  # Use provided threshold or current setting
    
    if use_real_data:
        # Fetch forecasted high temperature for today
        forecast_url = f"{WEATHER_BASE_URL}/forecast.json"
        forecast_params = {'key': WEATHER_API_KEY, 'q': location, 'days': 1, 'aqi': 'no', 'alerts': 'no'}
        forecast_response = requests.get(forecast_url, params=forecast_params)
        if forecast_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to fetch forecasted weather'}), 500
        forecast_data = forecast_response.json()
        current_temp = forecast_data['forecast']['forecastday'][0]['day']['maxtemp_f']
        today = datetime.now()
        avg_temp = 85
    else:
        current_temp = data.get('current_temp', 100)
        avg_temp = data.get('avg_temp', 85)

    # Check if temperature exceeds the test threshold
    temp_diff = current_temp - avg_temp
    should_alert = temp_diff >= test_threshold
    
    if should_alert:
        # Send push notifications
        send_push_notification(location, current_temp, avg_temp)

        # Send emails to all subscribers
        for subscriber in Subscriber.query.all():
            try:
                send_notification(subscriber.email, location, current_temp, avg_temp, years=30)
            except Exception as e:
                print(f"[ERROR] Failed to send test alert email to {subscriber.email}: {e}")

    return jsonify({
        'success': True,
        'location': location,
        'current_temp': current_temp,
        'avg_temp': avg_temp,
        'temp_diff': round(temp_diff, 1),
        'threshold': test_threshold,
        'alert_triggered': should_alert
    })

# --- Scheduler Endpoint for Cloud Scheduler ---
@app.route('/api/scheduler/check-temperatures', methods=['GET'])
def scheduler_check_temperatures():
    """Scheduler endpoint for Cloud Scheduler to trigger temperature checks"""
    start_time = datetime.now()
    trigger_type = request.args.get('trigger_type', 'cloud_scheduler')
    
    try:
        print(f"🌡️ Scheduler triggered temperature check at {start_time}")
        
        # Call the existing temperature check function
        response = check_temperatures()
        
        # Extract JSON data from the response
        if hasattr(response, 'get_json'):
            result = response.get_json()
        else:
            # If it's already a dict, use it directly
            result = response if isinstance(response, dict) else {}
        
        # Calculate duration
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Extract data for logging
        notifications_sent = result.get('notifications_sent', 0)
        details = result.get('details', [])
        
        # Extract locations and temperatures from details
        locations_checked = list(set([detail.get('location', 'Unknown') for detail in details]))
        temperatures_found = {detail.get('location', 'Unknown'): detail.get('current_temp', 0) for detail in details}
        
        # Log the activity
        log_scheduler_activity(
            trigger_type=trigger_type,
            locations_checked=locations_checked,
            temperatures_found=temperatures_found,
            alerts_triggered=notifications_sent,
            threshold_used=TEMP_THRESHOLD,
            status='success',
            duration_ms=duration_ms
        )
        
        if notifications_sent > 0:
            print(f"✅ Scheduler sent {notifications_sent} temperature alerts")
        else:
            print("ℹ️ Scheduler: No temperature alerts triggered")
        
        return jsonify({
            'success': True,
            'timestamp': start_time.isoformat(),
            'result': result,
            'duration_ms': duration_ms
        })
        
    except Exception as e:
        error_msg = f"Scheduler temperature check failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log the error
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        log_scheduler_activity(
            trigger_type=trigger_type,
            locations_checked=[],
            temperatures_found={},
            alerts_triggered=0,
            threshold_used=TEMP_THRESHOLD,
            status='error',
            error_message=error_msg,
            duration_ms=duration_ms
        )
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'timestamp': start_time.isoformat(),
            'duration_ms': duration_ms
        })

# --- Scheduler Health Check ---
@app.route('/api/scheduler/health', methods=['GET'])
def scheduler_health():
    """Health check endpoint for the scheduler"""
    try:
        # Check if we can access the database
        subscriber_count = Subscriber.query.count()
        device_count = Device.query.filter_by(is_active=True).count()
        
        # Check if weather API is accessible
        weather_status = 'unknown'
        if WEATHER_API_KEY:
            try:
                # Quick test of weather API
                test_response = requests.get(f"{WEATHER_BASE_URL}/current.json", 
                                          params={'key': WEATHER_API_KEY, 'q': 'New York'}, 
                                          timeout=5)
                weather_status = 'healthy' if test_response.status_code == 200 else 'error'
            except:
                weather_status = 'error'
        
        # Get recent scheduler activity
        recent_logs = SchedulerLog.query.order_by(SchedulerLog.timestamp.desc()).limit(5).all()
        last_check = recent_logs[0].timestamp if recent_logs else None
        
        # Debug timestamp information
        if last_check:
            now = datetime.now()
            diff_seconds = (now - last_check).total_seconds()
            print(f"🔍 Scheduler health debug: last_check={last_check}, now={now}, diff_seconds={diff_seconds}")
        
        # Get actual Cloud Scheduler job information
        job_name = None
        if CHECK_FREQUENCY == 'hourly':
            job_name = 'hourly-temperature-check'
            active_job = "hourly"
        elif CHECK_FREQUENCY == 'daily':
            job_name = 'daily-temperature-check'
            active_job = "daily"
        else:
            active_job = CHECK_FREQUENCY
        
        # Query Cloud Scheduler for actual next run time
        next_check_info = "Next check: Unknown"
        if job_name:
            job_info = get_cloud_scheduler_job_info(job_name)
            if job_info and job_info.get('nextRunTime'):
                try:
                    # Parse the nextRunTime (ISO 8601 format)
                    next_run_time = datetime.fromisoformat(job_info['nextRunTime'].replace('Z', '+00:00'))
                    # Convert to local time (assuming UTC)
                    next_run_local = next_run_time.replace(tzinfo=None)
                    next_check_info = f"Next check: {next_run_local.strftime('%I:%M %p')}"
                    print(f"🔍 Cloud Scheduler job {job_name} next run: {next_run_local}")
                except Exception as e:
                    print(f"❌ Error parsing next run time for {job_name}: {e}")
                    # Fallback to calculated time
                    if last_check:
                        if CHECK_FREQUENCY == 'hourly':
                            next_check_time = last_check + timedelta(hours=1)
                            now = datetime.now()
                            while next_check_time <= now:
                                next_check_time += timedelta(hours=1)
                            next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')}"
                        elif CHECK_FREQUENCY == 'daily':
                            tomorrow = last_check.date() + timedelta(days=1)
                            next_check_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=8))
                            now = datetime.now()
                            while next_check_time <= now:
                                next_check_time += timedelta(days=1)
                            next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')} tomorrow"
                    else:
                        # No last check, use current time + 1 hour for hourly
                        if CHECK_FREQUENCY == 'hourly':
                            now = datetime.now()
                            next_check_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                            next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')}"
                        elif CHECK_FREQUENCY == 'daily':
                            tomorrow = datetime.now().date() + timedelta(days=1)
                            next_check_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=8))
                            next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')} tomorrow"
            else:
                print(f"❌ Could not get Cloud Scheduler job info for {job_name}")
                # Fallback to calculated time (same logic as above)
                if last_check:
                    if CHECK_FREQUENCY == 'hourly':
                        next_check_time = last_check + timedelta(hours=1)
                        now = datetime.now()
                        while next_check_time <= now:
                            next_check_time += timedelta(hours=1)
                        next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')}"
                    elif CHECK_FREQUENCY == 'daily':
                        tomorrow = last_check.date() + timedelta(days=1)
                        next_check_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=8))
                        now = datetime.now()
                        while next_check_time <= now:
                            next_check_time += timedelta(days=1)
                        next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')} tomorrow"
                else:
                    if CHECK_FREQUENCY == 'hourly':
                        now = datetime.now()
                        next_check_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                        next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')}"
                    elif CHECK_FREQUENCY == 'daily':
                        tomorrow = datetime.now().date() + timedelta(days=1)
                        next_check_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=8))
                        next_check_info = f"Next check: {next_check_time.strftime('%I:%M %p')} tomorrow"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'subscribers': subscriber_count,
            'devices': device_count,
            'weather_api': weather_status,
            'last_check': last_check.isoformat() if last_check else None,
            'next_check_info': next_check_info,
            'threshold': TEMP_THRESHOLD,
            'frequency': CHECK_FREQUENCY,
            'active_job': active_job
        })
    except Exception as e:
        # Log the error
        log_scheduler_activity(
            trigger_type='health_check',
            locations_checked=[],
            temperatures_found={},
            alerts_triggered=0,
            threshold_used=TEMP_THRESHOLD,
            status='error',
            error_message=f'Scheduler health check failed: {str(e)}'
        )
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scheduler/job-control', methods=['POST'])
@requires_auth
def scheduler_job_control():
    """Control Cloud Scheduler jobs (pause/resume)"""
    try:
        data = request.get_json()
        job_name = data.get('job_name')
        action = data.get('action')
        
        if not job_name or not action:
            return jsonify({'success': False, 'error': 'Missing job_name or action'}), 400
        
        if action not in ['pause', 'resume']:
            return jsonify({'success': False, 'error': 'Action must be pause or resume'}), 400
        
        # Get project ID from environment or metadata
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            # Try to get from metadata service
            try:
                metadata_response = requests.get('http://metadata.google.internal/computeMetadata/v1/project/project-id', 
                                              headers={'Metadata-Flavor': 'Google'}, timeout=2)
                if metadata_response.status_code == 200:
                    project_id = metadata_response.text
            except:
                pass
        
        if not project_id:
            error_msg = "Could not determine Google Cloud project ID"
            log_scheduler_activity(
                trigger_type='job_control',
                locations_checked=[],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='error',
                error_message=f'{error_msg}: {job_name} {action}'
            )
            return jsonify({'success': False, 'error': error_msg}), 500
        
        # Use Cloud Scheduler REST API
        import requests
        from google.auth import default
        from google.auth.transport.requests import Request
        
        # Get credentials
        credentials, _ = default()
        credentials.refresh(Request())
        
        # Base URL for Cloud Scheduler API
        base_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/us-central1/jobs"
        headers = {
            'Authorization': f'Bearer {credentials.token}',
            'Content-Type': 'application/json'
        }
        
        # Make the API call
        control_url = f"{base_url}/{job_name}:{action}"
        response = requests.post(control_url, headers=headers)
        
        if response.status_code == 200:
            success_msg = f"Successfully {action}d {job_name}"
            print(f"✅ {success_msg}")
            log_scheduler_activity(
                trigger_type='job_control',
                locations_checked=[job_name],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='success',
                error_message=None
            )
            return jsonify({'success': True, 'message': success_msg})
        else:
            error_msg = f"Failed to {action} {job_name}: HTTP {response.status_code}"
            print(f"❌ {error_msg}")
            log_scheduler_activity(
                trigger_type='job_control',
                locations_checked=[job_name],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='error',
                error_message=f'{error_msg} - Response: {response.text}'
            )
            return jsonify({'success': False, 'error': error_msg}), 500
            
    except Exception as e:
        error_msg = f"Error controlling scheduler job: {str(e)}"
        print(f"❌ {error_msg}")
        log_scheduler_activity(
            trigger_type='job_control',
            locations_checked=[job_name] if 'job_name' in locals() else [],
            temperatures_found={},
            alerts_triggered=0,
            threshold_used=TEMP_THRESHOLD,
            status='error',
            error_message=error_msg
        )
        return jsonify({'success': False, 'error': error_msg}), 500

import os
import time
import subprocess

github_cache = {'data': None, 'timestamp': 0}
GITHUB_CACHE_TTL = 3600  # 1 hour
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def github_headers():
    headers = {'Accept': 'application/vnd.github+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

@app.route('/admin/time-tracking')
@requires_auth
def time_tracking():
    now = time.time()
    # Use cache if available and not expired
    if github_cache['data'] and now - github_cache['timestamp'] < GITHUB_CACHE_TTL:
        print('[DEBUG] Using cached GitHub commit data')
        rows, total_hours, total_mins, error = github_cache['data']
        return render_template('time_tracking.html', rows=rows, total_hours=total_hours, total_mins=total_mins, error=error)
    
    if not GITHUB_TOKEN:
        print('[WARNING] GITHUB_TOKEN is not set! Using unauthenticated GitHub API requests.')
    else:
        print('[DEBUG] Using GITHUB_TOKEN for authenticated GitHub API requests.')
    
    try:
        # First, get all commits from GitHub API
        commits = []
        page = 1
        per_page = 100
        
        while True:
            api_url = f'https://api.github.com/repos/151henry151/too-hot/commits?per_page={per_page}&page={page}'
            resp = requests.get(api_url, headers=github_headers())
            if resp.status_code != 200:
                raise Exception(f'GitHub API error: {resp.status_code}')
            data = resp.json()
            
            # If no more commits, break
            if not data:
                break
                
            for c in data:
                commit = c['sha']
                msg = c['commit']['message']
                date_str = c['commit']['committer']['date']
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                commits.append({'hash': commit, 'datetime': dt, 'msg': msg})
            
            # If we got fewer than per_page commits, we've reached the end
            if len(data) < per_page:
                break
                
            page += 1
        
        # Sort by datetime descending (newest first)
        commits.sort(key=lambda x: x['datetime'], reverse=True)
        
        # Filter out time tracking commits (robust substring check)
        filtered_commits = []
        for c in commits:
            msg_lc = c['msg'].lower()
            if not (
                'time tracking' in msg_lc or
                'time-tracking' in msg_lc or
                'timetracking' in msg_lc or
                'time_tracking' in msg_lc
            ):
                filtered_commits.append(c)
        commits = filtered_commits
        
        # Now efficiently process commits using database
        rows = []
        total_minutes = 0
        any_missing_stats = False
        commits_to_fetch = []
        
        # Check which commits we need to fetch from GitHub
        for i, c in enumerate(commits):
            commit_hash = c['hash']
            
            # Check if we already have this commit in the database
            existing_commit = CommitInfo.query.filter_by(commit_hash=commit_hash).first()
            
            if existing_commit:
                # Use existing data
                lines_changed = existing_commit.lines_changed
                time_spent = existing_commit.time_spent_minutes
                if time_spent is None:
                    # Calculate time spent if not stored
                    if i == len(commits) - 1:
                        time_spent = 190  # Special case for initial commit
                    else:
                        delta = (c['datetime'] - commits[i+1]['datetime']).total_seconds() / 60
                        if delta >= 120:
                            time_spent = min(lines_changed * 3 if lines_changed else 120, 180)
                        else:
                            time_spent = min(max(int(delta), 0), 120)
                    
                    # Update the database with calculated time
                    existing_commit.time_spent_minutes = time_spent
                    existing_commit.last_updated = datetime.utcnow()
                    db.session.commit()
            else:
                # Need to fetch this commit's stats
                commits_to_fetch.append((i, c))
                lines_changed = None
                time_spent = None
            
            # Calculate time spent if not already calculated
            if time_spent is None:
                if i == len(commits) - 1:
                    time_spent = 190  # Special case for initial commit
                else:
                    delta = (c['datetime'] - commits[i+1]['datetime']).total_seconds() / 60
                    if delta >= 120:
                        time_spent = min(lines_changed * 3 if lines_changed else 120, 180)
                    else:
                        time_spent = min(max(int(delta), 0), 120)
            
            total_minutes += time_spent
            
            # Format datetime as MM-DD h:mm AM/PM in US Eastern Time
            dt_eastern = c['datetime'].astimezone(timezone('US/Eastern'))
            dt_str = dt_eastern.strftime('%m-%d %I:%M %p')
            
            rows.append({
                'hash': c['hash'][:7],
                'full_hash': c['hash'],
                'msg': c['msg'],
                'datetime': dt_str,
                'time_spent': time_spent,
                'lines_changed': lines_changed
            })
        
        # Fetch missing commit stats in batches to avoid rate limiting
        if commits_to_fetch:
            print(f'[DEBUG] Fetching stats for {len(commits_to_fetch)} commits')
            for i, (index, c) in enumerate(commits_to_fetch):
                try:
                    stats_url = f'https://api.github.com/repos/151henry151/too-hot/commits/{c["hash"]}'
                    stats_resp = requests.get(stats_url, headers=github_headers())
                    
                    if stats_resp.status_code == 200:
                        stats = stats_resp.json().get('stats', {})
                        additions = stats.get('additions', 0)
                        deletions = stats.get('deletions', 0)
                        lines_changed = additions + deletions
                        
                        # Calculate time spent
                        if index == len(commits) - 1:
                            time_spent = 190  # Special case for initial commit
                        else:
                            delta = (c['datetime'] - commits[index+1]['datetime']).total_seconds() / 60
                            if delta >= 120:
                                time_spent = min(lines_changed * 3, 180)
                            else:
                                time_spent = min(max(int(delta), 0), 120)
                        
                        # Store in database
                        commit_info = CommitInfo(
                            commit_hash=c['hash'],
                            commit_message=c['msg'],
                            commit_date=c['datetime'],
                            lines_added=additions,
                            lines_deleted=deletions,
                            lines_changed=lines_changed,
                            time_spent_minutes=time_spent
                        )
                        db.session.add(commit_info)
                        
                        # Update the row with fetched data
                        rows[index]['lines_changed'] = lines_changed
                        rows[index]['time_spent'] = time_spent
                        
                    else:
                        any_missing_stats = True
                        rows[index]['lines_changed'] = None
                        
                    # Add small delay to avoid rate limiting
                    if i < len(commits_to_fetch) - 1:
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f'[ERROR] Failed to fetch stats for commit {c["hash"]}: {e}')
                    any_missing_stats = True
                    rows[index]['lines_changed'] = None
            
            # Commit all database changes
            try:
                db.session.commit()
            except Exception as e:
                print(f'[ERROR] Failed to commit database changes: {e}')
                db.session.rollback()
        
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        
        github_cache['data'] = (rows, total_hours, total_mins, None)
        github_cache['timestamp'] = now
        
        return render_template('time_tracking.html', rows=rows, total_hours=total_hours, total_mins=total_mins, error=None, any_missing_stats=any_missing_stats)
        
    except Exception as e:
        err_msg = f"Failed to fetch commit history: {e}"
        if not GITHUB_TOKEN:
            err_msg += " (No GITHUB_TOKEN set; using unauthenticated API calls with low rate limit)"
        github_cache['data'] = ([], 0, 0, err_msg)
        github_cache['timestamp'] = now
        return render_template('time_tracking.html', rows=[], total_hours=0, total_mins=0, error=err_msg)

@app.route('/admin/delete-subscriber', methods=['POST'])
@requires_auth
def admin_delete_subscriber():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Email required'}), 400
    sub = Subscriber.query.filter_by(email=email).first()
    if not sub:
        return jsonify({'success': False, 'error': 'Subscriber not found'}), 404
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Subscriber {email} deleted'})

@app.route('/admin/mobile-logs', methods=['GET'])
@requires_auth
def admin_mobile_logs():
    logs = DebugLog.query.filter(DebugLog.source.in_(['android', 'ios'])).order_by(DebugLog.timestamp.desc()).limit(100).all()
    return jsonify({'logs': [l.as_dict() for l in logs]})

# --- Settings API Endpoints ---
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current temperature alert settings"""
    return jsonify({
        'threshold': TEMP_THRESHOLD,
        'frequency': CHECK_FREQUENCY
    })

def update_cloud_scheduler_jobs(frequency):
    """Update Cloud Scheduler jobs based on frequency setting"""
    try:
        # Get project ID from environment or metadata
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            # Try to get from metadata service
            try:
                import requests
                metadata_response = requests.get('http://metadata.google.internal/computeMetadata/v1/project/project-id', 
                                              headers={'Metadata-Flavor': 'Google'}, timeout=2)
                if metadata_response.status_code == 200:
                    project_id = metadata_response.text
            except:
                pass
        
        if not project_id:
            error_msg = "Could not determine Google Cloud project ID"
            print(f"❌ {error_msg}")
            log_scheduler_activity(
                trigger_type='settings_update',
                locations_checked=[],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='error',
                error_message=f'{error_msg} - Frequency: {frequency}'
            )
            return False
        
        # Use Cloud Scheduler REST API instead of gcloud
        import requests
        try:
            from google.auth import default
            from google.auth.transport.requests import Request
            
            # Get credentials
            credentials, _ = default()
            credentials.refresh(Request())
            token = credentials.token
        except ImportError:
            error_msg = "google-auth module not available - cannot update Cloud Scheduler jobs"
            print(f"❌ {error_msg}")
            log_scheduler_activity(
                trigger_type='settings_update',
                locations_checked=[],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='error',
                error_message=f'{error_msg} - Frequency: {frequency}'
            )
            return False
        except Exception as e:
            error_msg = f"Failed to get Google Cloud credentials: {e}"
            print(f"❌ {error_msg}")
            log_scheduler_activity(
                trigger_type='settings_update',
                locations_checked=[],
                temperatures_found={},
                alerts_triggered=0,
                threshold_used=TEMP_THRESHOLD,
                status='error',
                error_message=f'{error_msg} - Frequency: {frequency}'
            )
            return False
        
        # Base URL for Cloud Scheduler API
        base_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/us-central1/jobs"
        headers = {
            'Authorization': f'Bearer {credentials.token}',
            'Content-Type': 'application/json'
        }
        
        if frequency == 'hourly':
            # Resume hourly job, pause daily job
            try:
                # Resume hourly job
                resume_url = f"{base_url}/hourly-temperature-check:resume"
                resume_response = requests.post(resume_url, headers=headers)
                print(f"🔍 Hourly job resume response: {resume_response.status_code}")
                
                # Pause daily job
                pause_url = f"{base_url}/daily-temperature-check:pause"
                pause_response = requests.post(pause_url, headers=headers)
                print(f"🔍 Daily job pause response: {pause_response.status_code}")
                
                if resume_response.status_code == 200 and pause_response.status_code == 200:
                    success_msg = "Cloud Scheduler: Enabled hourly job, paused daily job"
                    print(f"✅ {success_msg}")
                    log_scheduler_activity(
                        trigger_type='settings_update',
                        locations_checked=['hourly-temperature-check', 'daily-temperature-check'],
                        temperatures_found={},
                        alerts_triggered=0,
                        threshold_used=TEMP_THRESHOLD,
                        status='success',
                        error_message=None
                    )
                    return True
                else:
                    error_msg = f"Cloud Scheduler API calls failed: resume={resume_response.status_code}, pause={pause_response.status_code}"
                    print(f"❌ {error_msg}")
                    log_scheduler_activity(
                        trigger_type='settings_update',
                        locations_checked=['hourly-temperature-check', 'daily-temperature-check'],
                        temperatures_found={},
                        alerts_triggered=0,
                        threshold_used=TEMP_THRESHOLD,
                        status='error',
                        error_message=f'{error_msg} - Frequency: {frequency}'
                    )
                    return False
                    
            except Exception as e:
                error_msg = f"Error updating Cloud Scheduler jobs via API: {e}"
                print(f"❌ {error_msg}")
                log_scheduler_activity(
                    trigger_type='settings_update',
                    locations_checked=['hourly-temperature-check', 'daily-temperature-check'],
                    temperatures_found={},
                    alerts_triggered=0,
                    threshold_used=TEMP_THRESHOLD,
                    status='error',
                    error_message=f'{error_msg} - Frequency: {frequency}'
                )
                return False
                
        elif frequency == 'daily':
            # Resume daily job, pause hourly job
            try:
                # Resume daily job
                resume_url = f"{base_url}/daily-temperature-check:resume"
                resume_response = requests.post(resume_url, headers=headers)
                print(f"🔍 Daily job resume response: {resume_response.status_code}")
                
                # Pause hourly job
                pause_url = f"{base_url}/hourly-temperature-check:pause"
                pause_response = requests.post(pause_url, headers=headers)
                print(f"🔍 Hourly job pause response: {pause_response.status_code}")
                
                if resume_response.status_code == 200 and pause_response.status_code == 200:
                    success_msg = "Cloud Scheduler: Enabled daily job, paused hourly job"
                    print(f"✅ {success_msg}")
                    log_scheduler_activity(
                        trigger_type='settings_update',
                        locations_checked=['daily-temperature-check', 'hourly-temperature-check'],
                        temperatures_found={},
                        alerts_triggered=0,
                        threshold_used=TEMP_THRESHOLD,
                        status='success',
                        error_message=None
                    )
                    return True
                else:
                    error_msg = f"Cloud Scheduler API calls failed: resume={resume_response.status_code}, pause={pause_response.status_code}"
                    print(f"❌ {error_msg}")
                    log_scheduler_activity(
                        trigger_type='settings_update',
                        locations_checked=['daily-temperature-check', 'hourly-temperature-check'],
                        temperatures_found={},
                        alerts_triggered=0,
                        threshold_used=TEMP_THRESHOLD,
                        status='error',
                        error_message=f'{error_msg} - Frequency: {frequency}'
                    )
                    return False
                    
            except Exception as e:
                error_msg = f"Error updating Cloud Scheduler jobs via API: {e}"
                print(f"❌ {error_msg}")
                log_scheduler_activity(
                    trigger_type='settings_update',
                    locations_checked=['daily-temperature-check', 'hourly-temperature-check'],
                    temperatures_found={},
                    alerts_triggered=0,
                    threshold_used=TEMP_THRESHOLD,
                    status='error',
                    error_message=f'{error_msg} - Frequency: {frequency}'
                )
                return False
                
    except Exception as e:
        error_msg = f"Error updating Cloud Scheduler jobs: {e}"
        print(f"❌ {error_msg}")
        print("ℹ️  Note: This may not work in local development environment")
        log_scheduler_activity(
            trigger_type='settings_update',
            locations_checked=[],
            temperatures_found={},
            alerts_triggered=0,
            threshold_used=TEMP_THRESHOLD,
            status='error',
            error_message=f'{error_msg} - Frequency: {frequency}'
        )
        return False

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update temperature alert settings"""
    global TEMP_THRESHOLD, CHECK_FREQUENCY
    
    data = request.get_json()
    new_threshold = data.get('threshold', TEMP_THRESHOLD)
    new_frequency = data.get('frequency', CHECK_FREQUENCY)
    
    # Validate threshold
    if new_threshold not in [1, 10]:
        return jsonify({'success': False, 'error': 'Threshold must be 1 or 10 degrees'}), 400
    
    # Validate frequency
    if new_frequency not in ['hourly', 'daily']:
        return jsonify({'success': False, 'error': 'Frequency must be hourly or daily'}), 400
    
    # Update global variables
    TEMP_THRESHOLD = new_threshold
    CHECK_FREQUENCY = new_frequency
    
    # Update Cloud Scheduler jobs
    scheduler_updated = update_cloud_scheduler_jobs(new_frequency)
    
    print(f"✅ Settings updated: Threshold={TEMP_THRESHOLD}°F, Frequency={CHECK_FREQUENCY}")
    
    return jsonify({
        'success': True,
        'message': f'Settings updated: {TEMP_THRESHOLD}°F threshold, {CHECK_FREQUENCY} checks',
        'threshold': TEMP_THRESHOLD,
        'frequency': CHECK_FREQUENCY,
        'scheduler_updated': scheduler_updated
    })

@app.route('/api/migrate-db', methods=['POST'])
def migrate_database():
    """Run database migration to add missing columns"""
    try:
        from sqlalchemy import text
        
        # For SQLite, check if location column exists by trying to query it
        try:
            # Try to query the location column
            db.session.execute(text("SELECT location FROM device LIMIT 1"))
            print("✅ 'location' column already exists in Device table")
        except Exception as e:
            if "no such column" in str(e):
                print("Adding 'location' column to Device table...")
                db.session.execute(text("""
                    ALTER TABLE device 
                    ADD COLUMN location VARCHAR(128) DEFAULT 'auto'
                """))
                db.session.commit()
                print("✅ Successfully added 'location' column to Device table")
            else:
                raise e
        
        # Check if DebugLog.device_id needs to be changed from INTEGER to VARCHAR
        try:
            # Try to query device_id as string to see if it's already VARCHAR
            db.session.execute(text("SELECT device_id FROM debug_log LIMIT 1"))
            print("✅ DebugLog.device_id column exists")
            
            # Check if device_id column accepts strings by trying a direct SQL test
            try:
                # Try to insert a test record directly with SQL to avoid SQLAlchemy session issues
                db.session.execute(text("""
                    INSERT INTO debug_log (source, device_id, message, context, timestamp) 
                    VALUES ('test', 'TEST_MIGRATION', 'Testing device_id column type', 'Migration test', NOW())
                """))
                db.session.commit()
                print("✅ DebugLog.device_id column accepts strings - migration successful")
                # Clean up test log
                db.session.execute(text("DELETE FROM debug_log WHERE source = 'test' AND device_id = 'TEST_MIGRATION'"))
                db.session.commit()
            except Exception as test_error:
                if "InvalidTextRepresentation" in str(test_error):
                    print("❌ DebugLog.device_id is still INTEGER type - attempting to change...")
                    try:
                        # Clear existing data and alter column type in a fresh transaction
                        db.session.rollback()  # Ensure clean state
                        
                        # First, clear any existing data in device_id column
                        db.session.execute(text("UPDATE debug_log SET device_id = NULL"))
                        db.session.commit()
                        print("✅ Cleared existing device_id data")
                        
                        # Now alter the column type
                        db.session.execute(text("ALTER TABLE debug_log ALTER COLUMN device_id TYPE VARCHAR(128)"))
                        db.session.commit()
                        print("✅ Successfully changed DebugLog.device_id to VARCHAR")
                    except Exception as alter_error:
                        print(f"❌ Could not alter column type: {alter_error}")
                        print("⚠️  Manual database intervention required")
                else:
                    print(f"❌ Unexpected error testing device_id: {test_error}")
                    
        except Exception as e:
            if "no such column" in str(e):
                print("Adding 'device_id' column to DebugLog table...")
                db.session.execute(text("""
                    ALTER TABLE debug_log 
                    ADD COLUMN device_id VARCHAR(128)
                """))
                db.session.commit()
                print("✅ Successfully added 'device_id' column to DebugLog table")
            else:
                print(f"⚠️  DebugLog.device_id column issue: {e}")
                print("⚠️  Manual database intervention may be required for DebugLog.device_id")
        
        return jsonify({
            'success': True,
            'message': 'Database migration completed'
        })
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Migration failed: {str(e)}'
        }), 500

@app.route('/api/clear-commit-cache', methods=['POST'])
@requires_auth
def clear_commit_cache():
    """Clear the GitHub commit cache to force a fresh fetch"""
    try:
        global github_cache
        github_cache = {'data': None, 'timestamp': 0}
        return jsonify({'success': True, 'message': 'Commit cache cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create-order', methods=['POST'])
def create_order():
    """Create a new order for mobile app payments using PayPal backend"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product', 'color', 'size', 'quantity', 'total', 'platform', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Generate order ID
        order_id = f"ORDER_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create PayPal payment for the order
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": data['total'],
                    "currency": "USD"
                },
                "description": f"{data['quantity']}x {data['product']} ({data['color']}, {data['size']})",
                "item_list": {
                    "items": [{
                        "name": f"{data['product']} - {data['color']} - {data['size']}",
                        "price": data['total'],
                        "currency": "USD",
                        "quantity": data['quantity']
                    }]
                }
            }],
            "application_context": {
                "shipping_preference": "NO_SHIPPING",
                "user_action": "commit"
            },
            "redirect_urls": {
                "return_url": f"https://its2hot.org/payment-success?order_id={order_id}",
                "cancel_url": f"https://its2hot.org/payment-cancelled?order_id={order_id}"
            }
        }
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment(payment_data)
        
        if payment.create():
            # Store order details in session for later retrieval
            session[f'order_{order_id}'] = {
                'payment_id': payment.id,
                'product': data['product'],
                'color': data['color'],
                'size': data['size'],
                'quantity': data['quantity'],
                'total': data['total'],
                'platform': data['platform'],
                'payment_method': data['payment_method'],
                'created_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'payment_id': payment.id,
                'approval_url': payment.links[1].href,  # PayPal approval URL
                'message': 'Order created successfully with PayPal backend'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'PayPal payment creation failed: {payment.error}'
            }), 500
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/confirm-order', methods=['POST'])
def confirm_order():
    """Confirm an order after payment processing with PayPal backend"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['order_id', 'payment_result', 'platform']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        order_id = data['order_id']
        payment_result = data['payment_result']
        platform = data['platform']
        
        # Get order details from session
        order_data = session.get(f'order_{order_id}')
        if not order_data:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # For mobile payments (Apple Pay/Google Pay), we'll simulate PayPal approval
        # In production, you'd integrate with PayPal's mobile SDK or use webhooks
        if platform in ['ios', 'android']:
            # Simulate PayPal payment approval for mobile payments
            # In production, you'd verify the payment with PayPal's API
            payment_id = order_data.get('payment_id')
            
            # For now, we'll assume the mobile payment was successful
            # In production, you'd verify this with PayPal
            print(f"✅ Mobile payment confirmed for order {order_id} via {payment_result.get('method', 'unknown')}")
            
            # Create Printful order
            try:
                printful_order = create_printful_order({
                    'product': order_data['product'],
                    'color': order_data['color'],
                    'size': order_data['size'],
                    'quantity': order_data['quantity'],
                    'total': order_data['total'],
                    'payment_method': payment_result.get('method', 'mobile_payment'),
                    'platform': platform,
                    'order_id': order_id
                })
                
                # Send confirmation email
                # Note: You'd need to collect customer email in the mobile flow
                # send_order_confirmation(order_data)
                
                # Clean up session
                session.pop(f'order_{order_id}', None)
                
                return jsonify({
                    'success': True,
                    'order_id': order_id,
                    'printful_order_id': printful_order.get('id') if printful_order else None,
                    'message': 'Order confirmed and Printful order created successfully',
                    'payment_method': payment_result.get('method', 'mobile_payment')
                })
                
            except Exception as e:
                print(f"❌ Error creating Printful order: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Payment successful but Printful order creation failed: {str(e)}'
                }), 500
        else:
            # Web platform - handle through existing PayPal flow
            return jsonify({
                'success': True,
                'order_id': order_id,
                'message': 'Web order confirmed',
                'payment_method': 'paypal_web'
            })
        
    except Exception as e:
        print(f"❌ Error confirming order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Test Printful connection on startup
    print("🔍 Testing Printful API connection...")
    test_printful_connection()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
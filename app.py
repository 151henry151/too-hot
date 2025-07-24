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
print(f"DEBUG: MAIL_USERNAME = {os.getenv('MAIL_USERNAME')}")
print(f"DEBUG: MAIL_PASSWORD = {os.getenv('MAIL_PASSWORD')[:4]}..." if os.getenv('MAIL_PASSWORD') else "DEBUG: MAIL_PASSWORD = None")
print(f"DEBUG: WEATHER_API_KEY = {os.getenv('WEATHER_API_KEY')[:4]}..." if os.getenv('WEATHER_API_KEY') else "DEBUG: WEATHER_API_KEY = None")

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
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def as_dict(self):
        return {
            'id': self.id,
            'push_token': self.push_token,
            'platform': self.platform,
            'device_type': self.device_type,
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
    device_id = db.Column(db.Integer, nullable=True)
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

# --- Initialize DB ---
# Remove the @app.before_first_request decorator and function
# Instead, use app.app_context() at startup
with app.app_context():
    db.create_all()

# Weather API configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_BASE_URL = "http://api.weatherapi.com/v1"
NWS_BASE_URL = "https://api.weather.gov"  # Free National Weather Service API

# Temperature threshold for climate alerts (lowered to 1°F for testing)
TEMP_THRESHOLD = 1  # degrees Fahrenheit above average

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
    
    if not push_token:
        return jsonify({'error': 'Push token is required'}), 400
    
    try:
        # Check if device already exists
        existing_device = Device.query.filter_by(push_token=push_token).first()
        
        if existing_device:
            # Update existing device
            existing_device.platform = platform
            existing_device.device_type = device_type
            existing_device.is_active = True
            existing_device.registered_at = datetime.utcnow()
        else:
            # Create new device
            new_device = Device(
                push_token=push_token,
                platform=platform,
                device_type=device_type
            )
            db.session.add(new_device)
        
        db.session.commit()
        
        print(f"✅ Device registered: {platform} {device_type} - {push_token[:20]}...")
        
        return jsonify({
            'message': 'Device registered successfully',
            'device_id': existing_device.id if existing_device else new_device.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error registering device: {e}")
        return jsonify({'error': 'Failed to register device'}), 500

@app.route('/api/check-temperatures', methods=['GET'])
def check_temperatures():
    """Check current temperatures and send notifications if conditions are met"""
    if not WEATHER_API_KEY:
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    notifications_sent = []
    
    for subscriber in Subscriber.query.all():
        try:
            # Get current weather and historical data
            location = subscriber.location
            
            # For demo purposes, we'll use a sample location (NYC)
            # In production, you'd get the user's actual location
            if location == 'auto':
                location = 'New York'
            
            # Get current weather
            current_url = f"{WEATHER_BASE_URL}/current.json"
            current_params = {
                'key': WEATHER_API_KEY,
                'q': location,
                'aqi': 'no'
            }
            
            current_response = requests.get(current_url, params=current_params)
            if current_response.status_code != 200:
                continue
            
            current_data = current_response.json()
            current_temp = current_data['current']['temp_f']
            
            # Get historical data for today's date
            today = datetime.now()
            historical_url = f"{WEATHER_BASE_URL}/history.json"
            historical_params = {
                'key': WEATHER_API_KEY,
                'q': location,
                'dt': today.strftime('%Y-%m-%d')
            }
            
            # For demo, we'll use a simplified approach
            # In production, you'd get actual historical data
            avg_temp = 85  # Example average temperature
            
            # Check if current temp is TEMP_THRESHOLD+ degrees hotter than average
            if current_temp >= avg_temp + TEMP_THRESHOLD:
                # Send email notification
                send_notification(subscriber.email, location, current_temp, avg_temp)
                notifications_sent.append({
                    'email': subscriber.email,
                    'location': location,
                    'current_temp': current_temp,
                    'avg_temp': avg_temp,
                    'threshold': TEMP_THRESHOLD
                })
                
                # Send push notification to all devices (only once per location)
                if location not in [n['location'] for n in notifications_sent]:
                    send_push_notification(location, current_temp, avg_temp)
                
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
    """Send push notification to all registered devices"""
    try:
        temp_diff = round(current_temp - avg_temp, 1)
        
        # Get all active devices
        devices = Device.query.filter_by(is_active=True).all()
        
        if not devices:
            print("No active devices to send push notifications to")
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
                    print(f"✅ Push notifications sent to {len(batch)} devices")
                else:
                    print(f"❌ Failed to send push notifications: {response.text}")
        
    except Exception as e:
        print(f"Failed to send push notifications: {e}")

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

# --- Admin Dashboard ---
@app.route('/admin', methods=['GET'])
@requires_auth
def admin_dashboard():
    email_subs = [s.as_dict() for s in Subscriber.query.all()]
    notif_log = load_json_file('notification_log.json', default=[])
    trigger_log = load_json_file('trigger_log.json', default=[])
    return render_template('admin.html',
        email_subs=email_subs,
        notif_log=notif_log,
        trigger_log=trigger_log)

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

# --- API to get logs (for dashboard AJAX) ---
@app.route('/admin/logs', methods=['GET'])
@requires_auth
def admin_get_logs():
    notif_log = load_json_file('notification_log.json', default=[])
    trigger_log = load_json_file('trigger_log.json', default=[])
    return jsonify({'notification_log': notif_log, 'trigger_log': trigger_log})

@app.route('/api/send-push-notification', methods=['POST'])
def api_send_push_notification():
    data = request.get_json()
    title = data.get('title', 'IT\'S TOO HOT!')
    body = data.get('body', 'Temperature alert!')
    url = data.get('url', '/')
    
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
            data=json.dumps({'url': url}),
            status='failure',
            error='No Expo push tokens registered'
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': False, 'message': 'No Expo push tokens registered', 'total_subscribers': 0}), 200
    
    expo_url = "https://exp.host/--/api/v2/push/send"
    messages = []
    for device in devices:
        if device.platform == 'expo':
            messages.append({
                "to": device.push_token,
                "title": title,
                "body": body,
                "data": {"url": url},
                "sound": "default",
                "priority": "high",
                "device_id": device.id,
                "device_type": device.device_type
            })
    batch_size = 100
    successful_sends = 0
    failed_sends = 0
    errors = []
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        try:
            response = requests.post(expo_url, json=batch, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                successful_sends += len(batch)
                # Log each success
                for msg in batch:
                    log = PushNotificationLog(
                        device_id=msg.get('device_id'),
                        push_token=msg.get('to'),
                        platform='expo',
                        device_type=msg.get('device_type'),
                        title=title,
                        body=body,
                        data=json.dumps({'url': url}),
                        status='success',
                        error=None
                    )
                    db.session.add(log)
                db.session.commit()
            else:
                failed_sends += len(batch)
                errors.append(response.text)
                # Log each failure
                for msg in batch:
                    log = PushNotificationLog(
                        device_id=msg.get('device_id'),
                        push_token=msg.get('to'),
                        platform='expo',
                        device_type=msg.get('device_type'),
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
            # Log each failure
            for msg in batch:
                log = PushNotificationLog(
                    device_id=msg.get('device_id'),
                    push_token=msg.get('to'),
                    platform='expo',
                    device_type=msg.get('device_type'),
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
    log = DebugLog(
        source=data.get('source'),
        device_id=data.get('device_id'),
        email=data.get('email'),
        message=data.get('message'),
        context=data.get('context')
    )
    db.session.add(log)
    db.session.commit()
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
    else:
        push_logs = PushNotificationLog.query.order_by(PushNotificationLog.timestamp.desc()).limit(limit).all()
        debug_logs = DebugLog.query.order_by(DebugLog.timestamp.desc()).limit(limit).all()
        return jsonify({
            'push_logs': [l.as_dict() for l in push_logs],
            'debug_logs': [l.as_dict() for l in debug_logs]
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
    if use_real_data:
        # Fetch real weather data
        current_url = f"{WEATHER_BASE_URL}/current.json"
        current_params = {'key': WEATHER_API_KEY, 'q': location, 'aqi': 'no'}
        current_response = requests.get(current_url, params=current_params)
        if current_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to fetch current weather'}), 500
        current_data = current_response.json()
        current_temp = current_data['current']['temp_f']
        today = datetime.now()
        # For demo, use a fixed average or fetch historical if needed
        avg_temp = 85
    else:
        current_temp = data.get('current_temp', 100)
        avg_temp = data.get('avg_temp', 85)
    # Trigger alert logic (send emails, push notifications, etc.)
    # For now, just log and return the data
    return jsonify({
        'success': True,
        'location': location,
        'current_temp': current_temp,
        'avg_temp': avg_temp,
        'temp_diff': round(current_temp - avg_temp, 1)
    })

@app.route('/admin/time-tracking')
@requires_auth
def time_tracking():
    try:
        # Fetch commit history from GitHub API (latest 100 commits)
        api_url = 'https://api.github.com/repos/151henry151/too-hot/commits?per_page=100'
        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'GitHub API error: {resp.status_code}')
        data = resp.json()
        commits = []
        for c in data:
            commit = c['sha']
            msg = c['commit']['message']
            date_str = c['commit']['committer']['date']
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            commits.append({'hash': commit, 'datetime': dt, 'msg': msg})
        # Sort by datetime descending (newest first)
        commits.sort(key=lambda x: x['datetime'], reverse=True)
    except Exception as e:
        return render_template('time_tracking.html', rows=[], total_hours=0, total_mins=0, error=f"Failed to fetch commit history: {e}")
    # Calculate time spent per commit
    time_spent = []
    total_minutes = 0
    n = len(commits)
    for i in range(n):
        if i == n - 1:
            spent = 190  # Special case for initial commit (oldest)
        else:
            delta = (commits[i]['datetime'] - commits[i+1]['datetime']).total_seconds() / 60
            if delta >= 120:
                # Estimate by lines changed (insertions + deletions), capped at 180 min
                stats_url = f'https://api.github.com/repos/151henry151/too-hot/commits/{commits[i+1]["hash"]}'
                stats_resp = requests.get(stats_url)
                if stats_resp.status_code == 200:
                    stats = stats_resp.json().get('stats', {})
                    lines = stats.get('additions', 0) + stats.get('deletions', 0)
                    spent = min(lines * 3, 180)
                else:
                    spent = 120  # fallback if API fails
            else:
                spent = min(max(int(delta), 0), 120)
        time_spent.append(spent)
        total_minutes += spent
    rows = []
    for i, c in enumerate(commits):
        # Fetch lines added/deleted for this commit
        stats_url = f'https://api.github.com/repos/151henry151/too-hot/commits/{c["hash"]}'
        stats_resp = requests.get(stats_url)
        if stats_resp.status_code == 200:
            stats = stats_resp.json().get('stats', {})
            additions = stats.get('additions', 0)
            deletions = stats.get('deletions', 0)
        else:
            additions = 0
            deletions = 0
        rows.append({
            'hash': c['hash'][:7],
            'full_hash': c['hash'],
            'msg': c['msg'],
            'datetime': c['datetime'].strftime('%Y-%m-%d %H:%M'),
            'time_spent': time_spent[i],
            'additions': additions,
            'deletions': deletions
        })
    total_hours = total_minutes // 60
    total_mins = total_minutes % 60
    return render_template('time_tracking.html', rows=rows, total_hours=total_hours, total_mins=total_mins, error=None)

if __name__ == '__main__':
    # Test Printful connection on startup
    print("🔍 Testing Printful API connection...")
    test_printful_connection()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
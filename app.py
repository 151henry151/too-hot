from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_mail import Mail, Message
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import paypalrestsdk

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure PayPal
paypalrestsdk.configure({
    "mode": os.getenv('PAYPAL_MODE', 'sandbox'),  # sandbox or live
    "client_id": os.getenv('PAYPAL_CLIENT_ID'),
    "client_secret": os.getenv('PAYPAL_CLIENT_SECRET')
})

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Debug logging to see what environment variables are being read
print(f"DEBUG: MAIL_USERNAME = {os.getenv('MAIL_USERNAME')}")
print(f"DEBUG: MAIL_PASSWORD = {os.getenv('MAIL_PASSWORD')[:4]}..." if os.getenv('MAIL_PASSWORD') else "DEBUG: MAIL_PASSWORD = None")
print(f"DEBUG: WEATHER_API_KEY = {os.getenv('WEATHER_API_KEY')[:4]}..." if os.getenv('WEATHER_API_KEY') else "DEBUG: WEATHER_API_KEY = None")

mail = Mail(app)

# In-memory storage for subscribers (in production, use a database)
subscribers = []

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
    # Get product images from Printful
    product_images = get_printful_product_images()
    
    # Product details with real images
    products = {
        'tshirt': {
            'name': 'IT\'S TOO HOT! T-Shirt (Dark)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with white text on dark background',
            'printful_product_id': '387436926',
            'image': product_images.get('387436926', {}).get('url', url_for('static', filename='img/tshirt_text.png'))
        },
        'tshirt_light': {
            'name': 'IT\'S TOO HOT! T-Shirt (Light)',
            'price': 25.00,
            'description': 'High-quality cotton t-shirt with black text on light background',
            'printful_product_id': '387436861',
            'image': product_images.get('387436861', {}).get('url', url_for('static', filename='img/tshirt_text_black.png'))
        }
    }
    
    # Debug: Print what images we found
    print("🔍 Product images found:")
    for product_id, image_data in product_images.items():
        print(f"  {product_id}: {image_data.get('url', 'No URL')}")
    
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
    """Create order in Printful using newer API"""
    headers = {
        'Authorization': f'Bearer {PRINTFUL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
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
            'sync_product_id': order_data['product_id'],
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
    """Send welcome email to new subscriber"""
    try:
        subject = "🌍 Welcome to the Climate Movement - IT'S TOO HOT!"
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
        
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=body
        )
        
        mail.send(msg)
        print(f"Welcome email sent to {email}")
        
    except Exception as e:
        print(f"Failed to send welcome email to {email}: {e}")

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe a user to temperature notifications"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    email = data['email'].strip()
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if already subscribed
    if any(sub['email'] == email for sub in subscribers):
        return jsonify({'error': 'Email already subscribed'}), 409
    
    # Add subscriber
    location = data.get('location', 'auto')
    subscriber = {
        'email': email,
        'subscribed_at': datetime.now().isoformat(),
        'location': location
    }
    subscribers.append(subscriber)
    
    # Send welcome email
    try:
        send_welcome_email(email, location)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        # Don't fail the subscription if welcome email fails
    
    return jsonify({
        'message': 'Successfully subscribed to temperature notifications',
        'email': email
    }), 201

@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe a user from temperature notifications"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    email = data['email'].strip()
    
    # Remove subscriber
    global subscribers
    subscribers = [sub for sub in subscribers if sub['email'] != email]
    
    return jsonify({
        'message': 'Successfully unsubscribed from temperature notifications',
        'email': email
    }), 200

@app.route('/api/check-temperatures', methods=['GET'])
def check_temperatures():
    """Check current temperatures and send notifications if conditions are met"""
    if not WEATHER_API_KEY:
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    notifications_sent = []
    
    for subscriber in subscribers:
        try:
            # Get current weather and historical data
            location = subscriber.get('location', 'auto')
            
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
                # Send notification
                send_notification(subscriber['email'], location, current_temp, avg_temp)
                notifications_sent.append({
                    'email': subscriber['email'],
                    'location': location,
                    'current_temp': current_temp,
                    'avg_temp': avg_temp,
                    'threshold': TEMP_THRESHOLD
                })
                
        except Exception as e:
            print(f"Error processing subscriber {subscriber['email']}: {e}")
            continue
    
    return jsonify({
        'message': f'Processed {len(subscribers)} subscribers',
        'notifications_sent': len(notifications_sent),
        'threshold': TEMP_THRESHOLD,
        'details': notifications_sent
    })

def send_notification(email, location, current_temp, avg_temp):
    """Send climate alert notification to subscriber"""
    try:
        subject = f"🌡️ Climate Alert - {location} - IT'S TOO HOT!"
        body = f"""
        CLIMATE ALERT - Time to Take Action!
        
        Location: {location}
        Current Temperature: {current_temp}°F
        Average Temperature: {avg_temp}°F
        Climate Anomaly: +{current_temp - avg_temp}°F above normal
        
        This is a clear sign of climate change in action. Temperatures are {TEMP_THRESHOLD}°F+ 
        higher than historical averages for this time of year.
        
        ACTION REQUIRED:
        - Wear your "IT'S TOO HOT!" shirt today
        - Share this alert on social media
        - Start conversations about climate change
        - Contact your representatives about climate action
        
        This is not just hot weather - this is climate disruption happening now.
        Let's raise awareness together!
        
        #TooHot #ClimateAction #ClimateChange
        """
        
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=body
        )
        
        mail.send(msg)
        print(f"Notification sent to {email}")
        
    except Exception as e:
        print(f"Failed to send notification to {email}: {e}")

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Get list of all subscribers (for admin purposes)"""
    return jsonify({
        'subscribers': subscribers,
        'count': len(subscribers)
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

if __name__ == '__main__':
    # Test Printful connection on startup
    print("🔍 Testing Printful API connection...")
    test_printful_connection()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
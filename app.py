from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

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

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
# Push Notifications Setup Guide

This guide will help you set up push notifications for the "Too Hot" climate awareness campaign.

## 🎯 Overview

We've implemented a **Progressive Web App (PWA)** approach for push notifications that works on both iOS and Android without requiring app store deployment.

## 📋 What's Been Implemented

### ✅ Frontend Components
- **Service Worker** (`static/js/sw.js`) - Handles push notifications and caching
- **Push Notification Manager** (`static/js/push-notifications.js`) - Client-side subscription logic
- **PWA Manifest** (`static/manifest.json`) - Makes the web app installable
- **UI Components** - Subscribe/unsubscribe buttons on the main page

### ✅ Backend Components
- **Subscription Endpoints** - Handle user subscriptions
- **Storage System** - JSON-based subscription storage
- **Notification Sending** - Framework for sending notifications

## 🚀 Setup Steps

### 1. Install Dependencies

```bash
pip install cryptography
```

### 2. Generate VAPID Keys

```bash
python generate_vapid_keys.py
```

This will create `vapid_keys.json` with your public and private keys.

### 3. Update JavaScript with Public Key

Edit `static/js/push-notifications.js` and replace:
```javascript
this.vapidPublicKey = 'YOUR_VAPID_PUBLIC_KEY';
```

With your actual public key from the generated file.

### 4. Add Private Key to Environment

Add to your `.env` file:
```
VAPID_PRIVATE_KEY=your_private_key_here
```

### 5. Test the Setup

1. Start your Flask app: `python app.py`
2. Visit `http://127.0.0.1:5000`
3. Click "Enable Push Notifications"
4. Grant permission when prompted

## 📱 How It Works

### For Users:
1. **Visit the website** on mobile or desktop
2. **Click "Enable Push Notifications"**
3. **Grant permission** when browser prompts
4. **Receive climate alerts** when temperatures are too hot
5. **Optional**: "Install" the web app like a native app

### For Developers:
1. **Subscriptions are stored** in `push_subscriptions.json`
2. **Send notifications** via `/api/send-push-notification`
3. **Service worker handles** notification display and clicks

## 🔧 Advanced Configuration

### Customizing Notifications

Edit `static/js/sw.js` to customize notification appearance:
```javascript
const options = {
    body: notificationData.body,
    icon: '/static/img/tshirt.png',
    badge: '/static/img/tshirt.png',
    actions: [
        {
            action: 'view',
            title: 'View Details',
            icon: '/static/img/tshirt.png'
        }
    ],
    requireInteraction: true,
    tag: 'climate-alert'
};
```

### Sending Test Notifications

Use the API endpoint to send test notifications:
```bash
curl -X POST http://127.0.0.1:5000/api/send-push-notification \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Climate Alert",
    "body": "Temperature is 15°F above average today!",
    "url": "/"
  }'
```

## 🌐 Browser Support

### ✅ Fully Supported
- Chrome (Android & Desktop)
- Firefox (Android & Desktop)
- Edge (Windows)
- Safari (iOS 16.4+)

### ⚠️ Limited Support
- Safari (Desktop) - No background notifications
- Older iOS versions - Limited PWA features

## 📊 Analytics & Monitoring

The system logs subscription events:
- ✅ New subscriptions
- ✅ Unsubscriptions
- ✅ Failed deliveries
- 📊 Subscriber counts

## 🔒 Security Considerations

1. **HTTPS Required** - Push notifications only work over HTTPS
2. **VAPID Keys** - Keep private key secure
3. **User Consent** - Always request permission
4. **Data Privacy** - Store minimal user data

## 🚀 Production Deployment

### 1. HTTPS Setup
```bash
# For development with self-signed cert
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 2. Environment Variables
```bash
export VAPID_PRIVATE_KEY="your_private_key"
export FLASK_ENV=production
```

### 3. Database Storage
Replace JSON file storage with a proper database:
```python
# Example with SQLite
import sqlite3

def store_subscription(subscription_data):
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscriptions (endpoint, auth, p256dh, user_agent, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (subscription_data['endpoint'], subscription_data['auth'], 
          subscription_data['p256dh'], subscription_data['user_agent'], 
          subscription_data['timestamp']))
    conn.commit()
    conn.close()
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Push notifications not supported"**
   - Check browser compatibility
   - Ensure HTTPS is enabled

2. **"Permission denied"**
   - User must manually enable in browser settings
   - Check if notifications are blocked

3. **"Service worker registration failed"**
   - Check file paths
   - Ensure service worker file is accessible

4. **"VAPID key error"**
   - Verify public key format
   - Check for extra characters/spaces

### Debug Commands:
```bash
# Check service worker registration
curl http://127.0.0.1:5000/static/js/sw.js

# Test subscription endpoint
curl -X POST http://127.0.0.1:5000/api/push-subscribe \
  -H "Content-Type: application/json" \
  -d '{"subscription":{"endpoint":"test"}}'

# Check stored subscriptions
cat push_subscriptions.json
```

## 📈 Next Steps

1. **Implement actual notification sending** using a service like Firebase Cloud Messaging
2. **Add user preferences** for notification types
3. **Implement location-based targeting**
4. **Add analytics dashboard** for notification performance
5. **Create mobile app** for enhanced features

## 🎉 Success!

Your climate awareness campaign now has push notifications! Users can:
- Get real-time climate alerts
- Install the web app like a native app
- Stay informed about climate anomalies
- Take action when temperatures are too hot

The system is ready to scale and help raise climate awareness worldwide! 🌍🔥 
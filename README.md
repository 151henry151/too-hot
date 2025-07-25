# Too Hot - Climate Awareness Campaign

> **When temperatures are 1°F hotter than normal, wear your "IT'S TOO HOT!" shirt and start conversations about climate change.**

---

# 📚 Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Project Structure](#project-structure)
4. [API Endpoints](#api-endpoints)
5. [Environment Variables](#environment-variables)
6. [Backend Setup & Development](#backend-setup--development)
7. [Mobile App (React Native/Expo)](#mobile-app-react-nativeexpo)
8. [E-commerce & Printful Integration](#e-commerce--printful-integration)
9. [Deployment (Docker & GCP)](#deployment-docker--gcp)
10. [Troubleshooting & Support](#troubleshooting--support)
11. [Contributing](#contributing)
12. [License](#license)

---

# Project Overview

**Too Hot** is a climate activism platform that alerts you when your local temperature is significantly hotter than historical averages. When these climate anomalies occur, we encourage wearing "IT'S TOO HOT!" t-shirts to raise awareness and start important conversations about climate action.

- **Website:** https://its2hot.org
- **Cloud Run URL:** https://too-hot-ao5zbahlha-uc.a.run.app
- **GitHub:** https://github.com/151henry151/too-hot

---

# Key Features
- **Temperature Monitoring:** Checks your local weather against historical averages
- **Smart Alerts:** Notifies you when temperatures are 1°F+ hotter than normal
- **Push Notifications:** Mobile and web alerts for extreme heat events
- **E-commerce:** Order "IT'S TOO HOT!" shirts (Printful + PayPal integration)
- **Admin Dashboard:** Manage subscribers, logs, and notifications
- **Community Building:** Connects people through shared climate awareness

---

# Project Structure

```
too-hot/
  app.py                # Flask backend (API, web, shop, admin)
  scheduler.py          # Background temperature checks
  static/               # Static assets (images, mockups, CSS)
  templates/            # HTML templates (Flask)
  its2hot-app/          # Mobile app (React Native/Expo)
  ...                   # Setup scripts, guides, tests, etc.
```

---

# API Endpoints

## Public Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main campaign page |
| `/shop` | GET | T-shirt shop page |
| `/checkout` | GET | Checkout page |
| `/api/subscribe` | POST | Subscribe to temperature alerts (email) |
| `/api/unsubscribe` | POST | Unsubscribe from alerts |
| `/api/register-device` | POST | Register device for push notifications |
| `/api/unregister-device` | POST | Unregister device for push notifications |
| `/api/check-temperatures` | GET | Check current temperatures and send alerts |
| `/api/subscribers` | GET | List all email subscribers |
| `/api/push-subscribers` | GET | List all push notification subscribers |
| `/api/send-push-notification` | POST | Send a push notification to all devices |
| `/api/test-printful` | GET | Test Printful API connection |
| `/api/log-error` | POST | Log error from mobile app |
| `/api/log-push` | POST | Log push notification attempt |
| `/api/log-debug` | POST | Log debug info from mobile app |
| `/api/logs` | GET | Fetch logs (push/debug) |
| `/api/push-subscriber/<int:device_id>` | DELETE | Delete/unsubscribe a push device |
| `/api/test-temperature-alert` | POST | Trigger a test temperature alert |

## Admin Endpoints (require basic auth)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin` | GET | Admin dashboard |
| `/admin/resend-welcome` | POST | Resend welcome email |
| `/admin/send-test-email` | POST | Send test alert email |
| `/admin/send-test-notification` | POST | Send test push notification |
| `/admin/logs` | GET | Fetch notification/trigger logs |
| `/admin/time-tracking` | GET | Time tracking dashboard |
| `/admin/delete-subscriber` | POST | Delete an email subscriber |
| `/admin/mobile-logs` | GET | Fetch mobile app logs |

---

# Environment Variables

Copy `env.example` to `.env` and fill in your secrets:

```
# Weather API
WEATHER_API_KEY=your_weather_api_key_here

# Email (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# PayPal
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here

# Printful
PRINTFUL_API_KEY=your_printful_api_key_here

# Flask
SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Database (optional)
DATABASE_URL=sqlite:///too_hot.db

# Expo (for push notifications)
EXPO_TOKEN=your_expo_token_here
```

---

# Backend Setup & Development

## Prerequisites
- Python 3.11+
- Git
- [Google Cloud CLI](https://cloud.google.com/sdk) (for deployment)

## Local Development
1. **Clone and Setup:**
   ```bash
   git clone https://github.com/151henry151/too-hot.git
   cd too-hot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your API keys and email settings
   ```
2. **Run Locally:**
   ```bash
   python app.py
   # Visit http://localhost:5000
   ```
3. **Test Printful Connection:**
   ```bash
   curl http://127.0.0.1:5000/api/test-printful
   ```

## Backend Dependencies
- Flask, Flask-Mail, Flask-CORS, Flask-SQLAlchemy
- requests, python-dotenv, gunicorn, paypalrestsdk, psycopg2-binary, pytz

---

# Mobile App (React Native/Expo)

The mobile app is in [`its2hot-app/`](its2hot-app/). It is a cross-platform (iOS/Android/web) Expo app for:
- Push notifications for temperature alerts
- T-shirt shop and purchase flow
- Climate data and campaign info

## Features
- **Home:** Enable/disable notifications, campaign info, climate data
- **Shop:** Browse, select, and purchase shirts (PayPal integration)
- **Too Hot Today:** See today's temperature anomaly and share

## Setup & Development
1. **Install dependencies:**
   ```bash
   cd its2hot-app
   npm install
   ```
2. **Start the app:**
   ```bash
   npx expo start
   ```
   - Open in Expo Go, iOS/Android simulator, or web browser

## Configuration
- See [`its2hot-app/app.json`](its2hot-app/app.json) for bundle IDs, notification icons, etc.
- Uses Firebase for push notifications (see `google-services.json` and `GoogleService-Info.plist`)
- Main dependencies: Expo, React Native, @react-navigation, expo-notifications, firebase

## Main Screens
- **HomeScreen:** Enable notifications, campaign info, climate data
- **ShopScreen:** Select shirt design, color, size, quantity, and purchase
- **TooHotTodayScreen:** See and share today's temperature anomaly

---

# E-commerce & Printful Integration

- **Shop:** `/shop` (web) and Shop screen (mobile)
- **Checkout:** `/checkout` (web)
- **PayPal:** Secure payment processing (sandbox/live)
- **Printful:** Automatic order fulfillment via API
- **Order confirmation:** Email sent to customer
- **Admin:** View/manage orders and logs

See [PRINTFUL_SETUP_GUIDE.md](PRINTFUL_SETUP_GUIDE.md) and [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full details.

---

# Deployment (Docker & GCP)

## Docker (Local)
1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

## Google Cloud Run
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full instructions
- Key steps:
  1. Build and push Docker image
  2. Deploy to Cloud Run with all environment variables set
  3. Configure domain and SSL (optional)

## Cloud Build Example
See [`cloudbuild.yaml`](cloudbuild.yaml) for automated build/deploy steps.

---

# Troubleshooting & Support

- **Printful:** Test with `/api/test-printful` and check `.env` token
- **PayPal:** Use sandbox for testing, check credentials and mode
- **Email:** Use Gmail app password, check spam folder
- **Push Notifications:** Ensure Expo/Firebase config is correct
- **Logs:** Use `/api/logs` and `/admin/logs` for debugging
- **See:** [PRINTFUL_SETUP_GUIDE.md](PRINTFUL_SETUP_GUIDE.md) and [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

# Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

---

# License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

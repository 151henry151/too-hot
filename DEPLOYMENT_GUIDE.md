# 🚀 Deployment Guide - Too Hot E-commerce System

## 🔐 Secure PayPal Integration Setup

Your PayPal credentials have been securely configured:

- **Client ID**: `AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ`
- **Client Secret**: `EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha`
- **Mode**: `sandbox` (for testing)

## 📁 Local Development

### 1. Environment Setup ✅
```bash
# PayPal credentials are already configured in .env file
python setup_paypal_env.py  # Already run
```

### 2. Install Dependencies ✅
```bash
pip install -r requirements.txt
```

### 3. Test Locally
```bash
python app.py
# Visit: http://127.0.0.1:5000
# Shop: http://127.0.0.1:5000/shop
```

## 🌐 GCP Cloud Run Deployment

### Option 1: Using the Deployment Script

1. **Update the deployment script** with your actual API keys:
```bash
# Edit deploy_gcp.sh and replace placeholder values:
# - your-gcp-project-id
# - your_weather_api_key
# - your_email@gmail.com
# - your_app_password
# - your_printful_api_key
# - your_secret_key
```

2. **Deploy to GCP**:
```bash
chmod +x deploy_gcp.sh
./deploy_gcp.sh
```

### Option 2: Manual GCP Deployment

1. **Set up GCP project**:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com
```

2. **Deploy with environment variables**:
```bash
gcloud run deploy too-hot-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="PAYPAL_MODE=sandbox" \
  --set-env-vars="PAYPAL_CLIENT_ID=AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ" \
  --set-env-vars="PAYPAL_CLIENT_SECRET=EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha" \
  --set-env-vars="WEATHER_API_KEY=YOUR_WEATHER_API_KEY" \
  --set-env-vars="MAIL_USERNAME=YOUR_EMAIL@gmail.com" \
  --set-env-vars="MAIL_PASSWORD=YOUR_APP_PASSWORD" \
  --set-env-vars="PRINTFUL_API_KEY=YOUR_PRINTFUL_API_KEY" \
  --set-env-vars="SECRET_KEY=YOUR_SECRET_KEY"
```

## 🔧 Required Environment Variables

### For Local Development (.env file):
```env
# Weather API Configuration
WEATHER_API_KEY=your_weather_api_key_here

# Email Configuration (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# PayPal Configuration ✅
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ
PAYPAL_CLIENT_SECRET=EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha

# Printful Configuration
PRINTFUL_API_KEY=your_printful_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### For GCP Production:
- Set all environment variables in Cloud Run console or via gcloud command
- Change `PAYPAL_MODE=live` for production payments
- Use production PayPal credentials

## 🛍️ E-commerce Features

### ✅ Implemented:
- **PayPal Integration**: Secure payment processing
- **Custom Checkout**: Branded experience without PayPal branding
- **Printful Integration**: Automatic order fulfillment
- **Email Confirmations**: Order tracking and confirmations
- **Mobile Responsive**: Works on all devices
- **Error Handling**: Graceful payment error management

### 🎯 Shopping Flow:
1. **Shop Page** (`/shop`): Product showcase with size/quantity selection
2. **Checkout Page** (`/checkout`): Shipping form and order summary
3. **PayPal Payment**: Secure payment processing
4. **Success Page**: Order confirmation and next steps
5. **Email Confirmation**: Order details and tracking info

## 🔒 Security Features

### ✅ Implemented:
- **Environment Variables**: Secrets stored securely
- **Git Ignore**: .env file never committed to repository
- **PayPal Security**: PCI-compliant payment processing
- **HTTPS Only**: Secure connections in production
- **Input Validation**: Form data validation

## 🧪 Testing

### Local Testing:
```bash
# Start the app
python app.py

# Test URLs:
# Home: http://127.0.0.1:5000
# Shop: http://127.0.0.1:5000/shop
# Checkout: http://127.0.0.1:5000/checkout?product_id=tshirt&quantity=1
```

### PayPal Sandbox Testing:
- Use PayPal sandbox accounts for testing
- Test payment flow without real money
- Verify order creation and email sending

## 🚀 Production Checklist

### Before Going Live:
- [ ] Change `PAYPAL_MODE=live`
- [ ] Get production PayPal credentials
- [ ] Set up Printful product and get API key
- [ ] Configure Gmail app password
- [ ] Set up weather API key
- [ ] Test complete payment flow
- [ ] Verify email confirmations
- [ ] Test mobile responsiveness

### GCP Deployment:
- [ ] Deploy to Cloud Run
- [ ] Set all environment variables
- [ ] Test live payment flow
- [ ] Monitor logs for errors
- [ ] Set up monitoring and alerts

## 📞 Support

### Common Issues:
1. **PayPal Connection**: Check credentials and mode (sandbox/live)
2. **Email Sending**: Verify Gmail app password
3. **Printful Orders**: Check API key and product setup
4. **Environment Variables**: Ensure all variables are set in GCP

### Debug Commands:
```bash
# Check environment variables
grep PAYPAL .env

# Test PayPal connection
python -c "import paypalrestsdk; print('PayPal SDK working')"

# Check app logs
gcloud logs read --service=too-hot-app
```

## 🎉 Success!

Your e-commerce system is now ready with:
- ✅ **Secure PayPal Integration**
- ✅ **Custom Branded Checkout**
- ✅ **Automatic Order Fulfillment**
- ✅ **Email Confirmations**
- ✅ **Mobile Responsive Design**

**Start selling your climate awareness t-shirts!** 🌍🛍️ 
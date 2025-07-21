#!/bin/bash
# GCP Deployment Script with PayPal and Printful Environment Variables

# Set your GCP project ID
PROJECT_ID="your-gcp-project-id"

# Deploy to Cloud Run with environment variables
gcloud run deploy too-hot-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="PAYPAL_MODE=sandbox" \
  --set-env-vars="PAYPAL_CLIENT_ID=AQQBQnN4eMblzRmyLzOmpxwFlMO3VVfHfCSygAH2uudLH5DkZu5nESApFd2FAltXlAE-KPa4cZyeXYUJ" \
  --set-env-vars="PAYPAL_CLIENT_SECRET=EHUXgMkhrycyaT4yTU7qaNUYXJRkuw5sUbzL-s_pjvGvFhgr4dwpquN2-bMBTxTB1T9mG8UXf6WCbYha" \
  --set-env-vars="PRINTFUL_API_KEY=eWlXN3veWJXrQyOan2OEpHkQ9nuZuUqy6pZnmJjk" \
  --set-env-vars="WEATHER_API_KEY=your_weather_api_key" \
  --set-env-vars="MAIL_USERNAME=your_email@gmail.com" \
  --set-env-vars="MAIL_PASSWORD=your_app_password" \
  --set-env-vars="SECRET_KEY=your_secret_key"

echo "🚀 App deployed to GCP Cloud Run!"
echo "🔗 Your app URL will be shown above"

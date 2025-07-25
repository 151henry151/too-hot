#!/bin/bash

# Setup Cloud Scheduler Jobs for Too Hot Temperature Alerts
# This script creates Cloud Scheduler jobs to trigger temperature checks

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
MAIN_APP_URL="https://too-hot-ao5zbahlha-uc.a.run.app"

echo "Setting up Cloud Scheduler jobs for Too Hot temperature alerts..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Main App URL: $MAIN_APP_URL"

# Delete existing jobs if they exist
echo "Cleaning up existing scheduler jobs..."
gcloud scheduler jobs delete daily-temperature-check --location=$REGION --quiet 2>/dev/null || true
gcloud scheduler jobs delete hourly-temperature-check --location=$REGION --quiet 2>/dev/null || true
gcloud scheduler jobs delete peak-hours-temperature-check --location=$REGION --quiet 2>/dev/null || true

# Create daily temperature check job (8 AM daily)
echo "Creating daily temperature check job..."
gcloud scheduler jobs create http daily-temperature-check \
    --schedule="0 8 * * *" \
    --uri="$MAIN_APP_URL/api/scheduler/check-temperatures" \
    --http-method=GET \
    --location=$REGION \
    --description="Daily temperature check at 8 AM" \
    --time-zone="America/New_York"

# Create hourly temperature check job (every hour from 6 AM to 8 PM)
echo "Creating hourly temperature check job..."
gcloud scheduler jobs create http hourly-temperature-check \
    --schedule="0 6-20 * * *" \
    --uri="$MAIN_APP_URL/api/scheduler/check-temperatures" \
    --http-method=GET \
    --location=$REGION \
    --description="Hourly temperature check from 6 AM to 8 PM" \
    --time-zone="America/New_York"

# Create peak hours temperature check job (12 PM and 4 PM)
echo "Creating peak hours temperature check job..."
gcloud scheduler jobs create http peak-hours-temperature-check \
    --schedule="0 12,16 * * *" \
    --uri="$MAIN_APP_URL/api/scheduler/check-temperatures" \
    --http-method=GET \
    --location=$REGION \
    --description="Peak hours temperature check at 12 PM and 4 PM" \
    --time-zone="America/New_York"

echo ""
echo "Note: You can control the frequency of checks by:"
echo "1. Disabling jobs you don't want: gcloud scheduler jobs pause [job-name] --location=$REGION"
echo "2. Using the admin dashboard to set frequency to 'daily' for production"
echo "3. For production, you may want to pause hourly and peak-hours jobs:"
echo "   gcloud scheduler jobs pause hourly-temperature-check --location=$REGION"
echo "   gcloud scheduler jobs pause peak-hours-temperature-check --location=$REGION"

echo "Cloud Scheduler jobs created successfully!"
echo ""
echo "Job details:"
gcloud scheduler jobs list --location=$REGION

echo ""
echo "Test the scheduler health endpoint:"
echo "curl $MAIN_APP_URL/api/scheduler/health" 
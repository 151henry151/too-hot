# GCP Deployment Guide - Too Hot Temperature Alerts

This guide explains how to deploy the Too Hot temperature alert system on Google Cloud Platform with automatic scheduling.

## Architecture Overview

The system consists of a single Cloud Run service with integrated scheduling:

1. **Main App** (`too-hot`): Flask application handling web interface, API endpoints, email/push notifications, and scheduler endpoints
2. **Cloud Scheduler**: GCP managed service that triggers temperature checks via HTTP requests

## Prerequisites

- Google Cloud Project with billing enabled
- Cloud Build API enabled
- Cloud Run API enabled
- Cloud Scheduler API enabled
- Secret Manager API enabled

## Step 1: Deploy the Main Application

```bash
# Deploy the main app
gcloud builds submit --config cloudbuild.yaml
```

This will:
- Build the Docker image
- Deploy to Cloud Run
- Configure all secrets from Secret Manager
- Set up the main API endpoints and scheduler endpoints

## Step 2: Set Up Cloud Scheduler Jobs

```bash
# Run the setup script
./setup-cloud-scheduler.sh
```

This creates three scheduler jobs:
- **Daily check**: Runs at 8 AM every day
- **Hourly check**: Runs every hour from 6 AM to 8 PM
- **Peak hours check**: Runs at 12 PM and 4 PM

## Step 3: Verify Deployment

### Check Main App
```bash
# Test the main app
curl https://too-hot-ao5zbahlha-uc.a.run.app/api/subscribers
```

### Check Scheduler Endpoints
```bash
# Test the scheduler health
curl https://too-hot-ao5zbahlha-uc.a.run.app/api/scheduler/health

# Test manual temperature check
curl https://too-hot-ao5zbahlha-uc.a.run.app/api/scheduler/check-temperatures
```

### Check Scheduler Jobs
```bash
# List all scheduler jobs
gcloud scheduler jobs list --location=us-central1
```

## Step 4: Test the System

### Add a Test Subscriber
```bash
curl -X POST https://too-hot-ao5zbahlha-uc.a.run.app/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "location": "New York"}'
```

### Trigger a Test Alert
```bash
curl -X POST https://too-hot-ao5zbahlha-uc.a.run.app/api/test-temperature-alert \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "use_real_data": true}'
```

## Monitoring and Logs

### View Logs
```bash
# Main app logs (includes scheduler activity)
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=too-hot" --limit=50
```

### Check Scheduler Job History
```bash
# View job execution history
gcloud scheduler jobs describe daily-temperature-check --location=us-central1
```

## Troubleshooting

### Common Issues

1. **Weather API Key Not Working**
   ```bash
   # Check if secret exists
   gcloud secrets list
   
   # Update secret if needed
   echo "your-api-key" | gcloud secrets versions add weather-api-key --data-file=-
   ```

2. **Scheduler Not Triggering**
   ```bash
   # Check scheduler job status
   gcloud scheduler jobs list --location=us-central1
   
   # Manually trigger a job
   gcloud scheduler jobs run daily-temperature-check --location=us-central1
   ```

3. **Email Not Sending**
   ```bash
   # Check mail secrets
   gcloud secrets versions access latest --secret=mail-username
   gcloud secrets versions access latest --secret=mail-password
   ```

### Manual Testing

```bash
# Test temperature check manually
curl https://too-hot-ao5zbahlha-uc.a.run.app/api/scheduler/check-temperatures

# Check subscriber count
curl https://too-hot-ao5zbahlha-uc.a.run.app/api/subscribers

# Test push notifications
curl -X POST https://too-hot-ao5zbahlha-uc.a.run.app/api/send-push-notification \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Alert", "body": "Test notification"}'
```

## Cost Optimization

- **Single Service**: Only one Cloud Run service to manage
- **Cloud Scheduler**: Very low cost (~$0.10/month per job)
- **Scale to Zero**: Cloud Run can scale to zero when not in use

## Security

- All sensitive data stored in Secret Manager
- Service runs with minimal permissions
- HTTPS enforced on all endpoints
- No local environment files needed

## Updates and Maintenance

### Deploy Updates
```bash
# Deploy app updates
gcloud builds submit --config cloudbuild.yaml
```

### Update Secrets
```bash
# Update any secret
echo "new-value" | gcloud secrets versions add secret-name --data-file=-
```

### Monitor Performance
```bash
# Check Cloud Run metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

## Architecture Benefits

1. **Simplicity**: Single service to manage and deploy
2. **Cost Effective**: Only one Cloud Run service
3. **Reliability**: Cloud Scheduler provides guaranteed execution
4. **Monitoring**: Centralized logs and metrics
5. **Security**: All secrets managed by Secret Manager
6. **Maintainability**: Less complexity, easier to debug 
#!/bin/bash

# Deploy Too Hot Climate Awareness Campaign to Google Cloud Platform
# This script builds and deploys the application to Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌍 Deploying Too Hot Climate Awareness Campaign to GCP${NC}"

# Check if required environment variables are set
if [ -z "$MAIL_USERNAME" ] || [ -z "$MAIL_PASSWORD" ] || [ -z "$WEATHER_API_KEY" ]; then
    echo -e "${RED}❌ Error: Required environment variables not set${NC}"
    echo "Please set the following environment variables:"
    echo "  - MAIL_USERNAME: Your Gmail address"
    echo "  - MAIL_PASSWORD: Your Gmail app password"
    echo "  - WEATHER_API_KEY: Your WeatherAPI.com API key"
    echo ""
    echo "Example:"
    echo "  export MAIL_USERNAME=your-email@gmail.com"
    echo "  export MAIL_PASSWORD=your-app-password"
    echo "  export WEATHER_API_KEY=your-weather-api-key"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Please install the Google Cloud SDK:"
    echo "  https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: No project ID set${NC}"
    echo "Please set a project ID:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the Docker image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
IMAGE_NAME="gcr.io/$PROJECT_ID/too-hot:latest"
docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy too-hot \
    --image $IMAGE_NAME \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 5000 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production \
    --set-env-vars MAIL_USERNAME="$MAIL_USERNAME" \
    --set-env-vars MAIL_PASSWORD="$MAIL_PASSWORD" \
    --set-env-vars WEATHER_API_KEY="$WEATHER_API_KEY" \
    --set-env-vars SECRET_KEY="$(openssl rand -hex 32)"

# Get the service URL
SERVICE_URL=$(gcloud run services describe too-hot --platform managed --region us-central1 --format="value(status.url)")

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Test the application: curl $SERVICE_URL"
echo "2. Set up a custom domain (optional)"
echo "3. Configure monitoring and logging"
echo "4. Set up the scheduler service (separate deployment)"
echo ""
echo -e "${GREEN}🌍 The climate awareness campaign is now live!${NC}" 
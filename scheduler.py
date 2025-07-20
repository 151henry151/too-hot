#!/usr/bin/env python3
"""
Temperature Alert Scheduler
Runs periodic checks for temperature conditions and sends notifications.
"""

import requests
import time
import schedule
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('temperature_alerts.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:5000"
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def check_temperatures():
    """Check temperatures and send notifications"""
    try:
        logger.info("Starting temperature check...")
        
        response = requests.get(f"{API_BASE_URL}/api/check-temperatures")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Temperature check completed: {data['message']}")
            
            if data['notifications_sent'] > 0:
                logger.info(f"Sent {data['notifications_sent']} notifications")
                for detail in data['details']:
                    logger.info(f"Alert sent to {detail['email']} for {detail['location']}: "
                              f"Current: {detail['current_temp']}°F, Avg: {detail['avg_temp']}°F")
            else:
                logger.info("No temperature alerts triggered")
        else:
            logger.error(f"Failed to check temperatures: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error during temperature check: {e}")

def get_subscriber_count():
    """Get current subscriber count"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/subscribers")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Current subscribers: {data['count']}")
            return data['count']
        else:
            logger.error(f"Failed to get subscriber count: {response.status_code}")
            return 0
    except Exception as e:
        logger.error(f"Error getting subscriber count: {e}")
        return 0

def main():
    """Main scheduler function"""
    logger.info("Starting Too Hot Temperature Alert Scheduler")
    
    # Check if weather API key is configured
    if not WEATHER_API_KEY:
        logger.error("Weather API key not configured. Please set WEATHER_API_KEY in your environment.")
        return
    
    # Get initial subscriber count
    subscriber_count = get_subscriber_count()
    logger.info(f"Initial subscriber count: {subscriber_count}")
    
    # Schedule temperature checks
    # Check every hour during the day (6 AM to 8 PM)
    schedule.every().hour.at(":00").do(check_temperatures)
    
    # Also check at specific times for more frequent monitoring during peak hours
    schedule.every().day.at("08:00").do(check_temperatures)
    schedule.every().day.at("12:00").do(check_temperatures)
    schedule.every().day.at("16:00").do(check_temperatures)
    schedule.every().day.at("18:00").do(check_temperatures)
    
    logger.info("Scheduler configured. Running checks every hour and at peak times.")
    
    # Run the scheduler
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
            # Log status every 6 hours
            if datetime.now().hour % 6 == 0 and datetime.now().minute == 0:
                logger.info("Scheduler is running...")
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in scheduler: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main() 
import os
import time
import schedule
import requests
import tweepy
import logging
from datetime import datetime, UTC, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Try to load from .env file, silently continue if file not found
env_path = Path('.env')
if env_path.exists():
    logging.info("Loading environment from .env file")
    load_dotenv(env_path)
else:
    logging.info("No .env file found, using system environment variables")

# Verify Twitter API credentials are loaded
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
GRAFANA_TOKEN = os.environ.get('GRAFANA_TOKEN')

# Verify all required credentials are available
if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, GRAFANA_TOKEN]):
    logging.error("Missing required environment variables!")
    raise Exception("Missing required environment variables. Please ensure all credentials are set either in .env file or system environment.")

logging.info("Environment variables loaded successfully!")

def fetch_image():
    """Fetch the image from Grafana dashboard"""
    # Calculate yesterday's date range
    yesterday = datetime.now(UTC) - timedelta(days=1)
    from_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    url = "https://dashboard.notrustverify.ch/render/d-solo/MggjRL1Vz/overall-stats"
    params = {
        "panelId": "8",
        "var-coinbase": "false",
        "from": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "to": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "width": "720",
        "height": "480",
        "tz": "utc"
    }
    headers = {
        "Authorization": f"Bearer {GRAFANA_TOKEN}"
    }
    
    logging.info(f"Fetching data from {from_date} to {to_date}")
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        image_path = "/app/data/panel.jpg"
        with open(image_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Image saved successfully to {image_path}")
        return image_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch image: {str(e)}")
        if hasattr(response, 'status_code'):
            logging.error(f"Status code: {response.status_code}")
        return None

def post_to_twitter():
    """Post the image to Twitter"""
    try:
        logging.info("Initializing Twitter client")
        # Initialize Twitter client
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Initialize API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        
        # Fetch the image
        image_path = fetch_image()
        if image_path:
            logging.info("Uploading media to Twitter")
            # Upload media
            media = api.media_upload(filename=image_path)
            
            # Get yesterday's date for the tweet with month name and day
            yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%B %d")
            tweet_text = f"🔥 Daily $ALPH Burned - {yesterday}"
            
            logging.info("Posting tweet")
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            logging.info(f"Successfully posted tweet at {datetime.now(UTC)}")
        else:
            logging.error("Failed to fetch image, skipping tweet")
    except Exception as e:
        logging.error(f"Error posting to Twitter: {str(e)}")

def main():
    """Main function to schedule and run the bot"""
    logging.info("Starting Twitter bot...")
    
    # Schedule the job to run at 00:01 UTC
    schedule.every().day.at("00:01").do(post_to_twitter)
    logging.info("Scheduled daily post for 00:01 UTC")
    
    # Run the first post immediately
    # logging.info("Running initial post...")
    # post_to_twitter()
    
    # Keep the script running
    logging.info("Bot is now running. Waiting for scheduled tasks...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 
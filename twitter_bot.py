import os
import time
import schedule
import requests
import tweepy
from datetime import datetime, UTC, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Try to load from .env file, silently continue if file not found
env_path = Path('.env')
if env_path.exists():
    print("Loading environment from .env file")
    load_dotenv(env_path)
else:
    print("No .env file found, using system environment variables")

# Verify Twitter API credentials are loaded
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
GRAFANA_TOKEN = os.environ.get('GRAFANA_TOKEN')

# Verify all required credentials are available
if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, GRAFANA_TOKEN]):
    raise Exception("Missing required environment variables. Please ensure all credentials are set either in .env file or system environment.")

print("Environment variables loaded successfully!")

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
    
    print(f"Fetching data from {from_date} to {to_date}")
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        image_path = "/app/data/panel.jpg"
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    print(f"Failed to fetch image. Status code: {response.status_code}")
    return None

def post_to_twitter():
    """Post the image to Twitter"""
    try:
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
            # Upload media
            media = api.media_upload(filename=image_path)
            
            # Get yesterday's date for the tweet with month name and day
            yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%B %d")
            tweet_text = f"🔥 Daily $ALPH Burned - {yesterday}"
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            print(f"Successfully posted tweet at {datetime.now(UTC)}")
        else:
            print("Failed to fetch image")
    except Exception as e:
        print(f"Error posting to Twitter: {str(e)}")

def main():
    """Main function to schedule and run the bot"""
    print("Starting Twitter bot...")
    
    # Schedule the job to run at 00:01 UTC
    schedule.every().day.at("00:01").do(post_to_twitter)
    
    # Run the first post immediately
    post_to_twitter()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 
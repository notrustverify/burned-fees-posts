# Alephium Burned Fees Twitter Bot

This bot automatically posts daily updates about Alephium burned fees to Twitter. It fetches a graph from the Alephium dashboard and posts it at 00:00 UTC every day.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your Twitter API credentials:
```
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

To get these credentials:
1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Generate the API keys and access tokens
4. Make sure your app has read and write permissions

## Running the Bot

Simply run the Python script:
```bash
python twitter_bot.py
```

The bot will:
1. Make an initial post when started
2. Schedule daily posts at 00:00 UTC
3. Continue running until stopped

## Features

- Fetches the burned fees graph from the Alephium dashboard
- Posts daily updates with the graph image
- Includes the date and relevant hashtags in each tweet
- Runs automatically at 00:00 UTC
- Error handling and logging

## Notes

- The bot needs to be running continuously to post daily updates
- Consider using a process manager like `supervisor` or running it in a Docker container for production use
- Make sure your system time is correctly synchronized with UTC 
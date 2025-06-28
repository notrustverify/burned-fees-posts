FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY twitter_bot.py .

# Create directory for the image
RUN mkdir -p /app/data

CMD ["python", "twitter_bot.py"] 
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY twitter_bot.py .

# Create directory for the image
RUN mkdir -p /app/data

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "twitter_bot.py"] 
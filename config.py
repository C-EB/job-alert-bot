# job_alert_bot/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
load_dotenv()

# --- Telegram Bot Configuration ---
# Get your Telegram Bot Token from BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# --- Database Configuration ---
# Path to the SQLite database file
DATABASE_PATH = "job_alerts.db"

# --- Scraping Configuration ---
# User-Agent to use for HTTP requests to avoid being blocked
# Using a common browser User-Agent is recommended
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- Scheduler Configuration ---
# Time for the daily scraping job to run (in UTC)
# Example: "10:00" for 10:00 AM UTC
SCHEDULED_JOB_TIME = "10:00"

# --- Logging Configuration ---
LOGGING_LEVEL = "DEBUG" # Can be "DEBUG", "INFO", "WARNING", "ERROR"
import os
import logging

webhook_url_file = "webhook_url.txt"  # File to store the last set webhook URL
logger = logging.getLogger(__name__)


def read_last_webhook_url():
    try:
        with open(webhook_url_file, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        logger.error("Webhook URL file not found.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading webhook URL file: {e}")
        return None


def write_last_webhook_url(url):
    try:
        with open(webhook_url_file, "w") as file:
            file.write(url)
    except Exception as e:
        logger.error(f"Failed to write webhook URL to file: {e}")

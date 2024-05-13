import os
from dotenv import load_dotenv, set_key
import logging
import requests

logger = logging.getLogger(__name__)


# A list of all environment variables
ENV_VARIABLES = [
    "GROQ_API_KEY",
    "BOT_TOKEN",
    "WEBHOOK_URL",
    "HEROKU_API",
    "HEROKU_EMAIL",
    "GITGUARDIAN_API_KEY",
    "DATABASE_URL",
]

def update_database_url():
    HEROKU_API_KEY = os.getenv('HEROKU_API_KEY')
    HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
    url = f'https://api.heroku.com/apps/{HEROKU_APP_NAME}/config-vars'
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {HEROKU_API_KEY}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        config_vars = response.json()
        database_url = config_vars.get('DATABASE_URL')
        if database_url:
            set_key('.env', 'DATABASE_URL', database_url)
            logger.info("DATABASE_URL updated successfully in .env")
        else:
            logger.warning("DATABASE_URL not found in config vars")
    else:
        logger.error(f"Failed to fetch config vars: {response.status_code}")

def load_env_vars(env):
    if env == "dev":
        load_dotenv()
        update_database_url()

    env_vars = {}
    try:
        for var in ENV_VARIABLES:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
            else:
                print(f"Warning {var} not set")
        logger.info("Environment variables loaded")
        return env_vars

    except Exception as e:
        logger.error(f"Error loading environment variables: {e}")

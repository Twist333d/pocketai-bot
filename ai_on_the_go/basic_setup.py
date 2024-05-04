import os
from dotenv import load_dotenv
import logging

# Setup logger
logger = logging.getLogger(__name__)


# A list of all environment variables
ENV_VARIABLES = [
    'GROQ_API_KEY',
    'BOT_TOKEN',
    'WEBHOOK_URL',
    'HEROKU_API',
    'HEROKU_EMAIL',
    'GITGUARDIAN_API_KEY',
]

def load_env_vars(env):
    if env == 'dev':
        load_dotenv()

    env_vars ={}
    try:
        for var in ENV_VARIABLES:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
            else:
                print(f'Warning {var} not set')
        logger.info("Environment variables loaded")
        return env_vars

    except Exception as e:
        logger.error(f'Error loading environment variables: {e}')
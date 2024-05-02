# Telegram
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# utils
import logging
import os

# other modules
from ai_on_the_go.webhook_utils import write_last_webhook_url, read_last_webhook_url
from ai_on_the_go.llm_integration import get_llm_response, setup_llm_conversation

# General
from contextlib import asynccontextmanager
from collections import defaultdict

# Langchain
from langchain_groq import ChatGroq

# Fast API
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# initialize FastAPI
app = FastAPI()

# Get all the API keys:
GROQ_API_KEY = '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'
BOT_TOKEN = '7144711700:AAE3Wt-vrcpfM43wSK1eMFUMFXPcYKfte64'

# Telegram bot setup
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure langchain groq client
llm = ChatGroq(temperature=0.8, groq_api_key=GROQ_API_KEY, model_name='llama3-70b-8192')

# Dictionary to manage conversation for each user
conversations = defaultdict(lambda: None)#

# check, if webhook is valid
async def check_and_update_webhook():
    desired_webhook_url = os.getenv("WEBHOOK_URL", "https://pocketai-prod-64cf99db36a4.herokuapp.com/webhook")
    last_webhook_url = read_last_webhook_url()

    if last_webhook_url != desired_webhook_url:
        await bot.set_webhook(url=desired_webhook_url)
        write_last_webhook_url(desired_webhook_url)
        print("Webhook set successfully to", desired_webhook_url)
    else:
        print("Webhook already set to the correct URL, no update needed.")

# Let's replace on_event with lifespan
""" 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ """
    Defining lifespan context manager that will:
    - executes code before application accepts any requests
    - executes code after application has finished accepting any requests
    Use case: Loads the resources only before they are needed
    :param app:
    :return:
    """  """
    # initialize the application
    logger.debug("Starting application initialization.")
    try:
        await application.initialize()  # no longer needed
        # setup the webhook
        # Optionally check an environment variable to conditionally set the webhook
        if os.getenv("SET_WEBHOOK", "false").lower() in ['true', '1', 't']:
            await check_and_update_webhook()
        #webhook_url = f"https://ai-on-the-go-7a6698c2fd9b.herokuapp.com/webhook"
        #await bot.set_webhook(url=webhook_url)
        logger.info("Webhook setup complete.")
    except Exception as e:
        print(f"Error during application initialization: {e}")
"""

@app.on_event("startup")
async def startup():
    # initialize the application
    logger.debug("Starting application initialization.")
    try:
        await application.initialize()
        if os.getenv("SET_WEBHOOK", "false").lower() in ['true', '1', 't']:
            await check_and_update_webhook()
            logger.info("Webhook setup complete.")
    except Exception as e:
        print(f"Error during application initialization: {e}")

        # setup the webhook
        #webhook_url = f"https://ai-on-the-go-7a6698c2fd9b.herokuapp.com/webhook"
        #await bot.set_webhook(url=webhook_url)
        #logger.info("Webhook setup complete at %s", webhook_url)



# Command handler for /start
async def start(update:Update, context):
    logger.debug("Received /start command from user %s", update.effective_chat.id)
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! Welcome to AI On The Go Bot! Send any message to start AI-On The Go Bot."
        )
    except Exception as e:
        logger.error("Failed to send start message due to: %s", str(e))
        raise e


# Get message from user -> send to Groq API -> send back the response
async def handle_message(update:Update, context):
    user_text = update.message.text # extract text from the user message
    user_id = update.effective_chat.id
    logger.debug("Received message from user %s: %s", update.effective_chat.id, user_text)

    # check if user has a conversation
    if conversations[user_id] is None:
        conversations[user_id] = await setup_llm_conversation(llm)


    try:
        chat_response = await get_llm_response(conversations[user_id], user_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_response)
        logger.debug("Sent response to user %s: %s", update.effective_chat.id, chat_response)
    except Exception as e:
        logger.error("Error during message handling: %s", str(e))
        raise e

# Add handlers to the application
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Setup the webhook
@app.post('/webhook')
async def webhook_updates(request: Request):
    try:
        data = await request.json()
        logger.debug(f"Received webhook data: {data}")
        update = Update.de_json(data, bot)

        # if de_json doesn't raise an error, we assume it's a valid TG object
        await application.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        # log the error and send it back in the response for the debugging
        logger.error(f"Failed to process update: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"message": "Bad Request: Invalid data", "error": str(e)})


# Run the app using Uvicorn, if the script is run directly
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
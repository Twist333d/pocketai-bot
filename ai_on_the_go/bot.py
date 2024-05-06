# Telegram
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes

# utils
import logging
import os
from dotenv import load_dotenv

# other modules
from ai_on_the_go.llm_integration import get_llm_response, setup_llm_conversation
from ai_on_the_go.basic_setup import load_env_vars

# General
from collections import defaultdict

# Langchain
from langchain_groq import ChatGroq

# Fast API
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Setup the port
PORT = 5000

# initialize FastAPI
app = FastAPI()
bot = None
application = None

# Access env variables
load_dotenv()

# Load all environment variables
env = os.getenv("ENV", "dev")  # default to development
load_env_vars(env)  # get all env vars

# Extract each needed variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Set lower verbosity for httpx and telegram
# logging.getLogger('httpx').setLevel(logging.WARNING)
# logging.getLogger('telegram').setLevel(logging.WARNING)
# logging.getLogger('httpcore').setLevel(logging.WARNING)

# Configure langchain groq client
llm = ChatGroq(temperature=0.8, groq_api_key=GROQ_API_KEY,
               model_name="llama3-70b-8192")

# Dictionary to manage conversation for each user
conversations = defaultdict(lambda: None)  #


async def check_webhook():
    current_webhook_info = await bot.get_webhook_info()
    current_webhook_url = current_webhook_info.url
    logger.info(f"Current webhook URL: {current_webhook_url}")

    if current_webhook_url != WEBHOOK_URL:
        try:
            await bot.set_webhook(WEBHOOK_URL)
            logger.info("Webhook successfully updated")
        except Exception as e:
            logger.info(f"Webhook update failed: {e}")
    else:
        logger.info("Webhook already set, no update needed.")


# Command handler for /start
async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.effective_chat.id
    logger.info("Start command received")

    logger.debug(f"Received /start command from user: {user_chat_id}")
    try:
        await context.bot.send_message(
            chat_id=user_chat_id,
            text="Hello, how can I help you today?",
        )
    except Exception as e:
        logger.error("Failed to send start message due to: %s", str(e))
        raise e


# Get message from user -> send to Groq API -> send back the response
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text  # extract text from the user message
    user_id = update.effective_chat.id
    logger.debug("Received message from user %s: %s",
                 update.effective_chat.id, user_message)

    # check if user has a conversation
    if conversations[user_id] is None:
        conversations[user_id] = await setup_llm_conversation(llm)

    try:
        chat_response = await get_llm_response(conversations[user_id], user_message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_response)
        logger.debug("Sent response to user %s: %s",
                     update.effective_chat.id, chat_response)
    except Exception as e:
        logger.error("Error during message handling: %s", str(e))
        raise e


# Add handlers to the application
# application.add_handler(CommandHandler("start", start))
# application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))


# Setup the webhook
@app.post("/webhook")
async def webhook_updates(request: Request):
    global application
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


@app.on_event("startup")
async def startup():
    # initialize the application
    logger.debug("*** APPLICATION INITIALIZATION ***.")
    try:
        # Telegram bot setup
        logger.debug("*** BOT SETUP ***")

        # Create the application
        global bot
        global application
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        bot = application.bot

        # Add handlers after initialization is confirmed
        application.add_handler(CommandHandler("start", command_start))
        application.add_handler(MessageHandler(
            filters.TEXT & (~filters.COMMAND), handle_message))
        logger.debug("Handlers successfully added")

        # initialize
        await application.initialize()
        logger.debug(application)
        logger.debug(f"Bot Token: {bot.token}")
        logger.debug(f"Bot url: {bot.base_url}")  # Async call to get username
        logger.debug(f"Bot commands: {await bot.get_my_commands()}")

        # Setup webhook
        logger.debug("*** CHECKING WEBHOOK SETUP ***")
        await check_webhook()

    except Exception as e:
        logger.error(f"Error during application initialization: {e}")


# Run the app using Uvicorn, if the script is run directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

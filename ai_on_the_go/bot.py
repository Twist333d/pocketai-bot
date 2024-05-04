# Telegram
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

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

# initialize FastAPI
app = FastAPI()
# let's add another line just for testing

# Access env variables
load_dotenv()

# Load all environment variables
env = os.getenv("ENV", "dev")  # default to development
load_env_vars(env)  # get all env vars

# Extract each needed variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Telegram bot setup
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure langchain groq client
llm = ChatGroq(temperature=0.8, groq_api_key=GROQ_API_KEY,
               model_name="llama3-70b-8192")

# Dictionary to manage conversation for each user
conversations = defaultdict(lambda: None)  #


async def check_webhook():
    current_webhook_info = await bot.getWebhookInfo()
    current_webhook_url = current_webhook_info.url
    logger.info(f"Current webhook URL: {current_webhook_url}")

    if current_webhook_url != WEBHOOK_URL:
        try:
            await bot.setWebhook(WEBHOOK_URL)
            logger.info("Webhook successfully updated")
        except Exception as e:
            logger.info(f"Webhook update failed: {e}")
    else:
        logger.info("Webhook already set, no update needed.")


@app.on_event("startup")
async def startup():
    # initialize the application
    logger.debug("*** APPLICATION INITIALIZATION ***.")
    try:
        await application.initialize()
        logger.debug("*** CHECKING WEBHOOK SETUP ***")
        await check_webhook()

    except Exception as e:
        logger.error(f"Error during application initialization: {e}")


# Command handler for /start
async def start(update: Update, context):
    logger.debug("Received /start command from user %s",
                 update.effective_chat.id)
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! Welcome to AI On The Go Bot! Send any message to start AI-On The Go Bot.",
        )
    except Exception as e:
        logger.error("Failed to send start message due to: %s", str(e))
        raise e


# Get message from user -> send to Groq API -> send back the response
async def handle_message(update: Update, context):
    user_text = update.message.text  # extract text from the user message
    user_id = update.effective_chat.id
    logger.debug("Received message from user %s: %s",
                 update.effective_chat.id, user_text)

    # check if user has a conversation
    if conversations[user_id] is None:
        conversations[user_id] = await setup_llm_conversation(llm)

    try:
        chat_response = await get_llm_response(conversations[user_id], user_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_response)
        logger.debug("Sent response to user %s: %s",
                     update.effective_chat.id, chat_response)
    except Exception as e:
        logger.error("Error during message handling: %s", str(e))
        raise e


# Add handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(
    filters.TEXT & (~filters.COMMAND), handle_message))


# Setup the webhook
@app.post("/webhook")
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
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)

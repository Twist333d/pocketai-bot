import os
import asyncio
import logging
from fastapi.logger import  logger as fastapi_logger

from fastapi import FastAPI, Request, Response, HTTPException
from telegram import Bot, Update, MessageEntity

from telegram.ext import Application, CommandHandler, ContextTypes

# Initialize FastAPI app
app = FastAPI()

# Setup basic config for logging
logging.basicConfig(level=logging.DEBUG)
fastapi_logger.addHandler(logging.StreamHandler())
fastapi_logger.setLevel(logging.DEBUG)

# Retrieve your bot token and initialize your bot
BOT_TOKEN = "7144711700:AAE3Wt-vrcpfM43wSK1eMFUMFXPcYKfte64"
bot = Bot(token=BOT_TOKEN)


# Define the command handler function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fastapi_logger.debug("/Start command triggered")

    # Try to send a welcome message
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! Welcome to my first bot!")
        fastapi_logger.debug("Welcome message sent") # confirm message

        # Follow up with a question
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Which model would you like to use?"
        )
        fastapi_logger.debug("Model choice question sent")
    except Exception as e:
        fastapi_logger.error(f"Failed to send message: {e}", exc_info=True)


# Create an application for the bot with the command handler for '/start'
application = Application.builder().token(BOT_TOKEN).build()
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)


# FastAPI endpoint to receive updates via webhook
@app.post('/webhook')
async def process_update(request: Request) -> Response:
    update_data = await request.json()
    fastapi_logger.debug(f"Received update: {update_data}") # Log the incoming update
    update = Update.de_json(update_data, bot)

    # Update the update queue of the application
    # Try to process update:
    try:
        await application.update_queue.put(update)
        return Response(status_code=200)
    except Exception as e:
        error_msg = f"Failed to send message: {e}"
        fastapi_logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

# Set up your webhook URL like https://yourdomain.com/webhook in your application settings
def set_webhook():
    webhook_url =f"https://ai-on-the-go-7a6698c2fd9b.herokuapp.com/webhook"

    # Create an event loop and run the coroutine for setting the webhook
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.set_webhook(webhook_url))
    print(f"Webhook url set to {webhook_url}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "set_webhook":
        set_webhook()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 5000)))


from fastapi import FastAPI, Request, Response
from telegram import Bot, Update, MessageEntity
from credentials import bot_token

from telegram.ext import Application, CommandHandler, ContextTypes

# Initialize FastAPI app
app = FastAPI()

# Retrieve your bot token and initialize your bot
BOT_TOKEN = bot_token
bot = Bot(token=BOT_TOKEN)


# Define the command handler function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Welcome to your bot.")


# Create an application for the bot with the command handler for '/start'
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))


# FastAPI endpoint to receive updates via webhook
@app.post('/webhook')
async def process_update(request: Request) -> Response:
    update_data = await request.json()
    update = Update.de_json(update_data, bot)

    # Update the update queue of the application
    await application.update_queue.put(update)

    return Response(status_code=200)

# Set up your webhook URL like https://yourdomain.com/webhook in your application settings

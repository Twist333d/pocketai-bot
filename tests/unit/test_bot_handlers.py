from telegram import Update, User, Chat, Message
from datetime import datetime
from collections import defaultdict
import os

import pytest
from unittest.mock import patch, AsyncMock
from telegram.ext import ApplicationBuilder

# Import functions to be tested
from ai_on_the_go.bot import command_start, handle_message, webhook_updates

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Fixture for initializing the application
@pytest.fixture(scope="module")
async def application():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    await application.initialize()
    yield application
    await application.shutdown()






# ...

@pytest.mark.asyncio
async def test_start_command():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="/start",
            from_user=User(id=1, is_bot=False, first_name="Test"),
        ),
    )
    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    await command_start(update, context)
    context.bot.send_message.assert_called_once_with(chat_id=1, text="Hello, how can I help you today?")

@pytest.mark.asyncio
async def test_handle_message_success():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="Hello, bot!",
            from_user=User(id=1, is_bot=False, first_name="Test"),
        ),
    )
    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    with patch("ai_on_the_go.bot.setup_llm_conversation", return_value=AsyncMock()) as mock_setup:
        with patch("ai_on_the_go.bot.get_llm_response", return_value="Hello, human!") as mock_response:
            await handle_message(update, context)
            mock_response.assert_called_once_with(mock_setup.return_value, "Hello, bot!")
            context.bot.send_message.assert_called_once_with(chat_id=1, text="Hello, human!")

@pytest.mark.asyncio
async def test_handle_message_llm_failure():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="Hello, bot!",
            from_user=User(id=1, is_bot=False, first_name="Test"),
        ),
    )
    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    with patch("ai_on_the_go.bot.setup_llm_conversation", return_value=AsyncMock()) as mock_setup:
        with patch("ai_on_the_go.bot.get_llm_response", side_effect=Exception("LLM failure")) as mock_response:
            with pytest.raises(Exception):
                await handle_message(update, context)
            mock_response.assert_called_once()

@pytest.mark.asyncio
async def test_session_persistence():
    # Setup initial update and context
    update1 = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="First message",
            from_user=User(id=1, is_bot=False, first_name="Test"),
        ),
    )
    context1 = AsyncMock()
    context1.bot.send_message = AsyncMock()

    update2 = Update(
        update_id=2,
        message=Message(
            message_id=2,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="Second message",
            from_user=User(id=1, is_bot=False, first_name="Test"),
        ),
    )
    context2 = AsyncMock()
    context2.bot.send_message = AsyncMock()

    # Mock the conversation setup and response handling
    with patch("ai_on_the_go.bot.conversations", new_callable=lambda: defaultdict(lambda: None)) as mock_conversations:
        with patch("ai_on_the_go.bot.setup_llm_conversation", return_value=AsyncMock()) as mock_setup:
            with patch(
                "ai_on_the_go.bot.get_llm_response",
                side_effect=["Response to first message", "Response to second message"],
            ) as mock_response:
                # Process first message
                await handle_message(update1, context1)
                mock_response.assert_called_with(mock_setup.return_value, "First message")
                context1.bot.send_message.assert_called_with(chat_id=1, text="Response to first message")

                # Process second message
                await handle_message(update2, context2)
                mock_response.assert_called_with(mock_setup.return_value, "Second message")
                context2.bot.send_message.assert_called_with(chat_id=1, text="Response to second message")

    # Verify that the same conversation object is used for the same user
    assert (
        mock_conversations[1] == mock_setup.return_value
    ), "Conversation object should persist across messages from the same user"
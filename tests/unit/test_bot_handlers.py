from telegram import Update, User, Chat, Message
from datetime import datetime
from collections import defaultdict
import os

import pytest
from unittest.mock import patch, AsyncMock
from telegram.ext import ApplicationBuilder

# Import functions to be tested
from ai_on_the_go.bot import command_start, handle_message, webhook_updates
from ai_on_the_go.utils import escape_markdown


BOT_TOKEN = os.getenv("BOT_TOKEN")


# Fixture for initializing the application
@pytest.fixture(scope="module")
async def application():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    await application.initialize()
    yield application
    await application.shutdown()


@pytest.mark.asyncio
async def test_webhook_valid_request(application):
    request_data = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "date": int(datetime.now().timestamp()),
            "chat": {"id": 1, "type": "private"},
            "text": "Test message",
            "from": {"id": 1, "is_bot": False, "first_name": "Test"},
        },
    }
    request = AsyncMock()
    request.json = AsyncMock(return_value=request_data)

    with patch("ai_on_the_go.bot.application", application):
        with patch.object(application, "process_update", new_callable=AsyncMock) as mock_process_update:
            response = await webhook_updates(request)
            assert response.status_code == 200
            mock_process_update.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_with_different_update_types(application):
    inline_query_data = {
        "update_id": 1,
        "inline_query": {
            "id": "12345",
            "from": {"id": 1, "is_bot": False, "first_name": "Test"},
            "query": "search query",
            "offset": "",
        },
    }
    request = AsyncMock()
    request.json = AsyncMock(return_value=inline_query_data)

    with patch("ai_on_the_go.bot.application", application):
        with patch.object(application, "process_update", new_callable=AsyncMock) as mock_process_update:
            response = await webhook_updates(request)
            assert response.status_code == 200
            mock_process_update.assert_called_once()


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
    reply = "Welcome to PocketGPT Bot🤖! Click on the Menu button to see a list of available options."
    reply = escape_markdown(reply)
    context.bot.send_message.assert_called_once_with(chat_id=1, text=reply, parse_mode="MarkdownV2")


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

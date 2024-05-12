import os
import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, User, Chat, Message
from telegram.ext import ApplicationBuilder
from datetime import datetime
from dotenv import load_dotenv
import logging
from collections import defaultdict


# Import functions and components to be tested
from ai_on_the_go.bot import command_start, handle_message, webhook_updates
from ai_on_the_go.utils import escape_markdown

# Set environment variables (ensure these are set for your test environment)
os.environ["ENV"] = "dev"

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
async def application():
    """Fixture to initialize and tear down the Telegram application."""
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    await app.initialize()
    yield app
    await app.shutdown()


@pytest.mark.asyncio
async def test_webhook_valid_request(application):
    """Test to ensure webhook processing works correctly."""
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
    request.json.return_value = request_data

    with patch("ai_on_the_go.bot.application", application), patch(
        "ai_on_the_go.db.ensure_user_exists", AsyncMock(return_value=True)
    ):
        response = await webhook_updates(request)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_start_command(mocker):
    """Test the start command handling."""
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

    # Mock the ensure_user_exists function
    mocker.patch("ai_on_the_go.bot.ensure_user_exists", return_value=None)

    with patch("ai_on_the_go.utils.load_markdown_message", return_value="Welcome!"):
        await command_start(update, context)
        text = escape_markdown(
            "Welcome to *PocketGPT Bot 🤖*! Click on the *Menu* button to see a list of available options"
        )
        context.bot.send_message.assert_called_once_with(chat_id=1, text=text, parse_mode="MarkdownV2")


@pytest.mark.asyncio
async def test_handle_message_success():
    """Test handling of a successful message."""
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
    with patch("ai_on_the_go.bot.get_llm_response", return_value="Hello, human!"):
        await handle_message(update, context)
        context.bot.send_message.assert_called_once_with(
            chat_id=1, text=escape_markdown("Hello, human!"), parse_mode="MarkdownV2"
        )


@pytest.mark.asyncio
async def test_session_persistence():
    """Test that the session persistence mechanism works as expected."""
    context = AsyncMock()
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=1, type="private"),
        text="First message",
        from_user=User(id=1, is_bot=False, first_name="Test"),
    )
    update1 = Update(update_id=1, message=message)
    update2 = Update(update_id=2, message=message)

    with patch("ai_on_the_go.bot.conversations", new_callable=lambda: defaultdict(lambda: None)) as mock_conversations:
        await handle_message(update1, context)
        await handle_message(update2, context)
        assert (
            mock_conversations[1] is not None
        ), "Conversation object should persist across messages from the same user"

import pytest
from telegram import Update, User, Chat, Message
from unittest.mock import AsyncMock, patch
from datetime import datetime

# import start function
from ai_on_the_go.bot import start

@pytest.mark.asyncio
async def test_start_command():
    # Mocking Update and context objects from telegram
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type='private'),
            text="/start",
            from_user=User(id=1, is_bot=False, first_name="Test")
        )
    )

    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    # Patch the logger to prevent actual logging during tests
    with patch('ai_on_the_go.bot.logger') as mock_logger:
        await start(update, context)
        context.bot.send_message.assert_called_once_with(
            chat_id=1,
            text="Hello! Welcome to AI On The Go Bot! Send any message to start AI-On The Go Bot."
        )
        mock_logger.debug.assert_called()
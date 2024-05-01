import pytest
from telegram import Update, User, Chat, Message
from unittest.mock import AsyncMock, patch
from datetime import datetime
from collections import defaultdict

# import start function
from ai_on_the_go.bot import start, handle_message, application, get_llm_response, webhook


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


@pytest.mark.asyncio
async def test_handle_message_success():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type='private'),
            text="Hello, bot!",
            from_user=User(id=1, is_bot=False, first_name="Test")
        )
    )
    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    with patch('ai_on_the_go.bot.setup_llm_conversation', return_value=AsyncMock()) as mock_setup:
        with patch('ai_on_the_go.bot.get_llm_response', return_value="Hello, human!") as mock_response:
            await handle_message(update, context)
            mock_response.assert_called_once_with(mock_setup.return_value, "Hello, bot!")
            context.bot.send_message.assert_called_once_with(
                chat_id=1,
                text="Hello, human!"
            )

@pytest.mark.asyncio
async def test_handle_message_llm_failure():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type='private'),
            text="Hello, bot!",
            from_user=User(id=1, is_bot=False, first_name="Test")
        )
    )
    context = AsyncMock()
    context.bot.send_message = AsyncMock()

    with patch('ai_on_the_go.bot.setup_llm_conversation', return_value=AsyncMock()) as mock_setup:
        with patch('ai_on_the_go.bot.get_llm_response', side_effect=Exception("LLM failure")) as mock_response:
            with pytest.raises(Exception):
                await handle_message(update, context)
            mock_response.assert_called_once()



@pytest.mark.asyncio
async def test_webhook_valid_request():
    request = AsyncMock()
    request.json = AsyncMock(return_value={
        "update_id": 1,
        "message": {
            "message_id": 1,
            "date": int(datetime.now().timestamp()),
            "chat": {"id": 1, "type": 'private'},
            "text": "Test message",
            "from": {"id": 1, "is_bot": False, "first_name": "Test"}
        }
    })

    with patch('ai_on_the_go.bot.application.process_update') as mock_process_update:
        response = await webhook(request)
        assert response.status_code == 200
        mock_process_update.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_with_different_update_types():
    # Example of a non-message update, like an inline query
    inline_query_data = {
        "update_id": 1,
        "inline_query": {
            "id": "12345",
            "from": {
                "id": 1,
                "is_bot": False,
                "first_name": "Test"
            },
            "query": "search query",
            "offset": ""
        }
    }

    request = AsyncMock()
    request.json = AsyncMock(return_value=inline_query_data)

    with patch('ai_on_the_go.bot.application.process_update') as mock_process_update:
        response = await webhook(request)
        assert response.status_code == 200
        mock_process_update.assert_called_once()



@pytest.mark.asyncio
async def test_session_persistence():
    # Setup initial update and context
    update1 = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type='private'),
            text="First message",
            from_user=User(id=1, is_bot=False, first_name="Test")
        )
    )
    context1 = AsyncMock()
    context1.bot.send_message = AsyncMock()

    update2 = Update(
        update_id=2,
        message=Message(
            message_id=2,
            date=datetime.now(),
            chat=Chat(id=1, type='private'),
            text="Second message",
            from_user=User(id=1, is_bot=False, first_name="Test")
        )
    )
    context2 = AsyncMock()
    context2.bot.send_message = AsyncMock()

    # Mock the conversation setup and response handling
    with patch('ai_on_the_go.bot.conversations', new_callable=lambda: defaultdict(lambda: None)) as mock_conversations:
        with patch('ai_on_the_go.bot.setup_llm_conversation', return_value=AsyncMock()) as mock_setup:
            with patch('ai_on_the_go.bot.get_llm_response', side_effect=["Response to first message", "Response to second message"]) as mock_response:
                # Process first message
                await handle_message(update1, context1)
                mock_response.assert_called_with(mock_setup.return_value, "First message")
                context1.bot.send_message.assert_called_with(
                    chat_id=1,
                    text="Response to first message"
                )

                # Process second message
                await handle_message(update2, context2)
                mock_response.assert_called_with(mock_setup.return_value, "Second message")
                context2.bot.send_message.assert_called_with(
                    chat_id=1,
                    text="Response to second message"
                )

    # Verify that the same conversation object is used for the same user
    assert mock_conversations[1] == mock_setup.return_value, "Conversation object should persist across messages from the same user"

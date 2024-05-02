import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, AsyncMock
from ai_on_the_go.bot import app  # Ensure this import points to where your FastAPI app is defined


# Setup TestClient for FastAPI
@pytest.fixture
def client():
    return TestClient(app)


"""
def test_message_interaction_integration(client):
    update_data = {
        "update_id": 2,
        "message": {
            "message_id": 2,
            "date": int(datetime.now().timestamp()),
            "chat": {"id": 1, "type": 'private'},
            "text": "How are you?",
            "from": {"id": 1, "is_bot": False, "first_name": "Test"}
        }
    }
    with patch('telegram.Bot.send_message') as mock_send, \
         patch('ai_on_the_go.bot.get_llm_response', return_value="I'm good, thanks for asking!") as mock_llm:
        response = client.post("/webhook", json=update_data)
        assert response.status_code == 200
        mock_send.assert_called_once_with(chat_id=1, text="I'm good, thanks for asking!")
        mock_llm.assert_called_once()
"""


def test_error_handling_integration(client):
    malformed_data = {"random": "data"}
    with patch("telegram.Bot.send_message") as mock_send:
        response = client.post("/webhook", json=malformed_data)
        assert response.status_code == 500
        content = response.json()
        assert "error" in content
        assert "Invalid data" in content["message"]
        mock_send.assert_not_called()

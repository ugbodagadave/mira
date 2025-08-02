import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, User
from telegram.ext import ContextTypes

from src.bot import start, handle_message

@pytest.mark.asyncio
async def test_start_command():
    """Test the /start command handler."""
    # Mock user
    user = User(id=123, first_name="Test", is_bot=False)
    
    # Mock update
    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = AsyncMock()
    update.message.reply_html = AsyncMock()

    # Mock context
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Call the handler
    await start(update, context)

    # Assert the reply was called
    update.message.reply_html.assert_called_once()
    
    # Assert the welcome message is correct
    call_args = update.message.reply_html.call_args[0][0]
    assert "Test" in call_args  # Check that the user's name is present
    assert "I'm Mira, your personal AI agent for NFTs." in call_args  # Check for the static text


@pytest.mark.asyncio
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_calls_nlu(mock_classify_intent):
    """Test that handle_message calls the NLU processor."""
    # Arrange
    user_input = "some user message"
    nlu_response = {
        "intent": "unknown",
        "entities": {},
        "confidence": 0.5
    }
    mock_classify_intent.return_value = nlu_response

    update = MagicMock(spec=Update)
    update.message = AsyncMock()
    update.message.text = user_input
    update.message.reply_text = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_once_with(user_input)
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "Intent: unknown" in call_args

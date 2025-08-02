import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram import Update, User
from telegram.ext import ContextTypes

from src.bot import start

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

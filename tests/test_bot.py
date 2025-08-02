import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, User as TelegramUser
from telegram.ext import ContextTypes

from src.bot import start, handle_message
from src.database.models import User

@pytest.mark.asyncio
async def test_start_command():
    """Test the /start command handler."""
    # Mock user
    user = TelegramUser(id=123, first_name="Test", is_bot=False)
    
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
@patch('src.bot.db_manager.create_price_alert')
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_price_alert_intent(mock_classify_intent, mock_get_or_create_user, mock_create_price_alert):
    """Test the full flow for a 'set_price_alert' intent."""
    # Arrange
    user_input = "alert me if doodles drops below 10 eth"
    nlu_response = {
        "intent": "set_price_alert",
        "entities": {
            "collection_name": "doodles",
            "threshold_price": 10,
            "direction": "below"
        },
        "confidence": 0.98
    }
    mock_classify_intent.return_value = nlu_response
    mock_get_or_create_user.return_value = User(id=1, telegram_user_id=123, first_name="Test")
    mock_create_price_alert.return_value = None # We don't need the return value

    update = MagicMock(spec=Update)
    update.effective_user = TelegramUser(id=123, first_name="Test", is_bot=False)
    update.message = AsyncMock()
    update.message.text = user_input
    update.message.reply_text = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_once_with(user_input)
    mock_get_or_create_user.assert_called_once()
    mock_create_price_alert.assert_called_once()
    
    # Check that the confirmation message is sent
    update.message.reply_text.assert_called_with("✅ Alert set! I'll notify you if doodles goes below 10 ETH.")


@pytest.mark.asyncio
@patch('src.bot.gemini_service.generate_summary')
@patch('src.bot.unleash_nfts_service.get_collection_metrics')
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_summary_intent(mock_classify_intent, mock_get_or_create_user, mock_get_metrics, mock_generate_summary):
    """Test the full flow for a 'get_project_summary' intent."""
    # Arrange
    user_input = "summarize doodles"
    nlu_response = {
        "intent": "get_project_summary",
        "entities": {"collection_name": "doodles"},
        "confidence": 0.9
    }
    metrics_response = {"stats": {"floor_price": 1.2}}
    summary_response = "This is the summary for Doodles."

    mock_classify_intent.return_value = nlu_response
    mock_get_metrics.return_value = metrics_response
    mock_generate_summary.return_value = summary_response

    update = MagicMock(spec=Update)
    update.message = AsyncMock()
    update.message.text = user_input
    update.message.reply_text = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_once_with(user_input)
    mock_get_metrics.assert_called_once()
    mock_generate_summary.assert_called_once_with(metrics_response)
    
    # Check that the final summary is sent
    update.message.reply_text.assert_called_with(summary_response)


@pytest.mark.asyncio
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_fallback(mock_classify_intent, mock_get_or_create_user):
    """Test the fallback for unhandled intents."""
    # Arrange
    user_input = "some user message"
    nlu_response = {
        "intent": "unknown",
        "entities": {},
        "confidence": 0.5
    }
    mock_classify_intent.return_value = nlu_response
    mock_get_or_create_user.return_value = User(id=1, telegram_user_id=123, first_name="Test")

    update = MagicMock(spec=Update)
    update.effective_user = TelegramUser(id=123, first_name="Test", is_bot=False)
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


@pytest.mark.asyncio
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_greeting_intent(mock_classify_intent, mock_get_or_create_user):
    """Test that the 'greeting' intent triggers the start message."""
    # Arrange
    user_input = "hello"
    nlu_response = {
        "intent": "greeting",
        "entities": {},
        "confidence": 0.99
    }
    mock_classify_intent.return_value = nlu_response
    mock_get_or_create_user.return_value = User(id=1, telegram_user_id=123, first_name="Test")

    update = MagicMock(spec=Update)
    
    # Create a mock user object with the required attributes
    mock_user = MagicMock(spec=TelegramUser)
    mock_user.id = 123
    mock_user.first_name = "Test"
    mock_user.is_bot = False
    mock_user.mention_html.return_value = "Test"
    
    update.effective_user = mock_user
    update.message = AsyncMock()
    update.message.text = user_input
    update.message.reply_html = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_once_with(user_input)
    update.message.reply_html.assert_called_once()
    call_args = update.message.reply_html.call_args[0][0]
    assert "Hi Test!" in call_args
    assert "I'm Mira, your personal AI agent for NFTs." in call_args


@pytest.mark.asyncio
@patch('src.bot.db_manager.create_new_listing_alert')
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_handle_message_new_listing_alert_intent(mock_classify_intent, mock_get_or_create_user, mock_create_new_listing_alert):
    """Test the full flow for a 'set_new_listing_alert' intent."""
    # Arrange
    user_input = "alert me for new cryptopunks listings"
    nlu_response = {
        "intent": "set_new_listing_alert",
        "entities": {
            "collection_name": "cryptopunks"
        },
        "confidence": 0.95
    }
    mock_classify_intent.return_value = nlu_response
    mock_get_or_create_user.return_value = User(id=1, telegram_user_id=123, first_name="Test")
    mock_create_new_listing_alert.return_value = None

    update = MagicMock(spec=Update)
    update.effective_user = TelegramUser(id=123, first_name="Test", is_bot=False)
    update.message = AsyncMock()
    update.message.text = user_input
    update.message.reply_text = AsyncMock()

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_once_with(user_input)
    mock_get_or_create_user.assert_called_once()
    mock_create_new_listing_alert.assert_called_once()
    
    update.message.reply_text.assert_called_with("✅ Alert set! I'll notify you when there are new listings for cryptopunks.")

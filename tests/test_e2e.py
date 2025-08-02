import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update
from telegram.ext import ContextTypes
from telegram import User as TelegramUser

from src.bot import handle_message
from src.database.models import User

@pytest.mark.asyncio
@patch('src.bot.gemini_service.generate_summary')
@patch('src.bot.unleash_nfts_service.get_collection_metrics')
@patch('src.bot.db_manager.create_price_alert')
@patch('src.bot.db_manager.get_or_create_user')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_e2e_summary_and_alert_flow(
    mock_classify_intent,
    mock_get_or_create_user,
    mock_create_price_alert,
    mock_get_metrics,
    mock_generate_summary
):
    """
    E2E test simulating a user asking for a summary and then setting an alert.
    """
    # --- Arrange ---
    user = TelegramUser(id=123, first_name="E2E_Test", is_bot=False)
    db_user = User(id=1, telegram_user_id=123, first_name="E2E_Test")
    mock_get_or_create_user.return_value = db_user

    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # --- 1. User asks for a summary ---
    # Arrange
    summary_input = "tell me about cryptopunks"
    update.message.text = summary_input
    mock_classify_intent.return_value = {
        "intent": "get_project_summary",
        "entities": {"collection_name": "cryptopunks"}
    }
    mock_get_metrics.return_value = {"stats": {"floor_price": 50}}
    mock_generate_summary.return_value = "This is a summary for CryptoPunks."

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_with(summary_input)
    mock_get_metrics.assert_called_once()
    mock_generate_summary.assert_called_once()
    update.message.reply_text.assert_called_with("This is a summary for CryptoPunks.")

    # --- 2. User sets a price alert ---
    # Arrange
    alert_input = "alert me if punks go above 60 eth"
    update.message.text = alert_input
    update.message.reply_text.reset_mock() # Reset mock for the next call
    mock_classify_intent.return_value = {
        "intent": "set_price_alert",
        "entities": {"collection_name": "punks", "threshold_price": 60, "direction": "above"}
    }

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_with(alert_input)
    mock_create_price_alert.assert_called_once()
    update.message.reply_text.assert_called_with("✅ Alert set! I'll notify you if punks goes above 60 ETH.")

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from telegram import Update
from telegram.ext import ContextTypes, Application
from telegram import User as TelegramUser

from src.bot import handle_message
from src.database.manager import db_manager
from src.database.models import User, PriceAlert
from src.scheduler import check_price_alerts


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Fixture to set up and tear down the in-memory database for each test."""
    db_manager.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    db_manager.async_session = sessionmaker(
        db_manager.engine, expire_on_commit=False, class_=AsyncSession
    )
    await db_manager.init_db()
    yield
    await db_manager.engine.dispose()


@pytest.mark.asyncio
@patch('src.bot.gemini_service.generate_summary')
@patch('src.bot.unleash_nfts_service.get_collection_metrics')
@patch('src.bot.unleash_nfts_service.search_collection')
@patch('src.bot.classify_intent_and_extract_entities')
async def test_e2e_summary_and_alert_flow(
    mock_classify_intent,
    mock_search_collection,
    mock_get_metrics,
    mock_generate_summary
):
    """
    E2E test simulating a user asking for a summary and then setting an alert.
    This test now uses a real in-memory database.
    """
    # --- Arrange ---
    user = TelegramUser(id=123, first_name="E2E_Test", is_bot=False)
    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # --- 1. User asks for a summary ---
    summary_input = "tell me about cryptopunks"
    update.message.text = summary_input
    mock_classify_intent.return_value = {
        "intent": "get_project_summary",
        "entities": {"collection_name": "cryptopunks"}
    }
    mock_search_collection.return_value = {"metadata": {"name": "CryptoPunks", "contract_address": "0x123", "chain_id": 1}}
    mock_get_metrics.return_value = {"stats": {"floor_price": 50}}
    mock_generate_summary.return_value = "This is a summary for CryptoPunks."

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_with(summary_input)
    mock_search_collection.assert_called_once_with("cryptopunks")
    mock_get_metrics.assert_called_once()
    mock_generate_summary.assert_called_once()
    update.message.reply_text.assert_called_with("This is a summary for CryptoPunks.")

    # --- 2. User sets a price alert ---
    alert_input = "alert me if punks go above 60 eth"
    update.message.text = alert_input
    update.message.reply_text.reset_mock()
    mock_classify_intent.return_value = {
        "intent": "set_price_alert",
        "entities": {"collection_name": "punks", "threshold_price": 60, "direction": "above"}
    }

    # Act
    await handle_message(update, context)

    # Assert
    mock_classify_intent.assert_called_with(alert_input)
    update.message.reply_text.assert_called_with("✅ Alert set! I'll notify you if CryptoPunks goes above 60 ETH.")

    # --- 3. Verify alert is in the database ---
    db_user = await db_manager.get_or_create_user(123, "E2E_Test")
    assert db_user is not None
    async with db_manager.async_session() as session:
        result = await session.execute(select(PriceAlert).filter_by(user_id=db_user.id))
        alerts = result.scalars().all()
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.collection_name == "CryptoPunks"
        assert alert.threshold_price == 60
        assert alert.direction == "above"


@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_scheduler_finds_and_sends_alert(mock_get_metrics):
    mock_app = AsyncMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # --- Arrange ---
    # 1. Create a user and an active alert
    user = await db_manager.get_or_create_user(telegram_user_id=456, first_name="SchedulerTest")
    alert_data = {
        "collection_name": "cool cats",
        "collection_address": "0x1a92f7381b9f03921564a437210bb9396471050c",
        "chain": "ethereum",
        "threshold_price": 2.0,
        "direction": "below"
    }
    await db_manager.create_price_alert(user, alert_data)

    # 2. Mock the API response to simulate the price condition being met
    mock_get_metrics.return_value = {"floor_price": 1.9} # Price is below the 2.0 threshold

    # --- Act ---
    await check_price_alerts(mock_app)

    # --- Assert ---
    # 1. Check that the floor price was requested for the correct collection
    mock_get_metrics.assert_called_once_with(
        blockchain=1, # Assuming ethereum maps to 1
        address="0x1a92f7381b9f03921564a437210bb9396471050c"
    )

    # 2. Check that a notification message was sent
    mock_app.bot.send_message.assert_called_once()
    call_args = mock_app.bot.send_message.call_args
    assert call_args[1]['chat_id'] == 456 # Check telegram_user_id
    assert "🚨 Price Alert for cool cats!" in call_args[1]['text']
    assert "is now 1.9 ETH, which is below your alert threshold of 2.0 ETH" in call_args[1]['text']

    # 3. Verify the alert is now inactive
    async with db_manager.async_session() as session:
        result = await session.execute(select(PriceAlert).filter_by(user_id=user.id, is_active=True))
        alerts = result.scalars().all()
        assert len(alerts) == 0

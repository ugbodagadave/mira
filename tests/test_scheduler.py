import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram.ext import Application
from sqlalchemy import select

from src.scheduler import check_price_alerts
from src.database.manager import DatabaseManager
from src.database.models import User, PriceAlert

@pytest.fixture
async def db_manager_with_alerts():
    """Fixture to create an in-memory DB with a user and an active alert."""
    manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await manager.init_db()
    
    user = await manager.get_or_create_user(123, "Test")
    await manager.create_price_alert(user, {
        "collection_name": "Doodles",
        "collection_address": "0x1a92f7381b9f03921564a437210bb9396471050c",
        "chain": "ethereum",
        "threshold_price": 10.0,
        "direction": "below"
    })
    return manager

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that an alert is triggered and deactivated."""
    # Arrange
    mock_get_metrics.return_value = {"floor_price": 9.5}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_called_once()
    async with db_manager_with_alerts.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == False))
        alerts = result.scalars().all()
        assert len(alerts) == 1

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_not_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that an alert is not triggered."""
    # Arrange
    mock_get_metrics.return_value = {"floor_price": 10.5}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_not_called()

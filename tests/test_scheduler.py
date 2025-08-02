import pytest
from unittest.mock import AsyncMock, patch

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
        "collection_address": "0x123",
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
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        triggered_alerts = await check_price_alerts()

    # Assert
    assert len(triggered_alerts) == 1
    assert triggered_alerts[0].is_active == False

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_not_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that an alert is not triggered."""
    # Arrange
    mock_get_metrics.return_value = {"floor_price": 10.5}
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        triggered_alerts = await check_price_alerts()

    # Assert
    assert len(triggered_alerts) == 0

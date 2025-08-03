import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram.ext import Application
from sqlalchemy import select

from src.scheduler import check_price_alerts
from src.database.manager import DatabaseManager
from src.database.models import User, PriceAlert

@pytest.fixture
async def db_manager_with_alerts():
    """Fixture to create an in-memory DB and allow adding users and alerts."""
    manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await manager.init_db()
    
    async def _add_user_and_alert(telegram_id, collection_name, address, chain, threshold, direction, is_active=True):
        user = await manager.get_or_create_user(telegram_id, "Test")
        alert_data = {
            "collection_name": collection_name,
            "collection_address": address,
            "chain": chain,
            "threshold_price": threshold,
            "direction": direction,
        }
        # Directly control the is_active flag in the test setup
        async with manager.async_session() as session:
            new_alert = PriceAlert(
                user_id=user.id,
                collection_name=alert_data["collection_name"],
                collection_address=alert_data["collection_address"],
                chain=alert_data["chain"],
                threshold_price=alert_data["threshold_price"],
                direction=alert_data["direction"],
                is_active=is_active
            )
            session.add(new_alert)
            await session.commit()
        return user, new_alert

    manager.add_user_and_alert = _add_user_and_alert
    return manager

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_below_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that a 'below' alert is triggered and deactivated."""
    # Arrange
    await db_manager_with_alerts.add_user_and_alert(123, "Doodles", "0x123", "ethereum", 10.0, "below")
    mock_get_metrics.return_value = {"floor_price": 9.5}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_called_once()
    call_args = mock_app.bot.send_message.call_args
    assert call_args[1]['chat_id'] == 123
    assert "floor price is now 9.5 ETH" in call_args[1]['text']
    
    async with db_manager_with_alerts.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == False))
        alerts = result.scalars().all()
        assert len(alerts) == 1

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_above_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that an 'above' alert is triggered and deactivated."""
    # Arrange
    await db_manager_with_alerts.add_user_and_alert(456, "CryptoPunks", "0x456", "ethereum", 100.0, "above")
    mock_get_metrics.return_value = {"floor_price": 101.0}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_called_once()
    call_args = mock_app.bot.send_message.call_args
    assert call_args[1]['chat_id'] == 456
    assert "floor price is now 101.0 ETH" in call_args[1]['text']

    async with db_manager_with_alerts.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == False))
        alerts = result.scalars().all()
        assert len(alerts) == 1

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_not_triggered(mock_get_metrics, db_manager_with_alerts):
    """Test that an alert is not triggered if the price condition is not met."""
    # Arrange
    await db_manager_with_alerts.add_user_and_alert(789, "Azuki", "0x789", "ethereum", 50.0, "below")
    mock_get_metrics.return_value = {"floor_price": 50.5}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_not_called()
    async with db_manager_with_alerts.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == True))
        alerts = result.scalars().all()
        assert len(alerts) == 1

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_api_failure(mock_get_metrics, db_manager_with_alerts):
    """Test that nothing happens if the API call fails."""
    # Arrange
    await db_manager_with_alerts.add_user_and_alert(111, "Bored Apes", "0xabc", "ethereum", 200.0, "below")
    mock_get_metrics.return_value = None  # Simulate API failure
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_not_called()
    async with db_manager_with_alerts.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == True))
        alerts = result.scalars().all()
        assert len(alerts) == 1

@pytest.mark.asyncio
@patch('src.scheduler.unleash_nfts_service.get_collection_metrics')
async def test_check_price_alerts_only_active(mock_get_metrics, db_manager_with_alerts):
    """Test that only active alerts are checked."""
    # Arrange
    await db_manager_with_alerts.add_user_and_alert(222, "Active Alert", "0xdef", "ethereum", 10.0, "below", is_active=True)
    await db_manager_with_alerts.add_user_and_alert(333, "Inactive Alert", "0xghi", "ethereum", 20.0, "below", is_active=False)
    
    mock_get_metrics.return_value = {"floor_price": 9.0}
    mock_app = MagicMock(spec=Application)
    mock_app.bot.send_message = AsyncMock()
    
    # Act
    with patch('src.scheduler.db_manager', db_manager_with_alerts):
        await check_price_alerts(mock_app)

    # Assert
    mock_app.bot.send_message.assert_called_once() # Only the active alert should trigger
    call_args = mock_app.bot.send_message.call_args
    assert call_args[1]['chat_id'] == 222

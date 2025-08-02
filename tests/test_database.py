import pytest
from src.database.manager import DatabaseManager
from src.database.models import User

@pytest.fixture
async def db_manager():
    """Fixture to create an in-memory SQLite database for testing."""
    manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await manager.init_db()
    return manager

@pytest.mark.asyncio
async def test_get_or_create_user_new(db_manager: DatabaseManager):
    """Test creating a new user."""
    # Act
    user = await db_manager.get_or_create_user(123, "Test")

    # Assert
    assert user.telegram_user_id == 123
    assert user.first_name == "Test"
    assert user.id is not None

@pytest.mark.asyncio
async def test_get_or_create_user_existing(db_manager: DatabaseManager):
    """Test retrieving an existing user."""
    # Arrange
    await db_manager.get_or_create_user(123, "Test")

    # Act
    user = await db_manager.get_or_create_user(123, "Test")

    # Assert
    assert user.telegram_user_id == 123

@pytest.mark.asyncio
async def test_create_price_alert(db_manager: DatabaseManager):
    """Test creating a price alert."""
    # Arrange
    user = await db_manager.get_or_create_user(123, "Test")
    alert_data = {
        "collection_name": "Doodles",
        "collection_address": "0x123",
        "chain": "ethereum",
        "threshold_price": 10.5,
        "direction": "below"
    }

    # Act
    alert = await db_manager.create_price_alert(user, alert_data)

    # Assert
    assert alert.id is not None
    assert alert.user_id == user.id
    assert alert.collection_name == "Doodles"
    assert alert.direction == "below"

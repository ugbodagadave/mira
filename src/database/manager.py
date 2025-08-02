from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from src.config import config
from src.database.models import Base, User, PriceAlert

class DatabaseManager:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_or_create_user(self, telegram_user_id: int, first_name: str) -> User:
        async with self.async_session() as session:
            result = await session.execute(
                select(User).filter_by(telegram_user_id=telegram_user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(telegram_user_id=telegram_user_id, first_name=first_name)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    async def create_price_alert(self, user: User, alert_data: dict) -> PriceAlert:
        async with self.async_session() as session:
            alert = PriceAlert(
                user_id=user.id,
                collection_name=alert_data['collection_name'],
                collection_address=alert_data['collection_address'],
                chain=alert_data['chain'],
                threshold_price=alert_data['threshold_price'],
                direction=alert_data['direction'],
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert

# Use a placeholder for the DB URL if it's not set (for testing)
db_url = config.DATABASE_URL or "sqlite+aiosqlite:///:memory:"
db_manager = DatabaseManager(db_url)

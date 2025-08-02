import asyncio
from src.database.manager import db_manager
from src.database.models import Base

async def create_tables():
    """Connects to the database and creates all tables."""
    print("Connecting to the database and creating tables...")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())

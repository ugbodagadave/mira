import asyncio
from src.database.manager import db_manager
from src.database.models import Base

async def create_tables():
    """Connects to the database, drops all existing tables, and creates new ones."""
    print("Connecting to the database to re-create tables...")
    async with db_manager.engine.begin() as conn:
        # Drop all tables
        print("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        print("Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Tables re-created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())

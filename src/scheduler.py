import asyncio
from sqlalchemy.future import select

from src.database.manager import db_manager
from src.database.models import PriceAlert
from src.services.unleashnfts_api import unleash_nfts_service
from src.services.gemini_ai import gemini_service # Assuming alert logic will be here

async def check_price_alerts():
    """
    Fetches all active price alerts and checks if their conditions are met.
    """
    print("Checking price alerts...")
    async with db_manager.async_session() as session:
        result = await session.execute(select(PriceAlert).where(PriceAlert.is_active == True))
        alerts = result.scalars().all()

        for alert in alerts:
            print(f"Checking alert {alert.id} for {alert.collection_name}...")
            metrics = await unleash_nfts_service.get_collection_metrics(
                alert.chain, alert.collection_address
            )

            if not metrics or 'floor_price' not in metrics:
                print(f"Could not retrieve metrics for {alert.collection_name}")
                continue

            floor_price = metrics['floor_price']
            triggered = False
            if alert.direction == 'below' and floor_price < alert.threshold_price:
                triggered = True
            elif alert.direction == 'above' and floor_price > alert.threshold_price:
                triggered = True

            if triggered:
                print(f"ALERT TRIGGERED for {alert.collection_name}!")
                # In a real implementation, we would send a message via the Telegram bot.
                # For now, we'll just deactivate the alert to prevent spam.
                alert.is_active = False
                session.add(alert)
    
    await session.commit()
    print("Finished checking price alerts.")
    return [alert for alert in alerts if not alert.is_active]

async def main():
    await db_manager.init_db() # Ensure tables are created
    await check_price_alerts()

if __name__ == "__main__":
    asyncio.run(main())

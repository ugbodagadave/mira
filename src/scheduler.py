import asyncio
from sqlalchemy.future import select
from telegram.ext import Application

from src.database.manager import db_manager
from src.database.models import PriceAlert, User
from src.services.unleashnfts_api import unleash_nfts_service

async def check_price_alerts(app: Application):
    """
    Fetches all active price alerts, checks if their conditions are met,
    and sends a notification using the provided bot instance.
    """
    print("Checking price alerts...")
    async with db_manager.async_session() as session:
        # Join User table to get telegram_user_id
        stmt = (
            select(PriceAlert, User.telegram_user_id)
            .join(User, PriceAlert.user_id == User.id)
            .where(PriceAlert.is_active == True)
        )
        result = await session.execute(stmt)
        alerts_with_users = result.all()

        for alert, telegram_user_id in alerts_with_users:
            print(f"Checking alert {alert.id} for {alert.collection_name}...")
            
            # Assuming chain is stored as an integer, matching the API
            chain_id = 1 if alert.chain == "ethereum" else alert.chain

            metrics = await unleash_nfts_service.get_collection_metrics(
                blockchain=chain_id, address=alert.collection_address
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
                message = (
                    f"🚨 Price Alert for {alert.collection_name}! 🚨\n\n"
                    f"The floor price is now {floor_price} ETH, which is {alert.direction} "
                    f"your alert threshold of {alert.threshold_price} ETH."
                )
                try:
                    await app.bot.send_message(chat_id=telegram_user_id, text=message)
                    alert.is_active = False
                    session.add(alert)
                except Exception as e:
                    print(f"Failed to send message to {telegram_user_id}: {e}")

        await session.commit()
    print("Finished checking price alerts.")

async def main():
    # This is for standalone testing and won't be used by the bot itself
    from src.bot import create_app
    app = create_app()
    await db_manager.init_db()
    await check_price_alerts(app)

if __name__ == "__main__":
    asyncio.run(main())

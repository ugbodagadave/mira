import asyncio
import os
import logging
from src.bot import create_app
from src.config import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main() -> None:
    """Set up and run the bot with a webhook, managing the event loop correctly."""
    application = create_app()

    # --- Correct, non-blocking setup for running inside an existing event loop ---

    # 1. Initialize the application
    await application.initialize()

    # 2. Set the webhook
    port = int(os.environ.get("PORT", 8443))
    webhook_url = f"{config.WEBHOOK_URL}/{config.TELEGRAM_BOT_TOKEN}"
    await application.bot.set_webhook(url=webhook_url, allowed_updates=application.update_types)

    # 3. Start the application and the webhook server
    # We use the lower-level, non-blocking start_webhook method.
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url,
    )

    # 4. Keep the script running
    # In a real application, you might have a more sophisticated way to wait
    # for a shutdown signal. For this deployment, we'll just run forever.
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")

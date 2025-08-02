import asyncio
import os
from src.bot import create_app
from src.config import config

async def health(_: object) -> tuple[int, bytes]:
    """A simple health check endpoint that returns a 200 OK response."""
    return 200, b"OK"


async def main() -> None:
    """Set up and run the bot with a webhook."""
    application = create_app()

    # Add the health check endpoint
    application.add_handlers([(("/health", ["GET"]), health)])

    # Render provides the port to listen on via the PORT environment variable
    port = int(os.environ.get("PORT", 8443))
    
    # The webhook URL is derived from the Render service URL
    # It should be set in the environment variables for clarity
    webhook_url = f"{config.WEBHOOK_URL}/{config.TELEGRAM_BOT_TOKEN}"

    await application.bot.set_webhook(url=webhook_url)
    
    # The `python-telegram-bot` library's `Application` object is a fully-fledged ASGI app.
    # We can run it directly with its own simple web server.
    # We listen on all interfaces (0.0.0.0) inside the container.
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    asyncio.run(main())

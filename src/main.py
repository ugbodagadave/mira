import asyncio
import os
import logging
from aiohttp import web
from src.bot import create_app
from src.config import config
from src.scheduler import check_price_alerts

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def scheduler_webhook_handler(request: web.Request) -> web.Response:
    """Handles the GET request from the external cron job service."""
    secret = request.match_info.get("secret")
    if secret != config.SCHEDULER_SECRET:
        logger.warning("Unauthorized scheduler call attempt.")
        return web.Response(status=401, text="Unauthorized")

    logger.info("Scheduler webhook called, checking alerts...")
    # We need the application object to send messages
    application = request.app["telegram_app"]
    asyncio.create_task(check_price_alerts(application))
    
    return web.Response(text="Scheduler triggered.")

async def run_scheduler_server(application) -> web.AppRunner:
    """Sets up and runs the aiohttp server for the scheduler."""
    scheduler_app = web.Application()
    scheduler_app.router.add_get("/scheduler/{secret}", scheduler_webhook_handler)
    scheduler_app["telegram_app"] = application  # Make the app available to the handler

    runner = web.AppRunner(scheduler_app)
    await runner.setup()
    
    # Use a different port for the scheduler to avoid conflicts
    scheduler_port = int(os.environ.get("SCHEDULER_PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", scheduler_port)
    await site.start()
    logger.info(f"Scheduler server running on port {scheduler_port}")
    return runner

async def main() -> None:
    """Set up and run the bot and the scheduler server."""
    application = create_app()

    # --- Bot Setup ---
    await application.initialize()
    port = int(os.environ.get("PORT", 8443))
    webhook_url = f"{config.WEBHOOK_URL}/{config.TELEGRAM_BOT_TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=config.TELEGRAM_BOT_TOKEN,
        webhook_url=webhook_url,
    )
    logger.info(f"Telegram bot webhook server running on port {port}")

    # --- Scheduler Server Setup ---
    scheduler_runner = await run_scheduler_server(application)

    # Keep the script running
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await scheduler_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")

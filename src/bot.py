import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.config import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"Hi {user.mention_html()}! I'm Mira, your personal AI agent for NFTs.\n\n"
        "You can ask me for project summaries, set price alerts, and more. "
        "Just talk to me in natural language!\n\n"
        "For example, try asking: 'Give me a summary of the Doodles collection.'"
    )
    await update.message.reply_html(welcome_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all non-command messages."""
    # For now, we'll just echo the message back.
    # In the future, this will route to the NLU processor.
    await update.message.reply_text(f"Echo: {update.message.text}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == "__main__":
    main()

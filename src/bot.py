import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.config import config
from src.nlu.processor import classify_intent_and_extract_entities
from src.services.unleashnfts_api import unleash_nfts_service
from src.services.gemini_ai import gemini_service

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
    """Handles all non-command messages by routing them through the NLU processor."""
    user_input = update.message.text
    nlu_result = await classify_intent_and_extract_entities(user_input)
    
    intent = nlu_result.get('intent')
    entities = nlu_result.get('entities', {})

    if intent == 'get_project_summary':
        collection_name = entities.get('collection_name')
        if not collection_name:
            await update.message.reply_text("I'm sorry, I couldn't identify the collection name. Please try again.")
            return
        
        # This is a simplification. A real implementation would need to resolve the
        # collection name to an address and blockchain. For now, we'll assume a direct match.
        # We will use a placeholder address for now.
        collection_address = "0xbd49448e92423253930b3310a5563539a68e643e" # Doodles
        blockchain = "ethereum"

        await update.message.reply_text(f"Fetching summary for {collection_name}...")

        collection_data = await unleash_nfts_service.get_collection_metrics(blockchain, collection_address)
        
        if not collection_data:
            await update.message.reply_text("I'm sorry, I couldn't retrieve data for that collection.")
            return

        summary = await gemini_service.generate_summary(collection_data)
        await update.message.reply_text(summary)

    else:
        # Fallback for other intents
        response_text = (
            f"Intent: {intent}\n"
            f"Entities: {entities}\n"
            f"Confidence: {nlu_result.get('confidence')}"
        )
        await update.message.reply_text(response_text)


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

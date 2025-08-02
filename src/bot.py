import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.config import config
from src.nlu.processor import classify_intent_and_extract_entities
from src.services.unleashnfts_api import unleash_nfts_service
from src.services.gemini_ai import gemini_service
from src.database.manager import db_manager
from src.scheduler import check_price_alerts

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
    user = await db_manager.get_or_create_user(
        telegram_user_id=update.effective_user.id,
        first_name=update.effective_user.first_name
    )

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

    elif intent == 'set_price_alert':
        collection_name = entities.get('collection_name')
        threshold_price = entities.get('threshold_price')
        direction = entities.get('direction')

        if not all([collection_name, threshold_price, direction]):
            await update.message.reply_text("I'm missing some details for the alert. Please specify the collection, price, and direction (above/below).")
            return
            
        # Placeholder for collection address and chain
        alert_data = {
            "collection_name": collection_name,
            "collection_address": "0x123", # Placeholder
            "chain": "ethereum", # Placeholder
            "threshold_price": threshold_price,
            "direction": direction
        }
        
        await db_manager.create_price_alert(user, alert_data)
        await update.message.reply_text(f"✅ Alert set! I'll notify you if {collection_name} goes {direction} {threshold_price} ETH.")

    else:
        # Fallback for other intents
        response_text = (
            f"Intent: {intent}\n"
            f"Entities: {entities}\n"
            f"Confidence: {nlu_result.get('confidence')}"
        )
        await update.message.reply_text(response_text)


async def check_price_alerts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the scheduler webhook call."""
    # A simple secret key check for security
    # In a real app, you might use a more robust method
    secret = context.args[0] if context.args else None
    if secret != config.SCHEDULER_SECRET:
        logger.warning("Unauthorized scheduler call attempt.")
        return

    logger.info("Scheduler webhook called, checking alerts...")
    await check_price_alerts()


def create_app() -> Application:
    """Creates and configures the Telegram bot application."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("scheduler", check_price_alerts_handler))

    return application

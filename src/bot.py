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

        await update.message.reply_text(f"Searching for {collection_name}...")
        collection = await unleash_nfts_service.search_collection(collection_name)

        if not collection:
            await update.message.reply_text(f"I couldn't find a collection named {collection_name}. Please try another name.")
            return

        collection_address = collection["metadata"]["contract_address"]
        blockchain = collection["metadata"]["chain_id"]
        
        await update.message.reply_text(f"Fetching summary for {collection['metadata']['name']}...")

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

        await update.message.reply_text(f"Searching for {collection_name}...")
        collection = await unleash_nfts_service.search_collection(collection_name)

        if not collection:
            await update.message.reply_text(f"I couldn't find a collection named {collection_name}. Please try another name.")
            return

        collection_address = collection["metadata"]["contract_address"]
        chain = collection["metadata"]["chain_id"]
        
        alert_data = {
            "collection_name": collection['metadata']['name'],
            "collection_address": collection_address,
            "chain": str(chain),
            "threshold_price": threshold_price,
            "direction": direction
        }
        
        await db_manager.create_price_alert(user, alert_data)
        await update.message.reply_text(f"✅ Alert set! I'll notify you if {collection['metadata']['name']} goes {direction} {threshold_price} ETH.")

    elif intent == 'set_new_listing_alert':
        collection_name = entities.get('collection_name')

        if not collection_name:
            await update.message.reply_text("I'm sorry, I couldn't identify the collection name. Please try again.")
            return

        alert_data = {
            "collection_name": collection_name,
            "collection_address": "0x456",  # Placeholder
            "chain": "ethereum",  # Placeholder
        }

        await db_manager.create_new_listing_alert(user, alert_data)
        await update.message.reply_text(f"✅ Alert set! I'll notify you when there are new listings for {collection_name}.")

    elif intent == 'track_wallet':
        wallet_address = entities.get('wallet_address')

        if not wallet_address:
            await update.message.reply_text("I'm sorry, I couldn't identify the wallet address. Please try again.")
            return

        await db_manager.create_tracked_wallet(user, wallet_address)
        await update.message.reply_text(f"✅ Wallet tracking enabled! I'll monitor {wallet_address} for NFT activity.")

    elif intent == 'get_market_trends':
        await update.message.reply_text("Here is a summary of the current market trends...")

    elif intent == 'greeting':
        await start(update, context)

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
    await check_price_alerts(context.application)


def create_app() -> Application:
    """Creates and configures the Telegram bot application."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("scheduler", check_price_alerts_handler))

    return application

import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
load_dotenv()

class Config:
    """
    Configuration class to hold all secrets and settings.
    """
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BITCRUNCH_API_KEY = os.getenv("BITCRUNCH_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Basic validation to ensure keys are set
    if not all([TELEGRAM_BOT_TOKEN, BITCRUNCH_API_KEY, GEMINI_API_KEY, DATABASE_URL]):
        missing = [
            k for k, v in {
                "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
                "BITCRUNCH_API_KEY": BITCRUNCH_API_KEY,
                "GEMINI_API_KEY": GEMINI_API_KEY,
                "DATABASE_URL": DATABASE_URL
            }.items() if not v
        ]
        # In a real app, you'd raise an exception or log a fatal error.
        # For now, we'll print a warning.
        print(f"⚠️ WARNING: Missing required environment variables: {', '.join(missing)}")

# Instantiate config
config = Config()

import google.generativeai as genai
import json

from src.config import config

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

# Define the intents and entities the model should recognize
INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "set_price_alert",
                "set_new_listing_alert",
                "get_project_summary",
                "track_wallet",
                "get_market_trends",
                "greeting",
                "unknown"
            ]
        },
        "entities": {
            "type": "object",
            "properties": {
                "collection_name": {"type": "string"},
                "threshold_price": {"type": "number"},
                "direction": {"type": "string", "enum": ["above", "below"]},
                "wallet_address": {"type": "string"}
            }
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reasoning": {"type": "string"}
    },
    "required": ["intent", "confidence", "reasoning"]
}

async def classify_intent_and_extract_entities(user_input: str) -> dict:
    """
    Uses Gemini 2.5 Pro to classify user intent and extract entities.
    
    Args:
        user_input: The raw text from the user.
        
    Returns:
        A dictionary containing the classified intent, extracted entities,
        confidence score, and the model's reasoning.
    """
    prompt = f"""
    Analyze the following user request and classify it into one of the predefined intents.
    Extract any relevant entities based on the schema.
    
    Your response MUST be a valid JSON object that adheres to the following schema:
    {json.dumps(INTENT_SCHEMA, indent=2)}

    Here are the definitions for each intent:
    - 'set_price_alert': User wants to be notified about a price change for an NFT collection.
    - 'set_new_listing_alert': User wants to know when new NFTs from a collection are listed.
    - 'get_project_summary': User is asking for a summary or details about an NFT project.
    - 'track_wallet': User wants to monitor an Ethereum wallet address for NFT activity.
    - 'get_market_trends': User is asking for a general overview of the NFT market.
    - 'greeting': A simple greeting or introductory message.
    - 'unknown': The user's intent cannot be determined from the request.

    Provide a confidence score between 0 and 1.
    Provide a brief reasoning for your classification.

    User Request: "{user_input}"

    JSON Response:
    """
    
    try:
        response = await model.generate_content_async(prompt)
        # The response from Gemini might be wrapped in markdown, so we clean it.
        cleaned_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_json)
        return result
    except Exception as e:
        print(f"Error during NLU processing: {e}")
        return {
            "intent": "unknown",
            "entities": {},
            "confidence": 0.0,
            "reasoning": f"An error occurred during processing: {e}"
        }

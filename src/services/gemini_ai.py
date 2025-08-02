import google.generativeai as genai
import json

from src.config import config

genai.configure(api_key=config.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.summary_model = genai.GenerativeModel('gemini-2.5-pro')
        self.alert_model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_summary(self, collection_data: dict) -> str:
        """
        Generates a concise summary of an NFT collection using Gemini 2.5 Pro.
        
        Args:
            collection_data: A dictionary of data fetched from the UnleashNFTs API.
            
        Returns:
            A string containing the AI-generated summary.
        """
        prompt = f"""
        Based on the following data for an NFT collection, generate a concise and insightful summary for a potential investor or collector.
        
        Highlight key metrics like floor price, volume, and number of holders. Mention any notable trends.
        Keep the summary to 2-3 paragraphs.

        Data:
        {json.dumps(collection_data, indent=2)}

        Summary:
        """
        
        try:
            response = await self.summary_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error during summary generation: {e}")
            return "I'm sorry, I was unable to generate a summary at this time."

# Instantiate the service
gemini_service = GeminiService()

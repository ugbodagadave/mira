import httpx
from src.config import config

BASE_URL = "https://api.unleashnfts.com/api/v1"

class UnleashNFTsService:
    def __init__(self):
        self.api_key = config.BITCRUNCH_API_KEY
        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key
        }

    async def _request(self, method: str, endpoint: str, params: dict = None):
        """Helper function to make requests to the API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, f"{BASE_URL}{endpoint}", headers=self.headers, params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {e.request.url!r}.")
                return None

    async def get_collection_metrics(self, blockchain: str, address: str):
        """Get metrics for a specific collection."""
        endpoint = f"/collection/{blockchain}/{address}/metrics"
        return await self._request("GET", endpoint)

    async def get_collection_nfts(self, blockchain: str, address: str, limit: int = 50):
        """Get NFTs for a specific collection."""
        endpoint = f"/collection/{blockchain}/{address}/nfts"
        params = {"limit": limit}
        return await self._request("GET", endpoint, params=params)

    async def get_wallet_nfts(self, address: str, blockchain: str = "ethereum"):
        """Get NFTs held by a specific wallet."""
        endpoint = f"/wallet/{address}/nfts"
        params = {"blockchain": blockchain}
        return await self._request("GET", endpoint, params=params)

    async def get_market_trends(self):
        """Get overall market trends."""
        endpoint = "/market/trend"
        return await self._request("GET", endpoint)

# Instantiate the service
unleash_nfts_service = UnleashNFTsService()

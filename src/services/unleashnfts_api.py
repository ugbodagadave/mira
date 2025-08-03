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
                print(f"Making request to {BASE_URL}{endpoint} with params {params}")
                response = await client.request(
                    method, f"{BASE_URL}{endpoint}", headers=self.headers, params=params
                )
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.text}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {e.request.url!r}.")
                return None
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {e.request.url!r}.")
                return None

    async def get_collection_metrics(self, blockchain: str, address: str):
        """Get metrics for a specific collection."""
        endpoint = f"/collection/{blockchain}/{address}/metrics"
        # The 'metrics' parameter is required by the API.
        params = {"metrics": "volume"}
        return await self._request("GET", endpoint, params=params)

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

    async def search_collection(self, name: str, limit: int = 100, max_pages: int = 20):
        """
        Search for a collection by name. First, try a direct name search.
        If that fails, paginate through collections to find a match.
        """
        endpoint = "/collections"
        
        # --- Attempt 1: Direct search by name (assuming API supports it) ---
        params_by_name = {
            "blockchain": 1,
            "name": name
        }
        named_search_data = await self._request("GET", endpoint, params=params_by_name)
        if named_search_data and named_search_data.get("collections"):
            # The API might return multiple partial matches, find the best one
            for collection in named_search_data["collections"]:
                if name.lower() == collection.get("metadata", {}).get("name", "").lower():
                    return collection # Return exact match immediately
            return named_search_data["collections"][0] # Return the first result as best guess

        # --- Attempt 2: Paginate and search if direct search fails ---
        for page in range(max_pages):
            offset = page * limit
            params_paginate = {
                "blockchain": 1,
                "metrics": "volume",
                "sort_by": "volume",
                "sort_order": "desc",
                "time_range": "24h",
                "limit": limit,
                "offset": offset
            }
            collections_data = await self._request("GET", endpoint, params=params_paginate)

            if not collections_data or not collections_data.get("collections"):
                break

            for collection in collections_data["collections"]:
                if name.lower() in collection.get("metadata", {}).get("name", "").lower():
                    return collection

        return None

# Instantiate the service
unleash_nfts_service = UnleashNFTsService()

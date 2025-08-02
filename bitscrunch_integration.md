# UnleashNFTs (BitCrunch) API Integration

This document provides a detailed overview of how the Mira AI agent integrates with the UnleashNFTs API (formerly known as the BitCrunch API) to provide real-time NFT data.

## 1. Overview

The UnleashNFTs API is the primary data source for all NFT and blockchain-related information used by Mira. We interact with the API through a dedicated service module (`src/services/unleashnfts_api.py`), which handles all requests, authentication, and error handling.

## 2. Authentication

All requests to the UnleashNFTs API are authenticated using an API key sent in the request headers. The API key is stored securely as an environment variable (`BITCRUNCH_API_KEY`) and is never hardcoded. The service module automatically includes the following headers in every request:

```python
headers = {
    "accept": "application/json",
    "x-api-key": "your_api_key_here"
}
```

## 3. Implemented Services

The following UnleashNFTs API endpoints have been integrated into Mira:

### 3.1. Collection Metrics

-   **Endpoint:** `GET /api/v1/collection/{blockchain}/{address}/metrics`
-   **Purpose:** This endpoint is used to fetch real-time metrics for a specific NFT collection, such as floor price, trading volume, and holder counts.
-   **Mira's Usage:** This is the primary endpoint used for the **Project Summary** feature. The data retrieved is passed to the Gemini AI service to generate a concise summary. It is also used by the **Scheduler** to check the current floor price for active alerts.
-   **Key Implementation Details:**
    -   The `{blockchain}` path parameter must be the integer **chain ID** (e.g., `1` for Ethereum), not a string name.
    -   The request requires at least one metric to be specified in the `metrics` query parameter (e.g., `?metrics=volume`).

### 3.2. Collection NFTs

-   **Endpoint:** `GET /api/v1/collection/{blockchain}/{address}/nfts`
-   **Purpose:** This endpoint retrieves a list of all NFTs within a specific collection.
-   **Mira's Usage:** This endpoint is essential for the **New Listing Alerts** feature. The scheduler will periodically call this endpoint to check for new NFTs that have been listed.

### 3.3. Wallet NFTs

-   **Endpoint:** `GET /api/v1/wallet/{address}/nfts`
-   **Purpose:** This endpoint retrieves a list of all NFTs held by a specific wallet address.
-   **Mira's Usage:** This is the core endpoint for the **Wallet Activity Monitoring** feature. The scheduler will use this to monitor for changes in a wallet's NFT holdings.

### 3.4. Market Trends

-   **Endpoint:** `GET /api/v1/market/trend`
-   **Purpose:** This endpoint provides high-level data about the overall NFT market trends.
-   **Mira's Usage:** This endpoint is used for the **Market Trend Analysis** feature, providing the data needed for the Gemini AI to generate a market summary.

## 4. Error Handling

The `unleashnfts_api.py` service includes robust error handling for all API requests. It automatically handles:

-   **HTTP Status Errors:** If the API returns an error code (e.g., 404 Not Found, 500 Internal Server Error), the service will catch the error and return `None`, preventing the application from crashing.
-   **Request Errors:** If there is a network issue or the API is unreachable, the service will catch the error and return `None`.

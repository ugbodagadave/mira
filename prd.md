# Product Requirements Document: Telegram AI Agent Mira for NFT Alerts and Project Summaries

## 1. Introduction

This document outlines the requirements for a Telegram-based AI agent named Mira, designed to provide real-time NFT alerts and comprehensive project summaries through natural language interaction. The core objective is to deliver an AI-first, data-powered Web3 tool that is useful, interactive, and original, leveraging the BitCrunch API for data and Google's Gemini models for AI capabilities. The bot will be hosted on Render's free plan.

## 2. Goals

The primary goals of this project are:

* To provide timely and accurate NFT alerts to users based on customizable criteria expressed in natural language.
* To generate concise and insightful summaries of NFT projects, collections, and market trends in response to user queries.
* To offer an interactive and user-friendly experience within the Telegram messaging platform, allowing users to communicate with Mira naturally.
* To demonstrate the effective integration of Web3 data (BitCrunch API) with advanced AI capabilities (Gemini models).
* To build a scalable and maintainable solution hosted on a cost-effective platform (Render free plan).

## 3. Features

### 3.1. NFT Price Alerts

**Description:** Users can set up alerts for specific NFTs or collections based on price changes by expressing their request in natural language.

**BitCrunch API Endpoint Usage:**
* `GET /api/v1/collection/{blockchain}/{address}/metrics`: To fetch current price data for a collection.
* `GET /api/v1/collection/{blockchain}/{address}/trend`: To monitor price trends over time for detecting significant changes.

**Gemini Model Usage:**
* **Gemini 2.5 Flash (model name: `gemini-2.5-flash`)**: For real-time, low-latency processing of price data to identify alert triggers.

**User Interaction Flow:**
1. User sends a natural language request, such as "Mira, notify me if the price of Bored Ape Yacht Club drops below 50 ETH."
2. Mira uses Google Gemini's NLP to classify the intent as "set_price_alert" and extract entities like collection name, threshold price, and direction.
3. Mira validates the input, confirms the alert setup (e.g., "Got it! I'll notify you if the price of Bored Ape Yacht Club drops below 50 ETH."), and stores the alert configuration.
4. Mira periodically checks the collection's price using the BitCrunch API.
5. When the price condition is met, Mira sends a notification to the user.

### 3.2. New Listing Alerts

**Description:** Users can receive alerts when new NFTs from a specified collection are listed on major marketplaces by requesting in natural language.

**BitCrunch API Endpoint Usage:**
* `GET /api/v1/collection/{blockchain}/{address}/nfts`: To periodically check for newly listed NFTs within a collection.

**Gemini Model Usage:**
* **Gemini 2.5 Flash (model name: `gemini-2.5-flash`)**: For efficient processing of new NFT listings data.

**User Interaction Flow:**
1. User sends a natural language request, such as "Mira, alert me when there are new listings for CryptoPunks."
2. Mira uses NLP to classify the intent as "set_new_listing_alert" and extract the collection name.
3. Mira confirms the alert setup (e.g., "Sure! I'll let you know when there are new listings for CryptoPunks.") and stores the alert configuration.
4. Mira periodically checks for new listings using the BitCrunch API.
5. When new listings are detected, Mira sends a notification with details like NFT name, image, listing price, and marketplace link.

### 3.3. Project Summary Generation

**Description:** Users can request a summary of an NFT project or collection by asking Mira in natural language.

**BitCrunch API Endpoint Usage:**
* `GET /api/v1/collection/{blockchain}/{address}`: To retrieve general collection metadata.
* `GET /api/v1/collection/{blockchain}/{address}/metrics`: To get aggregate metrics like market cap, volume, and unique holders.
* `GET /api/v1/collection/{blockchain}/{address}/trend`: To understand recent trends in sales and volume.
* `GET /api/v1/collection/{blockchain}/{address}/traits`: To get information about the traits and their distribution.
* `GET /api/v1/collection/{blockchain}/{address}/rarity`: To get rarity data for the collection.

**Gemini Model Usage:**
* **Gemini 2.5 Pro (model name: `gemini-2.5-pro`)**: For generating comprehensive and nuanced summaries by synthesizing information from multiple API calls.

**User Interaction Flow:**
1. User sends a natural language request, such as "Mira, can you give me a summary of the Doodles collection?"
2. Mira uses NLP to classify the intent as "get_project_summary" and extract the collection name.
3. Mira fetches data from multiple BitCrunch API endpoints related to the collection.
4. Mira uses Gemini 2.5 Pro to synthesize the data into a concise and insightful summary.
5. Mira sends the summary to the user.

### 3.4. Wallet Activity Monitoring

**Description:** Users can monitor specific wallet addresses for NFT transactions by instructing Mira in natural language.

**BitCrunch API Endpoint Usage:**
* `GET /api/v1/wallet/{address}/nfts`: To get NFTs held by a wallet.
* `GET /api/v1/wallet/{address}/profile`: To get general wallet profile information.
* `GET /api/v1/wallet/{address}/metrics`: To get metrics related to wallet activity.

**Gemini Model Usage:**
* **Gemini 2.5 Flash (model name: `gemini-2.5-flash`)**: For efficient processing of wallet transaction data.

**User Interaction Flow:**
1. User sends a natural language request, such as "Mira, track the wallet 0x123... for NFT activity."
2. Mira uses NLP to classify the: intent as "track_wallet" and extract the wallet address.
3. Mira confirms the tracking setup (e.g., "Alright, I'll monitor the wallet 0x123... for NFT transactions.") and stores the wallet address.
4. Mira periodically checks for new transactions using the BitCrunch API.
5. When new transactions are detected, Mira sends a notification to the user with details of the activity.

### 3.5. Market Trend Analysis (On-Demand)

**Description:** Users can request a quick overview of overall NFT market trends by asking Mira in natural language.

**BitCrunch API Endpoint Usage:**
* `GET /api/v1/market/metrics`: To get aggregate market metrics.
* `GET /api/v1/market/trend`: To get market trend data.
* `GET /api/v1/collections`: To get top collections by various metrics.

**Gemini Model Usage:**
* **Gemini 2.5 Pro (model name: `gemini-2.5-pro`)**: For synthesizing market data into a digestible trend analysis.

**User Interaction Flow:**
1. User sends a natural language request, such as "Mira, what's the current trend in the NFT market?"
2. Mira uses NLP to classify the intent as "get_market_trends."
3. Mira fetches relevant market data from the BitCrunch API.
4. Mira uses Gemini 2.5 Pro to analyze the data and generate a summary of current trends.
5. Mira sends the market trend summary to the user.

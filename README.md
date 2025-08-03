![Mira Banner](mira-banner-03.png)

# Mira - Your Personal AI Agent for NFT Alerts & Summaries

Mira is a Telegram-based AI agent designed to provide real-time NFT alerts and comprehensive project summaries through natural language interaction. Powered by Google's Gemini 2.5 models and data from the UnleashNFTs API, Mira offers an intuitive, AI-first experience for NFT traders, collectors, and enthusiasts.

## Features
- **Natural Language Interaction**: Communicate with Mira using plain English.
- **Dynamic NFT Price Alerts**: Set up alerts for any NFT collection, and Mira will dynamically find it and track its floor price. Get notified when the price goes above or below your specified threshold. (Note: Collection search is dependent on the naming conventions of the UnleashNFTs API and may not find all collections.)
- **New Listing Alerts**: Get notified when new NFTs from a specific collection are listed on major marketplaces.
- **In-Depth Summaries**: Get concise, AI-generated summaries of NFT projects.
- **Wallet Activity Monitoring**: Track on-chain activity for any wallet address to monitor NFT transactions.
- **Market Trend Analysis**: Receive on-demand analysis of the NFT market to stay ahead of the curve.

## Getting Started

### Prerequisites
- Python 3.10+
- A Telegram Bot Token
- An UnleashNFTs (BitCrunch) API Key
- A Google Gemini API Key

### Local Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ugbodagadave/mira.git
    cd mira
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the project root and add the following variables. **Do not run the bot locally using a webhook.** For local development, you should use polling.

    ```env
    TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    BITCRUNCH_API_KEY="your_unleashnfts_api_key"
    GEMINI_API_KEY="your_gemini_api_key"
    DATABASE_URL="sqlite+aiosqlite:///mira_local.db" # For local testing
    SCHEDULER_SECRET="a_very_strong_random_secret"
    WEBHOOK_URL="https://example.com" # Placeholder for local run
    ```

## Deployment on Render

This project is configured for easy deployment on Render using the provided `render.yaml` file.

1.  **Fork the Repository:** Fork this repository to your own GitHub account.
2.  **Create a New Blueprint Service on Render:**
    - Go to your Render Dashboard.
    - Click "New" -> "Blueprint".
    - Connect the repository you just forked.
    - Render will automatically detect and configure the services based on `render.yaml`.
3.  **Set Environment Variables:** Before the first deployment, you **must** add the following secrets in the Render dashboard under the "Environment" section for the `mira-bot` service:
    - `TELEGRAM_BOT_TOKEN`
    - `BITCRUNCH_API_KEY`
    - `GEMINI_API_KEY`
    - `SCHEDULER_SECRET` (a strong, random string you create)
    - `WEBHOOK_URL` (the public URL Render assigns to your service, e.g., `https://mira-bot.onrender.com`)

## Scheduler Setup (Free Tier Workaround)

Because Render's free tier does not support native cron jobs, a webhook is used to trigger the alert checker. You must use an external cron job service (like [Cron-Job.org](https://cron-job.org/)) to call this webhook periodically.

1.  **Construct your Webhook URL:** The full URL for the cron job to call is: `https://<your-render-app-url>:8080/scheduler/<your-scheduler-secret>`
2.  **Configure the External Cron Job:**
    *   Go to a service like [Cron-Job.org](https://cron-job.org/).
    *   Create a new cron job.
    *   **URL:** Paste the full webhook URL you constructed.
    *   **Schedule:** Every 15 minutes is recommended.
    *   **HTTP Method:** GET
    *   Save the cron job. The scheduler is now active.

## Technology Stack
- **Backend**: Python (`python-telegram-bot`)
- **AI**: Google Gemini 2.5 Pro & Flash
- **Data**: UnleashNFTs API
- **Database**: PostgreSQL (on Render), SQLite (local)
- **Hosting**: Render (Native Python Runtime)

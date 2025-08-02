![Mira Banner](mira-banner-03.png)

# Mira - Your Personal AI Agent for NFT Alerts & Summaries

Mira is a Telegram-based AI agent designed to provide real-time NFT alerts and comprehensive project summaries through natural language interaction. Powered by Google's Gemini 2.5 models and data from the BitCrunch API, Mira offers an intuitive, AI-first experience for NFT traders, collectors, and enthusiasts.

## Features
- **Natural Language Interaction**: Communicate with Mira using plain English.
- **Custom NFT Alerts**: Set up alerts for price changes and new listings.
- **In-Depth Summaries**: Get concise, AI-generated summaries of any NFT project.
- **Wallet Monitoring**: Track on-chain activity for any wallet address.
- **Market Trends**: Receive on-demand analysis of the NFT market.

## Getting Started
*(Instructions to be added)*

## Scheduler Setup (Free Tier Workaround)
Because Render's free tier does not support cron jobs, a workaround is required to trigger the alert checker. An external cron job service (like [Cron-Job.org](https://cron-job.org/)) must be used to call a secure webhook.

1.  **Set the `SCHEDULER_SECRET` Environment Variable:** Add a secure, random string as `SCHEDULER_SECRET` in your Render environment variables.
2.  **Configure the External Cron Job:**
    *   **URL:** `https://<your-render-app-url>/scheduler?secret=<your-scheduler-secret>`
    *   **Schedule:** Every 5 minutes.

## Technology Stack
- **Backend**: Python
- **AI**: Google Gemini 2.5 Pro & Flash
- **Data**: BitCrunch API
- **Database**: PostgreSQL
- **Hosting**: Render

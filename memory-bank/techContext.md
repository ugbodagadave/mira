# Technical Context: Mira AI Agent

## 1. Technology Stack

- **Programming Language**: Python 3.10+
- **Telegram Bot Framework**: `python-telegram-bot` (v20.x, async-first)
- **HTTP Client**: `httpx` for asynchronous API requests.
- **AI Models**:
    - **NLU & Summarization**: Google Gemini 2.5 Pro (`gemini-2.5-pro`)
    - **Alert Processing**: Google Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Data Source**: UnleashNFTs API (v1) - formerly BitCrunch
    - **Base URL**: `https://api.unleashnfts.com/api/v1/`
    - **Image Detection URL**: `https://api-cdv.unleashnfts.com/api/v1/`
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with `asyncpg` driver.
- **Hosting**: Render (Free Plan) using a native Python runtime.

## 2. Environment Variables
The application requires the following environment variables to be set in the hosting environment (e.g., Render secrets):
- `TELEGRAM_BOT_TOKEN`: The token for the Telegram bot.
- `BITCRUNCH_API_KEY`: The API key for the BitCrunch service.
- `GEMINI_API_KEY`: The API key for Google AI Studio / Vertex AI.
- `DATABASE_URL`: The connection string for the PostgreSQL database.
- `SCHEDULER_SECRET`: A secret key to authenticate calls to the scheduler webhook.
- `WEBHOOK_URL`: The public URL of the Render web service (e.g., `https://your-app.onrender.com`).

## 3. Technical Constraints
- **Render Free Plan Limits**: The application must be optimized for low resource consumption (CPU, RAM). The free tier does not support native cron jobs, requiring a webhook-based approach for scheduled tasks.
- **Stateless Design**: To work reliably on Render, the application should be as stateless as possible. Persistent data must be stored in the PostgreSQL database.
- **API Rate Limits**: All API interactions (BitCrunch, Gemini, Telegram) must be designed to handle potential rate limits gracefully.

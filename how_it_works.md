# How Mira Works: A Technical Overview

This document provides a detailed technical explanation of the Mira AI agent's architecture and components.

## 1. Core Architecture

Mira is built on a modular, asynchronous architecture designed for scalability and maintainability. The primary components are:

-   **Telegram Bot Interface (`src/bot.py` & `src/main.py`):** This is the main entry point for the application. `bot.py` defines the handlers and creates the application object, while `main.py` runs the application's built-in web server. It uses the `python-telegram-bot` library to handle incoming messages and webhooks from Telegram.
-   **Natural Language Understanding (NLU) (`src/nlu/processor.py`):** All user messages are processed by the NLU module, which uses Google's Gemini 2.5 Pro model to classify the user's intent and extract relevant entities (e.g., collection names, prices, wallet addresses).
-   **Service Layer (`src/services/`):** All external API integrations are abstracted into a service layer. This includes services for the UnleashNFTs API (for searching collections, getting metrics, etc.) and Google's Gemini AI (for generating summaries).
-   **Database (`src/database/`):** User data, price alerts, new listing alerts, and tracked wallets are stored in a PostgreSQL database, managed by SQLAlchemy's asynchronous ORM.
-   **Scheduler (`src/scheduler.py`):** The logic for checking price alerts is contained in this module. It is not run as a separate process but is triggered via a secure webhook.

## 2. User Interaction Flow

1.  A user sends a message to Mira on Telegram.
2.  The `handle_message` function in `bot.py` receives the message.
3.  The message is passed to the `classify_intent_and_extract_entities` function in the NLU processor.
4.  The NLU processor sends a prompt to the Gemini 2.5 Pro model, which returns a JSON object containing the intent and entities.
5.  The `handle_message` function uses the intent to route the request to the appropriate logic block (e.g., `if intent == 'get_project_summary'`).
6.  **Dynamic Collection Search:** For a project summary, the bot first calls the `unleash_nfts_service.search_collection` function to find the best match for the user's query.
7.  The handler then calls the necessary services (e.g., `unleash_nfts_service.get_collection_metrics` and `gemini_service.generate_summary`).
8.  The final response is sent back to the user via the Telegram API.

## 3. Key Technologies

-   **Asynchronous Processing:** The entire application is built using Python's `asyncio` framework. This allows for efficient handling of concurrent requests and I/O-bound operations (like API calls and database queries).
-   **Test-Driven Development:** The project follows a strict TDD workflow. Every feature is accompanied by unit and integration tests, using `pytest` and `respx` to mock external services.

## 4. Deployment

The application is designed for deployment on Render using a `render.yaml` Blueprint. This defines the web service and the database.

-   **Runtime**: The application runs in Render's native Python environment, not a Docker container.
-   **Server**: It uses the `python-telegram-bot` library's own built-in webhook server, which proved more reliable than a Gunicorn/Uvicorn setup for this specific library.
-   **Scheduler**: Due to Render's free-tier limitations, scheduled tasks are handled by an external cron service (e.g., Cron-Job.org) that calls a secure webhook on the running web service. This triggers the scheduler logic.

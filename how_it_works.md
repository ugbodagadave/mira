# How Mira Works: A Technical Overview

This document provides a detailed technical explanation of the Mira AI agent's architecture and components.

## 1. Core Architecture

Mira is built on a modular, asynchronous architecture designed for scalability and maintainability. The primary components are:

-   **Telegram Bot Interface (`src/bot.py`):** This is the main entry point for the application. It uses the `python-telegram-bot` library to handle incoming messages from Telegram. It is responsible for routing user requests to the appropriate handlers.
-   **Natural Language Understanding (NLU) (`src/nlu/processor.py`):** All user messages are processed by the NLU module, which uses Google's Gemini 2.5 Pro model to classify the user's intent and extract relevant entities (e.g., collection names, prices).
-   **Service Layer (`src/services/`):** All external API integrations are abstracted into a service layer. This includes services for the UnleashNFTs API and Google's Gemini AI.
-   **Database (`src/database/`):** User data and alerts are stored in a PostgreSQL database, managed by SQLAlchemy's asynchronous ORM.
-   **Scheduler (`src/scheduler.py`):** A scheduler is responsible for periodically checking for triggered alerts.

## 2. User Interaction Flow

1.  A user sends a message to Mira on Telegram.
2.  The `handle_message` function in `bot.py` receives the message.
3.  The message is passed to the `classify_intent_and_extract_entities` function in the NLU processor.
4.  The NLU processor sends a prompt to the Gemini 2.5 Pro model, which returns a JSON object containing the intent and entities.
5.  The `handle_message` function uses the intent to route the request to the appropriate logic block (e.g., `if intent == 'get_project_summary'`).
6.  The handler calls the necessary services (e.g., `unleash_nfts_service.get_collection_metrics` and `gemini_service.generate_summary`).
7.  The final response is sent back to the user via the Telegram API.

## 3. Key Technologies

-   **Asynchronous Processing:** The entire application is built using Python's `asyncio` framework. This allows for efficient handling of concurrent requests and I/O-bound operations (like API calls and database queries).
-   **Containerization:** The application is containerized using Docker, which ensures a consistent environment for development and production. Two Dockerfiles are used: one for the main web application and one for the scheduler.
-   **Test-Driven Development:** The project follows a strict TDD workflow. Every feature is accompanied by unit and integration tests, using `pytest` and `respx` to mock external services.

## 4. Deployment

The application is designed for deployment on Render using a `render.yaml` Blueprint. This defines the web service, database, and the scheduler workaround (using an external cron job to call a webhook).

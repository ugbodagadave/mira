# System Patterns: Mira AI Agent

## 1. Core Architecture
Mira uses a modular, event-driven architecture designed for scalability and maintainability on a serverless-like platform (Render).

```mermaid
graph TD
    A[Telegram User] -->|Natural Language| B(Telegram Bot API)
    B --> C{Bot Application (bot.py)}
    C -->|User Input| D[NLU Processor (nlu/processor.py)]
    D -->|Intent & Entities| C
    C -->|Routes to Handler| E[Feature Handlers]
    E -->|Request Data| F[UnleashNFTs Service (services/unleashnfts_api.py)]
    F --> G(UnleashNFTs API)
    E -->|Request AI Task| H[Gemini Service (services/gemini_ai.py)]
    H --> I(Google Gemini API)
    E -->|CRUD Operations| J[Database Manager (database/manager.py)]
    J --> K[(PostgreSQL on Render)]
    C -->|Send Response| B

    L[Scheduler (scheduler.py)] -->|Triggers Job| M{Cron Job Runner}
    M --> J
    M --> F
    M --> H
    M -->|Sends Alert| B
```

## 2. Design Patterns

### 2.1. Service Layer
External integrations (UnleashNFTs, Gemini) are abstracted into their own service modules. This decouples the core business logic from the specific implementation details of the APIs, making it easier to manage, test, and potentially swap out services in the future.

### 2.2. Natural Language Understanding (NLU) Pipeline
1.  **Input**: Raw text from the user.
2.  **Processing**: The text is sent to the `NLU Processor`, which uses a prompt-engineered request to Gemini 2.5 Pro.
3.  **Output**: A structured object containing the classified `intent` (e.g., `get_project_summary`) and a dictionary of extracted `entities` (e.g., `{ "collection_name": "Bored Ape Yacht Club" }`).
4.  **Routing**: The main bot logic uses the `intent` to route the request to the appropriate handler function.

### 2.3. Database Schema
A simplified schema to start:

-   **users**
    -   `id` (PK)
    -   `telegram_user_id` (Unique)
    -   `first_name`
    -   `created_at`

-   **price_alerts**
    -   `id` (PK)
    -   `user_id` (FK to users.id)
    -   `collection_name`
    -   `collection_address`
    -   `chain`
    -   `threshold_price`
    -   `direction` ('above' or 'below')
    -   `is_active`
    -   `created_at`

*(Other tables for different alert types will be added as features are implemented.)*

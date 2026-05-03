# Architecture

CryptoPulse AI is organized as a small distributed system. Each service has a narrow responsibility so the project can be run locally while still resembling a production data application.

## Services

### Frontend

The frontend is a React and TypeScript dashboard built with Vite and Tailwind CSS. It shows the current market overview, coin details, chart history, auth forms, alert management, triggered alert history, and the agent question panel.

### API

The API is a FastAPI service. It owns the main product surface:

- market overview and history
- server-sent market stream
- auth and current-user routes
- alert creation and evaluation
- triggered alert history
- analytics summaries, anomalies, and recommendations
- readiness and metrics endpoints

The API uses SQLAlchemy for database access and Pydantic schemas for request/response validation.

### Agent

The agent is a separate FastAPI service. It calls backend analytics tools instead of querying the database directly. If `GROQ_API_KEY` is configured, the service uses Groq to plan tool usage and compose the final answer. If Groq is not configured, it falls back to deterministic responses.

### Ingestion

The ingestion service contains scripts for Binance WebSocket streaming, CoinGecko backfill/reference data, and a continuous local refresh worker. It writes market snapshots and can publish normalized events to Kafka.

### Streaming

The streaming service consumes market events and writes derived indicators or insight rows back to PostgreSQL. Spark job scaffolding is included for a heavier streaming path, while the local Docker setup keeps a lighter processor available for development.

## Data Flow

```text
External market data
        |
        v
Ingestion service
        |
        +--> PostgreSQL market_snapshots
        |
        +--> Kafka market topics
                 |
                 v
          Streaming processor
                 |
                 v
          technical_indicators / ai_insights
                 |
                 v
FastAPI backend
        |
        +--> React dashboard
        |
        +--> Agent service
```

## Database Tables

The main tables are:

- `users`
- `watched_assets`
- `market_snapshots`
- `technical_indicators`
- `user_alerts`
- `triggered_alerts`
- `ai_insights`

Bootstrap SQL is used for local Docker initialization. Alembic migrations are used for later schema changes.

## Agent Flow

```text
User question
        |
        v
Tool planning
        |
        v
Required tool guardrails
        |
        v
Backend tool calls
        |
        v
Grounded answer with sources
```

The guardrail step makes common prompts more reliable. For example, comparison questions always include `market.overview`, and risk/volatility questions include anomaly and recommendation data.

## Local Deployment

The local deployment uses Docker Compose:

- `postgres`
- `redis`
- `zookeeper`
- `kafka`
- `api`
- `agent`
- `frontend`
- `ingestion`
- `streaming`

The app is designed to be started with:

```bash
make up
```

## Production Gaps

The project is ready for local review and demonstration, but it would need more work before a real production deployment:

- managed secrets
- CI/CD
- scheduled alert evaluation
- production migration workflow
- stronger auth flows
- persistent logs and metrics
- cloud deployment configuration

# CryptoPulse AI

CryptoPulse AI is a crypto market monitoring product I am building as a side project. The idea is simple: bring live market data, technical signals, alerting, and AI-assisted market explanations into one dashboard that can grow from a local prototype into a deployable product.

The current version runs locally with Docker Compose. It includes a React dashboard, FastAPI backend, PostgreSQL storage, Kafka-based ingestion/processing services, and a separate agent service that can use Groq for grounded market Q&A.

## Product Direction

Crypto tools often split data, alerts, and explanations across different apps. CryptoPulse AI is meant to combine those workflows:

- watch tracked coins in one dashboard
- inspect price movement and technical indicators
- create alerts for price and volatility conditions
- review triggered alert history
- ask natural-language questions about the current market
- keep the agent grounded in backend data instead of generic market commentary

This is not financial advice software. It is a monitoring and explanation layer for crypto market data.

## Current Features

- Market overview cards with price, 24-hour movement, volume, RSI, volatility, and trend context
- Coin detail panel with stored price history and technical indicators
- JWT-based local accounts
- Alert creation for price and volatility rules
- Manual alert evaluation and triggered alert history
- Analytics endpoints for summaries, anomalies, and recommendations
- Groq-backed agent path with deterministic fallback when no key is configured
- Docker Compose stack for API, frontend, agent, Postgres, Redis, Kafka, ingestion, and streaming services

## Phase Roadmap

### Phase 1: Scaffold

The first phase focused on getting the project structure in place.

- Created the monorepo layout
- Added FastAPI, React, and agent service folders
- Added Docker Compose and Makefile commands
- Added initial SQL bootstrap files
- Added baseline health checks and tests

### Phase 2: Backend and Data Core

This phase built the API and database foundation.

- Added SQLAlchemy models and repositories
- Added JWT auth routes
- Added market overview and history endpoints
- Added user-specific alert storage
- Added analytics routes for summaries and anomaly data
- Added Alembic migration support

### Phase 3: Dashboard

This phase turned the project into a usable frontend app.

- Built the React dashboard shell
- Added market overview cards
- Added coin detail charts and indicator cards
- Connected auth and alert workflows to the backend
- Added the agent panel through the frontend proxy

### Phase 4: Analytics and Agent

This phase added the first version of market intelligence.

- Added anomaly scoring using volatility, momentum, and RSI
- Added recommendation endpoints for what to inspect next
- Added an agent service that calls backend analytics tools
- Supported questions about trends, anomalies, summaries, recommendations, and comparisons

### Phase 5: Local Reliability

This phase improved the app as a local product.

- Added readiness endpoints
- Added request metrics
- Added API and agent health checks
- Expanded backend tests
- Improved Docker health checks and developer commands

### Phase 6: Ingestion and Processing

This phase moved the data pipeline closer to a real streaming setup.

- Added Binance WebSocket ingestion support
- Added CoinGecko backfill/reference data support
- Added a continuous local ingestion worker
- Added Kafka-backed processing for derived indicators and insight rows
- Kept Spark scaffolding available for a heavier streaming path

### Phase 7: Alert Intelligence

This phase made alerts more useful after creation.

- Added triggered alert storage
- Added alert evaluation against latest stored market data
- Deactivated alerts after they trigger
- Added active and triggered alert sections in the dashboard
- Added the dashboard "Check alerts now" flow

### Phase 8: Groq-backed Agent

This phase made the agent more flexible.

- Added Groq chat completions support through environment config
- Added LLM-based tool planning over backend analytics tools
- Added deterministic tool requirements so important data is not missed
- Kept fallback responses for local demos without a Groq key
- Returned explicit backend sources with agent answers

## Architecture

```text
Market APIs / backfill
        |
        v
Ingestion service
        |
        +--> PostgreSQL market snapshots
        +--> Kafka market topics
                 |
                 v
          Streaming processor
                 |
                 v
          Indicators and insight rows
                 |
                 v
FastAPI backend <--> Agent service
        |
        v
React dashboard
```

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database/cache:** PostgreSQL, Redis
- **Streaming/data:** Kafka, Spark scaffolding, Python ingestion workers
- **Agent:** FastAPI service with optional Groq integration
- **Local orchestration:** Docker Compose and Makefile commands

## Repository Layout

```text
apps/
  agent/        Market Q&A service
  api/          FastAPI backend
  frontend/     React dashboard
services/
  ingestion/    Market ingestion and backfill workers
  ml/           Anomaly/forecasting modules
  streaming/    Kafka/Spark-oriented processing services
packages/
  shared/       Shared contracts and conventions
infra/
  sql/          Local database bootstrap SQL
docs/           Architecture and build notes
tests/          Cross-service test notes
```

## Running Locally

Copy the environment file:

```bash
cp .env.example .env
```

Start the stack:

```bash
make up
```

Open the app:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- API readiness: `http://localhost:8000/api/v1/system/ready`
- Agent readiness: `http://localhost:8080/health/ready`

Useful commands:

```bash
make down              # stop containers
make logs              # follow Docker Compose logs
make test              # run backend tests inside apps/api
make frontend-build    # build the frontend
make migrate           # run Alembic migrations in the API container
make ingest-once       # run one ingestion refresh in Docker
make stream-processor  # run the Kafka-backed processor locally
```

## Groq Setup

The agent works without Groq by using deterministic backend-tool responses. To enable the Groq-backed path, add these values to `.env`:

```bash
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

After changing `.env`, restart the agent:

```bash
docker compose up -d --build agent
```

## API Surface

- `GET /api/v1/market/overview`
- `GET /api/v1/market/history`
- `GET /api/v1/market/stream`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts`
- `POST /api/v1/alerts/evaluate`
- `GET /api/v1/alerts/triggered`
- `GET /api/v1/analytics/anomalies`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/recommendations`
- `GET /api/v1/system/ready`
- `GET /api/v1/system/metrics`

## Agent Behavior

The agent calls backend tools before answering. Current tools include:

- `market.overview`
- `analytics.anomalies`
- `analytics.summary`
- `analytics.recommendations`

Groq can choose tools, but the code still adds required tools for common question types. For example, comparison questions always include market overview data, and risk or volatility questions include anomaly and recommendation data.

## Alert Flow

Alerts can be created for price and volatility conditions. The current evaluator is manual:

```text
Create alert -> Check alerts now -> Store trigger -> Deactivate original alert
```

The next product step is to move this behind a scheduled worker and add notifications.

## Current Limits

- The app is built for local development and product exploration.
- Alert evaluation is manual right now.
- Kafka and Spark pieces are included, but the default local path still uses lightweight Python services where that is faster to run.
- Auth is basic and does not include password reset or email verification yet.
- Cloud deployment, CI/CD, and long-term observability still need to be added.

## Next Product Steps

- Scheduled alert evaluation
- Email, Discord, or webhook notifications for triggered alerts
- Agent recommendations for what alert to create
- Historical comparison tools for the agent
- CI for backend tests and frontend builds
- Render, Railway, or AWS deployment configuration

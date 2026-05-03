# CryptoPulse AI

CryptoPulse AI is a full-stack cryptocurrency monitoring project. It combines a React dashboard, a FastAPI backend, PostgreSQL storage, Kafka-based ingestion/processing services, and a small market-analysis agent backed by Groq when an API key is configured.

The goal of the project is to show how live market data can move through an application from ingestion, to analytics, to a user-facing dashboard. The app supports market overview cards, historical price charts, account-based alerts, triggered alert history, anomaly summaries, and natural-language market questions grounded in backend data.

## Main Features

- Live market dashboard with tracked assets, 24-hour movement, volume, RSI, volatility, and trend summaries
- Coin detail view with stored market history and technical indicators
- JWT authentication for local user accounts
- Alert creation for price and volatility rules
- Manual alert evaluation with triggered alert history
- Analytics endpoints for summaries, anomalies, and metric recommendations
- Agent service that selects backend tools and writes grounded market answers
- Docker Compose setup for local development across API, frontend, agent, Postgres, Redis, Kafka, ingestion, and streaming services

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
- **Agent:** FastAPI service using Groq's OpenAI-compatible chat completions API when `GROQ_API_KEY` is set
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

## Optional Groq Setup

The agent still works without Groq by falling back to deterministic tool responses. To enable the Groq-backed path, add these values to `.env`:

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

The agent service does not answer from memory alone. It chooses from backend tools such as:

- `market.overview`
- `analytics.anomalies`
- `analytics.summary`
- `analytics.recommendations`

The code also adds deterministic tool requirements for common question types. For example, comparison and risk questions always include market overview and anomaly data, even if the model planner selects a narrower set of tools.

## Implementation Notes

### Data flow

The local stack can run a continuous ingestion worker that refreshes market snapshots. Kafka is used as the processing boundary between ingestion and derived analytics, while PostgreSQL stores the rows served by the API.

### Alerts

Users can create price and volatility alerts. The current alert evaluator is manual through `POST /api/v1/alerts/evaluate` and the dashboard's "Check alerts now" button. When a rule triggers, the app stores a triggered-alert record and deactivates the original alert.

### Database lifecycle

The project includes both bootstrap SQL for a fresh local Docker volume and Alembic migrations for schema changes. In a production deployment, Alembic should be the single source for schema changes.

## Testing

Backend tests live under `apps/api/tests`.

```bash
make test
make frontend-build
```

During local development, I also used:

```bash
python3 -m py_compile apps/agent/src/logic.py
docker compose up -d --build
curl -s http://localhost:8000/api/v1/system/ready
curl -s http://localhost:8080/health/ready
```

## Current Limitations

- The public dashboard is intended for local/demo use, not financial decision-making.
- The alert evaluator is manual; a scheduled worker would be the next step.
- Kafka/Spark pieces are present, but the default local flow still relies on lightweight Python services for practical development.
- Secrets, CI/CD, cloud deployment manifests, and persistent observability are not included yet.
- Auth is intentionally minimal and does not include password reset or email verification.

## Future Work

- Add scheduled alert evaluation
- Add CI for backend tests and frontend builds
- Add deployment files for Render, Railway, or AWS
- Add notification delivery for triggered alerts
- Expand the agent with more tools, including alert recommendations and historical comparisons

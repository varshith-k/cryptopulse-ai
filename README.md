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

## Course Concepts Demonstrated

This project demonstrates the following key concepts from the AI Agents Intensive course
(the required minimum is three):

| Key concept | Where it lives | What it does |
| --- | --- | --- |
| **Agent system** | [apps/agent/src/logic.py](apps/agent/src/logic.py), [apps/agent/src/groq_client.py](apps/agent/src/groq_client.py) | An LLM-driven agent that plans which backend tools to call, enforces required tools per question type, then composes a grounded answer that cites its sources. |
| **MCP Server** | [apps/agent/src/mcp_server.py](apps/agent/src/mcp_server.py), [apps/agent/src/tools.py](apps/agent/src/tools.py) | A Model Context Protocol server that exposes the four grounded analytics tools to any MCP client (Claude Desktop, MCP Inspector, other agents) — from the same shared registry the agent itself uses. |
| **Security features** | [apps/api](apps/api) (JWT auth), `.env` / [.env.example](.env.example) | JWT-based accounts, per-user alert isolation, and secrets kept out of code (only `.env.example` is committed). |
| **Deployability** | [docker-compose.yml](docker-compose.yml), [Makefile](Makefile) | One-command Docker Compose stack for all ten services, with health/readiness endpoints for each. |
| **Agent skills / Agents CLI** | [apps/agent/src/cli.py](apps/agent/src/cli.py) | A terminal CLI that queries the grounded agent and prints the answer plus its tool sources. |

The single most important design choice is that the agent's toolset and the MCP
server are built from **one shared registry** ([apps/agent/src/tools.py](apps/agent/src/tools.py)),
so our own agent and any external MCP client always call the exact same grounded
tools — they can never drift apart.

## Current Features

- Market overview cards with price, 24-hour movement, volume, RSI, volatility, and trend context
- Coin detail panel with stored price history and technical indicators
- JWT-based local accounts
- Alert creation for price and volatility rules
- Manual alert evaluation and triggered alert history
- Outbound alert notifications via webhook (Discord/Slack) or email when an alert triggers
- Analytics endpoints for summaries, anomalies, and recommendations
- Real-time volatility detector: a dedicated Kafka consumer running a sliding-window z-score over the live tick stream
- Groq-backed agent path with deterministic fallback when no key is configured
- Docker Compose stack for API, frontend, agent, Postgres, Redis, Kafka, ingestion, streaming, and real-time detector services

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

### Phase 9: Real-time Anomaly Detection

This phase added true stream-time anomaly detection alongside the batch path.

- Added a dedicated `realtime` Kafka consumer service in its own consumer group
- Implemented a per-symbol sliding-window z-score detector with bounded memory
- Flagged ticks that deviate beyond a configurable threshold from the rolling mean
- Persisted flagged spikes and exposed them through a new analytics endpoint
- Added a live "volatility spikes" panel to the dashboard
- Added unit tests for the detector algorithm

### Phase 10: Alert Notifications

This phase made triggered alerts reach the user outside the dashboard.

- Added best-effort outbound notifications when an alert triggers
- Supported a generic webhook channel (Discord/Slack compatible)
- Supported an email channel over SMTP
- Kept all channels optional so local demos run unchanged with none configured
- Isolated delivery failures so they never break alert evaluation

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
                 +--> Streaming processor (consumer group A)
                 |         |
                 |         v
                 |    Indicators and insight rows
                 |
                 +--> Real-time detector (consumer group B)
                           |
                           v
                      Sliding-window volatility spikes
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
  realtime/     Sliding-window real-time volatility detector (Kafka consumer)
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
- `GET /api/v1/analytics/realtime-anomalies`
- `GET /api/v1/system/ready`
- `GET /api/v1/system/metrics`

## Agent Behavior

The agent calls backend tools before answering. Current tools include:

- `market.overview`
- `analytics.anomalies`
- `analytics.summary`
- `analytics.recommendations`

Groq can choose tools, but the code still adds required tools for common question types. For example, comparison questions always include market overview data, and risk or volatility questions include anomaly and recommendation data.

## MCP Server

The same four grounded tools are also exposed over the **Model Context Protocol**
so any MCP-compatible client can call them. The server
([apps/agent/src/mcp_server.py](apps/agent/src/mcp_server.py)) is built from the
shared tool registry ([apps/agent/src/tools.py](apps/agent/src/tools.py)), so the
MCP surface and the agent's own toolset are always identical.

Run it locally over stdio (the transport MCP clients launch):

```bash
cd apps/agent
pip install -r requirements.txt
python -m src.mcp_server
```

Point an MCP client (Claude Desktop, the MCP Inspector, or another agent) at it:

```json
{
  "mcpServers": {
    "cryptopulse": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "apps/agent",
      "env": { "BACKEND_BASE_URL": "http://localhost:8000" }
    }
  }
}
```

Exposed tools: `market_overview`, `analytics_anomalies`, `analytics_recommendations`,
and `analytics_summary(scope)`. Each tool's docstring and type hints become its
public MCP schema, so the client knows what it can call and why.

## Agent CLI

A thin terminal client ([apps/agent/src/cli.py](apps/agent/src/cli.py)) queries the
running agent and prints the grounded answer plus the tool sources behind it. The
agent must be running first (`make up` or `docker compose up -d --build`).

Run it inside the agent container (no host dependencies needed):

```bash
docker compose exec agent python -m src.cli "which coins are trending upward today?"
```

Or run it on the host (requires `python3` and `pip install httpx`):

```bash
cd apps/agent
python3 -m src.cli "which coins are trending upward today?"
```

It calls the agent's HTTP endpoint (the same one the dashboard uses), so it
exercises the full plan-tools → call-tools → compose-answer path.

## Security

- **JWT accounts** — local registration/login issue signed tokens; protected
  routes require a valid token.
- **Per-user isolation** — alerts and triggered-alert history are scoped to the
  authenticated user.
- **No secrets in code** — all credentials (Groq key, SMTP password, webhook URL,
  JWT secret) come from `.env`, which is git-ignored. Only [.env.example](.env.example)
  with placeholder values is committed.
- **Isolated failures** — notification delivery is best-effort and sandboxed so a
  failing channel can never break alert evaluation.

## Alert Flow

Alerts can be created for price and volatility conditions. The current evaluator is manual:

```text
Create alert -> Check alerts now -> Store trigger -> Notify -> Deactivate original alert
```

When an alert triggers, the API sends best-effort notifications to any configured
channel (see [Alert Notifications](#alert-notifications)). The next product step is to
move evaluation behind a scheduled worker so it runs automatically.

## Alert Notifications

When an alert triggers during evaluation, the API dispatches a notification to every
configured channel. Delivery is best-effort: an unconfigured channel is skipped, and a
channel that fails is logged but never breaks alert evaluation.

Two channels are supported, both configured from `.env`:

```bash
# Generic webhook (also works with Discord and Slack incoming webhooks)
ALERT_WEBHOOK_URL=https://discord.com/api/webhooks/xxxx/yyyy

# Email over SMTP (e.g. a Gmail app password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=you@example.com
ALERT_EMAIL_TO=you@example.com
```

The webhook payload includes a Discord/Slack-compatible `content` string plus a
structured `alert` object for custom consumers. With no channels configured, the app
runs exactly as before and simply records triggers without sending anything.

## Real-time Volatility Detection

The `realtime` service is a separate Kafka consumer that reads the same market tick
topic as the streaming processor but in its own consumer group, so the two run
independently. For each symbol it keeps a bounded `deque` of the most recent ticks
and scores every new tick against that window:

```text
z_score = (price - rolling_mean) / rolling_std
```

When `|z_score|` crosses the configured threshold (default 3.0) the tick is flagged as a
spike, written to the `realtime_anomalies` table, and surfaced on the dashboard. Memory
stays flat at O(symbols x window_size) because old ticks fall off the deque automatically.

Detector behavior is tunable from `.env`:

```bash
REALTIME_WINDOW_SIZE=60     # ticks kept per symbol
REALTIME_Z_THRESHOLD=3.0    # standard deviations required to flag a spike
REALTIME_MIN_SAMPLES=10     # ticks needed before scoring begins
```

This complements the batch anomaly scoring in the analytics endpoints: the batch path
reasons over daily indicators, while this path reacts to the live stream in real time.

## Current Limits

- The app is built for local development and product exploration.
- Alert evaluation is still triggered manually (notifications fire automatically once it runs).
- Kafka and Spark pieces are included, but the default local path still uses lightweight Python services where that is faster to run.
- Auth is basic and does not include password reset or email verification yet.
- Cloud deployment, CI/CD, and long-term observability still need to be added.

## Next Product Steps

- Scheduled alert evaluation (so notifications fire without the manual check)
- Agent recommendations for what alert to create
- Historical comparison tools for the agent
- CI for backend tests and frontend builds
- Render, Railway, or AWS deployment configuration

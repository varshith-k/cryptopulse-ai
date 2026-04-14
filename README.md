# CryptoPulse AI

CryptoPulse AI is a portfolio-grade platform for live cryptocurrency analytics, streaming data engineering, and grounded AI market intelligence. This repository evolves the original `CryptoTrendAnalytics` concept into a production-style system with a modern frontend, FastAPI backend, Kafka and Spark pipeline, PostgreSQL serving layer, and an agentic AI service for market explanations and anomaly-aware insights.

## Why this architecture

- **Frontend**: React, TypeScript, Vite, and Tailwind CSS provide a fast feedback loop and reusable UI primitives for dashboards, charts, alerts, and AI-assisted workflows.
- **Backend**: FastAPI is the best fit here because the platform combines typed APIs, async I/O, data science integration, and AI orchestration in Python. It also gives us automatic OpenAPI docs for a clean developer experience.
- **Streaming pipeline**: Kafka handles event ingestion, while Spark Structured Streaming is a realistic choice for sliding windows, feature engineering, and technical indicator computation.
- **Storage**: PostgreSQL stores curated market snapshots, indicators, alerts, and AI-generated artifacts for low-latency reads. Redis is reserved for cache and fan-out use cases.
- **AI layer**: A dedicated agent service lets us build grounded question-answering, daily summaries, anomaly explanations, and next-step recommendations over live project data.

## Phase roadmap

### Phase 1
- Initialize the monorepo structure
- Add service scaffolds and local orchestration
- Establish shared config, environment patterns, and docs

### Phase 2
- Implement FastAPI modules, auth, SQLAlchemy models, and REST plus SSE support
- Add Kafka ingestion and Spark processing skeletons
- Create batch backfill utilities and database seeds

### Phase 3
- Build the frontend landing page, market dashboard, and reusable component system
- Wire the UI to live and historical backend data

### Phase 4
- Add a grounded AI agent with tool-based reasoning
- Implement anomaly detection and lightweight forecasting

### Phase 5
- Expand tests, observability hooks, Docker hardening, and documentation
- Prepare final portfolio polish and deployment notes

## Current repository layout

```text
apps/
  agent/        Grounded AI service
  api/          FastAPI backend
  frontend/     React + TypeScript dashboard
services/
  ingestion/    Kafka producer and historical backfill
  ml/           Forecasting and anomaly modules
  streaming/    Spark Structured Streaming jobs
packages/
  shared/       Shared schemas and cross-service conventions
infra/
  sql/          Database bootstrap and seed data
tests/          Cross-service tests and integration fixtures
docs/           Architecture and build documentation
```

## Quick start

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Start the local stack:

   ```bash
   make up
   ```

3. Open the services:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Agent health: `http://localhost:8080/health`
- API readiness: `http://localhost:8000/api/v1/system/ready`
- Agent readiness: `http://localhost:8080/health/ready`

## What is implemented in Phase 1

- Production-style monorepo layout
- Minimal FastAPI service with typed configuration and seed overview data
- Minimal agent service with grounded summary scaffolding
- Frontend shell with landing page and architecture preview
- Docker Compose stack for PostgreSQL, Redis, Kafka, API, agent, and frontend
- Database bootstrap schema
- Developer scripts and initial tests

## Phase 2 progress

- PostgreSQL-backed FastAPI models and session management
- JWT authentication routes for register, login, and current user
- User-specific alerts API
- Database-seeded market overview endpoint with technical indicator context
- SSE endpoint for lightweight live market updates
- Historical backfill utility at `services/ingestion/src/backfill.py`

## Phase 3 progress

- API-driven React dashboard wired to the live market overview endpoint
- Coin detail panel with trend chart proxy and technical indicator cards
- Account-based alert workflow connected to JWT auth and alert creation routes
- AI insights panel connected to the agent service through Vite proxying
- Responsive landing plus dashboard experience ready for portfolio presentation

## Phase 4 progress

- Backend analytics routes for market summaries, anomaly detection, and metric recommendations
- Grounded agent logic that calls backend analytics tools instead of returning placeholders
- Rule-based anomaly scoring using volatility, momentum, and RSI extremes
- Natural-language handling for trend, summary, anomaly, comparison, and recommendation prompts

## Phase 5 progress

- Added API readiness and metrics endpoints for operational visibility
- Added request logging middleware and lightweight in-memory request counters
- Added agent readiness checks against backend dependencies
- Expanded backend tests to cover analytics, system readiness, and alert creation
- Hardened local orchestration with more health checks and clearer developer commands
- Rewrote project guidance for portfolio presentation and interview walkthroughs

## Phase 6 progress

- Split raw ingestion from derived analytics so Kafka now sits between market capture and indicator generation
- Added a dedicated streaming processor service that consumes market events from Kafka and writes technical indicators plus AI insight cards back to PostgreSQL
- Kept Spark job scaffolding in place while making the local Kafka processor path actually runnable end to end

### Authentication

- Register a local account through the dashboard or `POST /api/v1/auth/register`
- Optional sample credentials can be seeded only when `SEED_DEMO_USER=true`

## Core API surface

- `GET /api/v1/market/overview`
- `GET /api/v1/market/stream`
- `POST /api/v1/auth/login`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts`
- `GET /api/v1/analytics/anomalies`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/recommendations`
- `GET /api/v1/system/ready`
- `GET /api/v1/system/metrics`

## Local development workflow

```bash
cp .env.example .env
make up
make smoke
```

Helpful commands:

- `make down` stops the stack
- `make logs` tails Docker Compose logs
- `make test` runs backend tests
- `make frontend-build` verifies the frontend production build
- `make migrate` runs Alembic migrations inside the API container
- `python services/ingestion/src/backfill.py` inserts additional sample market rows locally
- `make stream-processor` runs the Kafka-backed analytics processor locally

## Architecture walkthrough

1. Market data is ingested through the `services/ingestion` layer and is designed to publish normalized events to Kafka.
2. Spark jobs in `services/streaming` are positioned to compute technical indicators and trend summaries.
3. PostgreSQL serves curated market data, indicators, alerts, and AI insight artifacts.
4. FastAPI exposes typed APIs, auth, SSE, analytics endpoints, and operational health checks.
5. The agent service tool-calls backend analytics endpoints to generate grounded answers.
6. The React dashboard consumes the API and agent through a browser-friendly Vite proxy layer.

## Portfolio highlights

- Built a full-stack crypto intelligence platform spanning React, FastAPI, PostgreSQL, Kafka, Spark, Docker, and an agentic AI service.
- Designed a modular data-serving layer with JWT auth, SSE live updates, alert workflows, analytics endpoints, and OpenAPI documentation.
- Implemented grounded AI reasoning over project data using backend tool calls for summaries, anomaly detection, comparisons, and metric recommendations.
- Added operational polish with Docker Compose orchestration, readiness checks, request metrics, automated tests, and developer workflow automation.

## What remains before real production deployment

- Replace seeded market data with a live exchange/provider ingestion path in the default runtime flow.
- Run Kafka to Spark to PostgreSQL indicator writes end to end instead of using the current seeded serving dataset.
- Add CI/CD, secrets management, cloud deployment manifests, and persistent observability tooling.
- Expand auth and account management with password reset, verification, and stronger session controls.
- Move from bootstrap SQL plus local Alembic scaffolding to a single migration-led database lifecycle in all environments.

## Live data direction

The recommended production-style data path for this project is:

`Binance WebSocket -> Kafka -> Spark Structured Streaming -> PostgreSQL`

This repository now includes the first practical pieces of that path:

- `services/ingestion/src/binance_stream.py` for real-time Binance mini-ticker ingestion
- `services/ingestion/src/coingecko_backfill.py` for CoinGecko historical/reference backfill
- `services/ingestion/src/runner.py` for a continuous local refresh worker
- normalized market event modeling and PostgreSQL snapshot writes in `services/ingestion/src/`
- `services/streaming/src/consumer.py` for Kafka-backed indicator and insight processing

This means the backend can start serving real externally sourced rows as soon as ingestion writes newer snapshots into `market_snapshots`, while the streaming processor refreshes derived analytics asynchronously.

## Continuous local refresh

For local development, the stack can now run a lightweight continuous ingestion worker that refreshes market snapshots on a fixed interval.

- Default refresh interval: `300` seconds
- Config variable: `INGESTION_REFRESH_INTERVAL_SECONDS`
- Docker service: `ingestion`
- Derived analytics processor service: `streaming`

This gives you a simple always-fresh local setup without needing to keep a manual backfill command running, while still exercising a Kafka-based processing boundary.

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
- Demo alert workflow connected to JWT auth and alert creation routes
- AI insights panel connected to the agent service through Vite proxying
- Responsive landing plus dashboard experience ready for portfolio demos

## Phase 4 progress

- Backend analytics routes for market summaries, anomaly detection, and metric recommendations
- Grounded agent logic that calls backend analytics tools instead of returning placeholders
- Rule-based anomaly scoring using volatility, momentum, and RSI extremes
- Natural-language handling for trend, summary, anomaly, comparison, and recommendation prompts

### Demo credentials

- Email: `demo@cryptopulse.ai`
- Password: `DemoPass123!`

## Upcoming implementation details

Phase 2 will replace the seeded overview responses with real database-backed services, then add authentication, live market ingestion, and the first ETL path for technical indicators.

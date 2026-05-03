# Phased Build Plan

## Phase 1: Architecture and scaffold

- Create a monorepo layout
- Stand up minimal backend, frontend, and agent services
- Add Docker Compose, environment configuration, and the initial SQL schema
- Initialize tests and developer workflows

## Phase 2: Backend and data engineering core

- Build domain modules for markets, indicators, alerts, and auth
- Add SQLAlchemy models and repository layer
- Implement Kafka producer and normalized event schemas
- Add a Spark Structured Streaming job for core indicators
- Create historical backfill and validation utilities

## Phase 3: Frontend dashboard

- Implement landing page and application shell
- Add live market dashboard and coin detail page
- Build charting, technical indicator cards, and alert forms
- Connect frontend state to backend APIs and live streams

## Phase 4: Agent and ML analytics

- Add tool-based market Q&A over project data
- Generate daily summaries and guided insights
- Implement anomaly detection and a lightweight forecast path
- Expose AI insight endpoints to the frontend

## Phase 5: Production polish

- Expand unit and integration tests
- Add logging, metrics hooks, and health checks
- Refine Docker setup and README
- Add final resume-ready outcomes and tradeoff notes

## Phase 7: Live monitoring and alert intelligence

- Evaluate active alert rules against the latest curated market data
- Store triggered alert history for user accounts
- Separate active and triggered alert views in the dashboard
- Add a manual check path that can later be moved behind a scheduler or worker

## Phase 8: Groq-powered grounded agent

- Add a Groq-backed LLM path for market questions
- Let the agent plan which backend analytics tools to call
- Compose natural-language answers from tool results with explicit sources
- Keep deterministic fallback behavior for local demos without an API key

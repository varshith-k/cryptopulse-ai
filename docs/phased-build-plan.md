# Build Plan

This file tracks the main project milestones. The phases are written as implementation checkpoints rather than a strict calendar.

## Phase 1: Project Scaffold

- Set up the monorepo layout
- Add initial API, frontend, and agent services
- Add Docker Compose, environment configuration, and bootstrap SQL
- Add basic tests and developer commands

## Phase 2: Backend and Data Core

- Add FastAPI modules for market data, analytics, alerts, auth, and system health
- Add SQLAlchemy models, repositories, and Alembic support
- Add JWT auth and user-specific alert storage
- Add market overview, history, and live stream endpoints
- Add historical backfill utilities

## Phase 3: Dashboard

- Build the React dashboard shell
- Add market overview cards and a coin detail panel
- Add historical charting and indicator cards
- Connect auth and alert creation flows to the backend
- Proxy API and agent requests through Vite for local development

## Phase 4: Analytics and Agent Service

- Add analytics endpoints for summaries, anomalies, and recommendations
- Add rule-based anomaly scoring using RSI, momentum, and volatility
- Add an agent service that calls backend analytics tools
- Support summary, comparison, anomaly, trend, and recommendation questions

## Phase 5: Local Reliability

- Add readiness and metrics endpoints
- Add request logging and basic request counters
- Add agent readiness checks against the backend
- Expand backend test coverage
- Improve Docker health checks and Makefile commands

## Phase 6: Ingestion and Processing

- Add Binance WebSocket ingestion support
- Add CoinGecko reference/backfill support
- Add a continuous local ingestion worker
- Add Kafka-backed processor service for derived indicators and insight rows
- Keep Spark job scaffolding for a heavier streaming-processing path

## Phase 7: Alert Evaluation

- Evaluate active alerts against the latest stored market data
- Store triggered alert history
- Deactivate alerts after they trigger
- Add active and triggered alert views in the dashboard
- Add a manual "check alerts now" flow

## Phase 8: Groq-backed Agent

- Add optional Groq configuration through environment variables
- Add LLM-based tool planning over backend analytics tools
- Merge model-selected tools with deterministic required tools for reliability
- Compose grounded answers from backend tool results
- Keep deterministic fallback behavior when Groq is not configured

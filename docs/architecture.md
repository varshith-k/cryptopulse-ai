# CryptoPulse AI Architecture

## System overview

CryptoPulse AI is designed as a layered platform:

1. **Market data ingestion**
   - Historical backfill scripts fetch OHLCV market data for selected symbols.
   - Real-time ingestion producers publish normalized tick events to Kafka.

2. **Streaming analytics**
   - Spark Structured Streaming reads Kafka topics.
   - ETL jobs calculate moving averages, RSI, MACD, rolling volatility, and trend summaries.
   - Curated outputs are written to PostgreSQL and optionally Redis.

3. **Serving layer**
   - FastAPI exposes prices, trend summaries, indicators, alerts, and live update feeds.
   - Authentication and user preference management live here.

4. **AI and ML layer**
   - The agent service answers grounded questions, generates summaries, and recommends next metrics to inspect.
   - An anomaly detection module scores unusual volatility and momentum shifts.

5. **Frontend**
   - A React dashboard consumes REST and live update channels.
   - Users can inspect coins, configure alerts, and ask natural-language questions.

## Data flow

```text
Market APIs / backfill
        |
        v
Kafka ingestion topics
        |
        v
Spark Structured Streaming jobs
        |
        +--> PostgreSQL curated tables
        +--> Redis cache / live pub-sub
        |
        v
FastAPI serving layer <--> Agent tools
        |
        v
React dashboard
```

## Key engineering decisions

- **FastAPI over Express**
  - Strong typing with Pydantic
  - Better synergy with data engineering and AI services in Python
  - Automatic OpenAPI docs reduce integration friction

- **Kafka + Spark**
  - Realistic for streaming ETL and windowed analytics
  - Good portfolio signal for data engineering roles

- **PostgreSQL**
  - Simple, proven serving layer for aggregated metrics and alert metadata

- **Dedicated agent service**
  - Clean separation between product APIs and AI-specific orchestration
  - Easier to evolve tool-calling and guardrails independently


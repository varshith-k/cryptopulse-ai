CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watched_assets (
    symbol VARCHAR(16) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    market VARCHAR(32) NOT NULL DEFAULT 'crypto'
);

CREATE TABLE IF NOT EXISTS market_snapshots (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL REFERENCES watched_assets(symbol),
    price_usd NUMERIC(18, 8) NOT NULL,
    percent_change_24h NUMERIC(10, 4) NOT NULL,
    volume_24h NUMERIC(20, 2),
    market_cap NUMERIC(20, 2),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL REFERENCES watched_assets(symbol),
    timeframe VARCHAR(16) NOT NULL,
    sma_20 NUMERIC(18, 8),
    ema_20 NUMERIC(18, 8),
    rsi_14 NUMERIC(10, 4),
    macd NUMERIC(18, 8),
    signal NUMERIC(18, 8),
    rolling_volatility NUMERIC(10, 4),
    trend_summary TEXT,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_alerts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    symbol VARCHAR(16) NOT NULL REFERENCES watched_assets(symbol),
    alert_type VARCHAR(64) NOT NULL,
    threshold NUMERIC(18, 8),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_insights (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(16),
    insight_type VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    confidence NUMERIC(5, 2),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO watched_assets(symbol, name)
VALUES
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('SOL', 'Solana')
ON CONFLICT (symbol) DO NOTHING;


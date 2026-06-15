from __future__ import annotations

from decimal import Decimal

import psycopg

from src.detector import VolatilitySignal


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS realtime_anomalies (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    price_usd NUMERIC(18, 8) NOT NULL,
    window_mean NUMERIC(18, 8) NOT NULL,
    window_std NUMERIC(18, 8) NOT NULL,
    z_score NUMERIC(10, 4) NOT NULL,
    deviation_pct NUMERIC(10, 4) NOT NULL,
    sample_size INTEGER NOT NULL,
    direction VARCHAR(16) NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_realtime_anomalies_detected_at
ON realtime_anomalies (detected_at DESC);
"""

INSERT_ANOMALY_SQL = """
INSERT INTO realtime_anomalies(
    symbol,
    price_usd,
    window_mean,
    window_std,
    z_score,
    deviation_pct,
    sample_size,
    direction,
    detected_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def ensure_schema(connection: psycopg.Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(CREATE_INDEX_SQL)
    connection.commit()


def write_anomaly(connection: psycopg.Connection, signal: VolatilitySignal) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            INSERT_ANOMALY_SQL,
            (
                signal.symbol,
                Decimal(str(signal.price)),
                Decimal(str(signal.window_mean)),
                Decimal(str(signal.window_std)),
                Decimal(str(round(signal.z_score, 4))),
                Decimal(str(round(signal.deviation_pct, 4))),
                signal.sample_size,
                signal.direction,
                signal.detected_at,
            ),
        )
    connection.commit()

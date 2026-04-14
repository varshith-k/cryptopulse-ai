from __future__ import annotations

from decimal import Decimal

import psycopg

from src.analytics import ComputedIndicator, GeneratedInsight


INSERT_INDICATOR_SQL = """
INSERT INTO technical_indicators(
    symbol,
    timeframe,
    sma_20,
    ema_20,
    rsi_14,
    macd,
    signal,
    rolling_volatility,
    trend_summary,
    computed_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

DELETE_INSIGHT_SQL = """
DELETE FROM ai_insights
WHERE insight_type = %s AND symbol IS NOT DISTINCT FROM %s
"""

INSERT_INSIGHT_SQL = """
INSERT INTO ai_insights(symbol, insight_type, title, content, confidence, generated_at)
VALUES (%s, %s, %s, %s, %s, %s)
"""


def write_indicator(connection: psycopg.Connection, indicator: ComputedIndicator) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            INSERT_INDICATOR_SQL,
            (
                indicator.symbol,
                indicator.timeframe,
                Decimal(str(indicator.sma_20)) if indicator.sma_20 is not None else None,
                Decimal(str(indicator.ema_20)) if indicator.ema_20 is not None else None,
                Decimal(str(indicator.rsi_14)) if indicator.rsi_14 is not None else None,
                Decimal(str(indicator.macd)) if indicator.macd is not None else None,
                Decimal(str(indicator.signal)) if indicator.signal is not None else None,
                (
                    Decimal(str(indicator.rolling_volatility))
                    if indicator.rolling_volatility is not None
                    else None
                ),
                indicator.trend_summary,
                indicator.computed_at,
            ),
        )
    connection.commit()


def replace_insight(connection: psycopg.Connection, insight: GeneratedInsight) -> None:
    with connection.cursor() as cursor:
        cursor.execute(DELETE_INSIGHT_SQL, (insight.insight_type, insight.symbol))
        cursor.execute(
            INSERT_INSIGHT_SQL,
            (
                insight.symbol,
                insight.insight_type,
                insight.title,
                insight.content,
                Decimal(str(insight.confidence)),
                insight.generated_at,
            ),
        )
    connection.commit()

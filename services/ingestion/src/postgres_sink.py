from decimal import Decimal

import psycopg

from src.schema import NormalizedMarketEvent


UPSERT_ASSET_SQL = """
INSERT INTO watched_assets(symbol, name, market)
VALUES (%s, %s, 'crypto')
ON CONFLICT (symbol) DO NOTHING
"""

INSERT_SNAPSHOT_SQL = """
INSERT INTO market_snapshots(symbol, price_usd, percent_change_24h, volume_24h, market_cap, observed_at)
VALUES (%s, %s, %s, %s, %s, %s)
"""


def write_market_event(connection: psycopg.Connection, event: NormalizedMarketEvent) -> None:
    with connection.cursor() as cursor:
        cursor.execute(UPSERT_ASSET_SQL, (event.base_symbol, event.base_symbol))
        cursor.execute(
            INSERT_SNAPSHOT_SQL,
            (
                event.base_symbol,
                Decimal(str(event.price_usd)),
                Decimal(str(event.percent_change_24h)),
                Decimal(str(event.volume_24h)) if event.volume_24h is not None else None,
                Decimal(str(event.market_cap)) if event.market_cap is not None else None,
                event.observed_at,
            ),
        )
    connection.commit()

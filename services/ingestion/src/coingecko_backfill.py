from __future__ import annotations

from datetime import UTC, datetime

import httpx
import psycopg

from src.config import settings
from src.kafka_sink import build_producer, publish_market_event
from src.postgres_sink import write_market_event
from src.schema import NormalizedMarketEvent


COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
}


def build_backfill_event(symbol: str, payload: dict) -> NormalizedMarketEvent:
    return NormalizedMarketEvent(
        source="coingecko",
        exchange_symbol=symbol,
        base_symbol=symbol,
        quote_symbol="USD",
        price_usd=float(payload["current_price"]),
        percent_change_24h=float(payload.get("price_change_percentage_24h", 0)),
        volume_24h=float(payload.get("total_volume", 0)),
        market_cap=float(payload.get("market_cap", 0)),
        event_type="snapshot",
        observed_at=datetime.now(UTC),
    )


def run_backfill() -> None:
    ids = ",".join(COIN_IDS.values())
    params = {
        "vs_currency": "usd",
        "ids": ids,
        "order": "market_cap_desc",
        "per_page": len(COIN_IDS),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }

    with httpx.Client(timeout=20) as client:
        response = client.get(f"{settings.coingecko_base_url}/coins/markets", params=params)
        response.raise_for_status()
        rows = response.json()

    rows_by_symbol = {
        item["symbol"].upper(): item for item in rows if item["symbol"].upper() in COIN_IDS
    }
    producer = build_producer()
    with psycopg.connect(settings.postgres_url) as connection:
        for symbol in COIN_IDS:
            payload = rows_by_symbol.get(symbol)
            if payload is None:
                continue
            event = build_backfill_event(symbol, payload)
            write_market_event(connection, event)
            publish_market_event(producer, event)
            print(
                f"[coingecko] inserted {symbol} price={event.price_usd:.4f} "
                f"change24h={event.percent_change_24h:.2f}%"
            )
            print(f"[kafka] published {symbol} to {settings.market_topic}")


def main() -> None:
    run_backfill()


if __name__ == "__main__":
    main()

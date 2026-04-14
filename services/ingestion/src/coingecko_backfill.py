from __future__ import annotations

from datetime import UTC, datetime

import httpx
import psycopg

from src.analytics import compute_indicator, fetch_daily_closes, generate_insights
from src.config import settings
from src.postgres_sink import replace_insight, write_indicator, write_market_event
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

        histories_by_symbol = {
            symbol: fetch_daily_closes(client, coin_id)
            for symbol, coin_id in COIN_IDS.items()
        }

    rows_by_symbol = {
        item["symbol"].upper(): item for item in rows if item["symbol"].upper() in COIN_IDS
    }

    events: dict[str, NormalizedMarketEvent] = {}
    computed_indicators = {}

    with psycopg.connect(settings.postgres_url) as connection:
        for symbol in COIN_IDS:
            payload = rows_by_symbol.get(symbol)
            if payload is None:
                continue
            event = build_backfill_event(symbol, payload)
            events[symbol] = event
            write_market_event(connection, event)
            indicator = compute_indicator(symbol, event, histories_by_symbol.get(symbol, []))
            computed_indicators[symbol] = indicator
            write_indicator(connection, indicator)
            print(
                f"[coingecko] inserted {symbol} price={event.price_usd:.4f} "
                f"change24h={event.percent_change_24h:.2f}%"
            )
            print(
                "[indicators] computed "
                f"{symbol} rsi="
                f"{indicator.rsi_14:.2f}" if indicator.rsi_14 is not None
                else f"[indicators] computed {symbol} rsi=n/a"
            )

        for insight in generate_insights(events, computed_indicators):
            replace_insight(connection, insight)
            print(f"[insights] refreshed {insight.insight_type} for {insight.symbol or 'market'}")


def main() -> None:
    run_backfill()


if __name__ == "__main__":
    main()

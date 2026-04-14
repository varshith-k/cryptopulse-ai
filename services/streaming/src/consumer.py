from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta

import httpx
import psycopg
from kafka import KafkaConsumer

from src.analytics import compute_indicator, fetch_daily_closes, generate_insights
from src.config import settings
from src.postgres_sink import replace_insight, write_indicator
from src.schema import NormalizedMarketEvent

HISTORY_CACHE_TTL = timedelta(hours=1)
history_cache: dict[str, tuple[list[float], datetime]] = {}


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.market_topic,
        bootstrap_servers=settings.kafka_broker,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=settings.consumer_group,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def process_batch(events: dict[str, NormalizedMarketEvent]) -> None:
    if not events:
        return

    indicators = {}
    with httpx.Client(timeout=20) as client:
        histories = {
            symbol: load_history(client, symbol, events[symbol].price_usd)
            for symbol in events
        }

    with psycopg.connect(settings.postgres_url) as connection:
        for symbol, event in events.items():
            indicator = compute_indicator(symbol, event, histories.get(symbol, []))
            indicators[symbol] = indicator
            write_indicator(connection, indicator)
            rsi_display = f"{indicator.rsi_14:.2f}" if indicator.rsi_14 is not None else "n/a"
            print(f"[streaming] computed {symbol} indicators: rsi={rsi_display}")

        for insight in generate_insights(events, indicators):
            replace_insight(connection, insight)
            print(
                f"[streaming] refreshed {insight.insight_type} "
                f"for {insight.symbol or 'market'}"
            )


def main() -> None:
    consumer = build_consumer()
    print(
        f"Starting Kafka market processor on topic {settings.market_topic} "
        f"with group {settings.consumer_group}."
    )

    while True:
        latest_events = collect_latest_events(consumer)
        if not latest_events:
            time.sleep(1)
            continue

        try:
            process_batch(latest_events)
        except Exception as exc:  # pragma: no cover
            print(f"[streaming] batch processing failed: {exc}")
            time.sleep(2)


def collect_latest_events(consumer: KafkaConsumer) -> dict[str, NormalizedMarketEvent]:
    latest_events: dict[str, NormalizedMarketEvent] = {}
    for poll_index, timeout_ms in enumerate((settings.poll_timeout_ms, 1000, 1000, 1000)):
        message_pack = consumer.poll(timeout_ms=timeout_ms)
        for _partition, messages in message_pack.items():
            for message in messages:
                event = NormalizedMarketEvent.model_validate(message.value)
                latest_events[event.base_symbol] = event

        if poll_index > 0 and not message_pack:
            break

    return latest_events


def load_history(client: httpx.Client, symbol: str, fallback_price: float) -> list[float]:
    cached = history_cache.get(symbol)
    now = datetime.now(UTC)
    if cached is not None:
        prices, fetched_at = cached
        if now - fetched_at < HISTORY_CACHE_TTL:
            return prices

    try:
        prices = fetch_daily_closes(client, symbol)
        if prices:
            history_cache[symbol] = (prices, now)
            return prices
    except Exception as exc:  # pragma: no cover
        print(f"[streaming] history fetch failed for {symbol}: {exc}")

    if cached is not None:
        return cached[0]
    return [fallback_price]


if __name__ == "__main__":
    main()

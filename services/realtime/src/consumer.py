from __future__ import annotations

import json
import time

import psycopg
from kafka import KafkaConsumer

from src.config import settings
from src.detector import SlidingWindowDetector, VolatilitySignal
from src.postgres_sink import ensure_schema, write_anomaly
from src.schema import NormalizedMarketEvent


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.market_topic,
        bootstrap_servers=settings.kafka_broker,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=settings.consumer_group,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def persist_anomalies(anomalies: list[VolatilitySignal]) -> None:
    if not anomalies:
        return
    try:
        with psycopg.connect(settings.postgres_url) as connection:
            for signal in anomalies:
                write_anomaly(connection, signal)
    except Exception as exc:  # pragma: no cover
        print(f"[realtime] failed to persist anomalies: {exc}")


def main() -> None:
    detector = SlidingWindowDetector(
        window_size=settings.window_size,
        z_threshold=settings.z_threshold,
        min_samples=settings.min_samples,
    )
    consumer = build_consumer()
    print(
        f"Starting real-time volatility detector on topic {settings.market_topic} "
        f"(window={settings.window_size}, z>={settings.z_threshold}, "
        f"min_samples={settings.min_samples})."
    )

    with psycopg.connect(settings.postgres_url) as connection:
        ensure_schema(connection)

    while True:
        message_pack = consumer.poll(timeout_ms=settings.poll_timeout_ms)
        if not message_pack:
            continue

        anomalies: list[VolatilitySignal] = []
        for _partition, messages in message_pack.items():
            for message in messages:
                try:
                    event = NormalizedMarketEvent.model_validate(message.value)
                except Exception as exc:  # pragma: no cover
                    print(f"[realtime] skipped malformed event: {exc}")
                    continue

                signal = detector.observe(
                    event.base_symbol, event.price_usd, event.observed_at
                )
                if signal.is_anomaly:
                    anomalies.append(signal)
                    print(
                        f"[realtime] ANOMALY {signal.symbol} price={signal.price:.4f} "
                        f"z={signal.z_score:.2f} dev={signal.deviation_pct:.2f}% "
                        f"({signal.direction})"
                    )
                else:
                    state = "warming up" if signal.sample_size < settings.min_samples else "ok"
                    print(
                        f"[realtime] {signal.symbol} price={signal.price:.4f} "
                        f"z={signal.z_score:.2f} [{state}]"
                    )

        persist_anomalies(anomalies)


if __name__ == "__main__":
    main()

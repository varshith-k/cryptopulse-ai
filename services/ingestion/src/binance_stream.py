from __future__ import annotations

import asyncio
import json

import psycopg
import websockets
from kafka import KafkaProducer

from src.config import settings
from src.postgres_sink import write_market_event
from src.schema import build_binance_event


def build_stream_url() -> str:
    streams = "/".join(f"{pair}@miniTicker" for pair in settings.tracked_pair_list)
    return f"{settings.binance_ws_url}?streams={streams}"


async def run_stream() -> None:
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_broker,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    with psycopg.connect(settings.postgres_url) as connection:
        async with websockets.connect(build_stream_url()) as websocket:
            print(f"Connected to Binance stream for {', '.join(settings.tracked_pair_list)}")
            while True:
                raw_message = await websocket.recv()
                envelope = json.loads(raw_message)
                payload = envelope["data"]
                event = build_binance_event(payload)
                write_market_event(connection, event)
                producer.send(settings.market_topic, event.model_dump(mode="json"))
                producer.flush()
                print(
                    f"[binance] {event.base_symbol} price={event.price_usd:.4f} "
                    f"change24h={event.percent_change_24h:.2f}%"
                )


def main() -> None:
    asyncio.run(run_stream())


if __name__ == "__main__":
    main()

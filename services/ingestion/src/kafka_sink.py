from __future__ import annotations

import json

from kafka import KafkaProducer

from src.config import settings
from src.schema import NormalizedMarketEvent


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_broker,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def publish_market_event(producer: KafkaProducer, event: NormalizedMarketEvent) -> None:
    producer.send(settings.market_topic, event.model_dump(mode="json"))
    producer.flush()

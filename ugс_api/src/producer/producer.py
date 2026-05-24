import json
from typing import Any

from kafka import KafkaProducer


class KafkaEventProducer:
    def __init__(self, producer: KafkaProducer, topic: str) -> None:
        self.producer = producer
        self.topic = topic

    def send(self, data: dict[str, Any]) -> None:
        self.producer.send(
            topic=self.topic,
            value=data,
        )
        self.producer.flush()


def create_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=[bootstrap_servers],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

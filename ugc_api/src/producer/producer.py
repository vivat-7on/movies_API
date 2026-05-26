import json
from typing import Any

from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata


class KafkaEventProducer:
    def __init__(self, producer: KafkaProducer, topic: str) -> None:
        self.producer = producer
        self.topic = topic

    def send(self, data: dict[str, Any]) -> FutureRecordMetadata:
        return self.producer.send(
            topic=self.topic,
            value=data,
        )

    def close(self) -> None:
        self.producer.flush(timeout=5)
        self.producer.close(timeout=5)

    def is_ready(self) -> bool:
        try:
            self.producer.partitions_for(self.topic)
            return True
        except Exception:
            return False


def create_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=[bootstrap_servers],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=3,
        linger_ms=100,
        request_timeout_ms=10_000,
    )

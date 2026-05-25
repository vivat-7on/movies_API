import json

from kafka import KafkaConsumer


def create_kafka_consumer(
    topics: str,
    bootstrap_servers: str,
    auto_offset_reset: str,
    group_id: str,
) -> KafkaConsumer:
    return KafkaConsumer(
        topics,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset=auto_offset_reset,
        group_id=group_id,
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

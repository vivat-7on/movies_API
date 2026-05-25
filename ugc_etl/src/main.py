from consumer.kafka_consumer import create_kafka_consumer
from loader.clickhouse_loader import ClickHouseLoader, create_clickhouse_client
from settings import Settings

config = Settings()

consumer = create_kafka_consumer(
    topics=config.KAFKA_TOPIC,
    bootstrap_servers=config.kafka_bootstrap_servers,
    auto_offset_reset="earliest",
    group_id=config.KAFKA_GROUP_ID,
)

clickhouse_client = create_clickhouse_client(
    host=config.CLICKHOUSE_HOST,
    port=config.CLICKHOUSE_PORT,
    user=config.CLICKHOUSE_USER,
    password=config.CLICKHOUSE_PASSWORD,
    database=config.CLICKHOUSE_DB,
)

loader = ClickHouseLoader(
    clickhouse_client=clickhouse_client,
    table=config.CLICKHOUSE_TABLE,
)

loader.create_events_table()

batch = []
if __name__ == "__main__":
    for message in consumer:
        print(message.value)

        batch.append(message.value)

        if len(batch) >= config.BATCH_SIZE:
            loader.insert_batch(batch)
            consumer.commit()
            batch.clear()

import logging
import time

from consumer.kafka_consumer import create_kafka_consumer
from loader.clickhouse_loader import ClickHouseLoader, create_clickhouse_client
from settings import Settings

logger = logging.getLogger(__name__)

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


def flush_butch(batch, loader, consumer) -> None:
    if not batch:
        return

    loader.insert_batch(batch)
    consumer.commit()
    logger.info("Insert batch", extra={"batch size": len(batch)})
    batch.clear()


def main():
    batch = []
    last_flush_at = time.monotonic()

    try:
        for message in consumer:
            batch.append(message.value)

            now = time.monotonic()
            should_flush_by_size = len(batch) >= config.BATCH_SIZE
            should_flush_by_time = now - last_flush_at >= config.BATCH_TIMEOUT_SECONDS

            if should_flush_by_size or should_flush_by_time:
                flush_butch(batch, loader, consumer)
                last_flush_at = time.monotonic()
    except KeyboardInterrupt:
        logger.info("ETL stopped by user")
    finally:
        flush_butch(batch, loader, consumer)
        consumer.close()


if __name__ == "__main__":
    main()

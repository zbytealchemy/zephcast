"""Example of using retry with MsgFlow consumers."""

import asyncio
import logging

from typing import List

from msgflow.core.consumers import ConsumerConfig, batch_consumer, consumer
from msgflow.core.retry import RetryConfig
from msgflow.kafka.async_client import AsyncKafkaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_retry(retry_count: int, exception: Exception) -> None:
    """Log retry attempts."""
    logger.warning("Retry %d: %s", retry_count, str(exception))


retry_config = RetryConfig(
    max_retries=3,
    retry_sleep=1.0,
    backoff_factor=2.0,
    exceptions=(ConnectionError, TimeoutError),
    on_retry=log_retry,
)

consumer_config = ConsumerConfig(
    retry=retry_config,
    auto_ack=True,
)


@consumer(config=consumer_config)
async def process_message(message: str) -> None:
    """Process a single message with retry."""
    if "error" in message:
        raise ConnectionError("Failed to process message")
    logger.info("Processed message: %s", message)


batch_config = ConsumerConfig(
    retry=retry_config,
    batch_size=3,
    batch_timeout=1.0,
)


@batch_consumer(config=batch_config)
async def process_batch(messages: List[str]) -> None:
    """Process a batch of messages with retry."""
    if any("error" in msg for msg in messages):
        raise TimeoutError("Failed to process batch")
    logger.info("Processed batch: %s", messages)


async def main() -> None:
    """Run the example."""
    client = AsyncKafkaClient(
        stream_name="retry-example",
        bootstrap_servers="localhost:9092",
    )

    try:
        await client.connect()

        test_messages = [
            "message1",
            "error_message",
            "message2",
            "message3",
            "error_message2",
            "message4",
        ]

        for message in test_messages:
            await client.send(message)
            logger.info("Sent message: %s", message)

        logger.info("Processing messages one by one...")
        async for message in client.receive():
            try:
                await process_message(message)
            except Exception as e:
                logger.error("Failed to process message after retries: %s", e)

        logger.info("Processing messages in batches...")
        batch: List[str] = []
        async for message in client.receive():
            batch.append(message)
            if len(batch) >= batch_config.batch_size:
                try:
                    await process_batch(batch)
                except Exception as e:
                    logger.error("Failed to process batch after retries: %s", e)
                batch = []

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

"""Example of using Kafka messaging clients."""

import asyncio
import logging

from zephcast.kafka import AsyncKafkaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def produce_messages(client: AsyncKafkaClient, count: int = 5) -> None:
    """Produce a series of messages."""
    async with client:
        for i in range(count):
            message = f"Message {i}"
            await client.send(message)
            logger.info("Produced: %s", message)
            await asyncio.sleep(1)

        await client.send("END")


async def consume_messages(client: AsyncKafkaClient) -> None:
    """Consume messages."""
    async with client:
        try:
            async for message in client.receive():
                logger.info("Consumed: %s", message)
                if message == "END":
                    break
        except Exception as e:
            logger.error("Error consuming messages: %s", e)


async def main() -> None:
    """Run the example."""
    topic_name = "example-topic"
    kafka_servers = "localhost:9092"

    producer: AsyncKafkaClient = AsyncKafkaClient(
        stream_name=topic_name, bootstrap_servers=kafka_servers
    )

    consumer1: AsyncKafkaClient = AsyncKafkaClient(
        stream_name=topic_name, bootstrap_servers=kafka_servers, group_id="consumer-group-1"
    )

    consumer2: AsyncKafkaClient = AsyncKafkaClient(
        stream_name=topic_name, bootstrap_servers=kafka_servers, group_id="consumer-group-2"
    )

    # Run producer and multiple consumers concurrently to demonstrate
    # Kafka's consumer group functionality
    await asyncio.gather(
        produce_messages(producer), consume_messages(consumer1), consume_messages(consumer2)
    )


if __name__ == "__main__":
    asyncio.run(main())

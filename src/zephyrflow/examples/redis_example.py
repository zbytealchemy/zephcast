"""Example of using Redis messaging clients."""

import asyncio
import logging

from zephyrflow.redis.async_client import AsyncRedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def produce_messages(client: AsyncRedisClient, count: int = 5) -> None:
    """Produce a series of messages."""
    async with client:
        for i in range(count):
            message = f"Message {i}"
            await client.send(message)
            logger.info("Produced: %s", message)
            await asyncio.sleep(1)

        # send END message so consumer can exit
        await client.send("END")


async def consume_messages(client: AsyncRedisClient) -> None:
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
    stream_name = "example-stream"
    redis_url = "redis://localhost:6379"

    producer = AsyncRedisClient(stream_name=stream_name, redis_url=redis_url)
    consumer = AsyncRedisClient(stream_name=stream_name, redis_url=redis_url)

    await asyncio.gather(produce_messages(producer), consume_messages(consumer))

    await producer.close()
    await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())

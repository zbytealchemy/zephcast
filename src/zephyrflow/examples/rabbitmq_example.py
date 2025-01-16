"""Example of using RabbitMQ messaging clients."""

import asyncio
import logging

from contextlib import suppress

from zephyrflow.rabbit import AsyncRabbitClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def produce_messages(client: AsyncRabbitClient, count: int = 5) -> None:
    """Produce a series of messages."""
    async with client:
        for i in range(count):
            message = f"Message {i}"
            await client.send(message)
            logger.info("Produced: %s", message)
            await asyncio.sleep(1)

        # send END message to terminate consumer
        await client.send("END")


async def consume_messages(client: AsyncRabbitClient) -> None:
    """Consume messages."""
    async with client:
        with suppress(Exception):
            async for message in client.receive():
                logger.info("Consumed: %s", message)
                if message == "END":
                    break


async def main() -> None:
    """Run the example."""
    exchange_name = "example-exchange"
    queue_name = "example-queue"
    routing_key = "example-routing-key"

    rabbitmq_url = "amqp://guest:guest@localhost:5672/"

    producer = AsyncRabbitClient(
        stream_name=routing_key,
        rabbitmq_url=rabbitmq_url,
        exchange_name=exchange_name,
        queue_name=queue_name,
    )

    consumer = AsyncRabbitClient(
        stream_name=routing_key,
        rabbitmq_url=rabbitmq_url,
        exchange_name=exchange_name,
        queue_name=queue_name,
    )

    await asyncio.gather(
        produce_messages(producer),
        consume_messages(consumer),
    )


if __name__ == "__main__":
    asyncio.run(main())

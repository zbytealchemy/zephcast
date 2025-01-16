"""Example of using both sync and async Redis clients together."""

import asyncio
import logging
import threading

from queue import Queue

from zephyrflow.redis.async_client import AsyncRedisClient
from zephyrflow.redis.sync_client import SyncRedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_producer(client: SyncRedisClient, message_queue: Queue[str]) -> None:
    """Synchronous producer that gets messages from a queue."""
    with client:
        while True:
            try:
                message = message_queue.get()
                if message == "STOP":
                    break
                client.send(message)
                logger.info("Sync producer sent: %s", message)
            except Exception as e:
                logger.error("Error in sync producer: %s", e)
                break


async def async_consumer(client: AsyncRedisClient) -> None:
    """Asynchronous consumer."""
    async with client:
        try:
            async for message in client.receive():
                logger.info("Async consumer received: %s", message)
        except Exception as e:
            logger.error("Error in async consumer: %s", e)


def run_sync_producer(client: SyncRedisClient, message_queue: Queue[str]) -> None:
    """Run the sync producer in a separate thread."""
    sync_producer(client, message_queue)


async def main() -> None:
    """Run the example."""
    stream_name = "mixed-example-stream"
    redis_url = "redis://localhost:6379"

    message_queue: Queue[str] = Queue()

    sync_client = SyncRedisClient(stream_name=stream_name, redis_url=redis_url)
    async_client = AsyncRedisClient(stream_name=stream_name, redis_url=redis_url)

    producer_thread = threading.Thread(target=run_sync_producer, args=(sync_client, message_queue))
    producer_thread.start()

    consumer_task = asyncio.create_task(async_consumer(async_client))

    test_messages = [f"Test message {i}" for i in range(5)]
    for message in test_messages:
        message_queue.put(message)
        await asyncio.sleep(1)

    message_queue.put("STOP")

    producer_thread.join()

    await asyncio.sleep(2)

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())

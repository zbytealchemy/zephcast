"""
Example of using ZephCast to create robust consumers with different patterns.
This example demonstrates:
1. Basic message processing
2. Batch message processing
3. Priority message handling
4. Graceful shutdown
"""

import asyncio
import json
import logging
import signal

from dataclasses import asdict, dataclass
from typing import Any

from zephcast.core.consumers import ConsumerConfig, async_batch_consumer, async_consumer
from zephcast.rabbit.async_client import AsyncRabbitClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Shutdown flag for graceful termination
shutdown_event = asyncio.Event()

RABBITMQ_BASE_CONFIG = {
    "rabbitmq_url": "amqp://guest:guest@localhost:5672/",
    "exchange_name": "example_exchange",
    "exchange_type": "direct",
}

# Special message to indicate end of processing
POISON_PILL = "SHUTDOWN"

@dataclass
class Message:
    """Message structure for our application."""
    id: str
    type: str
    priority: int
    payload: dict[str, Any]
    retry_count: int = 0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        data = json.loads(json_str)
        return cls(**data)

async def setup_consumers() -> tuple:
    high_priority_client = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="high_priority_queue",
        queue_name="high_priority_queue",
    )
    await high_priority_client.connect()

    standard_priority_client = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="standard_priority_queue",
        queue_name="standard_priority_queue",
    )
    await standard_priority_client.connect()

    batch_client = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="batch_queue",
        queue_name="batch_queue",
    )
    await batch_client.connect()

    @async_consumer(  # type: ignore[func-returns-value]
        high_priority_client,
        config=ConsumerConfig(auto_ack=True)
    )
    async def handle_high_priority(message: str) -> None:
        if message == POISON_PILL:
            logger.info("High priority consumer received shutdown signal")
            return

        if shutdown_event.is_set():
            return

        msg = Message.from_json(message)
        logger.info(f"Processing high priority message: {msg.id}")
        await asyncio.sleep(0.2)  # Emulate faster processing for high priority
        logger.info(f"Completed high priority message: {msg.id}")

    @async_consumer(  # type: ignore[func-returns-value]
        standard_priority_client,
        config=ConsumerConfig(auto_ack=True)
    )
    async def handle_standard_priority(message: str) -> None:
        if message == POISON_PILL:
            logger.info("Standard priority consumer received shutdown signal")
            return

        if shutdown_event.is_set():
            return

        msg = Message.from_json(message)
        logger.info(f"Processing standard priority message: {msg.id}")
        await asyncio.sleep(0.5)
        logger.info(f"Completed standard priority message: {msg.id}")

    @async_batch_consumer(  # type: ignore[func-returns-value]
        batch_client,
        config=ConsumerConfig(
            auto_ack=True,
            batch_size=3,
            batch_timeout=1.0
        )
    )
    async def handle_batch(messages: list[str]) -> None:
        if POISON_PILL in messages:
            logger.info("Batch consumer received shutdown signal")
            return

        if shutdown_event.is_set():
            return

        for message in messages:
            msg = Message.from_json(message)
            logger.info(f"Processing batch message: {msg.id}")
            await asyncio.sleep(0.1)
        logger.info(f"Completed batch of {len(messages)} messages")

    return (
        handle_high_priority,
        handle_standard_priority,
        handle_batch,
        high_priority_client,
        standard_priority_client,
        batch_client
    )

async def send_test_messages() -> None:
    """Send test messages with different priorities."""
    high_priority_producer = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="high_priority_queue",
        queue_name="high_priority_queue",
    )
    standard_priority_producer = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="standard_priority_queue",
        queue_name="standard_priority_queue",
    )
    batch_producer = AsyncRabbitClient(
        **RABBITMQ_BASE_CONFIG,  # type: ignore[arg-type]
        stream_name="batch_queue",
        queue_name="batch_queue",
    )

    await asyncio.gather(
        high_priority_producer.connect(),
        standard_priority_producer.connect(),
        batch_producer.connect()
    )

    try:
        for i in range(10):
            if shutdown_event.is_set():
                break

            # Create message with priority
            priority = i % 3
            message = Message(
                id=f"msg-{i}",
                type="test",
                priority=priority,
                payload={"value": i}
            )

            # Route message based on priority
            if priority == 0:
                await high_priority_producer.send(message.to_json())
                logger.info(f"Sent high priority message: {message.id}")
            elif priority == 1:
                await standard_priority_producer.send(message.to_json())
                logger.info(f"Sent standard priority message: {message.id}")
            else:
                await batch_producer.send(message.to_json())
                logger.info(f"Sent batch message: {message.id}")

            await asyncio.sleep(0.5)

        logger.info("Sending shutdown signals to all queues")
        await high_priority_producer.send(POISON_PILL)
        await standard_priority_producer.send(POISON_PILL)
        await batch_producer.send(POISON_PILL)

    finally:
        await asyncio.gather(
            high_priority_producer.close(),
            standard_priority_producer.close(),
            batch_producer.close()
        )

def handle_shutdown(sig: Any = None, frame: Any = None) -> None:
    """Handle shutdown signals."""
    logger.info("Shutdown signal received, cleaning up...")
    shutdown_event.set()

async def main() -> None:
    """Run the example."""
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, handle_shutdown)

    try:
        (handle_high_priority,
         handle_standard_priority,
         handle_batch,
         high_priority_client,
         standard_priority_client,
         batch_client) = await setup_consumers()

        producer_task = asyncio.create_task(send_test_messages())

        consumer_tasks = [
            asyncio.create_task(handle_high_priority()),
            asyncio.create_task(handle_standard_priority()),
            asyncio.create_task(handle_batch())
        ]

        try:
            await producer_task
            await asyncio.sleep(2)

            # Force cancel all consumer tasks
            for task in consumer_tasks:
                if not task.done():
                    task.cancel()

            await asyncio.gather(*consumer_tasks, return_exceptions=True)
        except asyncio.CancelledError:
            logger.info("Tasks cancelled")
        finally:
            for task in [producer_task, *consumer_tasks]:
                if not task.done():
                    task.cancel()

            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        high_priority_client.close(),
                        standard_priority_client.close(),
                        batch_client.close()
                    ),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Client cleanup timed out")

            logger.info("All tasks cancelled and clients closed")

    except Exception as e:
        logger.exception("Unexpected error: %s", e)
    finally:
        logger.info("Shutdown complete")
        # Force exit if still hanging
        import sys
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

"""Integration tests for RabbitMQ clients."""

import asyncio
import logging
import uuid

import pytest

from zephcast.aio.rabbit import RabbitClient as AsyncRabbitClient
from zephcast.aio.rabbit.types import RabbitConfig
from zephcast.core.exceptions import ConnectionError

from .conftest import RABBITMQ_URL, TEST_TIMEOUT

logger = logging.getLogger(__name__)


class TestRabbitMQAsyncClient:
    """Integration tests for RabbitMQ async client."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_async_send_receive(self, rabbitmq_queue: str) -> None:
        """Test basic send and receive functionality."""
        test_messages = ["test1", "test2", "test3"]
        received_messages: list[str] = []
        routing_key = f"test-route-{uuid.uuid4()}"
        exchange_name = f"test-exchange-{uuid.uuid4()}"

        config = RabbitConfig(
            url=RABBITMQ_URL,
            queue_name=rabbitmq_queue,
            exchange_name=exchange_name,
            exchange_type="direct",
            exchange_durable=False,
            queue_durable=True,
            routing_key=routing_key,  # Add routing key to config
        )

        producer = AsyncRabbitClient(stream_name=routing_key, config=config)
        consumer = AsyncRabbitClient(stream_name=routing_key, config=config)

        try:
            await producer.connect()
            await consumer.connect()

            if producer._connection is None:
                raise RuntimeError("Connection not established")

            channel = await producer._connection.channel()
            await channel.declare_exchange(
                exchange_name, type=config.exchange_type, durable=config.exchange_durable
            )
            queue = await channel.declare_queue(rabbitmq_queue, durable=config.queue_durable)
            await queue.bind(exchange=exchange_name, routing_key=routing_key)
            await channel.close()

            await asyncio.sleep(1)  # Reduced sleep time

            for message in test_messages:
                await producer.send(message)

            async def receive_messages() -> None:
                async for message, _ in consumer.receive():
                    received_messages.append(str(message))
                    if len(received_messages) == len(test_messages):
                        break

            try:
                await asyncio.wait_for(receive_messages(), timeout=10.0)
            except asyncio.TimeoutError:
                msg = f"Received {len(received_messages)} of {len(test_messages)}"
                pytest.fail(f"Timeout waiting for messages. {msg}")

            assert sorted(received_messages) == sorted(test_messages)

        finally:
            await asyncio.gather(producer.close(), consumer.close(), return_exceptions=True)

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_consumer_groups(self, rabbitmq_queue: str) -> None:
        """Test consumer group functionality."""
        test_messages = ["test1", "test2", "test3", "test4"]
        received_messages: list[str] = []
        routing_key = f"test-route-{uuid.uuid4()}"
        exchange_name = f"test-exchange-{uuid.uuid4()}"

        config = RabbitConfig(
            url=RABBITMQ_URL,
            queue_name=rabbitmq_queue,
            exchange_name=exchange_name,
            exchange_type="direct",
            exchange_durable=False,
            queue_durable=True,
        )

        producer = AsyncRabbitClient(stream_name=routing_key, config=config)
        consumer = AsyncRabbitClient(stream_name=routing_key, config=config)

        try:
            await producer.connect()
            await consumer.connect()

            await asyncio.sleep(1)

            receive_task = asyncio.create_task(
                self._receive_messages(consumer, received_messages, len(test_messages))
            )

            for message in test_messages:
                await producer.send(message)

            try:
                await asyncio.wait_for(receive_task, timeout=10.0)
            except asyncio.TimeoutError:
                msg = f"Received {len(received_messages)} of {len(test_messages)}"
                pytest.fail(f"Timeout waiting for messages. {msg}")

            assert sorted(received_messages) == sorted(test_messages)

        finally:
            await asyncio.gather(producer.close(), consumer.close(), return_exceptions=True)

    async def _receive_messages(
        self, consumer: AsyncRabbitClient, messages: list[str], expected_count: int
    ) -> None:
        """Helper method to receive messages until expected count is reached."""
        async for message, _ in consumer.receive():
            messages.append(str(message))
            if len(messages) >= expected_count:
                break

    @pytest.mark.asyncio
    @pytest.mark.timeout(5)
    async def test_error_handling(self, rabbitmq_queue: str) -> None:
        """Test error handling with invalid connection."""
        config = RabbitConfig(
            url="amqp://guest:guest@invalid:5672/",
            queue_name=rabbitmq_queue,
            exchange_name="test-exchange",
            exchange_type="direct",
            exchange_durable=False,
        )
        client = AsyncRabbitClient(stream_name="test-route", config=config)

        # For invalid connection tests, we don't even try to clean up
        # Just verify it raises the right error
        with pytest.raises(ConnectionError):
            await client.connect()

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_multiple_consumers(self, rabbitmq_queue: str) -> None:
        """Test multiple consumers receiving messages."""
        test_messages = ["test1", "test2", "test3"]
        received_messages: list[str] = []
        routing_key = f"test-route-{uuid.uuid4()}"
        exchange_name = f"test-exchange-{uuid.uuid4()}"

        config = RabbitConfig(
            url=RABBITMQ_URL,
            queue_name=rabbitmq_queue,
            exchange_name=exchange_name,
            exchange_type="direct",
            exchange_durable=False,
            queue_durable=True,
        )

        producer = AsyncRabbitClient(stream_name=routing_key, config=config)
        consumer1 = AsyncRabbitClient(stream_name=routing_key, config=config)
        consumer2 = AsyncRabbitClient(stream_name=routing_key, config=config)

        try:
            await producer.connect()
            await consumer1.connect()
            await consumer2.connect()

            await asyncio.sleep(1)

            receive_task1 = asyncio.create_task(
                self._receive_messages(consumer1, received_messages, len(test_messages))
            )
            receive_task2 = asyncio.create_task(
                self._receive_messages(consumer2, received_messages, len(test_messages))
            )

            for message in test_messages:
                await producer.send(message)
                await asyncio.sleep(0.1)

            try:
                done, pending = await asyncio.wait(
                    [receive_task1, receive_task2],
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=10.0,
                )

                for task in pending:
                    task.cancel()

                if not done:
                    msg = f"Received {len(received_messages)} of {len(test_messages)}"
                    pytest.fail(f"Timeout waiting for messages. {msg}")

            except asyncio.TimeoutError:
                msg = f"Received {len(received_messages)} of {len(test_messages)}"
                pytest.fail(f"Timeout waiting for messages. {msg}")

            assert sorted(received_messages) == sorted(test_messages)

        finally:
            await asyncio.gather(
                producer.close(), consumer1.close(), consumer2.close(), return_exceptions=True
            )

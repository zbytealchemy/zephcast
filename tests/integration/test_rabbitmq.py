"""Integration tests for RabbitMQ clients."""

import asyncio
import uuid

import pytest

from aio_pika.exceptions import AMQPConnectionError

from zephcast.rabbit.async_client import AsyncRabbitClient

from .conftest import RABBITMQ_URL, TEST_TIMEOUT


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

        client = AsyncRabbitClient(
            stream_name=routing_key,
            queue_name=rabbitmq_queue,
            rabbitmq_url=RABBITMQ_URL,
            exchange_name=exchange_name,
            exchange_type="direct",
            exchange_durable=False,
        )
        await client.connect()

        try:
            for message in test_messages:
                await client.send(message)
                await asyncio.sleep(0.1)

            async for message in client.receive():
                received_messages.append(message)
                if len(received_messages) == len(test_messages):
                    break

            assert len(received_messages) == len(test_messages)
            assert sorted(received_messages) == sorted(test_messages)

        finally:
            await asyncio.wait_for(client.close(), timeout=1)

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_consumer_groups(self, rabbitmq_queue: str) -> None:
        """Test consumer group functionality."""
        test_messages = ["test1", "test2", "test3", "test4"]
        consumers: list[AsyncRabbitClient] = []
        received_messages: list[list[str]] = [[], []]
        routing_key = f"test-route-{uuid.uuid4()}"
        exchange_name = f"test-exchange-{uuid.uuid4()}"

        producer = AsyncRabbitClient(
            stream_name=routing_key,
            queue_name=rabbitmq_queue,
            rabbitmq_url=RABBITMQ_URL,
            exchange_name=exchange_name,
            exchange_type="direct",
            exchange_durable=False,
        )
        await producer.connect()

        try:
            for _ in range(2):
                consumer = AsyncRabbitClient(
                    stream_name=routing_key,
                    queue_name=rabbitmq_queue,
                    rabbitmq_url=RABBITMQ_URL,
                    exchange_name=exchange_name,
                    exchange_type="direct",
                    exchange_durable=False,
                )
                await consumer.connect()
                consumers.append(consumer)

            await asyncio.sleep(1)

            for message in test_messages:
                await producer.send(message)
                await asyncio.sleep(0.1)

            await asyncio.sleep(1)

            async def consume(consumer: AsyncRabbitClient, messages: list[str]) -> None:
                start_time = asyncio.get_event_loop().time()
                timeout = 1.0
                try:
                    while True:
                        if asyncio.get_event_loop().time() - start_time > timeout:
                            break
                        try:

                            async def _consume() -> None:
                                async for msg in consumer.receive():
                                    messages.append(msg)
                                    await asyncio.sleep(0)

                            await asyncio.wait_for(_consume(), timeout=1.0)
                        except asyncio.TimeoutError:
                            if len(messages) >= len(test_messages) // 2:
                                break
                            continue
                        except Exception as e:
                            pytest.fail(f"Consumer failed: {e}")
                except Exception as e:
                    pytest.fail(f"Consumer failed: {e}")

            await asyncio.gather(
                consume(consumers[0], received_messages[0]),
                consume(consumers[1], received_messages[1]),
            )

            all_received = received_messages[0] + received_messages[1]
            assert len(all_received) == len(
                test_messages
            ), f"Expected {len(test_messages)} messages, got {len(all_received)}"
            assert sorted(all_received) == sorted(
                test_messages
            ), f"Messages don't match. Expected {test_messages}, got {all_received}"

        finally:
            for consumer in consumers:
                try:
                    await asyncio.wait_for(consumer.close(), timeout=1)
                except Exception as e:
                    print(f"Warning: Failed to close consumer: {e}")
            try:
                await asyncio.wait_for(producer.close(), timeout=1)
            except Exception as e:
                print(f"Warning: Failed to close producer: {e}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(5)
    async def test_error_handling(self, rabbitmq_queue: str) -> None:
        """Test error handling with invalid connection."""
        client = AsyncRabbitClient(
            stream_name="test-route",
            queue_name=rabbitmq_queue,
            rabbitmq_url="amqp://guest:guest@invalid:5672/",
            exchange_name="test-exchange",
            exchange_type="direct",
            exchange_durable=False,
        )

        with pytest.raises(AMQPConnectionError):
            await client.connect()

        await client.close()

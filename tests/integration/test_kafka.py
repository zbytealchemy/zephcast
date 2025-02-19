"""Integration tests for Kafka clients."""

import asyncio
import uuid

from typing import cast

import pytest

from zephcast.aio.kafka import KafkaClient as AsyncKafkaClient
from zephcast.aio.kafka.types import KafkaConfig
from zephcast.core.exceptions import ConnectionError

from .conftest import KAFKA_BOOTSTRAP_SERVERS, TEST_TIMEOUT


class TestKafkaAsyncClient:
    """Integration tests for Kafka async client."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_async_send_receive(self, kafka_async_client: AsyncKafkaClient, kafka_topic: str) -> None:
        """Test basic send and receive functionality."""
        test_messages = ["test1", "test2", "test3"]
        received_messages: list[str] = []

        client = kafka_async_client
        try:
            await client.connect()

            for message in test_messages:
                await client.send(message)

            async for msg, _ in client.receive():
                message_text = cast(str, msg)
                received_messages.append(message_text)
                if len(received_messages) == len(test_messages):
                    break

            assert sorted(received_messages) == sorted(test_messages)

        except Exception as e:
            pytest.fail(f"Test failed: {e}")
        finally:
            try:
                await client.close()
            except Exception as e:
                pytest.fail(f"Failed to close client: {e}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_consumer_groups(self, kafka_topic: str) -> None:
        """Test consumer group functionality with just 2 consumers."""
        test_messages = ["test1", "test2", "test3", "test4"]
        group_id = f"test-group-{uuid.uuid4()}"
        consumers: list[AsyncKafkaClient] = []
        received_messages: list[list[str]] = [[], []]

        producer = AsyncKafkaClient(
            stream_name=kafka_topic,
            connection_config=KafkaConfig(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS),
        )
        await producer.connect()

        timeout = 1

        try:
            for _ in range(2):
                consumer = AsyncKafkaClient(
                    stream_name=kafka_topic,
                    connection_config=KafkaConfig(
                        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                        group_id=group_id,
                        auto_offset_reset="earliest",
                    ),
                )
                await consumer.connect()
                consumers.append(consumer)

            await asyncio.sleep(2)

            for message in test_messages:
                await producer.send(message)
                await asyncio.sleep(0.1)

            await asyncio.sleep(1)

            async def consume(consumer: AsyncKafkaClient, messages: list[str]) -> None:
                start_time = asyncio.get_event_loop().time()
                try:
                    while True:
                        if asyncio.get_event_loop().time() - start_time > timeout:
                            break
                        try:

                            async def _consume() -> None:
                                async for msg in consumer.receive():
                                    msg_text, _ = msg
                                    messages.append(msg_text)  # type: ignore
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
    async def test_error_handling(self, kafka_topic: str) -> None:
        """Test error handling in the presence of invalid Kafka brokers."""
        client = AsyncKafkaClient(
            stream_name=kafka_topic, connection_config=KafkaConfig(bootstrap_servers="invalid:9092")
        )

        # For invalid connection tests, we don't even try to clean up
        # Just verify it raises the right error
        with pytest.raises(ConnectionError):
            await client.connect()

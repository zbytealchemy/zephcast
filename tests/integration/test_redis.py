"""Integration tests for Redis clients."""

import asyncio

import pytest

from zephyrflow.redis.async_client import AsyncRedisClient
from zephyrflow.redis.sync_client import SyncRedisClient

from .conftest import REDIS_URL


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_redis_async_send_receive(redis_async_client: AsyncRedisClient) -> None:
    """Test basic send and receive functionality."""

    test_messages = ["test1", "test2", "test3"]
    received_messages: list[str] = []

    async for client in redis_async_client:
        for message in test_messages:
            await client.send(message)  # type: ignore

        async for message in client.receive():  # type: ignore
            received_messages.append(message)
            if len(received_messages) == len(test_messages):
                break

        assert len(received_messages) == len(test_messages)
        assert sorted(received_messages) == sorted(test_messages)


@pytest.mark.timeout(30)
def test_redis_sync_send_receive(
    redis_sync_client: SyncRedisClient,
) -> None:
    """Test basic send and receive functionality."""
    test_messages = ["test1", "test2", "test3"]
    received_messages: list[str] = []

    for message in test_messages:
        redis_sync_client.send(message)

    for message in redis_sync_client.receive():
        received_messages.append(message)
        if len(received_messages) == len(test_messages):
            break

    assert len(received_messages) == len(test_messages)
    assert sorted(received_messages) == sorted(test_messages)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_redis_async_multiple_consumers(redis_stream: str) -> None:
    """Test multiple Redis consumers."""

    test_messages = ["test1", "test2", "test3"]
    consumer_count = 3
    consumers: list[AsyncRedisClient] = []
    received_messages: list[list[str]] = [[] for _ in range(consumer_count)]

    producer = AsyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
    await producer.connect()

    for _ in range(consumer_count):
        consumer = AsyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
        await consumer.connect()
        consumers.append(consumer)

    try:
        for message in test_messages:
            await producer.send(message)

        async def consume_messages(client: AsyncRedisClient, messages: list[str]) -> None:
            async for message in client.receive():
                messages.append(message)
                if len(messages) >= len(test_messages):
                    break

        await asyncio.gather(
            *[
                consume_messages(consumer, messages)
                for consumer, messages in zip(consumers, received_messages)
            ]
        )

        for consumer_messages in received_messages:
            assert len(consumer_messages) == len(test_messages)
            assert sorted(consumer_messages) == sorted(test_messages)

    finally:
        await producer.close()
        for consumer in consumers:
            await consumer.close()

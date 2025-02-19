"""Integration tests for Redis clients."""

import asyncio

from typing import Any, cast

import pytest

from zephcast.aio.redis import RedisClient as AsyncRedisClient
from zephcast.aio.redis.types import RedisConfig
from zephcast.sync.redis import RedisClient as SyncRedisClient

from .conftest import REDIS_URL


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_redis_async_send_receive(redis_async_client: AsyncRedisClient) -> None:
    """Test basic send and receive functionality."""
    test_messages = ["test1", "test2", "test3"]
    received_messages: list[str] = []

    for message in test_messages:
        await redis_async_client.send(message)

    async for msg, _ in redis_async_client.receive():
        message_text = cast(str, msg)
        received_messages.append(message_text)
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

    for message, _ in redis_sync_client.receive():
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
    received_messages: list[list[Any]] = [[] for _ in range(consumer_count)]

    config = RedisConfig(redis_url=REDIS_URL)
    producer = AsyncRedisClient(stream_name=redis_stream, config=config)
    await producer.connect()

    for _ in range(consumer_count):
        consumer = AsyncRedisClient(stream_name=redis_stream, config=config)
        await consumer.connect()
        consumers.append(consumer)

    try:
        for message in test_messages:
            await producer.send(message)

        async def consume_messages(client: AsyncRedisClient, messages: list[Any]) -> None:
            async for message in client.receive():
                message_text, _ = message
                messages.append(message_text)
                if len(messages) >= len(test_messages):
                    break

        await asyncio.gather(
            *[
                consume_messages(consumer, messages)
                for consumer, messages in zip(consumers, received_messages)
            ]
        )

        for messages in received_messages:
            assert len(messages) == len(test_messages)
            assert sorted(messages) == sorted(test_messages)

    finally:
        await producer.close()
        for consumer in consumers:
            await consumer.close()

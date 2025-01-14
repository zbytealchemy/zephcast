"""Integration tests for Redis clients."""

import asyncio

from typing import List

import pytest

from msgflow.redis.async_client import AsyncRedisClient

from .conftest import REDIS_URL, TEST_TIMEOUT


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
async def test_redis_async_send_receive(redis_async_client) -> None:
    test_messages = ["test1", "test2", "test3"]
    received_messages: List[str] = []

    async for client in redis_async_client:
        for message in test_messages:
            await client.send(message)

        async for message in client.receive():
            received_messages.append(message)
            if len(received_messages) == len(test_messages):
                break

        assert len(received_messages) == len(test_messages)
        assert sorted(received_messages) == sorted(test_messages)


@pytest.mark.timeout(TEST_TIMEOUT)
def test_redis_sync_send_receive(redis_sync_client) -> None:
    test_messages = ["test1", "test2", "test3"]
    received_messages: List[str] = []

    for message in test_messages:
        redis_sync_client.send(message)

    for message in redis_sync_client.receive():
        received_messages.append(message)
        if len(received_messages) == len(test_messages):
            break

    assert len(received_messages) == len(test_messages)
    assert sorted(received_messages) == sorted(test_messages)


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
async def test_redis_async_multiple_consumers(redis_stream) -> None:
    test_messages = ["test1", "test2", "test3"]
    consumer_count = 3
    consumers: List[AsyncRedisClient] = []
    received_messages: List[List[str]] = [[] for _ in range(consumer_count)]

    producer = AsyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
    await producer.connect()

    for _ in range(consumer_count):
        consumer = AsyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
        await consumer.connect()
        consumers.append(consumer)

    try:
        for message in test_messages:
            await producer.send(message)

        async def consume_messages(client: AsyncRedisClient, messages: List[str]) -> None:
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

"""Unit tests for asynchronous Redis client."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from zephcast.aio.redis.client import RedisClient
from zephcast.aio.redis.types import RedisConfig


@pytest.mark.asyncio
async def test_redis_client_connect() -> None:
    """Test async Redis client connection."""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True

    async def mock_from_url(*args: Any, **kwargs: Any) -> Any:
        return mock_client

    with patch("redis.asyncio.Redis.from_url", mock_from_url):
        config = RedisConfig(redis_url="redis://localhost:6379")
        client = RedisClient(stream_name="test-stream", config=config)

        try:
            await client.connect()
            assert client._connected
            mock_client.ping.assert_awaited_once()
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_redis_client_send() -> None:
    """Test sending message through async Redis client."""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True
    mock_client.xadd.return_value = "1-0"

    async def mock_from_url(*args: Any, **kwargs: Any) -> Any:
        return mock_client

    with patch("redis.asyncio.Redis.from_url", mock_from_url):
        config = RedisConfig(redis_url="redis://localhost:6379")
        client = RedisClient(stream_name="test-stream", config=config)

        message = "test message"

        try:
            await client.connect()
            await client.send(message)
            mock_client.xadd.assert_awaited_once_with("test-stream", {"data": message})
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_redis_client_connect_error() -> None:
    """Test Redis client connection error handling."""

    async def mock_from_url(*args: Any, **kwargs: Any) -> Any:
        raise ConnectionError("Failed to connect")

    with patch("redis.asyncio.Redis.from_url", mock_from_url):
        config = RedisConfig(redis_url="redis://invalid:6379")
        client = RedisClient(stream_name="test-stream", config=config)

        with pytest.raises(ConnectionError):
            await client.connect()

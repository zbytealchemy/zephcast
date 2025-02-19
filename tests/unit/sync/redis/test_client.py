"""Unit tests for synchronous Redis client."""
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from zephcast.sync.redis.client import RedisClient
from zephcast.sync.redis.types import RedisConfig
from zephcast.testing.helpers import assert_messages_equal, create_mock_client
from zephcast.testing.sync.mock_client import MockSyncClient


@pytest.fixture
def mock_redis_client() -> MockSyncClient:
    """Create a mock Redis client for testing."""
    config = RedisConfig(redis_url="redis://localhost:6379")
    return cast(MockSyncClient, create_mock_client(stream_name="test-stream", is_async=False, config=config))


@pytest.fixture
def redis_client() -> RedisClient:
    """Create a Redis client instance."""
    config = RedisConfig(redis_url="redis://localhost:6379")
    return RedisClient(stream_name="test-stream", config=config)


@patch("redis.Redis.from_url")
def test_real_redis_client_connect(mock_from_url: MagicMock, redis_client: RedisClient) -> None:
    """Test Redis client connection."""
    mock_redis = MagicMock()
    mock_from_url.return_value = mock_redis

    redis_client.connect()
    assert redis_client.redis_client is not None
    mock_from_url.assert_called_once_with("redis://localhost:6379")


@patch("redis.Redis.from_url")
def test_real_redis_client_send(mock_from_url: MagicMock, redis_client: RedisClient) -> None:
    """Test Redis client send operation."""
    mock_redis = MagicMock()
    mock_from_url.return_value = mock_redis

    redis_client.connect()
    redis_client.send("test message")

    mock_redis.xadd.assert_called_once_with(b"test-stream", {"data": "test message"})


@patch("redis.Redis.from_url")
def test_real_redis_client_receive(mock_from_url: MagicMock, redis_client: RedisClient) -> None:
    """Test Redis client receive operation."""
    mock_redis = MagicMock()
    mock_redis.xread.side_effect = [
        [[b"test-stream", [(b"1234567-0", {b"data": b"test message"})]]],
        None,
    ]
    mock_from_url.return_value = mock_redis

    redis_client.connect()
    messages = []
    metadata_list = []
    for message, metadata in redis_client.receive():
        messages.append(message)
        metadata_list.append(metadata)
        break

    assert messages == ["test message"]
    assert metadata_list[0].message_id == "1234567-0"
    assert metadata_list[0].timestamp == 1234.567

    mock_redis.xread.assert_called_with({b"test-stream": b"0"}, count=1, block=1000)


def test_real_redis_client_send_not_connected(redis_client: RedisClient) -> None:
    """Test send operation when not connected."""
    with pytest.raises(RuntimeError, match="Redis connection not established"):
        redis_client.send("test")


def test_real_redis_client_receive_not_connected(redis_client: RedisClient) -> None:
    """Test receive operation when not connected."""
    with pytest.raises(RuntimeError, match="Redis connection not established"):
        next(redis_client.receive())


@patch("redis.Redis.from_url")
def test_real_redis_client_close(mock_from_url: MagicMock, redis_client: RedisClient) -> None:
    """Test Redis client close operation."""
    mock_redis = MagicMock()
    mock_from_url.return_value = mock_redis

    redis_client.connect()
    redis_client.close()

    mock_redis.close.assert_called_once()
    assert redis_client.redis_client is None


def test_real_redis_client_context_manager() -> None:
    """Test Redis client context manager."""
    config = RedisConfig(redis_url="redis://localhost:6379")
    client = cast(
        MockSyncClient, create_mock_client(stream_name="test-stream", is_async=False, config=config)
    )

    with client:
        assert client._connected
    assert not client._connected


def test_real_redis_client_connection_error() -> None:
    """Test Redis client connection error."""
    config = RedisConfig(redis_url="redis://localhost:6379")
    client = MockSyncClient(
        stream_name="test-stream",
        config=config,
        raise_on_connect=True,
    )

    with pytest.raises(RuntimeError, match="Connection failed"):
        client.connect()


def test_redis_client_connect(mock_redis_client: MockSyncClient) -> None:
    """Test Redis client connection."""
    with mock_redis_client:
        assert mock_redis_client._connected


def test_redis_client_send(mock_redis_client: MockSyncClient) -> None:
    """Test sending message through Redis client."""
    with mock_redis_client:
        mock_redis_client.send("test message")
        assert_messages_equal(mock_redis_client.sent_messages, ["test message"])


def test_redis_client_receive() -> None:
    """Test receiving messages through Redis client."""
    test_messages = ["test1", "test2"]
    config = RedisConfig(redis_url="redis://localhost:6379")
    client = cast(
        MockSyncClient,
        create_mock_client("test-stream", is_async=False, config=config, received_messages=test_messages),
    )

    with client:
        received = []
        for msg in client.receive():
            received.append(msg)
            if len(received) == len(test_messages):
                break

    assert_messages_equal(received, test_messages)


def test_redis_client_config() -> None:
    """Test Redis client configuration."""
    config = RedisConfig(redis_url="redis://localhost:6379")
    client = cast(
        MockSyncClient, create_mock_client(stream_name="test-stream", is_async=False, config=config)
    )

    assert client.stream_name == "test-stream"
    assert client.connection_config["url"] == "mock://localhost"

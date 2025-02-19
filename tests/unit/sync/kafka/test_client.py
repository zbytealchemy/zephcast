"""Unit tests for synchronous Kafka client."""
from typing import TYPE_CHECKING

import pytest

from zephcast.testing.sync.mock_client import MockSyncClient

if TYPE_CHECKING:
    from zephcast.core.types import ConnectionConfig


@pytest.fixture
def kafka_client() -> MockSyncClient:
    """Create a mock Kafka client for testing."""
    config: "ConnectionConfig" = {
        "bootstrap_servers": "localhost:9092",
        "group_id": "test-group",
        "client_id": "test-client",
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
    }
    client = MockSyncClient(stream_name="test-topic", connection_config=config)
    return client


def test_kafka_client_connect(kafka_client: MockSyncClient) -> None:
    """Test Kafka client connection."""
    kafka_client.connect()
    assert kafka_client._connected


def test_kafka_client_connect_already_connected(kafka_client: MockSyncClient) -> None:
    """Test connecting when already connected."""
    kafka_client.connect()
    kafka_client.connect()
    assert kafka_client._connected


def test_kafka_client_close(kafka_client: MockSyncClient) -> None:
    """Test Kafka client close."""
    kafka_client.connect()
    kafka_client.close()
    assert not kafka_client._connected


def test_kafka_client_send(kafka_client: MockSyncClient) -> None:
    """Test sending message through Kafka client."""
    with kafka_client:
        kafka_client.send("test message")
        assert "test message" in kafka_client.sent_messages


def test_kafka_client_send_not_connected(kafka_client: MockSyncClient) -> None:
    """Test send operation when not connected."""
    with pytest.raises(RuntimeError, match="Client not connected"):
        kafka_client.send("test message")


def test_kafka_client_receive() -> None:
    """Test receiving messages through Kafka client."""
    test_messages = ["message1", "message2"]
    client = MockSyncClient(stream_name="test-topic", received_messages=test_messages)

    received = []
    with client:
        for message in client.receive():
            received.append(message)

    assert received == test_messages


def test_kafka_client_receive_not_connected(kafka_client: MockSyncClient) -> None:
    """Test receive operation when not connected."""
    with pytest.raises(RuntimeError, match="Client not connected"):
        next(kafka_client.receive())


def test_kafka_client_context_manager(kafka_client: MockSyncClient) -> None:
    """Test Kafka client context manager."""
    assert not kafka_client._connected

    with kafka_client:
        kafka_client.send("test message")
        assert kafka_client._connected
        assert "test message" in kafka_client.sent_messages  # type: ignore[unreachable]

    assert not kafka_client._connected  # type: ignore[unreachable]


def test_kafka_client_connection_error() -> None:
    """Test Kafka client connection error."""
    config: "ConnectionConfig" = {"raise_on_connect": True}
    client = MockSyncClient(stream_name="test-topic", connection_config=config)

    with pytest.raises(RuntimeError, match="Connection failed"):
        client.connect()

    assert not client._connected

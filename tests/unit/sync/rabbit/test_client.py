"""Unit tests for synchronous RabbitMQ client."""
from typing import cast
from unittest.mock import MagicMock, patch

import pika
import pytest

from zephcast.sync.rabbit.client import RabbitClient
from zephcast.sync.rabbit.types import RabbitConfig
from zephcast.testing.helpers import assert_messages_equal, create_mock_client
from zephcast.testing.sync.mock_client import MockSyncClient


@pytest.fixture
def rabbit_client() -> MockSyncClient:
    """Create a mock RabbitMQ client for testing."""
    config = RabbitConfig(
        url="amqp://guest:guest@localhost:5672/",
        queue_name="test-queue",
        exchange_name="test-exchange",
        exchange_type="direct",
        exchange_durable=True,
    )
    config_dict = {
        "url": config.url,
        "queue_name": config.queue_name,
        "exchange_name": config.exchange_name,
        "exchange_type": config.exchange_type,
        "exchange_durable": config.exchange_durable,
    }
    client = create_mock_client(stream_name="test-exchange", is_async=False, connection_config=config_dict)
    return cast(MockSyncClient, client)


@pytest.fixture
def real_rabbit_client() -> RabbitClient:
    """Create a real RabbitMQ client for testing with mocked internals."""
    config = RabbitConfig(
        url="amqp://guest:guest@localhost:5672/",
        queue_name="test-queue",
        exchange_name="test-exchange",
        exchange_type="direct",
        exchange_durable=True,
    )
    return RabbitClient(stream_name="test-routing-key", config=config)


def test_rabbit_client_init(rabbit_client: MockSyncClient) -> None:
    """Test RabbitMQ client initialization."""
    assert rabbit_client.stream_name == "test-exchange"
    assert rabbit_client.connection_config["exchange_name"] == "test-exchange"
    assert rabbit_client.connection_config["exchange_type"] == "direct"
    assert rabbit_client.connection_config["queue_name"] == "test-queue"


def test_rabbit_client_connect(rabbit_client: MockSyncClient) -> None:
    """Test RabbitMQ client connection."""
    with rabbit_client:
        assert rabbit_client._connected

    assert not rabbit_client._connected


@patch("pika.BlockingConnection")
def test_real_rabbit_client_connect(mock_connection: MagicMock, real_rabbit_client: RabbitClient) -> None:
    """Test real RabbitMQ client connection with mocked components."""
    mock_channel = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_connection_instance

    with real_rabbit_client:
        assert real_rabbit_client._connected
        assert real_rabbit_client._connection is not None
        assert real_rabbit_client._channel is not None

        mock_connection.assert_called_once()
        args = mock_connection.call_args[0]
        assert isinstance(args[0], pika.URLParameters)
        assert args[0].host == "localhost"
        assert args[0].port == 5672

        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test-exchange", exchange_type="direct", durable=True
        )

        mock_channel.queue_bind.assert_called_once_with(
            queue="test-queue", exchange="test-exchange", routing_key="test-routing-key"
        )


@patch("pika.BlockingConnection")
def test_real_rabbit_client_send(mock_connection: MagicMock, real_rabbit_client: RabbitClient) -> None:
    """Test sending message through real RabbitMQ client."""

    mock_channel = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_connection_instance

    with real_rabbit_client:
        test_message = "test message"
        real_rabbit_client.send(test_message)

        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args[1]
        assert call_kwargs["exchange"] == "test-exchange"
        assert call_kwargs["routing_key"] == "test-routing-key"
        assert call_kwargs["body"] == test_message.encode()
        assert isinstance(call_kwargs["properties"], pika.BasicProperties)
        assert call_kwargs["properties"].delivery_mode == 2  # persistent


@patch("pika.BlockingConnection")
def test_real_rabbit_client_receive(mock_connection: MagicMock, real_rabbit_client: RabbitClient) -> None:
    """Test receiving messages through real RabbitMQ client."""
    mock_channel = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_connection_instance

    mock_method1 = MagicMock()
    mock_method1.delivery_tag = 1
    mock_properties1 = MagicMock()
    mock_properties1.message_id = "msg1"
    mock_properties1.timestamp = 1000.0

    mock_method2 = MagicMock()
    mock_method2.delivery_tag = 2
    mock_properties2 = MagicMock()
    mock_properties2.message_id = "msg2"
    mock_properties2.timestamp = 2000.0

    mock_channel.basic_get.side_effect = [
        (mock_method1, mock_properties1, b"test1"),
        (mock_method2, mock_properties2, b"test2"),
        (None, None, None),
    ]

    with real_rabbit_client:
        received = []
        for msg, metadata in real_rabbit_client.receive():
            received.append(msg)
            assert metadata.message_id in ("msg1", "msg2")
            assert metadata.delivery_tag in (1, 2)
            assert metadata.timestamp in (1000.0, 2000.0)
            if len(received) == 2:
                break

        assert received == ["test1", "test2"]
        assert mock_channel.basic_get.call_count == 2
        mock_channel.basic_get.assert_called_with(queue="test-queue", auto_ack=True)


def test_rabbit_client_send_receive(rabbit_client: MockSyncClient) -> None:
    """Test sending and receiving messages."""
    test_messages = ["test1", "test2"]

    client = cast(
        MockSyncClient,
        create_mock_client(
            stream_name="test-exchange",
            is_async=False,
            connection_config=rabbit_client.connection_config,
            received_messages=test_messages.copy(),
        ),
    )

    with client:
        for msg in test_messages:
            client.send(msg)

        received = []
        for msg in client.receive():
            received.append(msg)
            if len(received) == len(test_messages):
                break

        assert_messages_equal(received, test_messages)


def test_rabbit_client_not_connected(rabbit_client: MockSyncClient) -> None:
    """Test operations on non-connected client."""
    with pytest.raises(RuntimeError, match="Client not connected"):
        rabbit_client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        next(rabbit_client.receive())


@patch("pika.BlockingConnection")
def test_real_rabbit_client_close(mock_connection: MagicMock, real_rabbit_client: RabbitClient) -> None:
    """Test closing real RabbitMQ client connections."""
    mock_channel = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_connection_instance

    with real_rabbit_client:
        pass

    mock_channel.close.assert_called_once()
    mock_connection_instance.close.assert_called_once()
    assert real_rabbit_client._channel is None
    assert real_rabbit_client._connection is None
    assert not real_rabbit_client._connected


@patch("pika.BlockingConnection")
def test_real_rabbit_client_no_exchange(mock_connection: MagicMock, real_rabbit_client: RabbitClient) -> None:
    """Test RabbitMQ client without exchange configuration."""
    real_rabbit_client.config = RabbitConfig(
        url=real_rabbit_client.config.url,
        queue_name=real_rabbit_client.config.queue_name,
        exchange_name=None,
        exchange_type=real_rabbit_client.config.exchange_type,
        exchange_durable=real_rabbit_client.config.exchange_durable,
    )

    mock_channel = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_connection_instance

    with real_rabbit_client:
        mock_channel.exchange_declare.assert_not_called()

        mock_channel.queue_declare.assert_called_once_with("test-queue", durable=True)
        mock_channel.queue_bind.assert_called_once_with(
            queue="test-queue",
            exchange="",
            routing_key="test-routing-key",
        )

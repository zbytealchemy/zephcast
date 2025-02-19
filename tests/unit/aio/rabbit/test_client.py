"""Unit tests for asynchronous RabbitMQ client."""
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from zephcast.aio.rabbit.client import RabbitClient
from zephcast.aio.rabbit.types import RabbitConfig
from zephcast.core.exceptions import ConnectionError


class AsyncContextManagerMock(AsyncMock):
    """Mock for async context managers."""

    async def __aenter__(self) -> Any:
        return self.return_value

    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.mark.asyncio
async def test_rabbit_client_close() -> None:
    """Test closing RabbitMQ client."""
    config = RabbitConfig(
        url="amqp://localhost:5672",
        queue_name="test-queue",
        exchange_name="test-exchange",
        exchange_type="direct",
        exchange_durable=True,
        use_pool=False,
    )
    rabbit_client = RabbitClient("test-stream", config)

    mock_connection = AsyncMock(spec=AbstractConnection)
    mock_channel = AsyncMock(spec=AbstractChannel)
    mock_queue = AsyncMock(spec=AbstractQueue)
    mock_exchange = AsyncMock()

    mock_channel.default_exchange = mock_exchange
    mock_channel.declare_queue.return_value = mock_queue
    mock_channel.declare_exchange.return_value = mock_exchange

    mock_connection.channel = AsyncMock(return_value=mock_channel)

    mock_connection.connect = AsyncMock(return_value=None)

    with patch.object(
        rabbit_client, "_create_connection", AsyncMock(return_value=mock_connection)
    ), patch.object(rabbit_client, "_create_channel", AsyncMock(return_value=mock_channel)):
        await rabbit_client.connect()

        with patch("asyncio.current_task", return_value=None), patch("asyncio.all_tasks", return_value=set()):
            await rabbit_client.close()

        mock_connection.close.assert_called_once()
        assert not rabbit_client.is_connected


@pytest.mark.asyncio
async def test_rabbit_client_connection_error() -> None:
    """Test RabbitMQ client connection error."""
    config = RabbitConfig(
        url="amqp://localhost:5672",
        queue_name="test-queue",
        exchange_name="test-exchange",
        exchange_type="direct",
        exchange_durable=True,
        use_pool=False,
    )
    client = RabbitClient("test-stream", config)

    async def raise_error(*args: Any, **kwargs: Any) -> None:
        raise ConnectionError("Connection failed")

    with patch.object(client, "_create_connection", side_effect=raise_error):
        with pytest.raises(ConnectionError) as exc_info:
            await client.connect()
        assert "Failed to connect to RabbitClient" in str(exc_info.value)
        assert not client.is_connected


@pytest.mark.asyncio
async def test_rabbit_client_not_connected() -> None:
    """Test operations on non-connected client."""
    client = RabbitClient(
        stream_name="test-stream",
        config=RabbitConfig(
            url="amqp://localhost:5672",
            queue_name="test-queue",
            exchange_name="test-exchange",
            exchange_type="direct",
            exchange_durable=True,
            use_pool=False,
        ),
    )

    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        async for _ in client.receive():
            pass

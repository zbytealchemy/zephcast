"""Unit tests for asynchronous base messaging client."""
from typing import cast

import pytest

from zephcast.testing.aio.mock_client import MockAsyncClient
from zephcast.testing.helpers import create_mock_client


@pytest.mark.asyncio
async def test_async_client_lifecycle() -> None:
    """Test async client connection lifecycle."""
    client = cast(MockAsyncClient, create_mock_client("test-stream", is_async=True))

    assert not client._connected
    await client.connect()
    assert client._connected
    await client.close()  # type: ignore[unreachable]
    assert not client._connected


@pytest.mark.asyncio
async def test_async_client_context_manager() -> None:
    """Test async client context manager."""
    client = cast(MockAsyncClient, create_mock_client("test-stream", is_async=True))

    async with client:
        assert client._connected
    assert not client._connected


@pytest.mark.asyncio
async def test_async_client_send_receive() -> None:
    """Test sending and receiving messages."""
    client = cast(MockAsyncClient, create_mock_client("test-stream", is_async=True))

    async with client:
        await client.send("test1")
        await client.send("test2")

        received = []
        async for msg in client:
            received.append(msg)

        assert received == ["test1", "test2"]


@pytest.mark.asyncio
async def test_async_client_operations_when_disconnected() -> None:
    """Test operations fail when client is not connected."""
    client = cast(MockAsyncClient, create_mock_client("test-stream", is_async=True))

    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        async for _ in client:
            pass

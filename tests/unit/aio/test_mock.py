"""Tests for asynchronous mock clients."""
from typing import cast

import pytest

from zephcast.testing import assert_messages_equal, create_mock_client
from zephcast.testing.aio.mock_client import MockAsyncClient


@pytest.mark.asyncio
async def test_async_client_send() -> None:
    """Test sending messages with async client."""
    client = cast(
        MockAsyncClient,
        create_mock_client(
            "test-stream",
            is_async=True,
        ),
    )

    async with client:
        await client.send("test1")
        await client.send("test2")

    assert_messages_equal(list(client.sent_messages), ["test1", "test2"])


@pytest.mark.asyncio
async def test_async_client_receive() -> None:
    """Test receiving messages with async client."""
    client = cast(
        MockAsyncClient,
        create_mock_client(
            "test-stream",
            is_async=True,
            received_messages=["test1", "test2"],
        ),
    )

    received = []
    async with client:
        async for msg in client.receive():
            received.append(msg)

    assert_messages_equal(received, ["test1", "test2"])


@pytest.mark.asyncio
async def test_async_client_not_connected() -> None:
    """Test operations on non-connected client."""
    client = cast(
        MockAsyncClient,
        create_mock_client(
            "test-stream",
            is_async=True,
        ),
    )

    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        async for _ in client.receive():
            pass

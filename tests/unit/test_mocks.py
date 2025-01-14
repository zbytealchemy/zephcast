"""Tests for mock clients."""

from typing import List, cast

import pytest

from msgflow.testing.helpers import assert_messages_equal, create_mock_client
from msgflow.testing.mock_client import MockAsyncClient, MockSyncClient


def test_sync_client_send() -> None:
    """Test sending messages with sync client."""
    client = cast(
        MockSyncClient[str],
        create_mock_client(
            "test-stream",
            is_async=False,
        ),
    )

    with client:
        client.send("test1")
        client.send("test2")

    assert_messages_equal(client.sent_messages, ["test1", "test2"])


def test_sync_client_receive() -> None:
    """Test receiving messages with sync client."""
    client = cast(
        MockSyncClient[str],
        create_mock_client(
            "test-stream",
            is_async=False,
            received_messages=["test1", "test2"],
        ),
    )

    with client:
        messages = list(client.receive())

    assert_messages_equal(messages, ["test1", "test2"])


@pytest.mark.asyncio
async def test_async_client_send() -> None:
    """Test sending messages with async client."""
    client = cast(
        MockAsyncClient[str],
        create_mock_client(
            "test-stream",
            is_async=True,
        ),
    )

    async with client:
        await client.send("test1")
        await client.send("test2")

    assert_messages_equal(client.sent_messages, ["test1", "test2"])


@pytest.mark.asyncio
async def test_async_client_receive() -> None:
    """Test receiving messages with async client."""
    client = cast(
        MockAsyncClient[str],
        create_mock_client(
            "test-stream",
            is_async=True,
            received_messages=["test1", "test2"],
        ),
    )

    messages: List[str] = []
    async with client:
        async for message in await client.receive():
            messages.append(message)

    assert_messages_equal(messages, ["test1", "test2"])


def test_client_not_connected() -> None:
    """Test operations on non-connected client."""
    client = cast(
        MockSyncClient[str],
        create_mock_client(
            "test-stream",
            is_async=False,
        ),
    )

    with pytest.raises(RuntimeError, match="Client not connected"):
        client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        list(client.receive())

"""Tests for synchronous mock clients."""
from typing import cast

import pytest

from zephcast.testing.helpers import assert_messages_equal, create_mock_client
from zephcast.testing.sync.mock_client import MockSyncClient


def test_sync_client_send() -> None:
    """Test sending messages with sync client."""
    client = cast(
        MockSyncClient,
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
        MockSyncClient,
        create_mock_client(
            "test-stream",
            is_async=False,
            received_messages=["test1", "test2"],
        ),
    )

    received = []
    with client:
        for msg in client.receive():
            received.append(msg)
            if len(received) == 2:
                break

    assert_messages_equal(received, ["test1", "test2"])


def test_sync_client_not_connected() -> None:
    """Test operations on non-connected client."""
    client = cast(
        MockSyncClient,
        create_mock_client(
            "test-stream",
            is_async=False,
        ),
    )

    with pytest.raises(RuntimeError, match="Client not connected"):
        next(client.receive())

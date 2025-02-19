"""Unit tests for synchronous base messaging client."""
import pytest

from zephcast.testing.sync.mock_client import MockSyncClient


def test_sync_client_lifecycle() -> None:
    """Test sync client connection lifecycle."""
    client = MockSyncClient("test-stream")

    assert not client._connected
    client.connect()
    assert client._connected
    client.close()  # type: ignore[unreachable]
    assert not client._connected


def test_sync_client_context_manager() -> None:
    """Test sync client context manager."""
    client = MockSyncClient("test-stream")

    with client:
        assert client._connected
    assert not client._connected


def test_sync_client_send_receive() -> None:
    """Test sending and receiving messages."""
    client = MockSyncClient("test-stream")

    with client:
        client.send("test1")
        client.send("test2")

        received = []
        for msg in client.receive():
            received.append(msg)
            if len(received) == 2:
                break

        assert received == ["test1", "test2"]


def test_sync_client_iterator() -> None:
    """Test client iterator protocol."""
    client = MockSyncClient("test-stream", received_messages=["test1", "test2"])

    with client:
        received = []
        for msg in client:
            received.append(msg)
            if len(received) == 2:
                break

        assert received == ["test1", "test2"]


def test_sync_client_operations_when_disconnected() -> None:
    """Test operations fail when client is not connected."""
    client = MockSyncClient("test-stream")

    with pytest.raises(RuntimeError, match="Client not connected"):
        client.send("test")

    with pytest.raises(RuntimeError, match="Client not connected"):
        next(client.receive())

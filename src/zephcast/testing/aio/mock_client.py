"""Async mock client for testing."""
from collections import deque
from collections.abc import AsyncIterator
from typing import Any, TypeVar

from zephcast.core.types import ConnectionConfig
from zephcast.testing.mock_client import MockBaseClient

T = TypeVar("T")


class MockAsyncClient(MockBaseClient):
    """Mock async client for testing."""

    def __init__(
        self,
        stream_name: str,
        connection_config: ConnectionConfig | None = None,
        sent_messages: list[str] | None = None,
        received_messages: list[str] | None = None,
    ) -> None:
        """Initialize mock client."""
        super().__init__(stream_name, connection_config)
        self.sent_messages = []
        self.received_messages = deque(received_messages or [])
        if sent_messages:
            self.sent_messages.extend(sent_messages)

    async def connect(self) -> None:
        """Connect to mock service."""
        if self.connection_config and self.connection_config.get("raise_on_connect"):
            raise RuntimeError("Connection failed")
        self._connected = True

    async def close(self) -> None:
        """Close mock connection."""
        self._connected = False

    async def send(self, message: str) -> None:
        """Send message to mock service."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        self.sent_messages.append(message)
        self.received_messages.append(message)

    async def receive(self) -> AsyncIterator[str]:
        """Receive messages from mock service."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        while self.received_messages:
            yield self.received_messages.popleft()

    def __aiter__(self) -> AsyncIterator[str]:
        """Make the client itself iterable."""
        return self.receive()

    async def __aenter__(self) -> "MockAsyncClient":
        """Enter async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        await self.close()

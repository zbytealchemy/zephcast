"""Sync mock client for testing."""
from collections import deque
from collections.abc import Iterator
from typing import Any, Callable, Optional

from zephcast.core.consumers import ConsumerConfig
from zephcast.core.types import ConnectionConfig
from zephcast.sync.consumers import (
    SyncConsumerConfig,
    batch_consumer as sync_batch_consumer,
    consumer as sync_consumer,
)


class MockSyncClient:
    """Mock sync client for testing."""

    def __init__(
        self,
        stream_name: str,
        connection_config: ConnectionConfig | None = None,
        sent_messages: list[str] | None = None,
        received_messages: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize mock client."""
        self.stream_name = stream_name
        config = {"url": "mock://localhost"}
        if connection_config:
            config.update(connection_config)
        config.update(kwargs)
        self.connection_config = config
        self._connected = False
        self.sent_messages = sent_messages or []
        self._received_messages = deque(received_messages or [])
        self._original_messages = list(received_messages or [])

    def connect(self) -> None:
        """Connect to mock service."""
        if self.connection_config.get("raise_on_connect"):
            raise RuntimeError("Connection failed")
        self._connected = True

    def close(self) -> None:
        """Close connection to mock service."""
        self._connected = False

    def __enter__(self) -> "MockSyncClient":
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()

    def send(self, message: str) -> None:
        """Send message to mock service."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        self.sent_messages.append(message)
        self._received_messages.append(message)

    def receive(self) -> Iterator[str]:
        """Receive messages from mock service."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        while self._received_messages:
            yield self._received_messages.popleft()

    def __iter__(self) -> Iterator[str]:
        """Make the client itself iterable."""
        return self.receive()

    def consumer(
        self, config: SyncConsumerConfig | None = None
    ) -> Callable[[Callable[[str], None]], Callable[[], None]]:
        """Decorator for synchronous message consumers."""
        return sync_consumer(self, config)

    def batch_consumer(
        self, config: Optional[ConsumerConfig] = None
    ) -> Callable[[Callable[[list[str]], None]], Callable[[], None]]:
        """Decorator for synchronous batch message consumers."""
        return sync_batch_consumer(self, config)  # type: ignore

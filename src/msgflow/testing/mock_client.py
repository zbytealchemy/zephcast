"""Mock messaging clients for testing."""

from typing import Any, AsyncGenerator, Generic, Iterator, List, Optional, TypeVar

from msgflow.core.base import AsyncMessagingClient, SyncMessagingClient

T = TypeVar("T")

NOT_CONNECTED = "Client not connected"


class MockSyncClient(SyncMessagingClient[T], Generic[T]):
    """Mock synchronous messaging client for testing."""

    def __init__(
        self,
        stream_name: str,
        sent_messages: Optional[List[T]] = None,
        received_messages: Optional[List[T]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize mock client.

        Args:
            stream_name: Name of the stream
            sent_messages: Pre-populated sent messages
            received_messages: Pre-populated received messages
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.stream_name = stream_name
        self.sent_messages = list(sent_messages or [])
        self.received_messages = list(received_messages or [])
        self.is_connected = False

    def connect(self) -> None:
        """Mock connect."""
        self.is_connected = True

    def send(self, message: T) -> None:
        """Record sent message."""
        if not self.is_connected:
            raise RuntimeError(NOT_CONNECTED)
        self.sent_messages.append(message)

    def receive(self) -> Iterator[T]:
        """Yield received messages."""
        if not self.is_connected:
            raise RuntimeError(NOT_CONNECTED)
        yield from self.received_messages
        self.received_messages.clear()

    def close(self) -> None:
        """Mock close."""
        self.is_connected = False


class MockAsyncClient(AsyncMessagingClient[T], Generic[T]):
    """Mock asynchronous messaging client for testing."""

    def __init__(
        self,
        stream_name: str,
        sent_messages: Optional[List[T]] = None,
        received_messages: Optional[List[T]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize mock client.

        Args:
            stream_name: Name of the stream
            sent_messages: Pre-populated sent messages
            received_messages: Pre-populated received messages
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.stream_name = stream_name
        self.sent_messages = list(sent_messages or [])
        self.received_messages = list(received_messages or [])
        self.is_connected = False

    async def connect(self) -> None:
        """Mock connect."""
        self.is_connected = True

    async def send(self, message: T) -> None:
        """Record sent message."""
        if not self.is_connected:
            raise RuntimeError(NOT_CONNECTED)
        self.sent_messages.append(message)

    async def receive(self) -> Any:
        """Yield received messages."""
        if not self.is_connected:
            raise RuntimeError(NOT_CONNECTED)

        async def _receive() -> AsyncGenerator[T, None]:
            for message in self.received_messages:
                yield message
            self.received_messages.clear()

        return _receive()

    async def close(self) -> None:
        """Mock close."""
        self.is_connected = False

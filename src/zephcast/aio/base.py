"""Base classes for asynchronous messaging clients."""
import logging

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Generic, Optional, TypeVar

from zephcast.core.types import MessageMetadata

logger = logging.getLogger(__name__)
T = TypeVar("T")


class AsyncBaseClient(ABC, Generic[T]):
    """Base class for async clients."""

    def __init__(self, stream_name: str) -> None:
        self.stream_name = stream_name
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the message broker."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""

    @abstractmethod
    async def send(self, message: T, **kwargs: Any) -> None:
        """Send a message."""

    @abstractmethod
    async def receive(
        self, timeout: Optional[float] = None
    ) -> AsyncGenerator[tuple[T, MessageMetadata], None]:
        """Receive messages.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            AsyncGenerator yielding tuples of (message, metadata)
        """

    def __aiter__(self) -> "AsyncBaseClient[T]":
        """Make the client itself iterable."""
        return self

    async def __anext__(self) -> tuple[T, MessageMetadata]:
        """Get the next message."""
        async for item in self.receive():  # type: ignore[attr-defined]
            return item  # type: ignore[no-any-return]
        raise StopAsyncIteration

    async def __aenter__(self) -> "AsyncBaseClient[T]":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

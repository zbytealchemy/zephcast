"""Base classes for messaging clients."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import (
    Any,
    Generic,
    Iterator,
    TypeVar,
)

T = TypeVar("T")


class SyncMessagingClient(ABC, Generic[T]):
    """Base class for synchronous messaging clients."""

    def __init__(
        self,
        stream_name: str,
        use_pool: bool = True,
        pool_size: int = 5,
        **kwargs: Any,
    ) -> None:
        """Initialize the messaging client.

        Args:
            stream_name: The name of the stream to use.
            use_pool: Whether to use a connection pool.
            pool_size: The size of the connection pool.
        """
        self.stream_name: str = stream_name
        self.use_pool: bool = use_pool
        self.pool_size: int = pool_size

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the messaging system."""

    @abstractmethod
    def send(self, message: T) -> None:
        """Send a message."""

    @abstractmethod
    def receive(self) -> Iterator[T]:
        """Receive messages."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""

    def __enter__(self) -> "SyncMessagingClient[T]":
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()

    def __iter__(self) -> Iterator[T]:
        """Return iterator."""
        return self.receive()


class AsyncMessagingClient(ABC, Generic[T]):
    """Base class for asynchronous messaging clients."""

    def __init__(
        self,
        stream_name: str,
        use_pool: bool = True,
        pool_size: int = 5,
        **kwargs: Any,
    ) -> None:
        """Initialize the messaging client.

        Args:
            stream_name: The name of the stream to use.
            use_pool: Whether to use a connection pool.
            pool_size: The size of the connection pool.
        """
        self.stream_name: str = stream_name
        self.use_pool: bool = use_pool
        self.pool_size: int = pool_size

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the messaging system."""

    @abstractmethod
    async def send(self, message: T) -> None:
        """Send a message."""

    @abstractmethod
    async def receive(self) -> AsyncIterator[T]:
        """Receive messages."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""

    async def __aenter__(self) -> "AsyncMessagingClient[T]":
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.close()

    def __aiter__(self) -> "AsyncMessagingClient[T]":
        """Return async iterator."""
        return self

    async def __anext__(self) -> T:
        """Get next message."""
        async for message in await self.receive():
            return message
        raise StopAsyncIteration

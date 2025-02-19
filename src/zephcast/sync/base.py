"""Base classes for synchronous messaging clients."""
import logging

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, Generic, TypeVar

from zephcast.core.types import MessageMetadata

logger = logging.getLogger(__name__)
T = TypeVar("T")


class SyncBaseClient(ABC, Generic[T]):
    """Base class for synchronous messaging clients."""

    def __init__(
        self,
        stream_name: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the client."""
        self.stream_name = stream_name
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the messaging system."""

    @abstractmethod
    def send(self, message: T) -> None:
        """Send a message."""

    @abstractmethod
    def receive(self, timeout: float | None = None) -> Iterator[tuple[T, MessageMetadata]]:
        """Receive messages.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            Iterator yielding tuples of (message, metadata)
        """

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""

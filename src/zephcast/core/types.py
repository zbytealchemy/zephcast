"""Core types used across ZephCast."""
from typing import Any, Optional

from typing_extensions import TypeAlias

# Basic message types
Headers: TypeAlias = dict[str, str]
Message: TypeAlias = str | bytes | dict[str, Any]

# Configuration types
ConnectionConfig: TypeAlias = dict[str, Any]

ClientOptions: TypeAlias = dict[str, Any]


class MessageMetadata:
    """Metadata for a message."""

    def __init__(
        self,
        message_id: str,
        timestamp: float,
        headers: Optional[Headers] = None,
        delivery_tag: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self.message_id = message_id
        self.timestamp = timestamp
        self.headers = headers or {}
        self.delivery_tag = delivery_tag
        self.extra = kwargs

"""ZephCast - A unified messaging library."""
from importlib.metadata import version

__version__ = version("zephcast")

# Core exports
from zephcast.core.consumers import ConsumerConfig, ExecutorType
from zephcast.core.exceptions import (
    ConnectionError,
    DependencyError,
    MessageError,
    ZephCastError,
)
from zephcast.core.types import (
    ClientOptions,
    ConnectionConfig,
    Headers,
    Message,
    MessageMetadata,
)
from zephcast.core.utils import deserialize_message, get_logger, serialize_message

__all__ = [
    "__version__",
    "Message",
    "MessageMetadata",
    "Headers",
    "ClientOptions",
    "ConnectionConfig",
    "ConsumerConfig",
    "ExecutorType",
    "ConnectionError",
    "DependencyError",
    "MessageError",
    "ZephCastError",
    "deserialize_message",
    "get_logger",
    "serialize_message",
]

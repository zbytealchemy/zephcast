"""Core package for zephcast."""

from zephcast.core.consumers import ConsumerConfig, ExecutorType
from zephcast.core.exceptions import ConnectionError, DependencyError, MessageError, ZephCastError
from zephcast.core.retry import RetryConfig
from zephcast.core.types import (
    ClientOptions,
    ConnectionConfig,
    Headers,
    Message,
    MessageMetadata,
)
from zephcast.core.utils import deserialize_message, get_logger, serialize_message

__all__ = [
    "ConsumerConfig",
    "ExecutorType",
    "ConnectionError",
    "DependencyError",
    "MessageError",
    "ZephCastError",
    "Message",
    "MessageMetadata",
    "Headers",
    "ClientOptions",
    "ConnectionConfig",
    "RetryConfig",
    "deserialize_message",
    "get_logger",
    "serialize_message",
]

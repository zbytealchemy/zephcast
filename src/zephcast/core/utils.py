"""Utility functions used across ZephCast."""
import json
import logging

from typing import Any, cast

from zephcast.core.types import Message


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: The name of the logger.

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)


def serialize_message(message: Message) -> bytes:
    """Serialize a message to bytes.

    Args:
        message: The message to serialize.

    Returns:
        bytes: The serialized message.
    """
    if isinstance(message, bytes):
        return message
    if isinstance(message, str):
        return message.encode("utf-8")
    if isinstance(message, dict):
        return json.dumps(message).encode("utf-8")
    raise TypeError(f"Unsupported message type: {type(message)}")


def deserialize_message(data: bytes) -> Message:
    """Deserialize a message from bytes.

    Args:
        data: The data to deserialize.

    Returns:
        Message: The deserialized message.
    """
    try:
        decoded = data.decode("utf-8")
        try:
            return cast(dict[str, Any], json.loads(decoded))  # Add cast here
        except json.JSONDecodeError:
            return decoded  # Returns str
    except UnicodeDecodeError:
        return data  # Returns bytes

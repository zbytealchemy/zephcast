"""Factory functions for creating mock clients."""
from typing import Any, TypeVar

from zephcast.core.types import ConnectionConfig
from zephcast.testing.aio.mock_client import MockAsyncClient
from zephcast.testing.sync.mock_client import MockSyncClient

MessageType = TypeVar("MessageType", bound=str)


def create_mock_client(
    stream_name: str,
    *,
    is_async: bool = True,
    connection_config: ConnectionConfig | None = None,
    sent_messages: list[str] | None = None,
    received_messages: list[str] | None = None,
    **kwargs: Any,
) -> MockAsyncClient | MockSyncClient:
    """Create a mock client for testing."""
    if is_async:
        return MockAsyncClient(
            stream_name=stream_name,
            connection_config=connection_config,
            sent_messages=sent_messages,
            received_messages=received_messages,
            **kwargs,
        )
    return MockSyncClient(
        stream_name=stream_name,
        connection_config=connection_config,
        sent_messages=sent_messages,
        received_messages=received_messages,
        **kwargs,
    )

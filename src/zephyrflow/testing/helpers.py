"""Test helpers for zephyrflow."""

from typing import Optional, TypeVar, Union

from .mock_client import MockAsyncClient, MockSyncClient

T = TypeVar("T")


def create_mock_client(
    stream_name: str,
    *,
    is_async: bool = True,
    sent_messages: Optional[list[T]] = None,
    received_messages: Optional[list[T]] = None,
) -> Union[MockAsyncClient[T], MockSyncClient[T]]:
    """Create a mock client for testing.

    Args:
        stream_name: Name of the stream
        is_async: Whether to create an async client
        sent_messages: Pre-populated sent messages
        received_messages: Pre-populated received messages

    Returns:
        Mock client instance
    """
    if is_async:
        return MockAsyncClient(
            stream_name=stream_name,
            sent_messages=sent_messages,
            received_messages=received_messages,
        )
    return MockSyncClient(
        stream_name=stream_name,
        sent_messages=sent_messages,
        received_messages=received_messages,
    )


def assert_messages_equal(
    actual: list[T],
    expected: list[T],
    *,
    msg: Optional[str] = None,
) -> None:
    """Assert that two lists of messages are equal.

    Args:
        actual: Actual messages
        expected: Expected messages
        msg: Optional message to display on failure
    """
    assert len(actual) == len(expected), (
        f"{msg + ': ' if msg else ''}" f"Length mismatch: {len(actual)} != {len(expected)}"
    )
    for i, (a, e) in enumerate(zip(actual, expected)):
        assert a == e, f"{msg + ': ' if msg else ''}" f"Mismatch at index {i}: {a} != {e}"

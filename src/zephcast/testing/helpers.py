"""Testing helpers for zephcast."""
from zephcast.testing.factory import create_mock_client

__all__ = [
    "assert_messages_equal",
    "create_mock_client",
]


def assert_messages_equal(actual: list, expected: list) -> None:
    """Assert that two lists of messages are equal."""
    assert len(actual) == len(expected), f"Expected {len(expected)} messages, got {len(actual)}"
    for a, e in zip(actual, expected):
        assert a == e, f"Expected message {e}, got {a}"

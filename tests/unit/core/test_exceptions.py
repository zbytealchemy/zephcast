"""Unit tests for core exceptions."""

from zephcast.core.exceptions import DependencyError


def test_dependency_error_missing_sync() -> None:
    """Test DependencyError for missing sync dependencies."""
    error = DependencyError.missing_sync("kafka")
    assert str(error) == (
        "Missing required dependency for sync Kafka client. " "Install with: poetry add zephcast[kafka]"
    )


def test_dependency_error_missing_async() -> None:
    """Test DependencyError for missing async dependencies."""
    error = DependencyError.missing_async("redis")
    assert str(error) == (
        "Missing required dependency for async Redis client. " "Install with: poetry add zephcast[redis]"
    )


def test_dependency_error_custom_message() -> None:
    """Test DependencyError with custom message."""
    error = DependencyError("Custom error message")
    assert str(error) == "Custom error message"

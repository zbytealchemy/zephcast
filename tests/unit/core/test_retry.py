"""Unit tests for core retry configuration."""

from zephcast.core.retry import RetryConfig


def test_retry_config_defaults() -> None:
    """Test RetryConfig default values."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.retry_sleep == 1.0
    assert config.backoff_factor == 2.0
    assert config.exceptions == (Exception,)


def test_retry_config_custom_values() -> None:
    """Test RetryConfig with custom values."""
    config = RetryConfig(
        max_retries=5,
        retry_sleep=0.5,
        backoff_factor=3.0,
        exceptions=(ValueError, TypeError),
    )
    assert config.max_retries == 5
    assert config.retry_sleep == 0.5
    assert config.backoff_factor == 3.0
    assert config.exceptions == (ValueError, TypeError)

"""Core exceptions for ZephCast."""


class ZephCastError(Exception):
    """Base exception for all ZephCast errors."""


class DependencyError(ZephCastError):
    """Raised when a required optional dependency is not installed."""

    @classmethod
    def missing_sync(cls, broker: str) -> "DependencyError":
        """Create error for missing sync dependency.

        Args:
            broker: The broker name (e.g., 'kafka', 'redis', 'rabbit')

        Returns:
            DependencyError with appropriate message
        """
        return cls(
            f"Missing required dependency for sync {broker.title()} client. "
            f"Install with: poetry add zephcast[{broker.lower()}]"
        )

    @classmethod
    def missing_async(cls, broker: str) -> "DependencyError":
        """Create error for missing async dependency.

        Args:
            broker: The broker name (e.g., 'kafka', 'redis', 'rabbit')

        Returns:
            DependencyError with appropriate message
        """
        return cls(
            f"Missing required dependency for async {broker.title()} client. "
            f"Install with: poetry add zephcast[{broker.lower()}]"
        )


class RetryError(ZephCastError):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, message: str, last_exception: Exception) -> None:
        """Initialize RetryError.

        Args:
            message: Error message
            last_exception: The last exception that caused the retry to fail
        """
        super().__init__(message)
        self.last_exception = last_exception


class ConnectionError(ZephCastError):
    """Raised when a connection error occurs."""


class MessageError(ZephCastError):
    """Raised when there's an error with message handling."""


class ConfigurationError(ZephCastError):
    """Raised when there's an error in client configuration.

    This includes invalid configuration values, missing required fields,
    or incompatible configuration combinations.
    """

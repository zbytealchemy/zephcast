"""Base retry configuration."""


class RetryConfig:
    """Base configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_sleep: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> None:
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retries
            retry_sleep: Initial sleep time between retries
            backoff_factor: Multiplier for sleep time after each retry
            exceptions: Exception types to retry on
        """
        self.max_retries = max_retries
        self.retry_sleep = retry_sleep
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions

# Synchronous Retry

## SyncRetryConfig

Configuration for synchronous retry behavior:

```python
from zephcast.sync.retry import SyncRetryConfig

retry_config = SyncRetryConfig(
    max_retries: int = 3,            # Maximum retry attempts
    retry_sleep: float = 1.0,        # Base sleep time between retries
    backoff_factor: float = 2.0,     # Exponential backoff multiplier
    exceptions: tuple = (Exception,), # Retryable exceptions
    on_retry: Callable = None        # Retry callback function
)
```

## Retry Behavior

### Exponential Backoff
The actual sleep time between retries is calculated as:
```python
sleep_time = retry_sleep * (backoff_factor ** retry_count)
```

### Retry Callback
```python
def on_retry(retry_count: int, exception: Exception) -> None:
    logger.warning(f"Retry {retry_count} due to {exception}")
```
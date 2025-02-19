# Asynchronous Retry

## AsyncRetryConfig

Configuration for asynchronous retry behavior:

```python
from zephcast.aio.retry import AsyncRetryConfig

retry_config = AsyncRetryConfig(
    max_retries: int = 3,            # Maximum retry attempts
    retry_sleep: float = 1.0,        # Base sleep time between retries
    backoff_factor: float = 2.0,     # Exponential backoff multiplier
    exceptions: tuple = (Exception,), # Retryable exceptions
    on_retry: Callable = None        # Async retry callback function
)
```

## Retry Behavior

### Exponential Backoff
The actual sleep time between retries is calculated as:
```python
sleep_time = retry_sleep * (backoff_factor ** retry_count)
```

### Async Retry Callback
```python
async def on_retry(retry_count: int, exception: Exception) -> None:
    await log_service.warning(f"Retry {retry_count} due to {exception}")
```
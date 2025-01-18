# Error Handling and Retry

MsgFlow provides robust error handling and retry capabilities to help you build reliable message processing systems.

## Retry Configuration

The `RetryConfig` class allows you to configure retry behavior:

```python
from zephcast.core.retry import RetryConfig

# Basic retry configuration
config = RetryConfig(
    max_retries=3,          # Maximum number of retry attempts
    retry_sleep=1.0,        # Initial sleep time between retries
    backoff_factor=2.0,     # Multiplier for sleep time after each retry
)

# Advanced retry configuration
config = RetryConfig(
    max_retries=5,
    retry_sleep=0.1,
    backoff_factor=2.0,
    exceptions=(ConnectionError, TimeoutError),  # Only retry these exceptions
    condition=lambda result: result is not None,  # Only retry if condition is False
    on_retry=lambda retries, exc: print(f"Retry {retries}: {exc}")  # Callback on each retry
)
```

## Using Retry with Consumers

You can add retry behavior to your message consumers using the `ConsumerConfig`:

```python
from zephcast.core.consumers import ConsumerConfig, consumer
from zephcast.core.retry import RetryConfig

# Configure retry behavior
retry_config = RetryConfig(
    max_retries=3,
    retry_sleep=1.0,
    backoff_factor=2.0
)

# Create consumer config with retry
consumer_config = ConsumerConfig(
    retry=retry_config,
    auto_ack=True
)

# Apply retry to a message consumer
@consumer(config=consumer_config)
async def process_message(message: str) -> None:
    # This function will retry up to 3 times if it fails
    result = await external_service.process(message)
    if not result.success:
        raise ValueError("Processing failed")
```

## Batch Consumer with Retry

Retry also works with batch consumers:

```python
from typing import List
from zephcast.core.consumers import ConsumerConfig, batch_consumer
from zephcast.core.retry import RetryConfig

# Configure retry for batch processing
retry_config = RetryConfig(
    max_retries=3,
    retry_sleep=1.0,
    exceptions=(ConnectionError,)
)

consumer_config = ConsumerConfig(
    retry=retry_config,
    batch_size=10,
    batch_timeout=1.0
)

@batch_consumer(config=consumer_config)
async def process_batch(messages: List[str]) -> None:
    # This function will retry the entire batch if it fails
    await external_service.process_batch(messages)
```

## Error Handling Best Practices

1. **Use Specific Exceptions**
   ```python
   # Good: Only retry specific exceptions
   retry_config = RetryConfig(
       exceptions=(ConnectionError, TimeoutError)
   )

   # Bad: Retry all exceptions
   retry_config = RetryConfig()  # Will retry any exception
   ```

2. **Add Retry Conditions**
   ```python
   # Good: Only retry if the result is invalid
   retry_config = RetryConfig(
       condition=lambda result: result.status_code == 200
   )
   ```

3. **Use Backoff**
   ```python
   # Good: Use exponential backoff
   retry_config = RetryConfig(
       retry_sleep=0.1,
       backoff_factor=2.0  # 0.1s, 0.2s, 0.4s, 0.8s, ...
   )
   ```

4. **Monitor Retries**
   ```python
   def log_retry(retry_count: int, exception: Exception) -> None:
       logger.warning(
           "Retry %d: %s",
           retry_count,
           str(exception)
       )

   retry_config = RetryConfig(
       on_retry=log_retry
   )
   ```

5. **Handle Cleanup**
   ```python
   @consumer(config=consumer_config)
   async def process_message(message: str) -> None:
       resources = []
       try:
           # Acquire resources
           resources.append(await get_resource())
           await process(message, resources)
       finally:
           # Always clean up resources
           for resource in resources:
               await resource.close()
   ```

## Client Error Handling

MsgFlow messaging clients (Kafka, RabbitMQ, Redis) handle errors as follows:

1. **Connection Errors**
   - Clients raise appropriate exceptions when connection fails
   - Resources are properly cleaned up
   - Use context managers for automatic cleanup

2. **Send Errors**
   - Failed sends raise exceptions immediately
   - No automatic retries at the client level
   - Use consumer retry for reliable message delivery

3. **Receive Errors**
   - Iterator stops on fatal errors
   - Temporary errors are logged
   - Use consumer retry for reliable message processing

Example:

```python
from zephcast.kafka.async_client import AsyncKafkaClient

async def safe_consume():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    try:
        await client.connect()
        async for message in client.receive():
            try:
                await process_message(message)
            except Exception as e:
                logger.error("Failed to process message: %s", e)
    except ConnectionError as e:
        logger.error("Kafka connection failed: %s", e)
    finally:
        await client.close()
```

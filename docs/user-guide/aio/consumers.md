# Asynchronous Consumers

## Overview

Asynchronous consumers in ZephCast provide non-blocking message processing with retry capabilities.

## AsyncConsumerConfig

```python
from zephcast.aio.consumers import AsyncConsumerConfig
from zephcast.aio.retry import AsyncRetryConfig

# Create retry configuration
retry_config = AsyncRetryConfig(
    max_retries=3,
    retry_sleep=1.0,
    backoff_factor=2.0,
    exceptions=(ConnectionError, TimeoutError)
)

# Create consumer configuration
config = AsyncConsumerConfig(
    retry=retry_config,
    batch_size=1,
    batch_timeout=1.0,
    executor_type=None,
    num_workers=1,
    auto_ack=True
)
```

## Single Message Consumer

```python
from zephcast.aio.consumers import consumer

@consumer(config=AsyncConsumerConfig(
    retry=AsyncRetryConfig(max_retries=3)
))
async def process_message(message: str) -> None:
    # Process single message with retry
    result = await external_service.process(message)
    if not result.success:
        raise ValueError("Processing failed")
```

## Batch Consumer

```python
from typing import List
from zephcast.aio.consumers import batch_consumer

@batch_consumer(config=AsyncConsumerConfig(
    retry=AsyncRetryConfig(max_retries=3),
    batch_size=10,
    batch_timeout=1.0
))
async def process_batch(messages: List[str]) -> None:
    # Process batch of messages with retry
    results = await external_service.process_batch(messages)
    if not all(r.success for r in results):
        raise ValueError("Batch processing failed")
```

## Parallel Processing

```python
from zephcast.core.consumers import ExecutorType
from zephcast.aio.consumers import consumer

config = AsyncConsumerConfig(
    retry=AsyncRetryConfig(max_retries=3),
    executor_type=ExecutorType.THREAD,
    num_workers=4
)

@consumer(config=config)
async def process_message(message: str) -> None:
    # CPU-bound operations will be executed in a thread pool
    await process_in_parallel(message)
```

## Error Handling

```python
from zephcast.aio.consumers import consumer
from zephcast.aio.retry import AsyncRetryConfig

async def on_retry(retry_count: int, exception: Exception) -> None:
    logger.warning(f"Retry {retry_count}: {exception}")

config = AsyncConsumerConfig(
    retry=AsyncRetryConfig(
        max_retries=3,
        exceptions=(ConnectionError, TimeoutError),
        on_retry=on_retry
    )
)

@consumer(config=config)
async def process_message(message: str) -> None:
    try:
        result = await external_service.process(message)
        if not result.success:
            raise ValueError("Processing failed")
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise
```
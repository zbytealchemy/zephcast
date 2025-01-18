# Error Handling

Proper error handling is crucial for building reliable messaging applications. This guide covers error handling strategies for ZephCast.

## Common Error Types

### Connection Errors

```python
from zephcast.kafka.async_client import AsyncKafkaClient
from kafka.errors import KafkaConnectionError

async def handle_connection_error():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    try:
        await client.connect()
    except KafkaConnectionError as e:
        print(f"Connection failed: {e}")
        # Implement retry logic or fallback
    finally:
        await client.close()
```

### Message Publishing Errors

```python
from zephcast.rabbit.async_client import AsyncRabbitClient
from aio_pika.exceptions import MessageError

async def handle_publish_error():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    try:
        await client.send("My message")
    except MessageError as e:
        print(f"Failed to publish message: {e}")
        # Handle failed publication
    finally:
        await client.close()
```

### Consumer Errors

```python
from zephcast.redis.async_client import AsyncRedisClient
from redis.exceptions import RedisError

async def handle_consumer_error():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    await client.connect()
    
    try:
        async for message in client.receive():
            try:
                # Process message
                process_message(message)
                await client.ack(message)
            except ProcessingError:
                # Handle processing failure
                await client.nack(message)
            except RedisError as e:
                print(f"Redis error: {e}")
                break
    finally:
        await client.close()
```

## Retry Strategies

### Exponential Backoff

```python
import asyncio
from zephcast.kafka.async_client import AsyncKafkaClient

async def exponential_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

async def publish_with_retry():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    await client.connect()
    
    try:
        await exponential_backoff(
            lambda: client.send("Important message")
        )
    finally:
        await client.close()
```

### Circuit Breaker

```python
import time
from zephcast.rabbit.async_client import AsyncRabbitClient

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.is_open = False
    
    async def call(self, func):
        if self.is_open:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.is_open = False
                self.failure_count = 0
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func()
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
            raise e

async def publish_with_circuit_breaker():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    breaker = CircuitBreaker()
    
    await client.connect()
    
    try:
        await breaker.call(
            lambda: client.send("Test message")
        )
    finally:
        await client.close()
```

## Dead Letter Handling

### RabbitMQ Dead Letter Exchange

```python
from zephcast.rabbit.async_client import AsyncRabbitClient

async def setup_dead_letter():
    # Main queue client
    main_client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        exchange_name="my-exchange",
        dead_letter_exchange="dlx",
        dead_letter_routing_key="failed",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    # Dead letter queue client
    dlq_client = AsyncRabbitClient(
        stream_name="failed",
        queue_name="dead-letter-queue",
        exchange_name="dlx",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await main_client.connect()
    await dlq_client.connect()
    
    try:
        # Process messages with dead letter handling
        async for message in main_client.receive():
            try:
                # Process message
                process_message(message)
                await main_client.ack(message)
            except Exception as e:
                # Message will be sent to dead letter queue
                await main_client.nack(message, requeue=False)
    finally:
        await main_client.close()
        await dlq_client.close()
```

## Best Practices

1. Always implement proper error handling
2. Use appropriate retry strategies
3. Set up dead letter queues/exchanges
4. Implement circuit breakers for external services
5. Log errors with context
6. Monitor error rates and types
7. Set appropriate timeouts
8. Clean up resources in finally blocks
9. Handle both expected and unexpected errors
10. Implement graceful degradation

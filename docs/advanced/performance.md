# Performance Optimization

This guide covers performance optimization techniques for ZephCast applications.

## Batch Processing

### Kafka Batch Publishing

```python
from zephcast.kafka.async_client import AsyncKafkaClient

async def batch_publish():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092",
        batch_size=16384,  # 16KB
        linger_ms=10,  # Wait up to 10ms to batch messages
        compression_type="snappy"
    )
    
    await client.connect()
    
    try:
        # Messages will be automatically batched
        for i in range(10000):
            await client.send(f"Message {i}")
    finally:
        await client.close()
```

### RabbitMQ Batch Publishing

```python
from zephcast.rabbit.async_client import AsyncRabbitClient

async def batch_publish():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/",
        batch_size=100,
        batch_timeout=1.0  # seconds
    )
    
    await client.connect()
    
    try:
        messages = [f"Message {i}" for i in range(1000)]
        await client.send_batch(messages)
    finally:
        await client.close()
```

## Connection Pooling

### Redis Connection Pool

```python
from zephcast.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="redis://localhost:6379",
    max_connections=10,
    min_connections=2
)
```

### RabbitMQ Channel Pool

```python
from zephcast.rabbit.async_client import AsyncRabbitClient

client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    rabbitmq_url="amqp://guest:guest@localhost:5672/",
    channel_pool_size=5
)
```

## Message Compression

### Kafka Compression

```python
from zephcast.kafka.async_client import AsyncKafkaClient

client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    compression_type="snappy",  # or "gzip", "lz4", "zstd"
    compression_level=6
)
```

### Custom Message Compression

```python
import zlib
from zephcast.rabbit.async_client import AsyncRabbitClient

async def compress_and_send():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    try:
        # Compress message
        message = "Large message content"
        compressed = zlib.compress(message.encode())
        
        # Send compressed message
        await client.send(compressed)
    finally:
        await client.close()
```

## Consumer Optimization

### Parallel Processing

```python
import asyncio
from zephcast.kafka.async_client import AsyncKafkaClient

async def parallel_processing():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )
    
    await client.connect()
    
    async def process_message(message):
        # Simulate async processing
        await asyncio.sleep(0.1)
        return f"Processed: {message}"
    
    try:
        tasks = []
        async for message in client.receive():
            # Process messages in parallel
            task = asyncio.create_task(process_message(message))
            tasks.append(task)
            
            # Limit concurrent tasks
            if len(tasks) >= 10:
                await asyncio.gather(*tasks)
                tasks = []
    finally:
        # Clean up remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
        await client.close()
```

### Prefetch Settings

```python
from zephcast.rabbit.async_client import AsyncRabbitClient

client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    rabbitmq_url="amqp://guest:guest@localhost:5672/",
    prefetch_count=100  # Number of unacked messages
)
```

## Memory Management

### Message Size Limits

```python
from zephcast.kafka.async_client import AsyncKafkaClient

client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    max_request_size=1048576,  # 1MB
    message_max_bytes=1000000
)
```

### Stream Trimming (Redis)

```python
from zephcast.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="redis://localhost:6379",
    max_stream_length=1000,  # Keep only last 1000 messages
    approximate_trimming=True
)
```

## Monitoring

### Performance Metrics

```python
import time
from zephcast.kafka.async_client import AsyncKafkaClient

async def monitor_performance():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    await client.connect()
    
    try:
        # Monitor publishing performance
        start_time = time.time()
        message_count = 0
        
        for i in range(10000):
            await client.send(f"Message {i}")
            message_count += 1
            
            if message_count % 1000 == 0:
                elapsed = time.time() - start_time
                rate = message_count / elapsed
                print(f"Publishing rate: {rate:.2f} messages/second")
    finally:
        await client.close()
```

## Best Practices

1. Use appropriate batch sizes
2. Enable message compression
3. Configure connection pools
4. Set proper prefetch counts
5. Monitor memory usage
6. Use parallel processing wisely
7. Implement backpressure
8. Monitor performance metrics
9. Use appropriate timeouts
10. Clean up resources properly

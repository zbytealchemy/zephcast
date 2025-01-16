# Redis Client Guide

The Redis client in ZephyrFlow provides a high-level interface for working with Redis Streams.

## Features

- Asynchronous message publishing and consumption
- Consumer groups
- Stream trimming
- Message acknowledgment
- Connection pooling
- SSL/TLS support

## Basic Usage

```python
from zephyrflow.redis.async_client import AsyncRedisClient

async def redis_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    await client.connect()
    
    # Send a message
    await client.send("Hello Redis!")
    
    # Receive messages
    async for message in client.receive():
        print(f"Received: {message}")
        break
    
    await client.close()
```

## Consumer Groups

```python
from zephyrflow.redis.async_client import AsyncRedisClient

async def consumer_group_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        consumer_group="my-group",
        consumer_name="consumer-1",
        redis_url="redis://localhost:6379"
    )
    
    await client.connect()
    
    async for message in client.receive():
        print(f"Consumer received: {message}")
        await client.ack(message)
    
    await client.close()
```

## Stream Management

### Stream Trimming

```python
from zephyrflow.redis.async_client import AsyncRedisClient

async def stream_trimming_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379",
        max_stream_length=1000
    )
    
    await client.connect()
    
    # Stream will be automatically trimmed
    for i in range(2000):
        await client.send(f"Message {i}")
    
    await client.close()
```

### Message Acknowledgment

```python
from zephyrflow.redis.async_client import AsyncRedisClient

async def ack_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        consumer_group="my-group",
        auto_ack=False,
        redis_url="redis://localhost:6379"
    )
    
    await client.connect()
    
    try:
        async for message in client.receive():
            try:
                # Process message
                print(f"Processing: {message}")
                # Acknowledge success
                await client.ack(message)
            except Exception:
                # Message will be redelivered
                continue
    finally:
        await client.close()
```

## Connection Management

### Connection Pooling

```python
from zephyrflow.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="redis://localhost:6379",
    max_connections=10,
    min_connections=2
)
```

### SSL/TLS Configuration

```python
from zephyrflow.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="rediss://localhost:6379",  # Note: rediss:// for SSL
    ssl_ca_certs="/path/to/ca.pem",
    ssl_certfile="/path/to/cert.pem",
    ssl_keyfile="/path/to/key.pem"
)
```

## Error Handling

```python
from zephyrflow.redis.async_client import AsyncRedisClient
from redis.exceptions import RedisError

async def error_handling_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    try:
        await client.connect()
        await client.send("test message")
    except RedisError as e:
        print(f"Redis error: {e}")
    finally:
        await client.close()
```

## Best Practices

1. Use consumer groups for scalable message processing
2. Configure appropriate stream length limits
3. Implement proper message acknowledgment
4. Use connection pooling for better performance
5. Monitor stream length and memory usage
6. Use SSL/TLS in production environments
7. Implement proper error handling and retries
8. Clean up old messages using XDEL or XTRIM
9. Monitor consumer group lag
10. Use appropriate connection timeouts

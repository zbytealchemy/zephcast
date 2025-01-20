# Redis API Reference

The Redis client provides a high-level interface for working with Redis Streams.

## Core Components

### AsyncRedisClient

The main client class for interacting with Redis Streams.

```python
from zephcast.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="redis://localhost:6379",
    consumer_group="my-group"  # Optional
)
```

#### Methods

- `connect()` - Establish connection to Redis
- `close()` - Close the connection
- `send(message)` - Add a message to the stream
- `receive()` - Async iterator for receiving messages
- `ack(message)` - Acknowledge a message (when using consumer groups)

#### Configuration Options

- `stream_name` - Stream name
- `redis_url` - Redis connection URL
- `consumer_group` - Consumer group name (optional)
- `consumer_name` - Consumer name (optional)
- `max_stream_length` - Maximum stream length (optional)
- `auto_ack` - Automatic acknowledgment (optional)
- `max_connections` - Connection pool size (optional)
- `min_connections` - Minimum connections in pool (optional)

### Usage Example

```python
import asyncio
from zephcast.redis.async_client import AsyncRedisClient

async def redis_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    await client.connect()
    
    try:
        await client.send("Hello Redis!")
        
        async for message in client.receive():
            print(f"Received: {message}")
            break
            
    finally:
        await client.close()

asyncio.run(redis_example())
```

### Consumer Group Example

```python
async def consumer_group_example():
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379",
        consumer_group="my-group",
        consumer_name="consumer-1",
        auto_ack=False
    )
    
    await client.connect()
    
    try:
        async for message in client.receive():
            try:
                print(f"Processing: {message}")
                await client.ack(message)
            except Exception as e:
                print(f"Processing failed: {e}")
                # Message will be redelivered
                continue
            
    finally:
        await client.close()

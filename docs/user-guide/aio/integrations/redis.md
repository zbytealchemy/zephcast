# Asynchronous Redis Integration

## AsyncRedisClient

```python
from zephcast.aio.redis import RedisClient
from zephcast.aio.redis.config import RedisConfig

config = RedisConfig(
    url="redis://localhost:6379",
    consumer_group="my-group",
    consumer_name="consumer-1"
)

client = RedisClient(
    stream_name="my-stream",
    config=config
)

# Basic usage
async with client:
    await client.send("Hello Redis!")
    async for message in client:
        print(f"Received: {message}")
        break
```

## Configuration

```python
class RedisConfig:
    url: str
    consumer_group: Optional[str]
    consumer_name: Optional[str]
    max_len: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
```

## Stream Processing

```python
# Stream processing with acknowledgment
async with client:
    async for message in client:
        try:
            await process_message(message)
            await client.ack(message)
        except Exception:
            await client.nack(message)
```

## Consumer Groups

```python
import asyncio

# Create multiple consumers in the same group
consumers = [
    RedisClient(
        stream_name="my-stream",
        config=RedisConfig(
            url="redis://localhost:6379",
            consumer_group="my-group",
            consumer_name=f"consumer-{i}"
        )
    )
    for i in range(3)
]

# Start all consumers
async def process_messages(client):
    async with client:
        async for message in client:
            await process_message(message)
            await client.ack(message)

async def main():
    async with asyncio.TaskGroup() as tg:
        for consumer in consumers:
            tg.create_task(process_messages(consumer))

asyncio.run(main())
```
# Synchronous Redis Integration

## RedisClient

```python
from zephcast.sync.integration.redis import RedisClient
from zephcast.sync.integration.redis.config import RedisConfig

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
with client:
    client.send("Hello Redis!")
    for message in client:
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
with client:
    for message in client:
        try:
            process_message(message)
            client.ack(message)
        except Exception:
            client.nack(message)
```
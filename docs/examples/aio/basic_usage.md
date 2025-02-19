# Basic Asynchronous Usage Examples

## Kafka Example

```python
import asyncio
from zephcast.aio.integration.kafka import KafkaClient
from zephcast.aio.integration.kafka.config import KafkaConfig

async def kafka_example():
    client = KafkaClient(
        stream_name="my-topic",
        config=KafkaConfig(
            bootstrap_servers="localhost:9092"
        )
    )
    
    async with client:
        # Send message
        await client.send("Hello Kafka!")
        
        # Receive messages
        async for message in client:
            print(f"Received: {message}")
            break

if __name__ == "__main__":
    asyncio.run(kafka_example())
```

## Redis Example

```python
import asyncio
from zephcast.aio.integration.redis import RedisClient
from zephcast.aio.integration.redis.config import RedisConfig

async def redis_example():
    client = RedisClient(
        stream_name="my-stream",
        config=RedisConfig(
            url="redis://localhost:6379"
        )
    )
    
    async with client:
        # Send message
        await client.send("Hello Redis!")
        
        # Receive messages
        async for message in client:
            print(f"Received: {message}")
            break

if __name__ == "__main__":
    asyncio.run(redis_example())
```
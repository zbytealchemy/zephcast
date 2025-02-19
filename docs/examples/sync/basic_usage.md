# Basic Synchronous Usage Examples

## Kafka Example

```python
from zephcast.sync.integration.kafka import KafkaClient
from zephcast.sync.integration.kafka.config import KafkaConfig

def kafka_example():
    client = KafkaClient(
        stream_name="my-topic",
        config=KafkaConfig(
            bootstrap_servers="localhost:9092"
        )
    )
    
    with client:
        # Send message
        client.send("Hello Kafka!")
        
        # Receive messages
        for message in client:
            print(f"Received: {message}")
            break

if __name__ == "__main__":
    kafka_example()
```

## Redis Example

```python
from zephcast.sync.integration.redis import RedisClient
from zephcast.sync.integration.redis.config import RedisConfig

def redis_example():
    client = RedisClient(
        stream_name="my-stream",
        config=RedisConfig(
            url="redis://localhost:6379"
        )
    )
    
    with client:
        # Send message
        client.send("Hello Redis!")
        
        # Receive messages
        for message in client:
            print(f"Received: {message}")
            break

if __name__ == "__main__":
    redis_example()
```
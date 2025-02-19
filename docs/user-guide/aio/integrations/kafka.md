# Asynchronous Kafka Integration

## AsyncKafkaClient

```python
from zephcast.aio.kafka import KafkaClient
from zephcast.aio.kafka.config import KafkaConfig

config = KafkaConfig(
    bootstrap_servers="localhost:9092",
    group_id="my-group",
    auto_offset_reset="earliest"
)

client = KafkaClient(
    stream_name="my-topic",
    config=config
)

# Basic usage
async with client:  # Automatically connects and closes
    await client.send("Hello Kafka!")
    async for message in client:  # Uses receive() under the hood
        print(f"Received: {message}")
        break
```

## Configuration

```python
class KafkaConfig:
    bootstrap_servers: str
    group_id: Optional[str]
    auto_offset_reset: str = "latest"
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
```

## Consumer Groups

```python
# Create multiple consumers in the same group
consumers = [
    KafkaClient(
        stream_name="my-topic",
        config=KafkaConfig(
            bootstrap_servers="localhost:9092",
            group_id="my-group"
        )
    )
    for _ in range(3)
]

# Start all consumers
async with asyncio.TaskGroup() as tg:
    for consumer in consumers:
        tg.create_task(process_messages(consumer))
```
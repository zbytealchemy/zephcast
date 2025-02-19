# Synchronous Kafka Integration

## KafkaClient

```python
from zephcast.sync.integration.kafka import KafkaClient
from zephcast.sync.integration.kafka.config import KafkaConfig

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
with client:  # Automatically connects and closes
    client.send("Hello Kafka!")
    for message in client:  # Uses receive() under the hood
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
```
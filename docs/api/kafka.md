# Kafka API Reference

The Kafka client provides a high-level interface for working with Apache Kafka.

## Core Components

### AsyncKafkaClient

The main client class for interacting with Kafka.

```python
from zephyrflow.kafka.async_client import AsyncKafkaClient

client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    group_id="my-group"  # Optional
)
```

#### Methods

- `connect()` - Establish connection to Kafka
- `close()` - Close the connection
- `send(message)` - Send a message to the configured topic
- `receive()` - Async iterator for receiving messages

#### Configuration Options

- `stream_name` - Topic name
- `bootstrap_servers` - Kafka broker addresses
- `group_id` - Consumer group ID (optional)
- `security_protocol` - Security protocol (optional)
- `sasl_mechanism` - SASL mechanism (optional)
- `sasl_plain_username` - SASL username (optional)
- `sasl_plain_password` - SASL password (optional)

### Usage Example

```python
import asyncio
from zephyrflow.kafka.async_client import AsyncKafkaClient

async def kafka_example():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    await client.connect()
    
    try:
        # Send a message
        await client.send("Hello Kafka!")
        
        # Receive messages
        async for message in client.receive():
            print(f"Received: {message}")
            break
            
    finally:
        await client.close()

asyncio.run(kafka_example())

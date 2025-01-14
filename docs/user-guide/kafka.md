# Kafka Client Guide

The Kafka client in MsgFlow provides a high-level interface for working with Apache Kafka.

## Features

- Asynchronous message publishing and consumption
- Consumer group support
- SSL/SASL authentication
- Automatic reconnection
- Configurable batch sizes and compression

## Basic Usage

```python
from msgflow.kafka.async_client import AsyncKafkaClient

async def kafka_example():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    await client.connect()
    
    # Send a message
    await client.send("Hello Kafka!")
    
    # Receive messages
    async for message in client.receive():
        print(f"Received: {message}")
        break
    
    await client.close()
```

## Consumer Groups

```python
from msgflow.kafka.async_client import AsyncKafkaClient

async def consumer_group_example():
    consumer = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )
    
    await consumer.connect()
    
    async for message in consumer.receive():
        print(f"Consumer received: {message}")
    
    await consumer.close()
```

## Security Configuration

### SSL/TLS

```python
client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    security_protocol="SSL",
    ssl_cafile="/path/to/ca.pem",
    ssl_certfile="/path/to/cert.pem",
    ssl_keyfile="/path/to/key.pem"
)
```

### SASL

```python
client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username="user",
    sasl_plain_password="password"
)
```

## Performance Tuning

### Batch Configuration

```python
client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    batch_size=16384,
    linger_ms=10,
    compression_type="snappy"
)
```

### Consumer Configuration

```python
client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    fetch_max_bytes=52428800,
    max_partition_fetch_bytes=1048576
)
```

## Error Handling

```python
from msgflow.kafka.async_client import AsyncKafkaClient
from kafka.errors import KafkaError

async def error_handling_example():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    try:
        await client.connect()
        await client.send("test message")
    except KafkaError as e:
        print(f"Kafka error: {e}")
    finally:
        await client.close()
```

## Best Practices

1. Always use consumer groups in production
2. Configure appropriate batch sizes for your use case
3. Use compression for large messages or high throughput
4. Implement proper error handling and retries
5. Monitor consumer lag and broker health
6. Use SSL/SASL in production environments
7. Configure appropriate timeout values
8. Implement proper cleanup in finally blocks

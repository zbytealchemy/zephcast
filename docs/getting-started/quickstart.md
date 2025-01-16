# Quick Start Guide

This guide will help you get started with ZephyrFlow by walking through basic examples for each supported message broker.

## Basic Concepts

ZephyrFlow provides a unified interface for working with different message brokers. The main concepts are:

- **Client**: A connection to a message broker
- **Stream**: A named channel for sending/receiving messages
- **Producer**: Sends messages to a stream
- **Consumer**: Receives messages from a stream

## Async Iterator Pattern

All async clients in ZephyrFlow implement the async iterator pattern, which provides a clean and Pythonic way to work with message streams:

```python
# Using async context manager for automatic connection management
async with client:
    # Using async iterator for message consumption
    async for message in client:
        print(f"Received: {message}")
```

This pattern is equivalent to:

```python
# Manual connection management
await client.connect()
try:
    # Manual message consumption
    async for message in client.receive():
        print(f"Received: {message}")
finally:
    await client.close()
```

## Kafka Example

Here's a complete example of using ZephyrFlow with Kafka:

```python
import asyncio
from msgflow.kafka.async_client import AsyncKafkaClient

async def kafka_example():
    # Create a client
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    async with client:
        # Send some messages
        await client.send("Hello Kafka!")
        await client.send("Message 2")
        await client.send("Message 3")
        
        # Receive and process messages
        async for message in client:
            print(f"Received from Kafka: {message}")
            # Break after receiving 3 messages
            if message == "Message 3":
                break

# Run the example
asyncio.run(kafka_example())
```

## RabbitMQ Example

Here's how to use ZephyrFlow with RabbitMQ:

```python
import asyncio
from msgflow.rabbit.async_client import AsyncRabbitClient

async def rabbitmq_example():
    # Create a client
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    async with client:
        # Send some messages
        await client.send("Hello RabbitMQ!")
        await client.send("Message 2")
        await client.send("Message 3")
        
        # Receive and process messages
        async for message in client:
            print(f"Received from RabbitMQ: {message}")
            # Break after receiving 3 messages
            if message == "Message 3":
                break

# Run the example
asyncio.run(rabbitmq_example())
```

## Redis Example

Here's how to use ZephyrFlow with Redis Streams:

```python
import asyncio
from msgflow.redis.async_client import AsyncRedisClient

async def redis_example():
    # Create a client
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    async with client:
        # Send some messages
        await client.send("Hello Redis!")
        await client.send("Message 2")
        await client.send("Message 3")
        
        # Receive and process messages
        async for message in client:
            print(f"Received from Redis: {message}")
            # Break after receiving 3 messages
            if message == "Message 3":
                break

# Run the example
asyncio.run(redis_example())
```

## Consumer Groups Example

Here's an example of using consumer groups with Kafka:

```python
import asyncio
from msgflow.kafka.async_client import AsyncKafkaClient

async def consumer_group_example():
    # Create multiple consumers in the same group
    consumers = [
        AsyncKafkaClient(
            stream_name="my-topic",
            group_id="my-group",
            bootstrap_servers="localhost:9092"
        )
        for _ in range(3)
    ]
    
    async with asyncio.gather(*(asyncio.create_task(consumer.connect()) for consumer in consumers)):
        # Create a producer
        producer = AsyncKafkaClient(
            stream_name="my-topic",
            bootstrap_servers="localhost:9092"
        )
        await producer.connect()
        
        # Send some messages
        for i in range(10):
            await producer.send(f"Message {i}")
        
        # Process messages with multiple consumers
        async def consume(client, consumer_id):
            async for message in client:
                print(f"Consumer {consumer_id} received: {message}")
        
        # Run consumers concurrently
        await asyncio.gather(*(
            consume(consumer, i) 
            for i, consumer in enumerate(consumers)
        ))
        
    # Clean up
    await asyncio.gather(*(consumer.close() for consumer in consumers))
    await producer.close()

# Run the example
asyncio.run(consumer_group_example())
```

## Next Steps

- Learn about [Configuration Options](../user-guide/configuration.md)
- See [Advanced Usage](../advanced/consumer-groups.md)
- Check out the [API Reference](../api/kafka.md)

# RabbitMQ Client Guide

The RabbitMQ client in ZephyrFlow provides a high-level interface for working with RabbitMQ, supporting various messaging patterns.

## Features

- Asynchronous message publishing and consumption
- Exchange types (direct, fanout, topic, headers)
- Queue bindings and routing
- Message persistence
- Dead letter exchanges
- Publisher confirms
- Consumer acknowledgments

## Basic Usage

```python
from zephyrflow.rabbit.async_client import AsyncRabbitClient

async def rabbitmq_example():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    # Send a message
    await client.send("Hello RabbitMQ!")
    
    # Receive messages
    async for message in client.receive():
        print(f"Received: {message}")
        break
    
    await client.close()
```

## Exchange Types

### Direct Exchange

```python
client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    exchange_name="my-exchange",
    exchange_type="direct",
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)
```

### Fanout Exchange

```python
client = AsyncRabbitClient(
    stream_name="",  # Routing key not used in fanout
    queue_name="my-queue",
    exchange_name="my-fanout",
    exchange_type="fanout",
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)
```

### Topic Exchange

```python
client = AsyncRabbitClient(
    stream_name="user.created.*",  # Topic pattern
    queue_name="user-events",
    exchange_name="events",
    exchange_type="topic",
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)
```

## Message Persistence

```python
client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    exchange_name="my-exchange",
    exchange_durable=True,
    queue_durable=True,
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)
```

## Dead Letter Exchange

```python
client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    exchange_name="my-exchange",
    dead_letter_exchange="dlx",
    dead_letter_routing_key="failed",
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)
```

## Publisher Confirms

```python
from zephyrflow.rabbit.async_client import AsyncRabbitClient

async def publisher_confirms_example():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        publisher_confirms=True,
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    try:
        # Send with confirmation
        confirmation = await client.send("Important message")
        if confirmation:
            print("Message confirmed by broker")
    finally:
        await client.close()
```

## Consumer Acknowledgments

```python
from zephyrflow.rabbit.async_client import AsyncRabbitClient

async def consumer_acks_example():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        auto_ack=False,
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    try:
        async for message in client.receive():
            try:
                # Process message
                print(f"Processing: {message}")
                # Acknowledge success
                await client.ack(message)
            except Exception:
                # Negative acknowledge on failure
                await client.nack(message, requeue=True)
    finally:
        await client.close()
```

## Best Practices

1. Use appropriate exchange types for your messaging pattern
2. Enable message persistence for important data
3. Use publisher confirms for critical messages
4. Implement proper consumer acknowledgments
5. Configure dead letter exchanges for failed messages
6. Set appropriate QoS prefetch values
7. Monitor queue lengths and consumer health
8. Use SSL in production environments
9. Implement proper connection and channel cleanup

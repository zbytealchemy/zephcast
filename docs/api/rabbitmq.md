# RabbitMQ API Reference

The RabbitMQ client provides a high-level interface for working with RabbitMQ.

## Core Components

### AsyncRabbitClient

The main client class for interacting with RabbitMQ.

```python
from msgflow.rabbit.async_client import AsyncRabbitClient

client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    rabbitmq_url="amqp://guest:guest@localhost:5672/",
    exchange_name="my-exchange"  # Optional
)
```

#### Methods

- `connect()` - Establish connection to RabbitMQ
- `close()` - Close the connection
- `send(message)` - Send a message with the configured routing key
- `receive()` - Async iterator for receiving messages
- `ack(message)` - Acknowledge a message
- `nack(message, requeue=True)` - Negative acknowledge a message

#### Configuration Options

- `stream_name` - Routing key
- `queue_name` - Queue name
- `rabbitmq_url` - RabbitMQ connection URL
- `exchange_name` - Exchange name (optional)
- `exchange_type` - Exchange type (optional)
- `exchange_durable` - Exchange durability (optional)
- `queue_durable` - Queue durability (optional)
- `auto_ack` - Automatic acknowledgment (optional)
- `prefetch_count` - Consumer prefetch count (optional)

### Usage Example

```python
import asyncio
from msgflow.rabbit.async_client import AsyncRabbitClient

async def rabbitmq_example():
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    await client.connect()
    
    try:
        # Send a message
        await client.send("Hello RabbitMQ!")
        
        # Receive messages
        async for message in client.receive():
            print(f"Received: {message}")
            await client.ack(message)
            break
            
    finally:
        await client.close()

asyncio.run(rabbitmq_example())

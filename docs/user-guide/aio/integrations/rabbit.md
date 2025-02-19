# Asynchronous RabbitMQ Integration

## AsyncRabbitClient

```python
from zephcast.aio.integration.rabbit import RabbitClient
from zephcast.aio.integration.rabbit.config import RabbitConfig

config = RabbitConfig(
    url="amqp://guest:guest@localhost:5672/",
    queue_name="my-queue",
    exchange_name="my-exchange",
    routing_key="my-routing-key"
)

client = RabbitClient(
    stream_name="my-stream",
    config=config
)

# Basic usage
async with client:  # Automatically connects and closes
    await client.send("Hello RabbitMQ!")
    async for message in client:  # Uses receive() under the hood
        print(f"Received: {message}")
        break
```

## Configuration

```python
class RabbitConfig:
    url: str
    queue_name: str
    exchange_name: str
    routing_key: str
    exchange_type: str = "direct"
    durable: bool = True
    auto_delete: bool = False
    prefetch_count: int = 1
    ssl: bool = False
    ssl_options: Optional[Dict[str, Any]] = None
```

## Exchange Types

```python
# Direct Exchange
config = RabbitConfig(
    url="amqp://localhost",
    exchange_name="direct_exchange",
    exchange_type="direct",
    queue_name="direct_queue",
    routing_key="direct_key"
)

# Topic Exchange
config = RabbitConfig(
    url="amqp://localhost",
    exchange_name="topic_exchange",
    exchange_type="topic",
    queue_name="topic_queue",
    routing_key="orders.#"  # Matches orders.created, orders.updated, etc.
)

# Fanout Exchange
config = RabbitConfig(
    url="amqp://localhost",
    exchange_name="fanout_exchange",
    exchange_type="fanout",
    queue_name="fanout_queue",
    routing_key=""  # Routing key is ignored for fanout exchanges
)
```

## Consumer Groups

```python
import asyncio

# Create multiple consumers in the same queue
consumers = [
    RabbitClient(
        stream_name="my-stream",
        config=RabbitConfig(
            url="amqp://localhost",
            queue_name="shared_queue",  # Same queue name for all consumers
            exchange_name="my_exchange",
            routing_key="my_key"
        )
    )
    for _ in range(3)
]

# Start all consumers
async def process_messages(client):
    async with client:
        async for message in client:
            await process_message(message)
            await client.ack(message)

async def main():
    async with asyncio.TaskGroup() as tg:
        for consumer in consumers:
            tg.create_task(process_messages(consumer))

asyncio.run(main())
```

## Message Acknowledgment

```python
async with client:
    async for message in client:
        try:
            await process_message(message)
            await client.ack(message)  # Acknowledge successful processing
        except Exception:
            await client.nack(message)  # Negative acknowledgment, message will be requeued
```
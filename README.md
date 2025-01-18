# ZephCast

ZephCast is a powerful and flexible messaging library that provides a unified interface for working with multiple message brokers. It currently supports Kafka, RabbitMQ, and Redis, offering both synchronous and asynchronous clients.

## Features

- **Multiple Broker Support**: 
  - Apache Kafka
  - RabbitMQ
  - Redis Streams
- **Unified Interface**: Consistent API across all message brokers
- **Async Support**: Native async/await support for all clients
- **Type Safety**: Full type hints support
- **Error Handling**: Robust error handling and recovery mechanisms
- **Consumer Groups**: Support for consumer groups in Kafka and RabbitMQ
- **Exchange Bindings**: Advanced RabbitMQ exchange and queue bindings
- **Stream Processing**: Redis Streams support for stream processing

## Requirements

- Python 3.8+
- Redis 5.0+ (for Redis Streams support)
- Kafka 2.0+
- RabbitMQ 3.8+

## Installation

```bash
# Install with poetry (recommended)
poetry add zephcast

# Install with pip
pip install zephcast
```

## Quick Start

### Async Iterator Pattern

All async clients in ZephCast:w
 implement the async iterator pattern, allowing you to use them in async for loops:

```python
async with client:  # Automatically connects and closes
    async for message in client:  # Uses receive() under the hood
        print(f"Received: {message}")
```

### Kafka Example

```python
from zephcast.kafka.async_client import AsyncKafkaClient

async def kafka_example():
    # Create a client
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    # Using async context manager
    async with client:
        # Send messages
        await client.send("Hello Kafka!")
        
        # Receive messages
        async for message in client:
            print(f"Received: {message}")
```

### RabbitMQ Example

```python
from zephcast.rabbit.async_client import AsyncRabbitClient

async def rabbitmq_example():
    # Create a client
    client = AsyncRabbitClient(
        stream_name="my-routing-key",
        queue_name="my-queue",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    # Connect
    await client.connect()
    
    # Send messages
    await client.send("Hello RabbitMQ!")
    
    # Receive messages
    async for message in client.receive():
        print(f"Received: {message}")
        break
    
    # Close connection
    await client.close()
```

### Redis Example

```python
from zephcast.redis.async_client import AsyncRedisClient

async def redis_example():
    # Create a client
    client = AsyncRedisClient(
        stream_name="my-stream",
        redis_url="redis://localhost:6379"
    )
    
    # Connect
    await client.connect()
    
    # Send messages
    await client.send("Hello Redis!")
    
    # Receive messages
    async for message in client.receive():
        print(f"Received: {message}")
        break
    
    # Close connection
    await client.close()
```

## Configuration

### Environment Variables

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka bootstrap servers (default: "localhost:9092")
- `RABBITMQ_URL`: RabbitMQ connection URL (default: "amqp://guest:guest@localhost:5672/")
- `REDIS_URL`: Redis connection URL (default: "redis://localhost:6379")

### Client Configuration

Each client accepts additional configuration parameters:

#### Kafka Client
- `group_id`: Consumer group ID
- `auto_offset_reset`: Offset reset strategy
- `security_protocol`: Security protocol
- `sasl_mechanism`: SASL mechanism
- `sasl_plain_username`: SASL username
- `sasl_plain_password`: SASL password

#### RabbitMQ Client
- `exchange_name`: Exchange name
- `exchange_type`: Exchange type
- `routing_key`: Routing key
- `queue_name`: Queue name
- `durable`: Queue durability
- `auto_delete`: Auto-delete queue

#### Redis Client
- `stream_max_len`: Maximum stream length
- `consumer_group`: Consumer group name
- `consumer_name`: Consumer name
- `block_ms`: Blocking time in milliseconds

## Advanced Usage

### Consumer Groups

```python
# Kafka Consumer Group
client = AsyncKafkaClient(
    stream_name="my-topic",
    group_id="my-group",
    bootstrap_servers="localhost:9092"
)

# RabbitMQ Consumer Group
client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    consumer_group="my-group",
    rabbitmq_url="amqp://guest:guest@localhost:5672/"
)

# Redis Consumer Group
client = AsyncRedisClient(
    stream_name="my-stream",
    consumer_group="my-group",
    redis_url="redis://localhost:6379"
)
```

### Error Handling

```python
try:
    await client.connect()
    await client.send("message")
except ConnectionError:
    # Handle connection errors
    pass
except TimeoutError:
    # Handle timeout errors
    pass
except Exception as e:
    # Handle other errors
    pass
finally:
    await client.close()
```

## Development

### Prerequisites

- Python 3.10+
- Poetry
- Docker (for running integration tests)

### Setup

```bash
# Clone the repository
git clone https://github.com/zbytealchemy/zephcast.git
cd zephcast

# Install dependencies
poetry install

# Run tests
poetry run pytest
```

### Running Integration Tests

Start the required services:

```bash
docker-compose up -d
```

Run the integration tests:

```bash
poetry run pytest tests/integration
```

## Contributing

We use rebase workflow for pull requests and allow no more then 2 commits per PR.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Apache Kafka](https://kafka.apache.org/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Redis](https://redis.io/)
- [aiokafka](https://github.com/aio-libs/aiokafka)
- [aio-pika](https://github.com/mosquito/aio-pika)
- [redis-py](https://github.com/redis/redis-py)

# Configuration Guide

MsgFlow provides flexible configuration options for each message broker. This guide covers all available configuration options and best practices.

## Environment Variables

MsgFlow supports configuration through environment variables:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your-username
KAFKA_SASL_PASSWORD=your-password

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_EXCHANGE_TYPE=direct
RABBITMQ_EXCHANGE_DURABLE=true
RABBITMQ_QUEUE_DURABLE=true

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0
REDIS_MAX_CONNECTIONS=10
```

## Client Configuration

### Kafka Client

```python
from msgflow.kafka.async_client import AsyncKafkaClient

client = AsyncKafkaClient(
    stream_name="my-topic",
    bootstrap_servers="localhost:9092",
    group_id="my-group",  # Optional: for consumer groups
    security_protocol="PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="your-username",
    sasl_plain_password="your-password"
)
```

### RabbitMQ Client

```python
from msgflow.rabbit.async_client import AsyncRabbitClient

client = AsyncRabbitClient(
    stream_name="my-routing-key",
    queue_name="my-queue",
    rabbitmq_url="amqp://guest:guest@localhost:5672/",
    exchange_name="my-exchange",  # Optional
    exchange_type="direct",  # Optional
    exchange_durable=True,  # Optional
    queue_durable=True  # Optional
)
```

### Redis Client

```python
from msgflow.redis.async_client import AsyncRedisClient

client = AsyncRedisClient(
    stream_name="my-stream",
    redis_url="redis://localhost:6379",
    db=0,  # Optional
    max_connections=10  # Optional
)
```

## Best Practices

1. **Environment Variables**: Use environment variables for sensitive information like credentials
2. **Connection Pooling**: Configure appropriate connection pool sizes for your use case
3. **Error Handling**: Set appropriate timeout and retry configurations
4. **Security**: Always use secure connections in production
5. **Monitoring**: Enable metrics collection for production monitoring

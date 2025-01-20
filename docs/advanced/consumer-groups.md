# Consumer Groups

Consumer groups allow multiple consumers to work together to process messages from a stream. Each message is delivered to only one consumer in the group.

## Overview

Consumer groups are supported by all three message brokers in ZephCast:

- Kafka: Native consumer groups
- RabbitMQ: Competing consumers pattern
- Redis: Stream consumer groups

## Kafka Consumer Groups

```python
import asyncio
from zephcast.kafka.async_client import AsyncKafkaClient

async def kafka_consumer_group():
    consumers = [
        AsyncKafkaClient(
            stream_name="my-topic",
            group_id="my-group",
            bootstrap_servers="localhost:9092"
        )
        for _ in range(3)
    ]
    
    await asyncio.gather(*(consumer.connect() for consumer in consumers))
    
    try:
        async def consume(client, consumer_id):
            async for message in client.receive():
                print(f"Consumer {consumer_id} received: {message}")
        
        await asyncio.gather(*(
            consume(consumer, i) 
            for i, consumer in enumerate(consumers)
        ))
    finally:
        await asyncio.gather(*(consumer.close() for consumer in consumers))
```

## RabbitMQ Competing Consumers

```python
import asyncio
from zephcast.rabbit.async_client import AsyncRabbitClient

async def rabbitmq_competing_consumers():
    consumers = [
        AsyncRabbitClient(
            stream_name="task-queue",
            queue_name="shared-queue",
            rabbitmq_url="amqp://guest:guest@localhost:5672/"
        )
        for _ in range(3)
    ]
    
    await asyncio.gather(*(consumer.connect() for consumer in consumers))
    
    try:
        async def consume(client, consumer_id):
            async for message in client.receive():
                print(f"Worker {consumer_id} processing: {message}")
                await asyncio.sleep(1)  # Simulate work
        
        await asyncio.gather(*(
            consume(consumer, i) 
            for i, consumer in enumerate(consumers)
        ))
    finally:
        await asyncio.gather(*(consumer.close() for consumer in consumers))
```

## Redis Stream Consumer Groups

```python
import asyncio
from zephcast.redis.async_client import AsyncRedisClient

async def redis_consumer_group():
    consumers = [
        AsyncRedisClient(
            stream_name="my-stream",
            consumer_group="my-group",
            consumer_name=f"consumer-{i}",
            redis_url="redis://localhost:6379"
        )
        for i in range(3)
    ]
    
    await asyncio.gather(*(consumer.connect() for consumer in consumers))
    
    try:
        async def consume(client, consumer_id):
            async for message in client.receive():
                print(f"Consumer {consumer_id} received: {message}")
                await client.ack(message)
        
        await asyncio.gather(*(
            consume(consumer, i) 
            for i, consumer in enumerate(consumers)
        ))
    finally:
        await asyncio.gather(*(consumer.close() for consumer in consumers))
```

## Best Practices

### Scaling

1. Start with a small number of consumers
2. Monitor processing throughput
3. Add consumers gradually as needed
4. Consider message ordering requirements

### Message Processing

1. Implement idempotent processing
2. Handle message failures gracefully
3. Consider using dead letter queues
4. Implement proper acknowledgment

### Monitoring

1. Track consumer lag
2. Monitor processing rates
3. Set up alerts for stuck consumers
4. Track message processing times

### Error Handling

1. Implement retry logic
2. Use dead letter exchanges/queues
3. Log failed messages
4. Monitor error rates

## Common Issues

### Message Ordering

When using consumer groups, message ordering is only guaranteed within a single partition (Kafka) or stream (Redis). If ordering is critical:

1. Use a single consumer
2. Use partition keys (Kafka)
3. Use separate queues (RabbitMQ)

### Rebalancing

When consumers join or leave the group, messages may be rebalanced:

1. Implement graceful shutdown
2. Handle duplicate messages
3. Use appropriate session timeouts
4. Monitor rebalancing events

### Performance

To optimize performance:

1. Tune batch sizes
2. Configure appropriate timeouts
3. Use connection pooling
4. Monitor resource usage

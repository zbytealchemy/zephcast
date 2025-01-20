# Examples

This page provides practical examples of using ZephCast in different scenarios.

## Basic Usage

### Simple Producer/Consumer

```python
import asyncio
from zephcast.kafka.async_client import AsyncKafkaClient

async def basic_example():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    try:
        await client.connect()
        
        await client.send("Hello, World!")
        
        async for message in client.receive():
            print(f"Received: {message}")
            break
            
    finally:
        await client.close()

asyncio.run(basic_example())
```

## Advanced Patterns

### Fan-out Pattern

```python
import asyncio
from zephcast.rabbit.async_client import AsyncRabbitClient

async def fan_out_example():
    producer = AsyncRabbitClient(
        stream_name="notifications",
        exchange_name="notifications",
        exchange_type="fanout",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    consumers = [
        AsyncRabbitClient(
            stream_name="notifications",
            queue_name=f"consumer-{i}",
            exchange_name="notifications",
            exchange_type="fanout",
            rabbitmq_url="amqp://guest:guest@localhost:5672/"
        )
        for i in range(3)
    ]
    
    try:
        await producer.connect()
        await asyncio.gather(*(consumer.connect() for consumer in consumers))
        
        await producer.send("Broadcast message")
        
        async def consume(client, consumer_id):
            async for message in client.receive():
                print(f"Consumer {consumer_id} received: {message}")
                break
        
        await asyncio.gather(*(
            consume(consumer, i) 
            for i, consumer in enumerate(consumers)
        ))
        
    finally:
        await producer.close()
        await asyncio.gather(*(consumer.close() for consumer in consumers))

asyncio.run(fan_out_example())
```

### Pub/Sub Pattern with Redis

```python
import asyncio
from zephcast.redis.async_client import AsyncRedisClient

async def pub_sub_example():
    publisher = AsyncRedisClient(
        stream_name="news-feed",
        redis_url="redis://localhost:6379"
    )
    
    subscribers = [
        AsyncRedisClient(
            stream_name="news-feed",
            consumer_group=f"group-{i}",
            redis_url="redis://localhost:6379"
        )
        for i in range(2)
    ]
    
    try:
        await publisher.connect()
        await asyncio.gather(*(sub.connect() for sub in subscribers))
        
        await publisher.send("Breaking news!")
        
        async def subscribe(client, sub_id):
            async for message in client.receive():
                print(f"Subscriber {sub_id} received: {message}")
                break
        
        await asyncio.gather(*(
            subscribe(sub, i) 
            for i, sub in enumerate(subscribers)
        ))
        
    finally:
        await publisher.close()
        await asyncio.gather(*(sub.close() for sub in subscribers))

asyncio.run(pub_sub_example())
```

## Error Handling

### Retry Pattern

```python
import asyncio
from zephcast.kafka.async_client import AsyncKafkaClient

async def retry_example():
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            await client.connect()
            await client.send("Test message")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(retry_delay * (attempt + 1))
    
    await client.close()

asyncio.run(retry_example())
```

## Integration Patterns

### Message Transformation

```python
import asyncio
import json
from zephcast.kafka.async_client import AsyncKafkaClient

async def transform_example():
    source = AsyncKafkaClient(
        stream_name="raw-data",
        bootstrap_servers="localhost:9092"
    )
    
    destination = AsyncKafkaClient(
        stream_name="processed-data",
        bootstrap_servers="localhost:9092"
    )
    
    try:
        await source.connect()
        await destination.connect()
        
        async for message in source.receive():
            try:
                data = json.loads(message)
                transformed = {
                    "id": data["id"],
                    "timestamp": data["timestamp"],
                    "value": data["value"] * 2 
                }
                await destination.send(json.dumps(transformed))
            except json.JSONDecodeError:
                print(f"Invalid JSON: {message}")
            except KeyError as e:
                print(f"Missing key: {e}")
    
    finally:
        await source.close()
        await destination.close()

asyncio.run(transform_example())
```

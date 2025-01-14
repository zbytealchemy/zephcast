# Examples

This page provides practical examples of using MsgFlow in different scenarios.

## Basic Usage

### Simple Producer/Consumer

```python
import asyncio
from msgflow.kafka.async_client import AsyncKafkaClient

async def basic_example():
    # Create a client
    client = AsyncKafkaClient(
        stream_name="my-topic",
        bootstrap_servers="localhost:9092"
    )
    
    try:
        # Connect
        await client.connect()
        
        # Send a message
        await client.send("Hello, World!")
        
        # Receive messages
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
from msgflow.rabbit.async_client import AsyncRabbitClient

async def fan_out_example():
    # Create a producer
    producer = AsyncRabbitClient(
        stream_name="notifications",
        exchange_name="notifications",
        exchange_type="fanout",
        rabbitmq_url="amqp://guest:guest@localhost:5672/"
    )
    
    # Create multiple consumers
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
        # Connect all clients
        await producer.connect()
        await asyncio.gather(*(consumer.connect() for consumer in consumers))
        
        # Send a message
        await producer.send("Broadcast message")
        
        # Receive on all consumers
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
from msgflow.redis.async_client import AsyncRedisClient

async def pub_sub_example():
    # Create publisher and subscribers
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
        # Connect all clients
        await publisher.connect()
        await asyncio.gather(*(sub.connect() for sub in subscribers))
        
        # Publish messages
        await publisher.send("Breaking news!")
        
        # Subscribe and receive
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
from msgflow.kafka.async_client import AsyncKafkaClient

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
from msgflow.kafka.async_client import AsyncKafkaClient

async def transform_example():
    # Create source and destination clients
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
        
        # Process and transform messages
        async for message in source.receive():
            # Transform the message
            try:
                data = json.loads(message)
                transformed = {
                    "id": data["id"],
                    "timestamp": data["timestamp"],
                    "value": data["value"] * 2  # Some transformation
                }
                # Send transformed message
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

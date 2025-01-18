# Testing Guide

This guide covers testing practices and guidelines for ZephCast.

## Test Structure

```
tests/
├── unit/
│   ├── test_kafka.py
│   ├── test_rabbitmq.py
│   └── test_redis.py
└── integration/
    ├── conftest.py
    ├── test_kafka.py
    ├── test_rabbitmq.py
    └── test_redis.py
```

## Running Tests

### All Tests

```bash
make test
```

### Unit Tests Only

```bash
make unit-test
```

### Integration Tests Only

```bash
make integration-test
```

## Test Configuration

### pytest Configuration

The `pyproject.toml` file contains pytest configuration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
testpaths = ["tests"]
timeout = 30
```

### Environment Variables

Set these environment variables for integration tests:

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Redis
REDIS_URL=redis://localhost:6379
```

## Writing Tests

### Unit Tests

```python
import pytest
from zephcast.kafka.async_client import AsyncKafkaClient

@pytest.mark.asyncio
async def test_kafka_client_creation():
    client = AsyncKafkaClient(
        stream_name="test-topic",
        bootstrap_servers="localhost:9092"
    )
    assert client.stream_name == "test-topic"
    assert client.bootstrap_servers == "localhost:9092"
```

### Integration Tests

```python
import pytest
from zephcast.rabbit.async_client import AsyncRabbitClient

@pytest.mark.asyncio
async def test_rabbitmq_send_receive(rabbitmq_async_client):
    # Send message
    await rabbitmq_async_client.send("test message")
    
    # Receive message
    async for message in rabbitmq_async_client.receive():
        assert message == "test message"
        break
```

### Test Fixtures

```python
import pytest
from zephcast.redis.async_client import AsyncRedisClient

@pytest.fixture
async def redis_client():
    client = AsyncRedisClient(
        stream_name="test-stream",
        redis_url="redis://localhost:6379"
    )
    await client.connect()
    yield client
    await client.close()
```

## Test Categories

### Functional Tests

Test basic functionality:

```python
@pytest.mark.asyncio
async def test_basic_functionality(kafka_client):
    # Test sending and receiving
    message = "test message"
    await kafka_client.send(message)
    
    async for received in kafka_client.receive():
        assert received == message
        break
```

### Error Tests

Test error conditions:

```python
@pytest.mark.asyncio
async def test_connection_error():
    client = AsyncKafkaClient(
        stream_name="test-topic",
        bootstrap_servers="invalid:9092"
    )
    
    with pytest.raises(Exception):
        await client.connect()
```

### Performance Tests

Test performance characteristics:

```python
import asyncio
import time

@pytest.mark.asyncio
async def test_batch_performance(kafka_client):
    start_time = time.time()
    message_count = 1000
    
    # Send batch of messages
    for i in range(message_count):
        await kafka_client.send(f"message-{i}")
    
    # Calculate throughput
    elapsed = time.time() - start_time
    rate = message_count / elapsed
    assert rate > 100  # Messages per second
```

## Test Best Practices

### 1. Test Isolation

- Use unique resource names per test
- Clean up resources after tests
- Don't rely on test execution order

### 2. Async Testing

- Use `pytest.mark.asyncio`
- Handle async cleanup properly
- Set appropriate timeouts

### 3. Error Handling

- Test both success and failure paths
- Verify error messages
- Test timeout scenarios

### 4. Resource Management

- Use fixtures for setup/teardown
- Clean up resources in finally blocks
- Handle connection cleanup

### 5. Test Organization

- Group related tests in classes
- Use descriptive test names
- Keep tests focused and small

## Continuous Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      kafka:
        image: confluentinc/cp-kafka
      rabbitmq:
        image: rabbitmq:3-management
      redis:
        image: redis
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: poetry run pytest
```

## Test Coverage

### Running Coverage

```bash
poetry run pytest --cov=zephcast
```

### Coverage Report

```bash
poetry run pytest --cov=zephcast --cov-report=html
```

## Debugging Tests

### Using pdb

```python
@pytest.mark.asyncio
async def test_with_debugger():
    import pdb; pdb.set_trace()
    # Test code here
```

### Verbose Output

```bash
poetry run pytest -v --tb=long
```

## Common Issues

1. **Hanging Tests**
   - Use timeouts
   - Check for unclosed resources
   - Verify async cleanup

2. **Flaky Tests**
   - Add retries for network operations
   - Use unique resource names
   - Handle race conditions

3. **Resource Leaks**
   - Use context managers
   - Clean up in finally blocks
   - Monitor resource usage

# Installation Guide

## Prerequisites

Before installing MsgFlow, ensure you have:

- Python 3.10 or higher
- pip or poetry for package management
- (Optional) Docker for running message brokers locally

## Installation Methods

### Using Poetry (Recommended)

Poetry is the recommended way to install MsgFlow as it provides better dependency management:

```bash
# Install poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install MsgFlow
poetry add msgflow
```

### Using pip

You can also install MsgFlow using pip:

```bash
pip install msgflow
```

## Installing Optional Dependencies

MsgFlow supports different message brokers. You can install only the dependencies you need:

```bash
# For Kafka support
poetry add msgflow[kafka]

# For RabbitMQ support
poetry add msgflow[rabbitmq]

# For Redis support
poetry add msgflow[redis]

# For all message brokers
poetry add msgflow[all]
```

## Setting Up Message Brokers

### Local Development

For local development, you can use Docker to run the message brokers:

```bash
# Create a docker-compose.yml file
cat > docker-compose.yml << EOL
version: '3'
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
EOL

# Start the services
docker-compose up -d
```

### Production Setup

For production, you'll want to use managed services or proper cluster setups:

- **Kafka**: [Confluent Cloud](https://www.confluent.io/confluent-cloud/) or self-hosted cluster
- **RabbitMQ**: [CloudAMQP](https://www.cloudamqp.com/) or self-hosted cluster
- **Redis**: [Redis Cloud](https://redis.com/redis-enterprise-cloud/) or self-hosted cluster

## Verifying Installation

You can verify your installation by running:

```python
import msgflow
print(msgflow.__version__)
```

Or by running the test suite:

```bash
poetry run pytest
```

## Next Steps

- Check out the [Quick Start Guide](quickstart.md)
- Learn about [Configuration](../user-guide/configuration.md)
- See [Examples](../user-guide/examples.md)

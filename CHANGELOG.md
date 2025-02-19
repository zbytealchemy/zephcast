# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Placeholder for changes since the `v1.0.0` release.

## [1.0.0] - 2025-01-25
### Added
- New project structure separating sync and async implementations
- Dedicated `sync` package for all synchronous operations
- Dedicated `aio` package for all asynchronous operations
- Migration guide for upgrading from v0.5.0 to v1.0.0

### Changed
- **BREAKING**: Moved all synchronous code to `zephcast.sync` package
- **BREAKING**: Moved all asynchronous code to `zephcast.aio` package
- **BREAKING**: Reorganized integration packages under respective sync/async directories
- Core utilities and interfaces now live in `zephcast.core` package

### Migration Guide
#### Importing Sync Clients
Before:
```python
from zephcast.kafka import KafkaClient
from zephcast.redis import RedisClient
from zephcast.rabbit import RabbitClient
```

After:
```python
from zephcast.sync.integration.kafka import KafkaClient
from zephcast.sync.integration.redis import RedisClient
from zephcast.sync.integration.rabbit import RabbitClient
```

#### Importing Async Clients
Before:
```python
from zephcast.kafka import AsyncKafkaClient
from zephcast.redis import AsyncRedisClient
from zephcast.rabbit import AsyncRabbitClient
```

After:
```python
from zephcast.aio.integration.kafka import KafkaClient
from zephcast.aio.integration.redis import RedisClient
from zephcast.aio.integration.rabbit import RabbitClient
```

#### Core Utilities
Before:
```python
from zephcast.retry import retry
from zephcast.consumers import consumer
```

After:
```python
from zephcast.core.retry import retry
from zephcast.sync.consumer import consumer  # for sync consumer
from zephcast.aio.consumer import consumer   # for async consumer
```

## [0.5.0] - 2025-01-18
### Added
- Support for multiple message brokers:
  - Apache Kafka client
  - RabbitMQ client
  - Redis Streams client
- Async and sync client implementations.
- Unified interface across all message brokers.
- Consumer groups support for Kafka and RabbitMQ.
- Advanced RabbitMQ exchange and queue bindings.
- Redis Streams support for stream processing.
- Comprehensive documentation.
- Full test suite with unit and integration tests.
- CI/CD pipeline with GitHub Actions.
- Type hints and mypy support.
- Code formatting with `ruff`.
- Pre-commit hooks configuration.

### Changed
- None.

### Deprecated
- None.

### Removed
- None.

### Fixed
- None.

### Security
- None.

## Notes
Releases `0.1.0` to `0.4.0` were experimental and are considered insignificant. These versions may be yanked from PyPI in the future. The `0.5.0` release marks the first stable release of the project.

[Unreleased]: https://github.com/zbytealchemy/zephcast/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/zbytealchemy/zephcast/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/zbytealchemy/zephcast/releases/tag/v0.5.0

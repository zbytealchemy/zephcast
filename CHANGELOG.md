# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Placeholder for changes since the `v0.5.0` release.

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

[Unreleased]: https://github.com/zbytealchemy/zephcast/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/zbytealchemy/zephcast/releases/tag/v0.5.0
# Contributing Guide

Thank you for your interest in contributing to MsgFlow! This guide will help you get started with contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/zephcast.git
cd zephcast
```

2. Install development dependencies:
```bash
poetry install
```

3. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

## Running Tests

### Unit Tests

```bash
poetry run pytest tests/unit
```

### Integration Tests

First, start the required services:

```bash
docker-compose up -d
```

Then run the tests:

```bash
poetry run pytest tests/integration
```

## Code Style

We use `ruff` for code formatting and linting:

```bash
# Format code
poetry run ruff format .

# Run linting
poetry run ruff check .
```

## Documentation

### Building Documentation

```bash
# Build documentation
poetry run mkdocs build

# Serve documentation locally
poetry run mkdocs serve
```

### Writing Documentation

- Use clear and concise language
- Include code examples
- Document all public APIs
- Add docstrings to all public functions and classes
- Keep the documentation up to date with code changes

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature/fix
3. Make your changes
4. Add/update tests
5. Update documentation
6. Run tests and linting
7. Submit a pull request

### Pull Request Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with `ruff`
- [ ] All tests passing
- [ ] No linting errors
- [ ] Changelog updated (if applicable)

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. GitHub Actions will automatically publish to PyPI

## Project Structure

```
zephcast/
├── src/
│   └── zephcast/
│       ├── kafka/
│       ├── rabbit/
│       └── redis/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── examples/
└── pyproject.toml
```

## Design Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write descriptive variable names
- Keep functions focused and small
- Document complex logic

### API Design

- Keep interfaces consistent across message brokers
- Use async/await for all I/O operations
- Provide sensible defaults
- Make configuration explicit
- Handle errors gracefully

### Testing

- Write unit tests for all functionality
- Include integration tests for each message broker
- Test error conditions
- Use fixtures for common setup
- Keep tests focused and readable

## Community

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and discussions
- Code of Conduct: Be respectful and inclusive

## License

MsgFlow is licensed under the MIT License. By contributing to MsgFlow, you agree to license your contributions under the same license.

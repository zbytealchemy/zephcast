# Contributing Guide

Thank you for your interest in contributing to ZephCast! This guide will help you get started with contributing to the project.

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
make unit-test
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

We use `ruff` for code formatting and linting and `mypy` for type checking:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check
```

## Documentation

### Building Documentation

```bash
# Build documentation
make docs
# Serve documentation locally
make docs-serve
```

### Writing Documentation

- Use clear and concise language
- Include code examples
- Document all public APIs
- Add docstrings to all public functions and classes
- Keep the documentation up to date with code changes

### No Need to Change These Files

Unless you have a very good reason, do NOT make any changes to the following files:
- docs/index.md
- .editorconfig
- .pre-commit-config.yml
- .readthedocs.yml
- dockercompose.yml
- LICENSE
- Makefile
- mkdocs.yml

If you believe a change is necessary, please discuss it in an issue or pull request before making any modifications.

## Pull Request Process

1. Fork the repository.
2. Create a new branch for your feature/fix.
   -Branch naming convention: Use the format issues/Issue-Number-Description. 
    For example, issues/5-fix-kafka-client.
3. Ensure each pull request is associated with a GitHub issue.
4. Make your changes.
   - Commit messages must follow the format: 
     Issue-IssueNumber: Description of the change. 
     For example, Issue-5: Fixed Kafka client reconnection logic.
   - Limit the number of commits in a pull request to 2.
5. Add/update tests.
6. Update documentation when necessary.
7. Run tests and linting.
8. Push to the branch.
9. Create a new pull request.

### Pull Request Checklist

Ensure the following before submitting a pull request:

- [ ] Tests added/updated
- [ ] Documentation updated when needed
- [ ] Code formatted with `ruff`
- [ ] Code linting passes
- [ ] Type checking passes
- [ ] All tests passing
- [ ] Changelog updated (if applicable)
- [ ] Branch is rebased on latest `main`
- [ ] No more than 2 commits per pull request
- [ ] Pull request associated with a GitHub issue
- [ ] Commit messages follow the format: `Issue-IssueNumber: Description of the change`

## Release Process

1. **Update Version**:
   - Update the version in `pyproject.toml` to reflect the new release version.
   - Update the `__version__` attribute in `src/zephcast/__init__.py` to match the version in `pyproject.toml`.

2. **Update Changelog**:
   - Add a new section in `CHANGELOG.md` for the release.
   - Document all notable changes, enhancements, bug fixes, and other updates.

3. **Create a Pull Request**:
   - Ensure all changes, including version updates and changelog modifications, are committed to a feature branch.
   - Submit a pull request targeting the `main` branch for review.
   - Follow the PR guidelines, ensuring:
     - The branch is rebased on the latest `main`.
     - All tests pass.
     - The pull request is associated with a GitHub issue.
     - The pull request includes no more than 2 commits.

4. **Enable the `RELEASE_FLAG` After Approval**:
   - Once the pull request is approved and merged into `main`, verify that:
     - The build pipeline has successfully completed.
     - All CI/CD checks have passed.
   - Contact the repository owner, **[zmastylo](https://github.com/zmastylo)**, to enable the `RELEASE_FLAG`.

5. **Manually Trigger the Publish Step**:
   - After the `RELEASE_FLAG` is enabled, the **publish** step in the CI/CD pipeline can be triggered manually.
   - This step will:
     - Automatically tag the release with the version from `pyproject.toml`.
     - Build the package.
     - Publish the package to PyPI.

6. **Verify the Release**:
   - Check that the package is available on PyPI.
   - Verify that the changelog, tags, and documentation reflect the new release version.

## Project Structure

```
zephcast/
|--.github/
│   └── workflows/
|── docs/
|-- src/
│   ├── __init__.py
│   ├── core/
│   ├── kafka/
│   ├── rabbit/
│   └── redis/
|   └── testing/
|-- tests/
|   |── __init__.py
|   ├── unit/
|   └── integration/
|-- .editorconfig
|-- .gitignore
|-- .pre-commit-config.yaml
|-- .readthedocs.yml
|-- docker-compose.yml
|-- LICENSE
|-- Makefile
|-- mkdocs.yml
└── pyproject.toml
|-- README.md
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

ZephCast is licensed under the MIT License. By contributing to ZephCast, you agree to license your contributions under the same license.

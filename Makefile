.PHONY: help install test lint format clean docs docs-serve integration-test

help:
	@echo "Available commands:"
	@echo "make install      - Install dependencies"
	@echo "make test        - Run all tests"
	@echo "make unit-test   - Run unit tests only"
	@echo "make integration-test - Run integration tests only"
	@echo "make lint        - Run linting"
	@echo "make format      - Format code"
	@echo "make clean       - Clean build artifacts"
	@echo "make docs        - Build documentation"
	@echo "make docs-serve  - Serve documentation locally"

lock:
	poetry lock

install: lock
	poetry install

install-dev: lock
	poetry install --with dev

install-all: lock
	poetry install --with dev
	poetry install --with test

test: unit-test integration-test

unit-test:
	poetry run pytest tests/unit --cov=zephcast --cov-report=term-missing

integration-test:
	poetry run pytest tests/integration -v

lint:
	poetry run ruff check .

format:
	poetry run ruff --fix .

type-check:
	poetry run mypy src tests

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf site
	find . -type d -name __pycache__ -exec rm -rf {} +

cache-purge:  ## Clean up Poetry cache
	poetry cache clear . --all
	rm -rf ~/Library/Caches/pypoetry
	rm -rf ~/.cache/pypoetry
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf .tox
	rm poetry.lock

clear-all: cache-purge clean
	poetry env remove --all

docs:
	poetry run mkdocs build

docs-serve:
	poetry run mkdocs serve

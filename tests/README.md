# Obelisk Test Suite

This directory contains the test suite for the Obelisk project with the new src-layout pattern.

## Directory Structure

```
tests/
├── conftest.py                    # Shared test fixtures and configuration
├── data/                          # Test data for all tests
├── unit/                          # Unit tests
│   ├── cli/                       # CLI tests
│   ├── core/                      # Core module tests
│   └── rag/                       # RAG unit tests
├── integration/                   # Integration tests
│   └── rag/                       # RAG integration tests
└── e2e/                           # End-to-end tests
```

## Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the interaction between multiple components
- **End-to-End Tests**: Test the entire system as a whole

## Running Tests

To run the tests, use pytest:

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/rag/test_document.py

# Run specific test function
poetry run pytest tests/unit/rag/test_document.py::test_process_file

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=src
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These include:

- `temp_dir`: Creates a temporary directory for tests
- `sample_vault`: Creates a sample vault with test content
- `vector_db_dir`: Creates a temporary vector database directory
- `mock_rag_config`: Creates a mock RAG configuration for testing

## Test Environment Variables

The following environment variables can be used to control test behavior:

- `SKIP_CLI_TESTS=1`: Skip tests that require CLI execution
- `SKIP_OLLAMA_TESTS=1`: Skip tests that require a running Ollama server
- `TEST_OLLAMA_URL`: Specify a custom Ollama URL for tests (default: http://localhost:11434)
- `TEST_OLLAMA_MODEL`: Specify a custom Ollama model for tests (default: llama3)
- `TEST_EMBEDDING_MODEL`: Specify a custom embedding model for tests (default: mxbai-embed-large)

## Writing Tests for src-layout

When adding new tests:

1. Follow the src-layout pattern for imports (e.g., `from src.obelisk.rag.common.config import RAGConfig`)
2. Use the appropriate test category (unit, integration, e2e)
3. Use fixtures from conftest.py when possible
4. Mock external services like Ollama when appropriate
5. Organize tests to mirror the source code structure
6. Ensure tests are isolated and don't depend on external resources
7. Include assertions that verify the expected behavior

## Mocking Strategy

For tests that interact with external services like Ollama:

1. Use `unittest.mock.patch` to mock the appropriate module
2. Configure the mock to return reasonable values
3. Use environment variables to control whether to use mocks or real services
4. For integration tests, mock only external services but use real internal components
5. For end-to-end tests, prefer to use mocks but allow overriding with environment variables
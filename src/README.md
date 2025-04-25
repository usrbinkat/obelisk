# Obelisk Source Code

This directory contains the source code for the Obelisk project, organized according to the src-layout pattern.

## Directory Structure

```
src/obelisk/
├── __init__.py                    # Package exports & version
├── cli/                           # Command-line interfaces
│   ├── __init__.py
│   ├── commands.py                # Main CLI entry point
│   └── rag.py                     # RAG-specific CLI commands
├── common/                        # Shared utilities
│   ├── __init__.py
│   └── config.py                  # Common configuration
├── core/                          # Core functionality
│   └── __init__.py
└── rag/                           # RAG functionality
    ├── __init__.py                # RAG package exports
    ├── api/                       # API endpoints
    │   ├── __init__.py
    │   └── openai.py              # OpenAI-compatible API
    ├── document/                  # Document processing
    │   ├── __init__.py
    │   ├── processor.py           # Document processor
    │   └── watcher.py             # File system watcher
    ├── embedding/                 # Embedding generation
    │   ├── __init__.py
    │   └── service.py             # Embedding service
    ├── storage/                   # Vector storage
    │   ├── __init__.py
    │   └── store.py               # Vector store implementation
    ├── common/                    # RAG-specific utilities
    │   ├── __init__.py
    │   └── config.py              # RAG configuration
    └── service/                   # Service coordination
        ├── __init__.py
        └── coordinator.py         # Main RAG service
```

## Module Dependencies

The modules are organized to follow a clean dependency flow:

- `common` provides utilities used by all modules
- `core` contains foundational functionality
- `rag` provides the RAG system components, organized by domain
  - `rag.common` contains shared utilities used by RAG components
  - `rag.document` handles document processing and watching
  - `rag.embedding` provides embedding generation
  - `rag.storage` manages vector storage
  - `rag.service` coordinates the RAG components
  - `rag.api` provides API endpoints
- `cli` provides command-line interfaces that use the other modules

## Installation

To install for development:

```bash
# Install base package
poetry install

# Install with RAG dependencies
poetry install --with rag

# Install with documentation dependencies
poetry install --with docs

# Install with development dependencies
poetry install --with dev

# Install all dependencies
poetry install --with rag,docs,dev
```
# Obelisk

RAG system with vector storage and AI integration.

## Overview

Obelisk is a RAG (Retrieval-Augmented Generation) system designed to provide context-aware AI interactions. It features a robust architecture for document processing, vector embedding, and AI-enhanced responses through integration with Ollama and OpenAI-compatible endpoints.

## Features

- **RAG Pipeline**: Complete document processing, embedding, and retrieval pipeline
- **Vector Storage**: Integration with ChromaDB and planned Milvus support
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API clients
- **Ollama Integration**: Local LLM support for both generation and embeddings
- **Document Monitoring**: Real-time updates when documents change
- **Docker Support**: Containerized deployment for all components
- **Python Src Layout**: Modern Python project structure with clean separation of concerns
- **Type Annotations**: Comprehensive type hints throughout the codebase

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Docker (optional, for containerized usage)

### Installation

```bash
# Clone the repository
git clone https://github.com/usrbinkat/obelisk.git
cd obelisk

# Install dependencies
poetry install
```

### Usage

#### CLI Commands

Obelisk provides a CLI for interacting with the RAG system:

```bash
# Show version
poetry run obelisk --version

# Show help
poetry run obelisk --help

# Index documents in the vault
poetry run obelisk rag index --vault /path/to/vault

# Query the RAG system
poetry run obelisk rag query "What is RAG?"

# Show system statistics
poetry run obelisk rag stats

# Start the RAG API server with OpenAI-compatible endpoint
poetry run obelisk rag serve --host 0.0.0.0 --port 8000 --watch
```

#### Docker Commands

```bash
# Run the full stack with Docker Compose
docker compose -f deployments/docker/compose/dev.yaml up

# Run only the RAG service
docker compose -f deployments/docker/compose/dev.yaml up obelisk-rag

# Run with Ollama integration
docker compose -f deployments/docker/compose/dev.yaml up ollama obelisk-rag
```

## License

[MIT](LICENSE)

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.
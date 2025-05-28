# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## DeepWiki MCP Integration

This project has been configured with DeepWiki MCP (Model Context Protocol) server integration. DeepWiki provides programmatic access to repository documentation and search capabilities.

### Configuration
The DeepWiki MCP server is configured in both:
- `.mcp.json` - For project-level MCP usage
- `.vscode/mcp.json` - For VS Code integration

### Available Tools
The DeepWiki MCP server provides three main tools:
1. **read_wiki_structure** - Get a list of documentation topics for a GitHub repository
2. **read_wiki_contents** - View documentation about a GitHub repository  
3. **ask_question** - Ask any question about a GitHub repository and get an AI-powered, context-grounded response

### Usage
- Base URL: `https://mcp.deepwiki.com/`
- SSE Endpoint: `https://mcp.deepwiki.com/sse` (recommended)
- No authentication required for public repositories
- Free service

### Key Features
- Supports SSE (Server-Sent Events) transport protocol
- Remote server accessible over HTTPS
- Works with any public GitHub repository
- Provides context-aware responses based on repository documentation

## Project Overview
Obelisk is a RAG (Retrieval-Augmented Generation) system with vector storage and AI integration. It transforms Obsidian vaults into MkDocs Material Theme sites with AI chat capabilities through a comprehensive RAG pipeline that provides context-aware responses. The tool preserves Obsidian's rich features including wiki links, callouts, and comments while delivering a modern documentation website.

## Repository
- GitHub: https://github.com/usrbinkat/obelisk

## Core Features
- Convert Obsidian vaults to MkDocs Material Theme sites (wiki links, callouts, comments)
- Complete RAG pipeline with document processing, embedding, and retrieval
- OpenAI-compatible API endpoint (`/v1/chat/completions`)
- Vector storage using Milvus with HNSW indexing
- LiteLLM integration for unified API access to multiple providers
- Ollama integration for local model management and hardware tuning
- Real-time document monitoring with file watcher
- Docker-based deployment with multi-service architecture
- Documentation versioning with mike
- Python src layout with comprehensive type annotations

## Key Commands

### Development with Task Runner
```bash
# Quick start commands
task run                # Fast dev server with live reload (port 8000)
task test-all          # Run all unit and integration tests
task test-rag          # Run RAG-specific tests
task clean-all         # Clean all artifacts (preserves Ollama and Milvus data)

# Docker commands
task docker-build      # Build and run entire stack
task docker            # Run Docker stack (detached)
task docker-logs       # View logs (use: task docker-logs -- service-name)
task docker-test       # Run initialization tests
task docker-clean      # Stop and remove all services/volumes

# Documentation
task build             # Build MkDocs site
task test              # Build with strict mode (catches errors)
task new -- page-name  # Create new markdown page in vault
```

### Documentation Deployment
```bash
# Deploy to GitHub Pages
poetry run mkdocs gh-deploy --force

# Version deployment with mike
poetry run mike deploy --push --update-aliases <VERSION> "<DESCRIPTION>"
poetry run mike set-default --push <VERSION>

# Serve with live reload and theme watching
poetry run mkdocs serve --livereload --watch-theme --open
```

### Creating Content Manually
```bash
# Create a new markdown file with frontmatter
mkdir -p vault
cat > vault/page-name.md << EOF
---
title: page-name
date: $(date +%Y-%m-%d)
---

EOF
```

### Python/Poetry Commands
```bash
# Install and run
poetry install --with rag,docs,dev,test  # Install all dependencies
poetry run obelisk --version              # Check installation

# RAG CLI commands
poetry run obelisk rag index --vault /path/to/vault    # Index documents
poetry run obelisk rag query "your question"            # Query the system
poetry run obelisk rag stats                            # Show statistics
poetry run obelisk rag serve --host 0.0.0.0 --port 8001 --watch  # Start API server

# Testing
poetry run pytest -xvs tests/unit/                      # Unit tests
poetry run pytest -xvs tests/integration/               # Integration tests
poetry run pytest -xvs tests/unit/rag/                  # RAG unit tests

# Linting and formatting
poetry run ruff check src/                              # Lint code
poetry run black src/                                   # Format code
```

### One-Shot Test Script
```bash
./test.sh  # Rebuild entire Docker stack from scratch and test
```

## Architecture

The project uses a Python src layout with the following key components:

### Core RAG System (`src/obelisk/rag/`)
1. **Service Layer** (`service/coordinator.py`):
   - `RAGService`: Main orchestrator connecting all components
   - Manages document processing, embeddings, and LLM queries
   - Handles document watching for real-time updates

2. **Document Processing** (`document/`):
   - `DocumentProcessor`: Parses markdown files with YAML frontmatter
   - `DocumentWatcher`: Monitors vault directory for changes
   - Hierarchical chunking based on markdown structure

3. **Embedding Service** (`embedding/service.py`):
   - Routes embeddings through LiteLLM by default
   - Supports multiple providers via unified API
   - Configurable 3072-dimensional embeddings (text-embedding-3-large)

4. **Vector Storage** (`storage/store.py`):
   - Milvus integration with HNSW indexing
   - Stores document chunks with metadata
   - Efficient similarity search with 3072-dimensional embeddings

5. **API Layer** (`api/`):
   - `openai.py`: Unified OpenAI-compatible chat completions endpoint
   - Routes all completions through LiteLLM by default
   - Supports provider override for hardware-specific operations

### CLI Interface (`src/obelisk/cli/`)
- `commands.py`: Main entry point and command parser
- `rag.py`: RAG-specific command handlers
- Subcommands: index, query, stats, config, serve

### Configuration (`src/obelisk/common/` and `src/obelisk/rag/common/`)
- Environment-based configuration with defaults
- Key settings: `VAULT_DIR`, `OLLAMA_URL`, `OLLAMA_MODEL`
- Separate configs for core and RAG subsystems

### Container Services (Ports)
- `obelisk`: MkDocs server (8000)
- `obelisk-rag`: RAG API service (8001)
- `ollama`: LLM server (11434)
- `open-webui`: Chat interface (8080)
- `litellm`: LLM proxy (4000)
- `milvus`: Vector database (19530)
- `init-service`: One-time initialization

## Project Structure
```
obelisk/
├── src/obelisk/           # Python package (src layout)
│   ├── cli/               # Command-line interface
│   ├── common/            # Shared configuration
│   └── rag/               # RAG system components
│       ├── api/           # API endpoints
│       ├── common/        # RAG configuration
│       ├── document/      # Document processing
│       ├── embedding/     # Embedding service
│       ├── service/       # RAG coordinator
│       └── storage/       # Vector storage
├── vault/                 # Documentation content
│   ├── assets/            # Static assets
│   ├── stylesheets/       # CSS customizations
│   ├── javascripts/       # JS customizations
│   └── overrides/         # HTML template overrides
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── scripts/           # Test utilities
├── deployments/docker/    # Docker configuration
├── mkdocs.yml            # MkDocs configuration
├── pyproject.toml        # Python project definition
├── Taskfile.yaml         # Task runner configuration
└── test.sh               # One-shot test script
```

## RAG Pipeline Flow

1. **Document Ingestion**: 
   - Markdown files are parsed from vault directory
   - YAML frontmatter extracted as metadata
   - Documents chunked hierarchically (respecting headers)

2. **Embedding Generation**:
   - Text chunks embedded via Ollama or OpenAI
   - Embeddings cached for performance
   - Automatic provider fallback

3. **Vector Storage**:
   - Embeddings stored in ChromaDB with metadata
   - Efficient similarity search using cosine distance
   - Collection management per vault

4. **Query Processing**:
   - User query embedded using same model
   - K-nearest neighbors retrieved from vector store
   - Context and query sent to LLM

5. **Response Generation**:
   - LLM generates response with retrieved context
   - OpenAI-compatible format returned
   - Streaming support available

## Environment Variables

Key configuration environment variables:
```bash
# Core settings
VAULT_DIR=/app/vault              # Directory containing markdown files
OBELISK_LOG_LEVEL=INFO           # Logging level

# Provider configuration
MODEL_PROVIDER=litellm           # Default provider (litellm/ollama)
FORCE_LITELLM_PROXY=true         # Force all completions through LiteLLM

# LiteLLM configuration
LITELLM_API_BASE=http://litellm:4000  # LiteLLM API endpoint
LITELLM_API_KEY=your-key             # LiteLLM API key

# Ollama configuration (for hardware tuning)
OLLAMA_URL=http://ollama:11434   # Ollama API endpoint
OLLAMA_MODEL=llama3              # Default Ollama model

# Model configuration
LLM_MODEL=gpt-4o                 # Default LLM model
EMBEDDING_MODEL=text-embedding-3-large  # Embedding model
EMBEDDING_DIM=3072               # Embedding dimension

# OpenAI configuration (via LiteLLM)
OPENAI_API_KEY=your-key          # For OpenAI models via LiteLLM
OPENAI_MODEL=gpt-4o              # OpenAI model selection

# Milvus vector storage
MILVUS_HOST=milvus               # Milvus server host
MILVUS_PORT=19530                # Milvus server port
MILVUS_COLLECTION=obelisk_rag    # Collection name
RETRIEVE_TOP_K=5                 # Number of documents to retrieve

# API server
API_HOST=0.0.0.0                 # API bind host
API_PORT=8001                    # API bind port
```

## Testing Strategy

### Unit Tests
```bash
poetry run pytest -xvs tests/unit/              # All unit tests
poetry run pytest -xvs tests/unit/rag/          # RAG-specific
poetry run pytest -xvs tests/unit/cli/          # CLI tests
```

### Integration Tests
```bash
poetry run pytest -xvs tests/integration/       # All integration
poetry run pytest -xvs tests/integration/rag/   # RAG integration
task test-prep-openai                           # Prepare OpenAI tests
```

### End-to-End Tests
```bash
task docker-build                               # Build and start stack
task docker-test                                # Run init tests
./test.sh                                       # Full rebuild test
```

### Test Files Organization
- `tests/unit/`: Isolated component tests
- `tests/integration/`: Multi-component tests
- `tests/e2e/`: Full system tests
- `tests/scripts/`: Test utilities and helpers
- `tests/data/`: Test fixtures

## Code Style and Quality

### Python Standards
- Target Python 3.12+ with full type annotations
- Use `src/` layout for better import management
- Prefer pathlib over os.path
- Use logging instead of print statements
- Follow PEP 8 with 88-char line length (Black)

### Linting and Formatting
```bash
poetry run black src/                # Auto-format code
poetry run ruff check src/           # Lint with ruff
poetry run mypy src/                 # Type checking (if configured)
```

### Import Organization
```python
# Standard library
import logging
from pathlib import Path
from typing import List, Dict, Any

# Third-party
from langchain.schema import Document
from fastapi import FastAPI

# Local - use absolute imports from src
from src.obelisk.rag.common.config import get_config
from src.obelisk.rag.service.coordinator import RAGService
```

## Common Development Workflows

### Adding New RAG Features
1. Create feature branch: `git checkout -b feat/rag-feature-name`
2. Implement in appropriate module under `src/obelisk/rag/`
3. Add unit tests in `tests/unit/rag/`
4. Test locally: `poetry run pytest -xvs tests/unit/rag/test_new_feature.py`
5. Test with Docker: `task docker-build && task docker-test`
6. Create PR with detailed description

### Debugging RAG Pipeline
```bash
# Check vector DB contents
poetry run obelisk rag stats

# Test document processing
poetry run obelisk rag index --vault ./test-vault

# Test query with verbose logging
OBELISK_LOG_LEVEL=DEBUG poetry run obelisk rag query "test question"

# Check API endpoints
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Running Single Tests
```bash
# Run specific test file
poetry run pytest -xvs tests/unit/rag/test_storage.py

# Run specific test function
poetry run pytest -xvs tests/unit/rag/test_storage.py::test_vector_search

# Run with coverage
poetry run pytest --cov=src/obelisk tests/unit/
```

## Important Implementation Details

### RAG Service Initialization
The `RAGService` in `src/obelisk/rag/service/coordinator.py` is the main entry point. It:
- Initializes embedding service with Ollama/OpenAI fallback
- Sets up ChromaDB vector storage
- Configures document processor with chunking strategy
- Manages file watcher for real-time updates

### Document Processing Pipeline
1. `DocumentProcessor.process_file()` reads markdown files
2. Extracts YAML frontmatter as metadata
3. Chunks based on markdown headers (preserves hierarchy)
4. Each chunk includes source file and metadata
5. Chunks are embedded and stored with IDs

### API Endpoint Implementation
The OpenAI-compatible endpoint (`/v1/chat/completions`) in `api/openai.py`:
- Accepts standard OpenAI chat format
- Performs RAG retrieval for context
- Supports streaming responses
- Returns OpenAI-compatible JSON structure

## Troubleshooting

### Common Issues
1. **Ollama connection failed**: Check `OLLAMA_URL` and that Ollama is running
2. **No documents found**: Verify `VAULT_DIR` path and file permissions
3. **Embedding errors**: Ensure embedding model is downloaded in Ollama
4. **Docker build fails**: Run `task clean-all` and retry

### Debug Commands
```bash
# Check service logs
task docker-logs -- obelisk-rag

# Verify Ollama models
docker exec ollama ollama list

# Test Ollama directly
curl http://localhost:11434/api/tags

# Check Milvus status
docker exec milvus-standalone milvus_cli
```

## Key Dependencies

- **Python 3.12+**: Required for modern type annotations and features
- **Poetry**: Package management and dependency resolution
- **Docker & Docker Compose**: Container orchestration
- **NVIDIA Container Toolkit**: GPU acceleration for Ollama (optional but recommended)
- **Task**: Modern task runner (alternative to Make)

### Python Package Dependencies
- **LangChain**: RAG pipeline orchestration
- **Milvus**: Production vector storage with HNSW indexing
- **FastAPI & Uvicorn**: API server
- **LiteLLM**: Unified API for multiple LLM providers
- **Ollama**: Local model management and hardware tuning
- **MkDocs Material**: Documentation site generation
- **Watchdog**: File system monitoring

## Documentation Standards

### Lean Documentation Specification
The project follows a lean documentation approach specified in `vault/LEAN_DOCUMENTATION.md`. This file serves as:

1. **Centralized Standard**: Defines how to create, maintain, and evaluate documentation
2. **Template Library**: Provides consistent templates for common documentation types
3. **Documentation Index**: Tracks all documentation artifacts and their status
4. **Quality Gates**: Defines review criteria and automation tools

### Key Documentation Principles
- **Just-In-Time**: Document only what's stable enough to survive sprints
- **Code-as-Documentation**: Leverage types, docstrings, and tests
- **Single Source of Truth**: One canonical location per concept
- **Automation First**: Generate what we can, write what we must

### Using the Standard
When creating or updating documentation:
1. Consult `vault/LEAN_DOCUMENTATION.md` for templates and patterns
2. Follow the stability indicators (🟢 Stable, 🟡 Experimental, 🔴 Unstable)
3. Add new documents to the documentation index
4. Use automation scripts where available

For documentation maintenance, evaluation, and refactoring, always refer to `vault/LEAN_DOCUMENTATION.md` as the source of truth to ensure consistency across all documentation artifacts.
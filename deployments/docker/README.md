# Obelisk Docker Infrastructure

This directory contains the Docker infrastructure for the Obelisk project, organized according to best practices for container-based deployment.

## Current Progress

The Docker infrastructure reorganization is currently in progress:

- [x] Initial directory structure created
- [x] Base Dockerfiles moved to the new structure
- [x] Docker Compose files reorganized by component
- [x] Development script created for testing
- [ ] Refactor Dockerfiles for optimized builds
- [ ] Implement multi-stage builds
- [ ] Optimize configuration management
- [ ] Add production environment configuration

## Directory Structure

```
docker/
├── compose/             # Docker compose configurations
│   ├── base/            # Base service definitions (imported by environments)
│   │   ├── core.yaml    # Core services (LiteLLM, Tika, etc.)
│   │   ├── rag.yaml     # RAG and Ollama services
│   │   └── vector-db.yaml # Vector database services (Milvus, etc.)
│   ├── dev.yaml         # Development environment
│   ├── prod.yaml        # Production environment (TODO)
│   └── test.yaml        # Testing environment (TODO)
├── config/              # Configuration for services
│   ├── litellm/         # LiteLLM configurations
│   └── ...              # Other service configurations (TODO)
└── images/              # Dockerfile definitions
    ├── base/            # Base image for all services (TODO)
    ├── core/            # MkDocs documentation container
    ├── rag/             # RAG service container
    └── init/            # Initialization container
```

## Services Overview

Obelisk consists of several integrated services:

1. **Core (MkDocs) Service**: Documentation server
2. **RAG Service**: Retrieval-Augmented Generation API
3. **Vector Database (Milvus)**: Storage for document embeddings
4. **LLM Service (Ollama)**: Local large language model
5. **LiteLLM Proxy**: API gateway for LLM services
6. **Open WebUI**: Web interface for chat
7. **Initialization Service**: Container setup and configuration

## Usage (Development)

To start the development environment with the new structure:

```bash
./scripts/dev-docker.sh
```

This script:
1. Sets up the necessary configuration files
2. Creates a default `.env` file if needed
3. Starts the Docker Compose services using the development configuration

## Next Steps

1. Refactor Dockerfiles to implement multi-stage builds
2. Create production-specific Docker Compose files
3. Optimize service configurations for different environments
4. Implement Kubernetes manifests for production deployment
5. Add comprehensive documentation for container architecture
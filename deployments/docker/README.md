# Obelisk Docker Infrastructure

This directory contains the Docker infrastructure for the Obelisk project, organized according to best practices for container-based deployment. It provides a modular and maintainable structure for running the Obelisk stack with its various services.

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

## Usage

The Docker infrastructure is managed through Task commands from the project root:

```bash
# Start the entire stack in detached mode
task docker

# Build and start services (with rebuilding containers)
task docker-build

# Validate Docker Compose configuration
task docker-config

# Check running containers
task docker-ps

# View logs (add service name to see specific service)
task docker-logs -- [service]

# Stop services
task docker-stop

# Stop and remove services
task docker-down

# Stop, remove services and clean up volumes
task docker-clean

# Run initialization tests
task docker-test
```

## Service Dependencies

The following diagram shows service dependencies:

```
obelisk (MkDocs)  ──────────────────────┐
                                        │
ollama ────┬─── litellm ─── litellm_db  │
           │         │                  │
           │         ├─── tika          │
           │         │                  │
           ├─── milvus ─── etcd         │
           │    │        │              │
           │    └─── minio              │
           │                            │
           └─── obelisk-rag ────────────┤
                                        │
                  open-webui ───────────┘
```

## Environment Configuration

All service configurations for the development environment are centralized in the `docker-compose/dev.yaml` file. Environment variables can be set through an `.env` file in the project root or provided directly to the Docker Compose command.
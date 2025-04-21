---
title: Containerization Architecture
date: 2025-04-21
---

# Obelisk Containerization Architecture

This document provides a comprehensive overview of Obelisk's containerization architecture, focusing on the Docker Compose configuration, container dependencies, and microservice interactions.

## Container Stack Overview

Obelisk leverages a microservices architecture implemented using Docker and Docker Compose to provide a complete ecosystem for documentation publishing with AI assistance and RAG capabilities.

```mermaid
graph TB
    %% Container Groups
    subgraph Core["Core Documentation Platform"]
        Obelisk["obelisk<br/>(MkDocs Server)"]
        ObeliskRAG["obelisk-rag<br/>(RAG API Service)"]
        Tika["tika<br/>(Document Processing)"]
    end
    
    subgraph AI["AI Model Services"]
        Ollama["ollama<br/>(Local LLM Host)"]
        LiteLLM["litellm<br/>(LLM Proxy)"]
        LiteLLMDB["litellm_db<br/>(PostgreSQL)"]
    end
    
    subgraph Vector["Vector Database Ecosystem"]
        Milvus["milvus<br/>(Vector DB)"]
        Etcd["etcd<br/>(Metadata Store)"]
        MinIO["minio<br/>(Object Storage)"]
    end
    
    subgraph Frontend["Frontend UI"]
        OpenWebUI["open-webui<br/>(Chat Interface)"]
    end
    
    %% Dependencies
    LiteLLMDB --> LiteLLM
    Etcd --> Milvus
    MinIO --> Milvus
    
    Ollama --> LiteLLM
    Milvus --> ObeliskRAG
    Ollama --> ObeliskRAG
    Tika --> OpenWebUI
    
    ObeliskRAG --> LiteLLM
    Milvus --> OpenWebUI
    LiteLLM --> OpenWebUI
    Ollama --> OpenWebUI
    
    classDef coreStyle fill:#C5E8B7,stroke:#000,stroke-width:1px
    classDef aiStyle fill:#BFD7ED,stroke:#000,stroke-width:1px
    classDef vectorStyle fill:#FFD8BE,stroke:#000,stroke-width:1px
    classDef frontendStyle fill:#FFB5DA,stroke:#000,stroke-width:1px
    
    class Obelisk,ObeliskRAG,Tika coreStyle
    class Ollama,LiteLLM,LiteLLMDB aiStyle
    class Milvus,Etcd,MinIO vectorStyle
    class OpenWebUI frontendStyle
```

## Container Services

### Core Components

| Service | Image | Description | Ports | Key Dependencies |
|---------|-------|-------------|-------|------------------|
| **obelisk** | Custom build | Documentation server running MkDocs with Material theme | 8000 | None |
| **obelisk-rag** | Custom build | Retrieval-Augmented Generation API service | 8001 | Ollama, Milvus |
| **tika** | apache/tika:latest-full | Document processing and content extraction | 9998 | None |

### AI Services

| Service | Image | Description | Ports | Key Dependencies |
|---------|-------|-------------|-------|------------------|
| **ollama** | ollama/ollama:latest | Local LLM hosting with GPU support | 11434 | None |
| **litellm** | ghcr.io/berriai/litellm:main-latest | LLM provider proxy for unified API access | 4000 | litellm_db, ollama |
| **litellm_db** | postgres:16.1 | Database for LiteLLM configuration and logging | 5432 | None |

### Vector Database

| Service | Image | Description | Ports | Key Dependencies |
|---------|-------|-------------|-------|------------------|
| **milvus** | milvusdb/milvus:v2.5.10 | High-performance vector database | 19530, 9091 | etcd, minio |
| **etcd** | quay.io/coreos/etcd:v3.5.18 | Distributed key-value store for Milvus metadata | 2379 | None |
| **minio** | minio/minio:RELEASE.2023-03-20T20-16-18Z | S3-compatible object storage for Milvus | 9000, 9001 | None |

### Frontend

| Service | Image | Description | Ports | Key Dependencies |
|---------|-------|-------------|-------|------------------|
| **open-webui** | ghcr.io/open-webui/open-webui:main | Web interface for chatbot and RAG interaction | 8080 | litellm, tika, ollama, milvus |

## Dependency Flow

The container services form a layered architecture with specific dependencies:

```mermaid
flowchart TD
    %% Base Infrastructure Layer
    subgraph Base["Base Infrastructure Layer"]
        MinIO["minio (Object Storage)"]
        Etcd["etcd (Metadata Store)"]
        LiteLLMDB["litellm_db (PostgreSQL)"]
        Tika["tika (Document Processing)"]
    end

    %% Core Services Layer
    subgraph Core["Core Services Layer"]
        Milvus["milvus (Vector DB)"]
        Ollama["ollama (Local LLM Host)"]
        Obelisk["obelisk (MkDocs Server)"]
    end

    %% Integration Layer
    subgraph Integration["Integration Layer"]
        LiteLLM["litellm (LLM Proxy)"]
        ObeliskRAG["obelisk-rag (RAG API)"]
    end

    %% User Interface Layer
    subgraph UI["User Interface Layer"]
        OpenWebUI["open-webui (Chat Interface)"]
    end

    %% Dependencies between layers
    MinIO --> Milvus
    Etcd --> Milvus
    LiteLLMDB --> LiteLLM
    
    Milvus --> ObeliskRAG
    Ollama --> ObeliskRAG
    Ollama --> LiteLLM
    
    ObeliskRAG --> OpenWebUI
    LiteLLM --> OpenWebUI
    Tika --> OpenWebUI
    Milvus --> OpenWebUI
    
    %% Styling
    classDef baseStyle fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef coreStyle fill:#e6f3ff,stroke:#333,stroke-width:1px
    classDef integrationStyle fill:#fff2e6,stroke:#333,stroke-width:1px
    classDef uiStyle fill:#f9e6ff,stroke:#333,stroke-width:1px
    
    class MinIO,Etcd,LiteLLMDB,Tika baseStyle
    class Milvus,Ollama,Obelisk coreStyle
    class LiteLLM,ObeliskRAG integrationStyle
    class OpenWebUI uiStyle
```

## Data Flow

The container architecture implements several key data flows:

### 1. Document Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Obelisk as Obelisk MkDocs
    participant ObeliskRAG as Obelisk RAG
    participant Milvus as Milvus Vector DB
    
    User->>+Obelisk: Edit/Add Markdown Documents
    Obelisk->>+ObeliskRAG: Document Update Event
    ObeliskRAG->>ObeliskRAG: Generate Embeddings
    ObeliskRAG->>+Milvus: Store Vectors & Metadata
    Milvus-->>-ObeliskRAG: Storage Confirmation
    ObeliskRAG-->>-Obelisk: Indexing Complete
```

### 2. RAG Query Flow

```mermaid
sequenceDiagram
    participant User
    participant OpenWebUI as Open WebUI
    participant Milvus as Milvus Vector DB
    participant ObeliskRAG as Obelisk RAG
    participant LiteLLM as LiteLLM Proxy
    participant Ollama as Ollama LLM
    
    User->>+OpenWebUI: Ask Question
    OpenWebUI->>+ObeliskRAG: Query for Context
    ObeliskRAG->>+Milvus: Vector Similarity Search
    Milvus-->>-ObeliskRAG: Relevant Document Chunks
    ObeliskRAG-->>-OpenWebUI: Context Information
    OpenWebUI->>+LiteLLM: LLM Request with Context
    LiteLLM->>+Ollama: Route to Local LLM
    Ollama-->>-LiteLLM: Generate Response
    LiteLLM-->>-OpenWebUI: Enhanced Response
    OpenWebUI-->>-User: Display Answer
```

## Volume Management

The Docker Compose configuration defines persistent volumes for data storage:

| Volume Name | Description | Used By |
|-------------|-------------|---------|
| **data** | General data storage | open-webui |
| **models** | LLM model storage | ollama, open-webui |
| **ollama** | Ollama configuration | ollama |
| **open-webui** | OpenWebUI configuration | open-webui |
| **rag-data** | RAG pipeline data | obelisk-rag |
| **rag-vault** | Document vault storage | obelisk-rag |
| **postgres_data** | PostgreSQL database files | litellm_db |
| **milvus_data** | Milvus database files | milvus |
| **etcd_data** | etcd storage | etcd |
| **minio_data** | MinIO object storage | minio |

## Network Configuration

All services are connected through a custom bridge network called `ollama-net`, which enables:
- Service discovery by container name
- Isolated communication between containers
- Security through network isolation

```yaml
networks:
  ollama-net:
    driver: bridge
```

## Docker Compose Environment Variables

The Docker Compose configuration uses environment variables for service configuration:

### OpenWebUI Configuration

```yaml
- RETRIEVAL_ENABLED=true
- RETRIEVAL_VECTOR_STORE=milvus
- MILVUS_URI=http://milvus:19530
- MILVUS_HOST=milvus
- MILVUS_PORT=19530
```

### Obelisk-RAG Configuration

```yaml
- VECTOR_DB=milvus
- MILVUS_URI=http://milvus:19530
- MILVUS_HOST=milvus
- MILVUS_PORT=19530
```

### LiteLLM Configuration

```yaml
- LITELLM_MASTER_KEY=sk-1234
- LITELLM_ADMIN_PASSWORD=admin
- DATABASE_URL=postgresql://postgres:postgres@litellm_db:5432/postgres
- OLLAMA_API_BASE=http://ollama:11434
```

## Healthchecks

The Docker Compose configuration implements healthchecks for critical services:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/stats"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

## Resource Management

The Ollama service is configured with GPU access when available:

```yaml
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - NVIDIA_DRIVER_CAPABILITIES=compute,utility
  - CUDA_VISIBLE_DEVICES=0
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          capabilities: [gpu]
          count: all
```

## Container Build Process

Two custom Dockerfiles are used for building Obelisk services:

1. **Dockerfile**: Builds the main Obelisk documentation service
2. **Dockerfile.rag**: Builds the Obelisk RAG service with additional dependencies

## Deployment Patterns

The Docker Compose configuration supports multiple deployment patterns:

1. **Core Documentation Only**:
   ```bash
   docker-compose up obelisk
   ```

2. **Documentation with RAG**:
   ```bash
   docker-compose up obelisk obelisk-rag milvus etcd minio
   ```

3. **Full AI Stack**:
   ```bash
   docker-compose up
   ```

## Performance Considerations

The containerized architecture is optimized for performance with:

1. **Volume Mounts**: Persistent storage for data that needs to survive container restarts
2. **Logging Controls**: Maximum log file size and rotation to prevent disk space issues
   ```yaml
   logging:
     driver: json-file
     options:
       max-size: "5m"
       max-file: "2"
   ```
3. **Restart Policies**: Automatic restart for critical services
   ```yaml
   restart: unless-stopped
   ```
   
## Container Maintenance

To maintain the containerized infrastructure:

1. **Prune Unused Resources**:
   ```bash
   docker system prune -a
   ```

2. **Update Images**:
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   ```

3. **View Logs**:
   ```bash
   docker-compose logs -f [service-name]
   ```

## Related Documentation

For additional information on specific components:

- [Docker Configuration](../development/docker.md): Core Docker setup information
- [Architecture Diagram](architecture.md): Full system architecture
- [Vector Database Integration](rag/vector-database.md): Details on vector database options
- [Milvus Integration](rag/milvus/integration.md): Specific details on Milvus configuration
- [Using RAG](rag/using-rag.md): How to use RAG features
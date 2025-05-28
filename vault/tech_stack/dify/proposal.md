# Dify Integration for Obelisk RAG Platform

## Overview

This directory contains the Dify integration components for the Obelisk RAG platform, providing an enterprise-grade chat interface with native Milvus vector database support and LiteLLM proxy integration.

## Repository Structure

```
.
├── docker-compose.yaml       # Complete Dify + infrastructure services
├── .env.template            # Environment configuration template
├── nginx/
│   ├── nginx.conf          # Main nginx configuration
│   └── proxy.conf          # Proxy settings for WebSocket support
├── scripts/
│   ├── quick-start.sh      # Automated deployment script
│   └── health-check.sh     # Service health validation
└── docs/
    ├── migration-guide.md   # Open-WebUI to Dify migration
    ├── configuration.md     # Detailed configuration notes
    └── tech_stack/
        └── dify.md         # Technical documentation (this file)
```

## Quick Start

```bash
# 1. Prepare configuration
cp .env.template .env
# Edit .env with your settings

# 2. Deploy Dify
./scripts/quick-start.sh

# 3. Initialize Dify
# Navigate to http://localhost:8080/install
```

## Key Features

- **Native Milvus Integration**: First-class vector database support without adapters
- **LiteLLM Proxy Compatible**: Seamless integration with existing LLM routing
- **Enterprise Ready**: Multi-tenancy, RBAC, SSO, and API-first design
- **Microservices Architecture**: Horizontally scalable components
- **RAG Optimized**: Advanced chunking, embedding, and retrieval strategies

## Service Components

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| dify_nginx | Reverse proxy | 8080 | `/` |
| dify_api | Core API service | 5001 | `/console/api/health` |
| dify_worker | Async job processor | - | Container status |
| dify_web | React frontend | 3000 | `/` |
| dify_db | PostgreSQL database | 5432 | `pg_isready` |
| dify_redis | Cache & queue | 6379 | `redis-cli ping` |
| dify_sandbox | Code execution | 8194 | `/health` |

## Configuration Overview

### Critical Settings

```yaml
# Vector Database
VECTOR_STORE: milvus
MILVUS_URI: http://milvus:19530  # Must use service name

# LLM Provider (via UI configuration)
Provider: OpenAI-API-compatible
Base URL: http://litellm:4000
API Key: <from LiteLLM configuration>
```

### Security Configurations

- Generate unique `SECRET_KEY` with `openssl rand -base64 42`
- Change all default passwords in production
- Configure CORS settings appropriately
- Enable rate limiting for API endpoints

## Operational Commands

```bash
# View logs
docker-compose logs -f dify_api

# Scale workers
docker-compose up -d --scale dify_worker=3

# Backup data
./scripts/backup-dify.sh

# Health check
./scripts/health-check.sh
```

## Integration Points

### Milvus Vector Database
- Collections: Named as `Dify_<dataset_id>`
- Embedding dimensions: Configured per model
- Index type: IVF_FLAT (configurable)

### LiteLLM Proxy
- Configure via Dify UI, not environment variables
- Supports all LiteLLM-routed models
- Maintains OpenAI-compatible interface

### Document Processing
- Tika integration for file extraction
- Configurable chunking strategies
- Parallel processing via worker pool

## Monitoring

- Metrics: Available at `<service>:<port>/metrics`
- Logs: Structured JSON output
- Alerts: Configure based on SLI thresholds

## Maintenance

### Updates
```bash
# Pull latest images
docker-compose pull

# Rolling update
docker-compose up -d --no-deps dify_api
```

### Backups
- Database: Daily PostgreSQL dumps
- Milvus: Snapshot API
- Storage: Incremental file sync

## Troubleshooting

| Issue | Check | Solution |
|-------|-------|----------|
| Connection refused | Service names in configs | Use Docker service names, not localhost |
| Slow queries | Milvus index stats | Optimize index parameters |
| High memory | Worker resource limits | Tune chunk size or scale horizontally |

## Documentation

- [Technical Architecture](./docs/tech_stack/dify.md)
- [Migration Guide](./docs/migration-guide.md)
- [Configuration Details](./docs/configuration.md)
- [Dify Official Docs](https://docs.dify.ai)

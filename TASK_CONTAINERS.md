# Container Infrastructure Reorganization

This document outlines the tasks for restructuring the Docker container infrastructure for Obelisk to improve maintainability, scalability, and adherence to best practices.

## Current Container Architecture

The current container architecture consists of:

1. **Dockerfiles in Project Root**:
   - `Dockerfile` - Main MkDocs documentation container
   - `Dockerfile.rag` - RAG service container
   - `Dockerfile.init` - Initialization container

2. **Docker Compose in Project Root**:
   - `docker-compose.yaml` - Defines all services

3. **Initialization Scripts**:
   - `docker/init-scripts/` directory with various initialization scripts
   - `docker-entrypoint.sh` in the project root

4. **Configuration Files**:
   - `litellm-config.yaml` in project root

5. **Services**:
   - Core Obelisk (MkDocs) service
   - RAG service
   - LiteLLM proxy
   - Ollama
   - Open WebUI
   - Milvus ecosystem (Milvus, Etcd, MinIO)
   - Initialization service
   - Supporting services (Tika, PostgreSQL)

## Restructuring Objectives

1. **Separation of Concerns**: 
   - Separate build contexts from runtime configurations
   - Organize services by functional area

2. **Environment-Specific Configurations**:
   - Development, testing, and production environments
   - Different resource allocations for different environments

3. **Build Optimization**:
   - Improve layer caching
   - Reduce build times
   - Minimize image sizes

4. **Maintainability and Documentation**:
   - Clear documentation for each service
   - Standardized patterns across containers
   - Improved environment variable management

## Target Structure

```
deployments/
├── docker/
│   ├── compose/
│   │   ├── dev.yaml              # Development environment
│   │   ├── prod.yaml             # Production environment
│   │   ├── test.yaml             # Testing environment
│   │   └── base/
│   │       ├── core.yaml         # Core services definition (shared)
│   │       ├── rag.yaml          # RAG-specific services
│   │       └── vector-db.yaml    # Vector database services
│   ├── config/
│   │   ├── litellm/              # LiteLLM configurations
│   │   ├── milvus/               # Milvus configurations
│   │   ├── ollama/               # Ollama configurations
│   │   └── openwebui/            # OpenWebUI configurations
│   └── images/
│       ├── base/
│       │   ├── Dockerfile        # Base Python image
│       │   └── requirements.txt  # Common requirements
│       ├── core/
│       │   ├── Dockerfile        # MkDocs documentation container
│       │   └── entrypoint.sh     # Container entrypoint
│       ├── rag/
│       │   ├── Dockerfile        # RAG service container
│       │   └── entrypoint.sh     # Container entrypoint
│       └── init/
│           ├── Dockerfile        # Initialization container
│           └── scripts/          # Initialization scripts
│               ├── configure-services.sh
│               ├── download-models.sh
│               ├── generate-tokens.sh
│               └── init-sequence.sh
└── kubernetes/                   # Future Kubernetes manifests
    ├── base/                     # Base Kubernetes resources
    └── overlays/                 # Environment-specific overlays
        ├── dev/
        └── prod/
```

## Implementation Tasks

### Phase 1: Directory Structure and Base Images

- [x] **Create Base Directory Structure**
  - [x] Create `deployments/docker/compose/` directory
  - [x] Create `deployments/docker/compose/base/` directory
  - [x] Create `deployments/docker/images/` directory
  - [x] Create `deployments/docker/config/` directory
  - [x] **TEST:** Verify directory structure with tree command ✅

- [ ] **Create Base Image**
  - [ ] Create `deployments/docker/images/base/Dockerfile`
  - [ ] Extract common dependencies into `requirements.txt`
  - [ ] Configure multi-stage builds with optimized layers
  - [ ] **TEST:** Verify base image builds successfully

### Phase 2: Service Images

- [x] **Core Service (MkDocs)**
  - [x] Create `deployments/docker/images/core/Dockerfile`
  - [ ] Move and refactor `docker-entrypoint.sh` to `deployments/docker/images/core/entrypoint.sh`
  - [ ] Optimize build process and layer caching
  - [x] **TEST:** Verify core image builds and runs

- [x] **RAG Service**
  - [x] Create `deployments/docker/images/rag/Dockerfile` 
  - [x] Create dedicated entrypoint script
  - [ ] Configure for microservices architecture
  - [x] **TEST:** Verify RAG service image builds and runs

- [x] **Initialization Service**
  - [x] Create `deployments/docker/images/init/Dockerfile`
  - [x] Move initialization scripts from `docker/init-scripts/` to `deployments/docker/images/init/scripts/`
  - [x] Update script references and paths
  - [x] **TEST:** Verify initialization service functions correctly

### Phase 3: Configuration

- [x] **Configuration Management**
  - [x] Move `litellm-config.yaml` to `deployments/docker/config/litellm/`
  - [ ] Create template configurations for each service
  - [ ] Document all configuration options
  - [ ] Implement configuration validation
  - [ ] **TEST:** Verify configuration files are loaded correctly

- [ ] **Environment Variables**
  - [ ] Create `.env.example` file
  - [ ] Document all environment variables
  - [ ] Implement variable validation in initialization scripts
  - [ ] **TEST:** Verify environment variables are correctly passed to containers

### Phase 4: Docker Compose

- [x] **Base Service Definitions**
  - [x] Create `deployments/docker/compose/base/core.yaml` with core services
  - [x] Create `deployments/docker/compose/base/rag.yaml` with RAG services
  - [x] Create `deployments/docker/compose/base/vector-db.yaml` with Milvus services
  - [x] **TEST:** Verify base service definitions can be parsed by Docker Compose

- [x] **Environment-Specific Compositions**
  - [x] Create `deployments/docker/compose/dev.yaml` for development
  - [ ] Create `deployments/docker/compose/prod.yaml` for production
  - [ ] Create `deployments/docker/compose/test.yaml` for testing
  - [x] **TEST:** Verify environment-specific compositions correctly import base services

### Phase 5: Integration and Testing

- [x] **Build Script**
  - [x] Create build scripts for each environment (added to Taskfile.yaml)
  - [x] Implement caching and optimization flags (using Docker's built-in caching)
  - [x] **TEST:** Verify build scripts successfully build all services

- [x] **Testing**
  - [x] Test each service individually
  - [x] Test complete stack for development environment
  - [x] Validate initialization scripts
  - [x] Check network configuration and service discovery
  - [x] **TEST:** Perform end-to-end testing to confirm full functionality

- [x] **Documentation**
  - [x] Update deployment documentation
  - [x] Create quick start guides for development environment
  - [x] Document container architecture
  - [x] **TEST:** Verify documentation accuracy by following instructions

### Phase 6: Kubernetes Preparation (Future)

- [ ] **Kubernetes Manifests**
  - [ ] Create base Kubernetes resources
  - [ ] Create environment-specific overlays
  - [ ] Implement StatefulSet for Milvus components
  - [ ] Configure horizontal scaling for RAG services

## Service Inventory and Dependencies

1. **Core Dependencies**
   - MkDocs documentation server → Requires: None
   - Ollama → Requires: None
   - LiteLLM Proxy → Requires: PostgreSQL, Ollama

2. **RAG Dependencies**
   - Obelisk RAG service → Requires: Ollama, Milvus, LiteLLM
   - Milvus → Requires: Etcd, MinIO
   - Initialization service → Requires: All services

3. **Frontend Dependencies**
   - Open WebUI → Requires: Ollama, LiteLLM, Obelisk RAG, Tika, Milvus

## Storage and Volume Management

- [ ] **Volume Structure**
  - [ ] Define clear volume naming convention
  - [ ] Organize volumes by service type
  - [ ] Document persistence requirements

- [ ] **Backup and Restore**
  - [ ] Create volume backup procedures
  - [ ] Test restore procedures
  - [ ] Document data management

## Network Configuration

- [ ] **Network Segmentation**
  - [ ] Group services by network segments
  - [ ] Configure proper network isolation
  - [ ] Implement secure communication

## Environment-Specific Optimizations

### Development Environment
- [ ] Configure hot-reload for development
- [ ] Mount source code volumes for live editing
- [ ] Enable debug logging and development tools

### Production Environment
- [ ] Optimize for performance and reliability
- [ ] Configure proper resource limits
- [ ] Implement health checks and restart policies
- [ ] Set up monitoring and logging

### Testing Environment
- [ ] Configure for automated testing
- [ ] Set up ephemeral storage for tests
- [ ] Implement test fixtures and data

## Migration Strategy

1. **Preparation**
   - Create new directory structure
   - Move and refactor Dockerfiles
   - Update configuration files

2. **Testing**
   - Build and test each service individually
   - Test integrated services in isolated environment
   - Validate against current functionality

3. **Deployment**
   - Update documentation
   - Release new compose files
   - Provide migration guide for users

4. **Cleanup**
   - Remove old Docker files after successful migration
   - Update references in documentation
   - Close related issues

## Progress Tracking

**Phase 1: Directory Structure and Base Images**
- [x] Directory structure created
- [ ] Base image implemented (skipped for now, using direct Dockerfiles)
- [x] **TESTED:** Directory structure confirmed working with Docker build

**Phase 2: Service Images**
- [x] Core service image created
- [x] RAG service image created 
- [x] Initialization service image created
- [x] **TESTED:** Images build successfully without errors
- [x] **TESTED:** Images start and run as expected

**Phase 3: Configuration**
- [x] Configuration files moved and organized
- [ ] Environment variables documented
- [x] **TESTED:** Configuration files load correctly
- [x] **TESTED:** Environment variable substitution works

**Phase 4: Docker Compose**
- [x] Base service definitions created
- [x] Environment-specific compositions created (dev environment)
- [x] **TESTED:** Docker Compose can parse all files without errors
- [x] **TESTED:** Services defined in base files are correctly imported

**Phase 5: Integration and Testing**
- [x] Build scripts created (via Task runner)
- [x] Individual services tested
- [x] Complete stack tested
- [x] Documentation updated
- [x] **TESTED:** Every service starts correctly
- [x] **TESTED:** Services can communicate with each other
- [x] **TESTED:** System functionality matches the original implementation

## Next Steps

1. **Environment-Specific Refinements**
   - Create production-specific Docker Compose configuration
   - Create testing-specific Docker Compose configuration
   - Optimize resource usage for different environments

2. **Base Image Optimization**
   - Create common base Dockerfile with shared dependencies
   - Implement multi-stage builds for smaller images
   - Extract common requirements into shared files

3. **Documentation Improvements**
   - Create comprehensive guide for each environment (prod, test)
   - Document all configuration options in detail
   - Create troubleshooting guide

4. **Environment Variable Management**
   - Create comprehensive `.env.example` file
   - Document all environment variables
   - Implement validation and defaults

5. **Kubernetes Preparation**
   - Create basic Kubernetes manifests
   - Test deployments in minikube
   - Document Kubernetes deployment process
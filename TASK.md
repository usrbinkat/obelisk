# Obelisk Project Restructuring Plan

This document outlines the plan for restructuring the Obelisk project to follow industry best practices, improve maintainability, and prepare for microservices architecture.

## Goals

- [ ] Reorganize the codebase for improved clarity and maintainability
- [ ] Prepare the architecture for microservices transition
- [ ] Follow industry best practices for Python project organization
- [ ] Improve developer experience and reduce onboarding time
- [ ] Create a foundation for community growth

## High-Level Structure

```
obelisk/
├── src/                           # Source code
│   └── obelisk/                   # Main package
├── tests/                         # All tests
├── docs/                          # Documentation source
├── deployments/                   # Deployment configurations
├── scripts/                       # Utility scripts
├── vault/                         # MkDocs content (unchanged)
└── [essential root files]         # README, pyproject.toml, etc.
```

## Implementation Plan

### Phase 1: Package Restructuring

- [ ] Create the `src` directory structure
- [ ] Move core Obelisk package to src/obelisk
  - [ ] Update `__init__.py` with proper exports
  - [ ] Create subpackages for different modules

- [ ] Reorganize the RAG package
  - [ ] Create proper submodules (document, embedding, storage, api)
  - [ ] Move code to appropriate locations
  - [ ] Update imports throughout the codebase

- [ ] Update pyproject.toml to work with src layout
  - [ ] Update dependencies as needed
  - [ ] Fix any package metadata

- [ ] Ensure the restructured package works as expected
  - [ ] Test imports and basic functionality
  - [ ] Fix any issues with module resolution

### Phase 2: Test Reorganization

- [ ] Create proper test structure
  - [ ] Organize into unit, integration, and e2e categories
  - [ ] Create central test data directory

- [ ] Move existing tests to the new structure
  - [ ] Fix imports and paths as needed
  - [ ] Ensure all tests continue to work

- [ ] Create common test fixtures
  - [ ] Add shared conftest.py
  - [ ] Standardize test setup and teardown

- [ ] Improve test coverage
  - [ ] Identify areas needing better coverage
  - [ ] Add new tests as needed

### Phase 3: Deployment Reorganization

- [x] Create deployments directory
  - [x] Set up docker subdirectories
  - [x] Prepare for future kubernetes manifests

- [x] Reorganize Docker files
  - [x] Move Dockerfiles to appropriate locations
  - [x] Update Docker builds to use new structure
  - [x] Split docker-compose files by environment

- [x] Update initialization scripts
  - [x] Move to proper locations
  - [x] Ensure they work with new structure

- [x] Test all deployment configurations
  - [x] Ensure services work correctly
  - [x] Verify initialization and configuration

#### Deployment Reorganization Details

The Docker infrastructure has been completely reorganized:

1. **Directory Structure**:
   - Created `/deployments/docker/` structure with subfolders for images, compose files, and configuration
   - Organized Dockerfiles by service type (core, rag, init)
   - Restructured compose files with base configurations for modularity

2. **Task Integration**:
   - Added Taskfile tasks for managing Docker infrastructure:
     - `task docker` - Start services in detached mode
     - `task docker-build` - Build and start services
     - `task docker-logs` - View service logs
     - `task docker-stop` - Stop services
     - `task docker-config` - Validate configuration
     - `task docker-test` - Run initialization tests

3. **Environment Configuration**:
   - Created comprehensive `.env.example` file with detailed documentation
   - Documented all environment variables used by containers
   - Updated test scripts to work with the new structure

4. **Testing**:
   - Verified all services build and run successfully in the new structure
   - Ran comprehensive tests including rag functionality
   - Validated container initialization and inter-service communication

### Phase 4: Documentation Improvements

- [ ] Create docs directory structure
  - [ ] Set up sections for api, architecture, development, and user docs
  - [ ] Move existing documentation to appropriate locations

- [x] Update documentation to reflect new structure
  - [x] Update Docker infrastructure documentation
  - [ ] Update code references
  - [ ] Add structure diagrams

- [ ] Improve API documentation
  - [ ] Document public interfaces
  - [ ] Add examples and usage guides

- [ ] Add guidelines for the new structure
  - [ ] Update contributing guidelines
  - [ ] Document code organization principles

#### Documentation Improvements Details

The following documentation improvements have been completed:

1. **Docker Infrastructure Documentation**:
   - Updated `/deployments/docker/README.md` with usage instructions
   - Created service dependency diagram and explanations
   - Added detailed command examples and explanations

2. **Environment Variables Documentation**:
   - Created a comprehensive `.env.example` file with detailed comments for all variables
   - Organized variables by functional area (LiteLLM, Ollama, RAG, etc.)
   - Added option descriptions and defaults where applicable

### Phase 5: Final Integration

- [ ] Clean up the root directory
  - [ ] Remove unnecessary files
  - [ ] Consolidate remaining files

- [ ] Create project-wide scripts
  - [ ] Add development helpers
  - [ ] Create CI utilities

- [ ] Update project README
  - [ ] Describe new structure
  - [ ] Update getting started guide

- [ ] Final testing
  - [ ] Run all tests
  - [ ] Verify documentation builds
  - [ ] Ensure deployment works

## Detailed Restructuring Targets

### Source Code Restructuring

```
src/obelisk/
├── __init__.py                    # Package exports & version
├── cli/                           # Command-line interfaces
│   ├── __init__.py
│   ├── core.py                    # Core CLI
│   └── rag.py                     # RAG CLI
├── common/                        # Shared utilities
│   ├── __init__.py
│   ├── config.py                  # Common configuration
│   └── utils.py                   # Shared utilities
├── core/                          # Core functionality
│   ├── __init__.py
│   ├── convert.py                 # Document conversion
│   └── obsidian.py                # Obsidian utilities
└── rag/                           # RAG functionality
    ├── __init__.py                # Package exports & version
    ├── api/                       # API endpoints
    │   ├── __init__.py
    │   ├── app.py                 # FastAPI application
    │   ├── models.py              # Pydantic models
    │   └── routes.py              # API routes
    ├── document/                  # Document processing service
    │   ├── __init__.py
    │   ├── processor.py           # Document processor
    │   ├── chunker.py             # Text chunking
    │   ├── metadata.py            # Metadata extraction
    │   └── reconciliation.py      # Document reconciliation
    ├── embedding/                 # Embedding service
    │   ├── __init__.py
    │   ├── service.py             # Embedding service
    │   ├── providers/             # Provider implementations
    │   │   ├── __init__.py
    │   │   ├── ollama.py          # Ollama provider
    │   │   └── openai.py          # OpenAI provider
    │   └── cache.py               # Embedding cache
    ├── storage/                   # Vector storage service
    │   ├── __init__.py
    │   ├── base.py                # Base storage interface
    │   ├── chroma.py              # ChromaDB implementation
    │   └── milvus.py              # Milvus implementation
    ├── config.py                  # Configuration utilities
    ├── models.py                  # Shared data models
    └── service.py                 # Main service coordinator
```

### Tests Restructuring

```
tests/
├── conftest.py                    # Shared test fixtures and configuration
├── data/                          # Test data for all tests
│   ├── documents/                 # Sample markdown documents
│   ├── vectors/                   # Sample vector data
│   └── embeddings/                # Sample embeddings
├── unit/                          # Unit tests
│   ├── cli/                       # CLI tests
│   ├── core/                      # Core module tests
│   └── rag/                       # RAG unit tests
│       ├── document/              # Document processing tests
│       ├── embedding/             # Embedding tests
│       ├── storage/               # Storage tests
│       └── test_service.py        # Service tests
├── integration/                   # Integration tests
│   └── rag/                       # RAG integration tests
└── e2e/                           # End-to-end tests
    ├── test_rag_api.py            # RAG API e2e tests
    └── test_containers.py         # Container tests
```

### Deployment Restructuring

```
deployments/
├── docker/
│   ├── compose/
│   │   ├── base/                  # Base service definitions
│   │   │   ├── core.yaml          # Core services
│   │   │   ├── rag.yaml           # RAG services
│   │   │   └── vector-db.yaml     # Vector database services
│   │   ├── dev.yaml               # Development compose configuration
│   │   ├── prod.yaml              # Production compose configuration (planned)
│   │   └── test.yaml              # Testing compose configuration (planned)
│   ├── config/
│   │   ├── litellm/               # LiteLLM configurations
│   │   │   └── config.yaml
│   │   └── litellm_config.yaml    # Top-level LiteLLM config
│   ├── images/
│   │   ├── core/                  # Core Obelisk service
│   │   │   └── Dockerfile
│   │   ├── rag/                   # RAG service
│   │   │   ├── Dockerfile
│   │   │   └── entrypoint.sh
│   │   └── init/                  # Initialization service
│   │       ├── Dockerfile
│   │       └── scripts/
│   │           ├── init-sequence.sh
│   │           ├── configure-services.sh
│   │           ├── download-models.sh
│   │           └── generate-tokens.sh
│   └── README.md                  # Docker infrastructure documentation
└── kubernetes/                    # Future Kubernetes manifests (planned)
```

This structure has been completely implemented with the exception of the production and testing environment compose files, which are planned for future development.

### Documentation Restructuring

```
docs/
├── api/                           # API documentation
│   ├── index.md                   # API overview
│   ├── rag-api.md                 # RAG API docs
│   └── cli.md                     # CLI reference
├── architecture/                  # Architecture documentation
│   ├── index.md                   # Architecture overview
│   ├── rag/                       # RAG-specific architecture
│   │   ├── index.md               # RAG overview
│   │   ├── document.md            # Document processing
│   │   ├── embedding.md           # Embedding system
│   │   └── storage.md             # Vector storage
│   └── diagrams/                  # Architecture diagrams
├── development/                   # Developer guides
│   ├── index.md                   # Development overview
│   ├── setup.md                   # Development setup
│   ├── conventions.md             # Code conventions
│   ├── testing.md                 # Testing guide
│   └── release.md                 # Release process
├── user/                          # User guides
│   ├── index.md                   # User overview
│   ├── installation.md            # Installation guide
│   ├── configuration.md           # Configuration guide
│   └── tutorials/                 # Step-by-step tutorials
└── index.md                       # Documentation home
```

## Microservices Path

This restructuring is designed to support the transition to microservices:

- Each subdirectory in the `rag` package can become its own microservice
- Clear interfaces between components make extraction easier
- Shared utilities are isolated for reuse across services
- Deployment configurations are prepared for multi-service deployment

## Status Tracking

Overall Project Status: In Progress

- [ ] Phase 1: Package Restructuring - Not Started
- [ ] Phase 2: Test Reorganization - Not Started
- [x] Phase 3: Deployment Reorganization - Completed
- [ ] Phase 4: Documentation Improvements - Partially Completed
- [ ] Phase 5: Final Integration - Not Started
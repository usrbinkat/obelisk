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

- [x] Create the `src` directory structure
- [x] Move core Obelisk package to src/obelisk
  - [x] Update `__init__.py` with proper exports
  - [x] Create subpackages for different modules

- [x] Reorganize the RAG package
  - [x] Create proper submodules (document, embedding, storage, api)
  - [x] Move code to appropriate locations
  - [x] Update imports throughout the codebase

- [x] Update pyproject.toml to work with src layout
  - [x] Update dependencies as needed
  - [x] Fix any package metadata

- [x] Ensure the restructured package works as expected
  - [x] Test imports and basic functionality
  - [x] Fix any issues with module resolution
  - [x] Add proper entry point via __main__.py

### Phase 2: Test Reorganization

- [x] Create proper test structure
  - [x] Organize into unit, integration, and e2e categories
  - [x] Create central test data directory

- [x] Move existing tests to the new structure
  - [x] Fix imports and paths as needed
  - [x] Ensure all tests continue to work

- [x] Create common test fixtures
  - [x] Add shared conftest.py
  - [x] Standardize test setup and teardown
  - [x] Fix test isolation with environment variables

- [x] Improve test coverage
  - [x] Add tests for watcher functionality
  - [x] Add tests for API endpoints
  - [x] Configure warning filters for third-party libraries

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
  - [x] Update code references for Docker paths
  - [x] Add docstrings to new module files
  - [ ] Add structure diagrams (in progress)

- [ ] Improve API documentation
  - [x] Document RAG API interfaces
  - [x] Update function signatures with type hints
  - [ ] Add examples and usage guides (in progress)

- [ ] Add guidelines for the new structure
  - [x] Update import patterns throughout codebase
  - [ ] Update contributing guidelines (in progress)
  - [ ] Document code organization principles (in progress)

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

- [x] Clean up the root directory
  - [x] Remove unnecessary Docker files
  - [x] Move Docker files to deployments directory
  - [x] Remove cleanup plan after implementation

- [ ] Perform legacy file cleanup
  - [ ] Compare each file in obelisk/ with its src/obelisk/ counterpart
  - [ ] Ensure no functionality is lost in the transition
  - [ ] Remove old files only after verification
  - [ ] Document any special cases or file preservation

- [ ] Create project-wide scripts
  - [x] Add testing environment helpers
  - [ ] Create CI utilities (in progress)

- [ ] Update project README
  - [ ] Describe new structure
  - [ ] Update getting started guide with src-layout instructions

- [ ] Final testing
  - [x] Run all unit and integration tests
  - [ ] Verify documentation builds
  - [ ] Test Docker deployment with new structure

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

- [x] Phase 1: Package Restructuring - Completed
  - [x] Create src directory structure
  - [x] Implement Python src-layout pattern
  - [x] Move and refactor code to new locations
  - [x] Update imports and dependencies
  - [x] Fix import resolution and module boundaries
- [x] Phase 2: Test Reorganization - Completed
  - [x] Create unit/integration/e2e test structure
  - [x] Move tests to new locations
  - [x] Fix test fixtures and environment issues
  - [x] Ensure all tests pass with new structure
- [x] Phase 3: Deployment Reorganization - Completed
- [x] Phase 4: Documentation Improvements - Partially Completed
  - [x] Update Docker infrastructure documentation
  - [x] Update environment variables documentation
  - [x] Update test script to work with new Docker paths
  - [x] Add docstrings to new module files
  - [ ] Create architecture diagrams (in progress)
- [ ] Phase 5: Final Integration - In Progress
  - [x] Clean up Docker-related files in root directory
  - [x] Update references to new file paths
  - [ ] Perform legacy file cleanup (next step)
  - [ ] Update README with new structure
  - [ ] Verify Docker deployment with new structure
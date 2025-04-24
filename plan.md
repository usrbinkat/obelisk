# Obelisk Package Restructuring Plan

This document outlines the detailed implementation plan for the package restructuring phase of the Obelisk project reorganization (Issue #35, PR #36, Implementation Issue #37). It includes specific steps and progress tracking to ensure alignment with the architectural vision.

## Overview

We're ready to implement the Python package restructuring (Phase 1 of the project reorganization) after successfully completing the Docker infrastructure reorganization (Phase 3). This restructuring will follow the src-layout pattern, improve module organization, and prepare for future microservices extraction as outlined in the architecture diagram.

## Related Issues

This plan addresses or relates to the following GitHub issues:

- #35: Enhancement: Implement Project Structure Reorganization (main issue)
- #36: PR: Professional Project Structure Reorganization (in progress)
- #37: Implement src-layout pattern and module boundaries (implementation)
- #33: Feature: Document Reconciliation Microservice (future)
- #34: Feature: Embedding Generation Microservice (future)
- #21: Create integrated test suite for RAG functionality
- #12: Implement Stateful File Tracking for RAG Service

## Architecture Alignment

This restructuring will directly support the architecture described in `/vault/chatbot/architecture.md` by:

1. Creating clear module boundaries between components shown in the architecture diagram
2. Establishing proper interfaces between the Document Processing Pipeline, Vector Persistence, and AI Service Layer
3. Separating concerns to prepare for future microservices extraction
4. Implementing a unified CLI structure with the RAG functionality as a subcommand
5. Creating a foundation for the Document Reconciliation and Embedding Generation components

## Implementation Checklist

### A. Preparation and Planning

- [x] Research Python src-layout pattern best practices
- [x] Analyze existing code organization and dependencies
- [x] Document current package structure and imports
- [x] Create restructuring plan (this document)
- [x] Set up temporary testing environment

### B. Source Directory Structure

- [x] Create src directory structure
  - [x] Create `/src` directory
  - [x] Create `/src/obelisk` package directory
  - [x] Update `pyproject.toml` for src layout
  - [x] Create module architecture

- [x] Configure package metadata
  - [x] Update import resolution in `pyproject.toml`
  - [x] Create minimal `pyproject.toml` entries
  - [x] Update version management

### C. Core Package Reorganization

- [x] Move and refactor core modules
  - [x] Move `__init__.py` with version information
  - [x] Create unified CLI structure in `/src/obelisk/cli/`
    - [x] Create main CLI entry point
    - [x] Implement subcommand architecture
    - [x] Move RAG CLI functionality to subcommand
  - [x] Move `config.py` to `/src/obelisk/common/`
  - [x] Create structure for `convert.py` in `/src/obelisk/core/`
  - [x] Update imports to absolute paths
  - [x] Test core functionality

### D. RAG Package Reorganization

- [x] Create RAG module structure aligned with architecture diagram
  - [x] Create `/src/obelisk/rag/api/` directory
  - [x] Create `/src/obelisk/rag/document/` directory for Document Reconciliation
  - [x] Create `/src/obelisk/rag/embedding/` directory for Embedding Generation
  - [x] Create `/src/obelisk/rag/storage/` directory for Vector Persistence
  - [x] Create `/src/obelisk/rag/common/` directory (utilities)
  - [x] Create `/src/obelisk/rag/service/` directory (RAG API service)

- [x] Move and refactor RAG components
  - [x] Move API-related code to `/src/obelisk/rag/api/`
  - [x] Move document processing to `/src/obelisk/rag/document/`
    - [x] Separate processor and watcher components
    - [x] Implement improved watched file handling
  - [x] Move embedding service to `/src/obelisk/rag/embedding/`
    - [x] Create basic embedding service structure
    - [x] Prepare for future provider interfaces
  - [x] Move storage code to `/src/obelisk/rag/storage/`
    - [x] Create vector database abstraction structure
    - [x] Prepare for multiple backend support
  - [x] Extract common utilities to `/src/obelisk/rag/common/`
  - [x] Move service code to `/src/obelisk/rag/service/`
  - [x] Update imports to absolute paths

- [x] Define clear interfaces
  - [x] Create basic interface structure for each module
  - [x] Separate code by functional boundaries
  - [x] Ensure proper import dependencies

### E. Test Reorganization

- [x] Set up test directory structure
  - [x] Create `/tests/unit/` directory
  - [x] Create `/tests/integration/` directory
  - [x] Create `/tests/e2e/` directory
  - [x] Create `/tests/data/` for test fixtures

- [x] Move existing tests
  - [x] Move core tests to appropriate directories
  - [x] Move RAG tests to unit/integration directories
  - [x] Create test fixtures and conftest.py
  - [x] Move test data to centralized location

- [x] Fix test imports and paths
  - [x] Update test imports to use absolute paths
  - [x] Ensure tests can run from project root
  - [x] Fix test isolation issues with environment variables
  - [x] Add proper test warning filters

### F. CLI and Entry Point Updates

- [x] Implement unified CLI architecture
  - [x] Create main `obelisk` entry point
  - [x] Implement `obelisk rag` subcommand
    - [x] Separate subcommand code from service implementation
    - [x] Ensure backward compatibility
  - [x] Update `pyproject.toml` entry points to single entry point
  - [x] Create `__main__.py` for module execution
  - [x] Add CLI test framework

- [x] Add development commands
  - [x] Add test command structure in CLI
  - [x] Fix CLI import structure for new layout
  - [x] Prepare for additional command implementations

### G. Testing and Validation

- [x] Test core functionality
  - [x] Test import resolution in new structure
  - [x] Test configuration module
  - [x] Test core utilities

- [x] Test RAG functionality
  - [x] Test document processing
  - [x] Test embedding generation
  - [x] Test vector storage
  - [x] Test API endpoints
  - [x] Add tests for watcher functionality

- [x] Verify test framework
  - [x] Fix environment variable handling in tests
  - [x] Fix test initialization issues
  - [x] Ensure proper test isolation
  - [x] Add warning filters for third-party libraries

### H. Documentation and Integration

- [x] Update documentation
  - [x] Add docstrings to new modules
  - [x] Update import examples in code
  - [ ] Update developer guides (in progress)
  - [ ] Document package structure (in progress)

- [x] Prepare for Docker integration
  - [x] Ensure src layout works with Docker builds
  - [x] Update package metadata for Docker usage
  - [ ] Test container builds with updated structure (pending)
  - [ ] Verify service functionality (pending)

## Implementation Strategy

### Phase 1: Basic Structure and Unified CLI

First, we'll set up the src directory structure and implement the unified CLI:

1. Create the directory structure
2. Implement the main `obelisk` CLI with subcommand architecture
3. Move core modules with minimal changes
4. Update pyproject.toml for basic functionality
5. Test core imports and functionality

### Phase 2: RAG Component Refactoring

Once the core structure is in place, we'll refactor the RAG components:

1. Create the RAG module structure aligned with architecture diagram
2. Move components one by one, testing each
3. Update imports and dependencies
4. Define clear interfaces between components
5. Separate RAG service implementation from CLI code

### Phase 3: Test Reorganization

After the source code is restructured, we'll reorganize the tests:

1. Create test directory structure
2. Move and update unit tests first
3. Then move integration and e2e tests
4. Create shared test fixtures and utilities

### Phase 4: Final Integration and Validation

Finally, we'll ensure everything works together:

1. Test package installation and imports
2. Test unified CLI functionality
3. Test Docker container builds
4. Update documentation

## Testing Approach

To ensure we don't break functionality during the restructuring:

1. **Incremental Testing**: Test each component after moving it
2. **Import Validation**: Ensure imports resolve correctly
3. **Functionality Testing**: Verify core functions work as expected
4. **Integration Testing**: Test components working together
5. **Docker Testing**: Test container builds with updated structure

## Progress Tracking

- Current Status: ✅ Complete restructuring with src-layout, test reorganization, and task management
- Completed Steps:
  1. ✅ Performed careful file-by-file cleanup:
     - ✅ Compared original files with refactored versions to ensure no functionality was lost
     - ✅ Analyzed each file in `/obelisk` directory against `/src/obelisk` counterparts
     - ✅ Verified all test functionality in old test files has equivalents in new structure
     - ✅ Documented special cases in implementation changes
     - ✅ Removed legacy files after verification
     - ✅ Moved utility scripts from `/hack` to `/tests/scripts` with proper organization
  2. ✅ Enhanced Taskfile.yaml with improved cleanup and testing tasks:
     - ✅ Added new test-all task to run all unit and integration tests
     - ✅ Enhanced clean-all task to remove cache files and test artifacts
     - ✅ Updated Docker commands to use modern "docker compose" syntax
     - ✅ Created test-rag and test-rag-e2e tasks for focused testing
     - ✅ Updated script paths from hack/ to tests/scripts/
  3. ✅ Updated docs and README to reflect new structure:
     - ✅ Refocused README on RAG system capabilities
     - ✅ Updated usage examples to match new CLI commands
     - ✅ Updated tests/README.md with comprehensive directory structure
     - ✅ Documented utility scripts categorization and organization
  4. ✅ Verified all tests pass with new structure
  5. ✅ Completed git commits with detailed, technically informative messages

- Next Steps:
  1. Complete Docker integration verification with refactored code
  2. Merge changes back to main via PR
  3. Update GitHub issue #37 with completion status and implementation details
  4. Add relevant checkmarks to PR #36 once verification is complete

## Docker Integration Verification Plan

The final verification step is to ensure all Docker components work correctly with the restructured codebase. This section outlines the comprehensive testing approach.

### 1. Container Build Verification

```bash
# Clean environment before building
task clean-all

# Build all containers with new structure
docker compose -f deployments/docker/compose/dev.yaml build

# Verify image creation
docker images | grep obelisk
```

Verify all required images are built successfully:
- obelisk-core
- obelisk-rag
- obelisk-init
- litellm

### 2. Basic Service Startup

```bash
# Start core services only
docker compose -f deployments/docker/compose/dev.yaml up -d ollama litellm obelisk-rag

# Check service health
docker compose -f deployments/docker/compose/dev.yaml ps
docker compose -f deployments/docker/compose/dev.yaml logs obelisk-rag
```

Verify:
- All services start without errors
- No import errors in logs
- Services reach ready state

### 3. Initialization Sequence Testing

```bash
# Test init container functionality
task docker-test-init

# Verify Ollama model downloads
docker compose -f deployments/docker/compose/dev.yaml exec ollama ollama list
```

Run initialization test script:
```bash
./tests/scripts/docker/test_init.py
```

Verify:
- Init container completes successfully
- Required models are downloaded
- Services properly configured

### 4. RAG Functionality Testing

Execute RAG system tests against running containers:

```bash
# Test RAG functionality with containers
./tests/scripts/integration/test_rag.py --docker

# Test specific RAG components
./tests/scripts/integration/test_rag_e2e.py --container
```

Use task runner for standard tests:
```bash
task test-rag-container
```

Verify:
- Document indexing works
- Vector storage connectivity functions
- Query responses return expected results

### 5. API Integration Testing

Test the OpenAI-compatible API endpoints:

```bash
# Test OpenAI API integration
./tests/scripts/integration/test_openai_integration.sh

# Verify endpoint functionality
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/llama3",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

Verify:
- API endpoints respond correctly
- Request/response format matches OpenAI spec
- Error handling works properly

### 6. End-to-End System Testing

Perform complete system tests:

```bash
# Start all services
docker compose -f deployments/docker/compose/dev.yaml up -d

# Run e2e test suite
./tests/scripts/integration/test_e2e_openai.py
```

Use the comprehensive e2e test task:
```bash
task test-e2e-full
```

Verify:
- Complete workflow from document to query response
- Integration between all services
- System handles errors gracefully

### 7. Performance Validation

Check system performance metrics:

```bash
# Monitor resource usage
docker stats --no-stream

# Test with multiple concurrent requests
./tests/scripts/integration/test_rag_concurrency.py --threads 10
```

Verify:
- Memory usage within expected ranges
- Response times acceptable
- System stable under load

### 8. Container Version Verification

Ensure all containers are using the proper versions:

```bash
# Check container versions
./tests/scripts/docker/check_container_versions.sh
```

Verify:
- All components using expected versions
- No version mismatches between services

### 9. Vector Database Integration

Test specific vector database connections:

```bash
# Test ChromaDB integration
task test-rag-chroma

# Test Milvus integration (if available)
./tests/scripts/integration/test_rag_milvus.py --docker
```

Verify:
- Vector database connections successful
- Storage and retrieval operations function correctly
- Migrations and schema handling work properly

### 10. Cleanup and Documentation

After successful verification:

```bash
# Stop all containers
docker compose -f deployments/docker/compose/dev.yaml down

# Clean testing artifacts
task clean-all
```

Document any issues or workarounds in:
- GitHub PR comments
- Updated deployment documentation
- Release notes for future reference

## Future Architecture Support

This restructuring lays critical groundwork for:

1. **Document Reconciliation Microservice**: The `/src/obelisk/rag/document/` module is designed to be extractable as a standalone microservice (issue #33)
2. **Embedding Generation Microservice**: The `/src/obelisk/rag/embedding/` module is designed to be extractable as a standalone microservice (issue #34)
3. **Vector Persistence Layer**: The `/src/obelisk/rag/storage/` module provides clean interfaces for different vector database backends
4. **Unified Command Interface**: The restructured CLI with subcommands provides a consistent user experience
5. **Enhanced Testing**: Improved test structure supports better test coverage (related to issue #21)

## Conclusion

This plan provides a structured approach to implementing the package restructuring phase. By following this plan, we'll achieve a more maintainable, scalable package structure that aligns with the architecture diagram while maintaining a unified CLI experience.
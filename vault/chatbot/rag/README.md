# Obelisk RAG Documentation

This document serves as the central reference for Obelisk's Retrieval Augmented Generation (RAG) implementation. It provides an overview of components, configuration options, and integration points, while directing readers to specific documentation files for detailed information.

## Current Implementation

The Obelisk RAG system provides document indexing, vector storage, and query capabilities through a modular architecture with the following key components:

### Core Components

| Component | Documentation | Purpose |
|-----------|---------------|---------|
| Document Processor | [implementation.md](./implementation.md) | Handles markdown parsing, chunking, and metadata extraction |
| Embedding Service | [implementation.md](./implementation.md) | Generates vector embeddings using Ollama |
| Vector Storage | [vector-database.md](./vector-database.md) | Stores and retrieves document vectors using ChromaDB |
| Query Pipeline | [query-pipeline.md](./query-pipeline.md) | Processes queries to retrieve relevant context |
| RAG Service | [implementation.md](./implementation.md) | Central service orchestrating all RAG components |

### APIs & Integration

| Feature | Documentation | Status |
|---------|---------------|--------|
| OpenAI-compatible API | [using-rag.md](./using-rag.md) | ✅ Implemented |
| Ollama Integration | [ollama-integration.md](./ollama-integration.md) | ✅ Implemented |
| OpenWebUI Integration | [openwebui-integration.md](./openwebui-integration.md) | ✅ Implemented |

### User Guides

- [getting-started.md](./getting-started.md) - Step-by-step guide with RAG overview and first-time setup
- [using-rag.md](./using-rag.md) - Comprehensive usage documentation with examples
- [implementation-status.md](./implementation-status.md) - Current implementation status and roadmap

## Vector Database Implementation

The current implementation uses ChromaDB for vector storage. Future development roadmap includes potential migration to Milvus Lite for improved performance and scalability.

| Database | Status | Documentation |
|----------|--------|---------------|
| ChromaDB | Current Implementation | [vector-database.md](./vector-database.md) |
| Milvus Lite | Future Roadmap | [vector-database.md](./vector-database.md) |

## Documentation Progress

Based on the analysis in `task.md`, we've made significant improvements to the documentation:

### Completed Tasks

✅ **High Priority**
- Consolidated API to use only the OpenAI-compatible endpoint 
- Created comprehensive `openwebui-integration.md` documentation
- Updated vector database documentation to reflect ChromaDB implementation
- Fixed WebUI integration inconsistencies

✅ **Medium Priority**
- Updated API documentation with OpenAI-compatible format
- Fixed environment variable inconsistencies (`OLLAMA_URL` vs `OLLAMA_API_URL`)
- Added detailed document chunking documentation to `implementation.md`
- Documented error handling strategies and debug mode

### All Tasks Completed ✅

1. **Low Priority Items**
   - ✅ Document the discrepancy between documented embedding batching and implementation
   - ✅ Update roadmap documentation to clearly mark implemented vs. planned features in architecture-draft.md
   - ✅ Add debug mode documentation
   - ✅ Improve troubleshooting guidance with more examples in using-rag.md

## Documentation Maintenance Guidelines

When updating the RAG documentation, follow these principles:

1. **Accuracy**: Documentation must precisely match the implemented code
2. **Completeness**: Cover all aspects including setup, configuration, usage, and APIs
3. **Examples**: Include working code samples for key functionality
4. **Future Direction**: Clearly label future roadmap items vs. current implementation

### Document Update Matrix

| When changing... | Update these docs |
|------------------|-------------------|
| API endpoints | `using-rag.md` |
| Configuration options | `using-rag.md`, `getting-started.md` |
| Vector database | `vector-database.md`, `implementation.md` |
| Query pipeline | `query-pipeline.md`, `implementation.md` |
| OpenWebUI integration | `openwebui-integration.md` (to be created) |
| Ollama integration | `ollama-integration.md` |

## Related Documentation

Architecture documentation and detailed implementation information can be found in separate files:

- [architecture-draft.md](./architecture-draft.md) - Technical architecture with implementation status markers
- [implementation-status.md](./implementation-status.md) - Implementation roadmap and current status

## Implementation Notes

The current RAG implementation includes:

1. **Document Processing**
   - Markdown parsing with YAML frontmatter extraction
   - RecursiveCharacterTextSplitter for document chunking
   - Real-time file watching with the watchdog library

2. **Embedding Generation**
   - Ollama integration using mxbai-embed-large model
   - 1024-dimension vector embeddings
   - Support for both document and query embedding

3. **Vector Storage**
   - ChromaDB for vector database storage
   - Metadata filtering for search refinement
   - Local persistence on disk

4. **Query Processing**
   - Top-k similarity search with configurable parameters
   - Contextual prompt construction
   - LLM response generation via Ollama

5. **API & Integration**
   - OpenAI-compatible API endpoint for tool integration
   - Source information included in API responses
   - Docker containerization for deployment

## Configuration Reference

The RAG system can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| VAULT_DIR | Directory containing markdown files | /app/vault |
| CHROMA_DIR | Directory for vector database | /app/data/chroma_db |
| OLLAMA_URL | URL of the Ollama service | http://ollama:11434 |
| OLLAMA_MODEL | Ollama model for generation | llama3 |
| EMBEDDING_MODEL | Model for embeddings | mxbai-embed-large |
| RETRIEVE_TOP_K | Number of document chunks to retrieve | 3 |
| API_HOST | Host to bind API server | 0.0.0.0 |
| API_PORT | Port for API server | 8000 |
| LOG_LEVEL | Logging level | INFO |
| RAG_DEBUG | Enable debug mode | false |
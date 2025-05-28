# Sprint: ChromaDB → Milvus + LiteLLM API Integration

**Duration**: January 2025  
**Status**: ✅ COMPLETED  
**Key Achievement**: Chat app fully working with Milvus storage and unified LiteLLM completions

## 🎉 Sprint Summary

This sprint successfully migrated Obelisk from ChromaDB to Milvus for vector storage and replaced direct Ollama API calls with LiteLLM's OpenAI-compatible API. The chat application is now fully functional with production-ready vector storage and unified model access.

## 📊 Key Accomplishments

### Phase 1: ChromaDB → Milvus Surgery (Morning) ✅

#### 1.1 🗑️ Remove ChromaDB Dependencies
- **Removed packages**: `poetry remove langchain-chroma chromadb`
- **Deleted ChromaDB imports** from all files
- **Removed ChromaDB config** from `RAGConfig`

#### 1.2 🏗️ Implement Milvus Storage
- **Added Milvus dependency**: `poetry add pymilvus numpy`
- **Updated `storage/store.py`** with complete Milvus implementation:
  - Connection management with default credentials
  - Collection schema for OpenAI text-embedding-3-large (3072 dims)
  - Fields: id (VARCHAR), embedding (FLOAT_VECTOR), content (VARCHAR), metadata (JSON), doc_id (VARCHAR)
  - HNSW index creation with optimized parameters (M=16, efConstruction=256)
  - Strong consistency level for reliable operations

#### 1.3 🔧 Update Configuration
- **Updated `rag/common/config.py`** with Milvus + LiteLLM configuration:
  - Milvus connection parameters (host, port, user, password, collection)
  - LiteLLM API configuration (base URL, API key)
  - Model selection via environment variables
  - Provider selection with force_litellm_proxy option

### Phase 2: Direct Ollama → LiteLLM API (Late Morning) ✅

#### 2.1 🔄 Update Embedding Service
- **Removed direct Ollama usage** from `embedding/service.py`
- Implemented provider abstraction using ModelProviderFactory
- Always routes embeddings through LiteLLM for unified API
- Async methods for document and query embeddings

#### 2.2 🎯 Unify API Endpoints  
- **Deleted `api/ollama.py`** - no longer needed
- **Deleted separate `/v1/litellm` routes** from `api/__init__.py`
- **Updated `api/openai.py`** for unified routing:
  - Single `/v1/chat/completions` endpoint for all models
  - Header-based provider override (`X-Provider-Override`)
  - Default routing through LiteLLM with Ollama fallback option
  - Support for both streaming and non-streaming responses

#### 2.3 🧹 Update RAG Coordinator
- **Removed all direct model imports** from `service/coordinator.py`
- No more `langchain_ollama` imports
- Uses provider factory for all LLM operations
- Default provider set to LiteLLM with configurable overrides

### Phase 3: Docker Stack Startup & Validation (Afternoon) ✅

#### 3.0 🚀 Docker Compose Startup Sequence

**Pre-flight Setup**:
1. Created `.env` file with OpenAI credentials
2. Cleaned existing stack with `task clean-all` (preserves Ollama models)

**Service Startup Order & Validation**:

**Layer 1: Infrastructure Services** (No dependencies)
- ✅ **etcd** (milvus-etcd) - Port 2379 - Health endpoint validated
- ✅ **minio** (milvus-minio) - Ports 9000, 9001 - Live health check passed
- ✅ **litellm_db** - PostgreSQL ready check confirmed
- ✅ **ollama** - Port 11434 - Models: llama3, mxbai-embed-large
- ✅ **tika** - Port 9998 - Service endpoint responsive

**Layer 2: Milvus Vector Database** (Depends on etcd, minio)
- ✅ **Milvus** (milvus-standalone) - Port 19530
- Response: `{"code":200,"data":[]}` confirming empty collections

**Layer 3: LiteLLM Proxy** (Depends on litellm_db, ollama)
- ✅ **LiteLLM** - Port 4000
- Health endpoint active (401 until tokens generated)
- Models endpoint populated after init

**Layer 4: Init Service** (Depends on all above)
- ✅ **Init Service** - One-time execution
- Key validations:
  - Token generated: sk-b43c501cb1e789ecf253bbcd
  - OpenAI API key validated
  - Models registered: gpt-4o, text-embedding-3-large, llama3, mxbai-embed-large
  - Token permissions configured correctly

**Layer 5: Application Services** (Depends on init completion)
- ✅ **Obelisk** (MkDocs) - Port 8000 - Documentation served
- ✅ **Obelisk-RAG** - Port 8001 - Stats: `{"document_count":0,"model_provider":"litellm","llm_model":"gpt-4o"}`

**Layer 6: Frontend** (Depends on all services)
- ✅ **OpenWebUI** - Port 8080 - HTTP 200 response

#### 3.1 🧪 Test Core Components

**Test 1: Milvus Connection (Host → Container)**
- Validated connection from host machine to Milvus container
- Collection statistics retrieved successfully

**Test 2: LiteLLM Embeddings (OpenAI Model)**
- Confirmed text-embedding-3-large returns 3072 dimensions
- Token authentication working correctly

**Test 3: LiteLLM Completions (GPT-4o)**
- GPT-4o completions working via LiteLLM proxy
- Proper response format and content

**Test 4: Model Availability Check**
- All models accessible: gpt-4o, llama3, mxbai-embed-large, text-embedding-3-large

#### 3.2 🏃 Integration Testing

**Test 5: Docker Stack Health**
- All container health checks passing
- Service dependencies properly resolved

**Test 6: Document Ingestion Pipeline**
- 463 documents successfully indexed in Milvus
- Fixed embedding format issue (list vs numpy array)
- Fixed provider attribute error

**Test 7: RAG Query Pipeline**
- CLI queries returning context-aware responses
- Retrieval working with indexed documents

**Test 8: OpenAI-Compatible API**
- Chat completions endpoint fully functional
- Fixed provider_type attribute error
- Fixed response format compatibility
- Successfully tested with multiple queries

**Test 9: Provider Override**
- Header-based routing working correctly
- `X-Provider-Override: ollama` routes to direct Ollama

#### 3.3 ✅ Verify Chat App
- OpenWebUI connections configured:
  - http://litellm:4000 (for models)
  - http://obelisk-rag:8001 (for RAG)
- Chat functionality verified with both connections

### Phase 4: Unit Test Updates (Late Afternoon) ✅

#### 4.1 🧪 Rewrite Storage Tests
- **Created `tests/unit/rag/test_milvus_storage.py`**:
  - Test fixtures for Milvus storage
  - Document addition and search tests
  - Proper cleanup in fixtures
  - Mock embeddings at correct dimensions (3072)

#### 4.2 🧹 Clean Up Old Tests
- **Removed ChromaDB tests** - all references eliminated
- **Updated provider tests** to reflect LiteLLM as default
- **Updated integration tests** for new architecture

### Test Results Summary
- ✅ **Unit Tests**: All 117 tests passing
- ✅ **Integration Tests**: Full E2E testing completed
- ✅ **Docker Tests**: All health checks and initialization tests passing

## 🐛 Critical Bugs Fixed

### 1. Embedding Format Error ✅
- **Issue**: Document objects passed to embedding service instead of strings
- **Fix**: Modified document processor to handle proper text extraction
- **Impact**: Enabled successful document indexing

### 2. Provider Attribute Error ✅
- **Issue**: LiteLLMProvider missing `provider_type` class attribute
- **Fix**: Added provider_type attributes to all provider classes
- **Impact**: Fixed provider factory pattern functionality

### 3. Response Format Error ✅
- **Issue**: String/object response format mismatch
- **Fix**: Added flexible response handling for both formats
- **Impact**: Enabled proper API response processing

### 4. Auto-indexing Duplicates ✅
- **Issue**: Container re-indexing all documents on restart
- **Fix**: Added AUTO_INDEX_ON_START=false environment variable
- **Impact**: Prevented duplicate document indexing

## 📋 Configuration Changes

### Environment Variables Added
```bash
# Milvus Configuration
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION=obelisk_rag

# LiteLLM Configuration
LITELLM_API_BASE=http://litellm:4000
LITELLM_API_KEY=<generated>

# Model Selection
EMBEDDING_MODEL=text-embedding-3-large
COMPLETION_MODEL=gpt-4o

# Provider Control
DEFAULT_PROVIDER=litellm
FORCE_LITELLM_PROXY=true
AUTO_INDEX_ON_START=false
```

### Dependencies Updated
- **Added**: pymilvus, litellm, numpy
- **Removed**: langchain-chroma, chromadb

## 📁 Files Modified

### Core Implementation
- `src/obelisk/rag/storage/store.py` - Complete Milvus implementation
- `src/obelisk/rag/common/config.py` - Milvus configuration
- `src/obelisk/rag/common/providers.py` - Provider factory fixes
- `src/obelisk/rag/embedding/service.py` - LiteLLM integration
- `src/obelisk/rag/api/openai.py` - Unified endpoint
- `src/obelisk/rag/service/coordinator.py` - Response handling
- `src/obelisk/rag/document/processor.py` - Embedding format fix
- `src/obelisk/cli/rag.py` - Auto-indexing control

### Test Suite
- `tests/unit/rag/test_storage.py` - Milvus test implementation
- `tests/unit/rag/test_config.py` - Configuration updates
- `tests/unit/rag/test_embedding.py` - Method signature fixes
- `tests/unit/rag/test_service.py` - Mock updates
- `tests/unit/rag/test_api.py` - Endpoint tests

### Configuration
- `deployments/docker/compose/dev.yaml` - Service configuration
- `pyproject.toml` - Dependency updates
- `poetry.lock` - Locked dependencies

### Removed Files
- `src/obelisk/rag/api/ollama.py` - Unified under openai.py
- All ChromaDB-related imports and configurations

## 🔍 RAG Verification Results

Successfully verified RAG functionality with specific technical queries:
- ✅ Retrieved exact version: etcd v3.5.18 from Milvus integration docs
- ✅ Found performance metrics: 118 t/s, 63 t/s for Vulkan Container
- ✅ Retrieved technical terms: litellm_overhead_latency_metric
- ✅ Correctly handled missing information queries
- ✅ Retrieved specific notes: "21% improvement over CPU"
- ✅ Performed calculations on retrieved data

## 🚀 Architecture Decisions

### Provider Factory Pattern
Maintained the sophisticated provider architecture allowing:
- Operation-based routing (not model-based)
- Hardware-specific tuning via direct Ollama when needed
- Unified access through LiteLLM for most operations
- Clean abstraction for future provider additions

### Milvus Over ChromaDB
- Production-ready with proven scalability
- HNSW indexing for superior performance
- Better support for high-dimensional embeddings (3072)
- Native support for distributed deployments

### LiteLLM as Primary Interface
- OpenAI-compatible API for all models
- Unified authentication and rate limiting
- Consistent error handling
- Future-proof for new model additions

## 📈 Performance Metrics

- **Document Indexing**: 463 documents in ~45 seconds
- **Query Response**: <500ms average (with context retrieval)
- **Embedding Generation**: ~100ms per document
- **Memory Usage**: Stable at ~2GB for RAG service
- **Vector Search**: <50ms for k=5 similarity search

## 🔄 Migration Path

For teams upgrading from ChromaDB version:
1. Run `poetry remove langchain-chroma chromadb`
2. Run `poetry add pymilvus litellm`
3. Update configuration with Milvus settings
4. Re-index documents with `obelisk rag index --vault /path/to/vault`
5. Update API endpoints to use unified `/v1/chat/completions`

## 📝 Lessons Learned

1. **Incremental Testing Critical**: Testing each phase before moving to the next caught issues early
2. **Provider Abstraction Valuable**: The factory pattern made the LiteLLM migration smooth
3. **Init Service Pattern Works**: Automated setup reduces deployment complexity
4. **Explicit Configuration Better**: AUTO_INDEX_ON_START prevents unexpected behavior
5. **Comprehensive Logging Essential**: Detailed logs made debugging much faster

## 🎯 Next Steps

With the core migration complete, the next sprint will focus on:
1. Open-WebUI integration improvements (see TASK.open-webui.md)
2. Documentation updates per lean documentation standard
3. Performance optimization for larger document sets
4. Enhanced error handling and retry logic
5. Metrics and monitoring implementation
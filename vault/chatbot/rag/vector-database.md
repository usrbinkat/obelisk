# Vector Database Integration

The Obelisk RAG pipeline uses a vector database to store and query document embeddings. This page documents the current implementation and future options.

## Current Implementation: ChromaDB

Obelisk's RAG system currently uses **ChromaDB** as its vector database. ChromaDB was chosen for its:

- Lightweight embeddable architecture
- Ease of integration with LangChain
- Simple persistence model
- Good performance for small to medium document collections
- No additional services required (runs in-process)

### Configuration

ChromaDB is configured through environment variables or the RAG configuration system:

```bash
# Configure ChromaDB storage location
export CHROMA_DIR="/path/to/vectordb"
```

The default storage location is `./.obelisk/vectordb/` in development and `/app/data/chroma_db` in Docker.

### Implementation Details

The current ChromaDB implementation:

- Uses persistent storage at the configured CHROMA_DIR location
- Stores document content, metadata, and embeddings
- Utilizes the default ChromaDB collection
- Filters metadata to ensure compatibility (only primitive types)
- Provides similarity search with configurable k value (default: 3)
- Integrates with Ollama's embedding models (default: mxbai-embed-large)

### Limitations

The current implementation has some limitations:

- Limited metadata filtering capabilities
- No batch optimization for large document sets
- Basic error handling for database corruption
- No custom ChromaDB settings for advanced use cases

## Future Vector Database Options

As Obelisk's RAG system evolves, several alternative vector databases are being evaluated for different use cases and scale requirements:

| Database | Description | Use Case |
|----------|-------------|----------|
| Milvus | Distributed vector database | Large-scale deployments |
| FAISS | Meta's efficient similarity search | High-performance requirements |
| Qdrant | Scalable vector search engine | Advanced filtering needs |
| Weaviate | Knowledge graph + vector search | Complex semantic relationships |

## Current Embedding Implementation

The current implementation uses:

- **Local embedding models** via Ollama (default: `mxbai-embed-large`)
- 1024-dimension vectors optimized for semantic similarity
- Synchronous embedding generation through Ollama's API

## Database Schema

The ChromaDB instance currently stores:

1. **Document embeddings**: Vector representations of content chunks (1024-dimensional)
2. **Metadata**: Basic information about each chunk (source, title, etc.)
3. **Document content**: The original text for retrieval

Current metadata schema includes:

```json
{
  "metadata": {
    "source": "development/docker.md",
    "title": "Docker Configuration",
    "chunk_id": "dev-docker-compose-001"
  },
  "text": "The `docker-compose.yaml` file orchestrates the complete Obelisk stack, including optional AI components..."
}
```

> Note: Only primitive data types (string, number, boolean) are supported in metadata to ensure ChromaDB compatibility.

## Storage & Persistence

The current ChromaDB implementation uses persistent storage:

- Default location: `./.obelisk/vectordb/` (development) or `/app/data/chroma_db` (Docker)
- Configurable via `CHROMA_DIR` environment variable
- Mounted as a Docker volume in containerized deployments for persistence
- Uses ChromaDB's built-in persistence mechanism

## Current Query Implementation

The RAG query process:

1. Embed the user query using the same embedding model
2. Perform similarity search to find the top-k most relevant chunks (default k=3)
3. Extract and format the retrieved chunks for context
4. Generate a response using the retrieved context

## Integration Points

The current vector database integrates with:

- **RAG CLI**: Direct interface for indexing and querying
- **Document watcher**: Monitors file changes for real-time updates
- **Ollama API**: Uses Ollama for embeddings and generation
- **OpenAI-compatible API**: Provides an endpoint for tools like Open WebUI

## Current Configuration Options

Configure the vector database through environment variables:

```bash
# Vector database location
export CHROMA_DIR="/path/to/db"

# Number of results to retrieve
export RETRIEVE_TOP_K=5

# Embedding model to use
export EMBEDDING_MODEL="mxbai-embed-large" 
```

## Future Enhancements

Planned improvements to the vector database implementation:

1. **Advanced Filtering**: Enhanced metadata filtering capabilities
2. **Hybrid Search**: Combining vector search with keyword search
3. **Batch Processing**: Optimized handling of large document collections
4. **Milvus Integration**: Support for Milvus as an alternative backend
5. **Custom Collection Management**: Multiple collections for different document types

## Alternative Databases

While ChromaDB is the default vector database for Obelisk's RAG implementation, several alternatives can be considered for different use cases:

### Qdrant

**Benefits for Obelisk:**
- High-performance search with HNSW algorithm
- Powerful filtering capabilities
- Cloud-hosted or self-hosted options
- Strong scaling capabilities

**Integration Example:**
```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize Qdrant client
client = QdrantClient(host="localhost", port=6333)

# Create collection for Obelisk embeddings
client.create_collection(
    collection_name="obelisk_docs",
    vectors_config=models.VectorParams(
        size=768,  # Embedding dimensions
        distance=models.Distance.COSINE
    )
)

# Store embeddings
client.upload_points(
    collection_name="obelisk_docs",
    points=[
        models.PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={"text": text, "metadata": metadata}
        )
        for chunk_id, embedding, text, metadata in zip(ids, embeddings, texts, metadatas)
    ]
)
```

### Milvus

**Benefits for Obelisk:**
- Cloud-native architecture
- Handles billions of vectors
- Excellent for large documentation sites
- Advanced query capabilities

**When to choose Milvus:**
- Your documentation exceeds 100,000 pages
- You need multi-tenant isolation
- You require complex metadata filtering
- Enterprise deployment with high availability requirements

### FAISS (with SQLite)

**Benefits for Obelisk:**
- Extremely lightweight
- Optimized for in-memory performance
- No additional services required
- Perfect for small to medium documentation

**Integration approach:**
- Store vectors in FAISS
- Use SQLite for metadata and text storage
- Join results using document IDs

### Configuring Alternative Databases

To use an alternative vector database with Obelisk:

```yaml
# In a future configuration file
rag:
  vector_db:
    type: "qdrant"  # Options: chroma, qdrant, milvus, faiss
    connection:
      host: "localhost"
      port: 6333
    collection: "obelisk_docs"
    embedding_dimensions: 768
```
# Vector Database Integration

The Obelisk RAG pipeline will require a vector database to store and query document embeddings. This page outlines the planned implementation details.

## Vector Database Options

Several vector database options are being evaluated for integration with Obelisk:

| Database | Description | Deployment |
|----------|-------------|------------|
| Chroma | Lightweight, open-source | Embedded or server |
| FAISS | Meta's efficient similarity search | In-memory |
| Qdrant | Scalable vector search engine | Docker container |
| Weaviate | Knowledge graph + vector search | Docker container |
| Milvus | Distributed vector database | Kubernetes or Docker |

The initial implementation will likely use **ChromaDB** for its simplicity and easy integration.

## Embedding Models

Document chunks will be converted to vector embeddings using:

- **Local embedding models** via Ollama (e.g., `nomic-embed-text`)
- **Optional integration** with OpenAI embeddings for higher quality

## Database Schema

The vector database will store:

1. **Document embeddings**: Vector representations of content chunks
2. **Metadata**: Structured information about each chunk
3. **Document content**: The original text for retrieval

Example schema:

```json
{
  "embedding": [0.123, 0.456, ...],  // Vector embedding
  "metadata": {
    "source": "development/docker.md",
    "title": "Docker Configuration",
    "heading_path": ["Docker Configuration", "Docker Compose Configuration"],
    "last_updated": "2023-04-15",
    "tags": ["docker", "configuration"],
    "chunk_id": "dev-docker-compose-001"
  },
  "text": "The `docker-compose.yaml` file orchestrates the complete Obelisk stack, including optional AI components..."
}
```

## Storage & Persistence

The vector database will be stored in a configurable location:

- Default: `./.obelisk/vectordb/`
- Configurable via environment variables or config file
- Docker volume mount for containerized deployments

## Query Optimization

Several techniques will optimize retrieval performance:

1. **Filtering**: Pre-filter by metadata before vector search
2. **Hybrid search**: Combine keyword and semantic search
3. **Re-ranking**: Two-stage retrieval with initial recall and re-ranking
4. **Caching**: Frequently accessed embeddings and results

## Integration Points

The vector database will integrate with:

- **Obelisk build process**: Generate embeddings during site building
- **Incremental updates**: Update embeddings when content changes
- **Ollama API**: Connect with the model server for retrieval
- **Open WebUI**: Provide context to the chat interface

## Configuration Options

Users will be able to configure the vector database through:

```yaml
# Example future configuration (mkdocs.yml)
plugins:
  - obelisk-rag:
      embedding_model: nomic-embed-text
      vector_db: chroma
      vector_db_path: ./.obelisk/vectordb
      chunk_size: 512
      chunk_overlap: 128
      filter_private_content: true
      incremental_updates: true
```

## Performance Considerations

Database performance will be optimized for different deployment scenarios:

- **Small sites**: In-memory vector database
- **Medium sites**: Local persistent database
- **Large sites**: Dedicated database service
- **Multi-user deployments**: Shared database with caching

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
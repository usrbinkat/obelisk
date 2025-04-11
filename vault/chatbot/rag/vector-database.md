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
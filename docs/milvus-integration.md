# Milvus Vector Database Integration

This document describes the integration of Milvus vector database into the Obelisk project to enhance RAG (Retrieval-Augmented Generation) capabilities.

## Overview

[Milvus](https://milvus.io/) is an open-source vector database designed for embedding similarity search and AI applications. It provides:

- High-performance vector similarity search
- Scalable architecture
- Flexible index types for different use cases
- Support for hybrid search (vector + scalar filtering)

In the Obelisk project, Milvus serves as the vector database backend for storing and retrieving document embeddings used in the RAG pipeline.

## Architecture

The Milvus integration consists of the following components:

1. **Milvus Standalone Service**: A self-contained Milvus instance that includes:
   - Milvus Server
   - Metadata Management (etcd)
   - Storage Backend (MinIO)

2. **OpenWebUI Integration**: Configuration to use Milvus as the vector store for OpenWebUI's RAG features.

3. **Obelisk-RAG Integration**: Configuration to use Milvus as the vector store for Obelisk's RAG service.

## Deployment

The Milvus integration is defined in the `docker-compose.yaml` file and includes:

### Milvus Ecosystem Services

1. **etcd**: For metadata management
   ```yaml
   etcd:
     container_name: milvus-etcd
     image: quay.io/coreos/etcd:v3.5.18
     # Configuration...
   ```

2. **MinIO**: For storage management
   ```yaml
   minio:
     container_name: milvus-minio
     image: minio/minio:RELEASE.2023-03-20T20-16-18Z
     # Configuration...
   ```

3. **Milvus Server**: The main Milvus service
   ```yaml
   milvus:
     container_name: milvus-standalone
     image: milvusdb/milvus:v2.5.10
     # Configuration...
   ```

### OpenWebUI Integration

OpenWebUI is configured to use Milvus for its RAG features:

```yaml
open-webui:
  # Other configuration...
  environment:
    # RAG configuration
    - RETRIEVAL_ENABLED=true
    - RETRIEVAL_VECTOR_STORE=milvus
    - MILVUS_URI=http://milvus:19530
    - MILVUS_HOST=milvus
    - MILVUS_PORT=19530
    # Other environment variables...
```

### Obelisk-RAG Integration

The Obelisk-RAG service is configured to use Milvus:

```yaml
obelisk-rag:
  # Other configuration...
  environment:
    # Milvus configuration
    - VECTOR_DB=milvus
    - MILVUS_URI=http://milvus:19530
    - MILVUS_HOST=milvus
    - MILVUS_PORT=19530
    # Other environment variables...
```

## Verification

The Milvus integration has been verified using test scripts that:

1. Connect to Milvus and create a collection
2. Insert document embeddings
3. Create an index for efficient searching
4. Perform vector similarity searches
5. Verify connectivity from OpenWebUI

Test scripts can be found in the `/hack` directory:
- `test_milvus.py`: Basic Milvus functionality test
- `test_rag_milvus.py`: Verification of RAG configuration
- `test_rag_e2e.py`: End-to-end RAG pipeline test

## Usage

When the Obelisk stack is deployed with `docker-compose up`, the Milvus integration is automatically configured and available. Users can:

1. Upload documents via the OpenWebUI interface
2. Embed documents into the Milvus vector database
3. Use RAG for enhanced AI responses based on document context

No additional configuration is required for basic usage.

## Advanced Configuration

For advanced configurations, you can modify the following environment variables:

### Milvus Server Configuration
- `ETCD_ENDPOINTS`: etcd endpoint for metadata storage
- `MINIO_ADDRESS`: MinIO address for object storage

### OpenWebUI RAG Configuration
- `RETRIEVAL_ENABLED`: Enable/disable RAG features
- `RETRIEVAL_VECTOR_STORE`: Vector database type (milvus)
- `MILVUS_URI`/`MILVUS_HOST`/`MILVUS_PORT`: Connection parameters

### Obelisk-RAG Configuration
- `VECTOR_DB`: Vector database type (milvus)
- `MILVUS_URI`/`MILVUS_HOST`/`MILVUS_PORT`: Connection parameters

## Troubleshooting

Common issues and solutions:

1. **Cannot connect to Milvus**: Ensure the Milvus service is running and network settings are correct
   ```bash
   docker ps | grep milvus
   docker logs milvus-standalone
   ```

2. **Vector search returns no results**: Verify collection exists and has data
   ```python
   from pymilvus import connections, utility
   connections.connect("default", host="localhost", port="19530")
   print(utility.list_collections())
   ```

3. **OpenWebUI RAG not working**: Check OpenWebUI logs for connection issues
   ```bash
   docker logs open-webui | grep -i milvus
   ```
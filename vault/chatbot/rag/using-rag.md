---
title: Using the RAG System
date: 2025-04-11
---

# Using the Obelisk RAG System

This guide provides step-by-step instructions for setting up and using the Retrieval Augmented Generation (RAG) system in Obelisk. The RAG system enhances your chatbot by providing it with contextual information from your documentation.

## Quick Start

The RAG system is accessible through the `obelisk-rag` command-line tool. Here's how to get started:

```bash
# Index your documentation
obelisk-rag index

# Query the system
obelisk-rag query "What is Obelisk?"

# Start the API server
obelisk-rag serve --watch
```

## Installation

The RAG system is included with Obelisk. If you've already installed Obelisk using Poetry, you have everything you need:

```bash
# Verify installation
poetry run obelisk-rag --help
```

If you're using Docker, the RAG system is available in the Obelisk container:

```bash
docker-compose up obelisk
docker exec -it obelisk obelisk-rag --help
```

## Setup and Configuration

### Basic Configuration

By default, the RAG system is configured to:

1. Read documentation from the `./vault` directory
2. Store vector embeddings in `./.obelisk/vectordb`
3. Connect to Ollama at `http://localhost:11434`
4. Use `llama3` as the LLM and `mxbai-embed-large` as the embedding model

You can view the current configuration with:

```bash
obelisk-rag config --show
```

### Custom Configuration

You can customize the configuration using:

1. **Environment variables**:

```bash
# Set the vault directory
export VAULT_DIR="/path/to/your/docs"

# Set the Ollama URL
export OLLAMA_URL="http://ollama:11434"

# Set the models
export OLLAMA_MODEL="mistral"
export EMBEDDING_MODEL="mxbai-embed-large"

# Set chunking parameters
export CHUNK_SIZE="1500"
export CHUNK_OVERLAP="200"

# Set retrieval parameters
export RETRIEVE_TOP_K="5"

# Set API settings
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

2. **Command-line configuration**:

```bash
# Set a configuration value
obelisk-rag config --set "vault_dir=/path/to/your/docs"
obelisk-rag config --set "ollama_model=mistral"
```

3. **Command-specific options**:

```bash
# Specify vault directory for indexing
obelisk-rag index --vault /path/to/your/docs

# Specify API host and port
obelisk-rag serve --host 0.0.0.0 --port 9000
```

## Indexing Your Documentation

Before you can query your documentation, you need to index it. This process:

1. Reads all markdown files in your vault
2. Extracts content and metadata
3. Chunks the content into appropriate segments
4. Generates embeddings for each chunk
5. Stores the embeddings in a vector database

To index your documentation:

```bash
# Index using the default vault directory
obelisk-rag index

# Index a specific directory
obelisk-rag index --vault /path/to/your/docs
```

The indexing process might take some time depending on the size of your documentation. Progress will be displayed in the console.

## Querying the System

Once your documentation is indexed, you can query it:

```bash
# Ask a question
obelisk-rag query "How do I customize the theme?"

# Get JSON output
obelisk-rag query "What is the configuration format?" --json
```

The system will:

1. Convert your query to an embedding
2. Find the most relevant document chunks
3. Include those chunks as context for the LLM
4. Generate a response based on the documentation

The output includes:
- The query
- The generated response
- The sources of information used

## Starting the API Server

For integration with applications, you can start the RAG API server:

```bash
# Start the server
obelisk-rag serve

# Start the server with document watching
obelisk-rag serve --watch

# Specify host and port
obelisk-rag serve --host 0.0.0.0 --port 9000
```

The `--watch` flag enables real-time document monitoring, so changes to your documentation will be automatically indexed.

### API Endpoints

The API server provides the following endpoints:

1. **GET /stats**
   - Returns statistics about the RAG system
   - Example: `curl http://localhost:8000/stats`

2. **POST /query**
   - Processes a query using the RAG system
   - Example:
     ```bash
     curl -X POST http://localhost:8000/query \
       -H "Content-Type: application/json" \
       -d '{"query": "What is Obelisk?"}'
     ```

## Integration with Open WebUI

You can integrate the RAG API with Open WebUI to enhance the chat interface with your documentation.

### Setup

1. Ensure the RAG API server is running:
   ```bash
   obelisk-rag serve --watch
   ```

2. In Open WebUI, add a new API-based model:
   - Name: "Obelisk RAG"
   - Base URL: "http://localhost:8000"
   - API Path: "/query"
   - Request Format:
     ```json
     {
       "query": "{prompt}"
     }
     ```
   - Response Path: "response"

3. Select the "Obelisk RAG" model in the chat interface

Now your chat interface will provide responses based on your documentation!

## Advanced Features

### Vector Database Management

You can view statistics about the vector database:

```bash
# View database stats
obelisk-rag stats

# View stats in JSON format
obelisk-rag stats --json
```

### Document Watching

The RAG system can watch for changes to your documentation and update the index in real-time:

```bash
# Start the API server with document watching
obelisk-rag serve --watch
```

This is useful during development when you're actively updating your documentation.

## Debugging

If you encounter issues, you can enable debug mode:

```bash
# Enable debug mode
export RAG_DEBUG=1
obelisk-rag query "Why isn't this working?"
```

## Architecture

The Obelisk RAG system consists of several components:

1. **Document Processor**: Handles parsing and chunking of markdown files
2. **Embedding Service**: Generates vector embeddings using Ollama
3. **Vector Storage**: Stores and retrieves embeddings using ChromaDB
4. **RAG Service**: Integrates all components for document retrieval and generation
5. **CLI Interface**: Provides command-line access to the system

For more details on the architecture, see [Architecture Draft](architecture-draft.md) and [Implementation](implementation.md).

## Next Steps

Now that you have the RAG system set up, you might want to:

1. [Customize the prompt template](query-pipeline.md#customizing-prompts)
2. [Integrate with other vector databases](vector-database.md#alternative-databases)
3. [Evaluate and improve retrieval quality](evaluation.md)
4. [Explore advanced Ollama models](ollama-integration.md#advanced-models)
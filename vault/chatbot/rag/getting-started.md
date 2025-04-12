---
title: Getting Started with RAG
date: 2025-04-11
---

# Getting Started with Obelisk RAG

This guide will help you get started with the Retrieval Augmented Generation (RAG) system in Obelisk. We'll walk through the process of setting up your environment, initializing the system, and making your first query.

## Prerequisites

Before you start, ensure you have:

1. **Obelisk installed**: The RAG system is part of Obelisk
2. **Ollama running**: The system requires Ollama for LLMs and embeddings
3. **Documentation in your vault**: Some markdown files to index

## Step 1: Start Ollama

The RAG system requires Ollama for generating embeddings and providing LLM capabilities. You can run Ollama using Docker:

```bash
docker-compose up ollama -d
```

Wait for Ollama to start up (this might take a minute).

## Step 2: Pull Required Models

The RAG system needs models for embedding generation and text generation. You can pull them using:

```bash
# Pull the LLM model (llama3 is recommended)
docker exec -it ollama ollama pull llama3

# Pull the embedding model
docker exec -it ollama ollama pull mxbai-embed-large
```

This step will download the required models. The embedding model is optimized for generating high-quality embeddings for document retrieval.

## Step 3: Configure the RAG System

The default configuration should work for most users, but you can customize it if needed:

```bash
# View current configuration
obelisk-rag config --show

# Set a different vault directory if needed
obelisk-rag config --set "vault_dir=/path/to/your/docs"

# Set different Ollama URL if needed
obelisk-rag config --set "ollama_url=http://ollama:11434"
```

## Step 4: Index Your Documentation

Before you can query your documentation, you need to index it:

```bash
obelisk-rag index
```

This process will:
1. Read all markdown files in your vault
2. Extract the content and metadata
3. Split the content into chunks
4. Generate embeddings for each chunk
5. Store everything in a vector database

You should see a progress report in the console as files are processed.

## Step 5: Make Your First Query

Now you can query your documentation:

```bash
obelisk-rag query "What is Obelisk?"
```

The system will:
1. Convert your query to an embedding
2. Find the most relevant document chunks
3. Use those chunks as context for the LLM
4. Generate a response based on your documentation

You should see a response that's specifically informed by your documentation.

## Step 6: Start the API Server (Optional)

If you want to integrate with other applications or want the real-time document watching feature, you can start the API server:

```bash
obelisk-rag serve --watch
```

This will:
1. Start a REST API server (default: http://0.0.0.0:8000)
2. Provide endpoints for querying and stats
3. Watch for changes to documentation files and update the index automatically

## Troubleshooting

### Common Issues

1. **Connection errors with Ollama**:
   
   ```
   Error: Failed to connect to Ollama service at http://localhost:11434
   ```
   
   Ensure Ollama is running and accessible at the configured URL. You may need to adjust the URL with:
   
   ```bash
   obelisk-rag config --set "ollama_url=http://ollama:11434"
   ```

2. **No results when querying**:
   
   ```
   No documents found for query: What is Obelisk?
   ```
   
   Check that your documentation has been indexed successfully. Run `obelisk-rag stats` to see how many documents are in the database.

3. **Model not found errors**:
   
   ```
   Error: Model 'llama3' not found
   ```
   
   Ensure you have pulled the required models using Ollama.

### Enabling Debug Mode

If you're encountering issues, you can enable debug mode for more detailed logs:

```bash
export RAG_DEBUG=1
obelisk-rag query "What is Obelisk?"
```

## Next Steps

Now that you have the RAG system up and running, you can:

1. Learn about [advanced configuration options](using-rag.md)
2. Integrate with [Open WebUI](../openwebui.md) for a chat interface
3. Explore the [RAG architecture](architecture-draft.md) in depth
4. Read about the [implementation details](implementation.md) if you want to customize the system
5. Review [evaluation techniques](evaluation.md) to measure and improve performance

---

For more detailed usage information, see [Using the RAG System](using-rag.md).
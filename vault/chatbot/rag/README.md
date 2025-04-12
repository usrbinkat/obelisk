# Obelisk RAG Documentation

This directory contains documentation for the Retrieval Augmented Generation (RAG) system in Obelisk. 

## Available Guides

- [Overview](index.md) - Introduction to the RAG system and its architecture
- [Getting Started](getting-started.md) - Step-by-step guide to setting up the RAG system
- [Using the RAG System](using-rag.md) - Detailed usage instructions and configuration options
- [Architecture](architecture-draft.md) - Detailed architecture design document
- [Implementation](implementation.md) - Implementation details and considerations
- [Evaluation](evaluation.md) - Methods for evaluating RAG performance
- [Ollama Integration](ollama-integration.md) - Details on integrating with Ollama
- [Vector Database](vector-database.md) - Information about the vector database
- [Query Pipeline](query-pipeline.md) - Details on the query processing pipeline

## Quick Start

```bash
# Index your documentation
obelisk-rag index

# Query your documentation
obelisk-rag query "What is Obelisk?"

# Start the API server with document watching
obelisk-rag serve --watch
```

For detailed setup instructions, see [Getting Started](getting-started.md).

## Key Features

- Document processing and chunking
- Vector embeddings using Ollama
- Vector storage using ChromaDB
- Retrieval augmented generation
- Real-time document watching
- REST API for integration
- Command-line interface

## Architecture Overview

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  Markdown     │       │               │       │               │
│  Documents    │──────▶│  Document     │──────▶│  Vector       │
│  (vault/)     │       │  Processor    │       │  Database     │
└───────────────┘       └───────────────┘       └───────────────┘
                                                        │
                                                        ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│               │       │               │       │               │
│  User         │──────▶│  Query        │◀──────│  Retrieval    │
│  Interface    │       │  Processor    │       │  Engine       │
└───────────────┘       └───────────────┘       └───────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │               │
                        │  Ollama LLM   │
                        │               │
                        └───────────────┘
```

The RAG system has been fully implemented with the following components:
- Document processor for parsing and chunking markdown files
- Embedding service using Ollama models
- Vector storage using ChromaDB
- RAG service for document retrieval and generation
- CLI interface for user interaction
- REST API for integration with other services

For more details, see the [Architecture](architecture-draft.md) document.
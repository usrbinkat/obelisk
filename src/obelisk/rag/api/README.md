# Obelisk RAG API

This directory contains the API interfaces for the Obelisk RAG system.

## Components

### OpenAI-Compatible API

Located in `openai.py`, this module provides an OpenAI-compatible API endpoint:

- `/v1/chat/completions`: Processes chat completion requests
  - Compatible with the OpenAI Chat API format
  - Automatically performs RAG to enhance responses
  - Returns both the AI response and source documents

This API allows tools and interfaces that work with the OpenAI API to seamlessly integrate with Obelisk.

### Ollama API Proxy

Located in `ollama.py`, this module provides a proxy to the Ollama API with RAG enhancements:

- `/api/{path}`: Proxies requests to the Ollama API
  - Enhances chat and generation requests with relevant context
  - Passes through other requests unchanged
  - Maintains the Ollama API format for compatibility

- `/ollama/api/{path}`: Alternative proxy path used by some clients like OpenWebUI

The proxy enhances Ollama's capabilities by intercepting chat and generation requests, adding relevant context from the documents, and then forwarding the enhanced request to Ollama.

## Usage

These APIs are automatically set up when running the RAG service with:

```bash
obelisk rag serve
```

They can be accessed at:

- OpenAI-compatible API: `http://localhost:8001/v1/chat/completions`
- Ollama API proxy: `http://localhost:8001/api/*`

## Integration

The APIs are designed to work with various clients:

- **OpenAI clients**: Connect directly to the `/v1/chat/completions` endpoint
- **Ollama clients**: Connect to the proxy endpoints for enhanced responses
- **OpenWebUI**: Works with both the OpenAI-compatible API and the Ollama proxy
# Obelisk RAG - Retrieval Augmented Generation

This document provides instructions for using the Obelisk RAG (Retrieval Augmented Generation) system with Docker. The RAG system allows you to query your documentation using natural language and get context-aware responses using a local large language model (LLM).

## Requirements

- Docker and Docker Compose
- At least 8GB of RAM (16GB+ recommended)
- NVIDIA GPU (optional but recommended for better performance)

## Quick Start

1. Start the services:

```bash
docker-compose up -d
```

2. Wait for the services to initialize. This may take a few minutes the first time as Ollama downloads the required models.

3. The RAG API will be available at http://localhost:8001.

## Adding Documents

There are several ways to add markdown documents to the RAG system:

### Option 1: Copy files directly to the volume

```bash
# Create a sample document
mkdir -p sample-docs
echo "# Sample Document\n\nThis is a test document." > sample-docs/sample.md

# Copy files to the Docker volume
docker cp sample-docs/. obelisk-rag:/app/vault/
```

### Option 2: Mount a local directory

Edit the `docker-compose.yaml` file and replace:

```yaml
volumes:
  - rag-vault:/app/vault
```

with:

```yaml
volumes:
  - ./your-local-docs:/app/vault:ro  # Read-only mount of your local docs
```

Then restart the service:

```bash
docker-compose restart obelisk-rag
```

## Querying Your Documents

You can query your documents using the API:

```bash
# Simple query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Obelisk?"}'
```

## Viewing Statistics

```bash
# Get statistics about the RAG system
curl http://localhost:8001/stats
```

## Advanced Configuration

You can configure the RAG system by modifying the environment variables in the `docker-compose.yaml` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `VAULT_DIR` | Directory containing markdown files | `/app/vault` |
| `CHROMA_DIR` | Directory for vector database | `/app/data/chroma_db` |
| `OLLAMA_URL` | URL of the Ollama service | `http://ollama:11434` |
| `OLLAMA_MODEL` | Ollama model for generation | `llama3` |
| `EMBEDDING_MODEL` | Model for embeddings | `mxbai-embed-large` |
| `RETRIEVE_TOP_K` | Number of document chunks to retrieve | `3` |
| `API_HOST` | Host to bind API server | `0.0.0.0` |
| `API_PORT` | Port for API server | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Using with GPU Acceleration

The docker-compose.yaml file already includes GPU configuration for Ollama. If you don't have a GPU or NVIDIA Container Toolkit installed, you'll need to modify the Ollama service configuration by commenting out or removing the GPU-related sections:

```yaml
ollama:
  # Remove or comment out these lines if you don't have GPU support
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
    - NVIDIA_DRIVER_CAPABILITIES=compute,utility
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            capabilities: [gpu]
            count: all
```

If you need to install NVIDIA Container Toolkit, see [NVIDIA Container Toolkit documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for installation instructions.

## Available Models

You can use different models with the Obelisk RAG system. Some recommended models:

- `llama3`: Good general-purpose model (8B parameters)
- `phi-3-mini`: Lightweight model with good performance (3.8B parameters)
- `mixtral`: Larger model with strong reasoning capabilities (8x7B parameters)
- `mistral`: Good for technical content (7B parameters)

To download a model:

```bash
# Pull the model using Ollama
docker exec -it ollama ollama pull llama3
```

Then update the `OLLAMA_MODEL` environment variable in the `docker-compose.yaml` file.

## Troubleshooting

- **Ollama connection errors**: Make sure the Ollama service is running and the `OLLAMA_URL` is set correctly.
- **Model not found errors**: Pull the model using Ollama with `docker exec -it ollama ollama pull <model-name>`.
- **Memory issues**: Reduce the number of concurrent requests or use a smaller model.
- **Empty responses**: Make sure your documents have been properly indexed. Check the logs for errors.
- **MkDocs Git Plugin Issues**: If MkDocs fails to start with Git-related errors, ensure the container has:
  1. Git installed via apt-get
  2. The following environment variables set:
     ```
     ENV GIT_PYTHON_REFRESH=quiet
     ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git
     ```
- **Chromium/Puppeteer Testing Issues**: For UI testing with Puppeteer, ensure the devcontainer has all required dependencies:
  ```
  chromium-browser
  libgtk-4-1
  libvulkan1
  libgraphene-1.0-0
  libxslt1.1
  libvpx9
  libevent-2.1-7
  libopus0
  libwebpmux3
  libxkbcommon-x11-0
  libgles2
  gstreamer1.0-plugins-base
  gstreamer1.0-plugins-good
  gstreamer1.0-plugins-bad
  libgstreamer1.0-0
  gstreamer1.0-libav
  ```

## Container Structure

The Docker environment consists of several integrated services:

- **ollama**: Hosts the language models for embedding and generation
- **open-webui**: Web interface for interacting with Ollama models directly
- **obelisk**: Documentation site built with MkDocs
- **obelisk-rag**: RAG service that connects to Ollama and provides document search capabilities

## Integrating with Open WebUI

Open WebUI is configured to use the RAG service through environment variables in the docker-compose.yaml file:

```yaml
environment:
  # RAG configuration
  - RAG_ENABLED=true
  - RAG_SERVICE_TYPE=custom
  - RAG_SERVICE_URL=http://obelisk-rag:8000
  - RAG_TEMPLATE=You are a helpful assistant. Use the following pieces of retrieved context to answer the user's question. If you don't know the answer, just say that you don't know.

    Context:
    {{context}}

    User question: {{query}}
```

This allows users to access the RAG capabilities directly through the Open WebUI interface at http://localhost:8080. When asking questions, the WebUI will automatically retrieve relevant context from the indexed documentation and include it in the prompt to the language model.
FROM python:3.12-slim

WORKDIR /app

# Install curl, debugging tools, and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    procps \
    net-tools \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy Poetry configuration and lock files
COPY pyproject.toml poetry.lock /app/

# Install poetry
RUN pip install --no-cache-dir poetry

# Configure poetry to not create virtualenv
RUN poetry config virtualenvs.create false

# Install dependencies from lock file
RUN poetry install --no-interaction --no-ansi --no-root --with=rag

# Copy the RAG implementation files
COPY src/ /app/src/

# Create data directory
RUN mkdir -p /app/data
RUN mkdir -p /app/vault

# Expose RAG API port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH="/app"
ENV VAULT_DIR="/app/vault"
ENV OLLAMA_URL="http://ollama:11434"
ENV OLLAMA_MODEL="llama3"
ENV EMBEDDING_MODEL="text-embedding-3-large"
ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"
ENV LOG_LEVEL="DEBUG"
ENV WATCH_DOCS="true"
ENV PYTHONUNBUFFERED="1"

# Add a health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/stats || exit 1

# Run the RAG service (will use --watch flag if WATCH_DOCS is true)
COPY ./deployments/docker/images/rag/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
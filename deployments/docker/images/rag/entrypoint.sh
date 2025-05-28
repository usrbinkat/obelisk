#!/bin/bash
set -e

echo "Starting Obelisk RAG service..."

# Load tokens from volume if available
if [ -f "/app/tokens/api_tokens.env" ]; then
    echo "Loading API tokens from /app/tokens/api_tokens.env"
    # Use set -a to export all variables automatically
    set -a
    source /app/tokens/api_tokens.env
    set +a
    # Export the LiteLLM API token
    export LITELLM_API_KEY="${LITELLM_API_TOKEN}"
    echo "Loaded LITELLM_API_KEY: ${LITELLM_API_KEY:0:10}..."
else
    echo "Warning: No tokens file found at /app/tokens/api_tokens.env"
fi

# Basic networking info
echo "Container hostname: $(hostname)"
echo "Container IP: $(hostname -i || echo 'Not available')"

# Print environment variables (excluding sensitive ones)
echo "Environment variables:"
env | grep -v '_KEY\|PASSWORD\|SECRET\|TOKEN\|CREDENTIAL' | sort

# Check if vault directory exists in the volume
if [ "$(ls -A /app/vault)" ]; then
    echo "Vault directory contains $(find /app/vault -type f -name "*.md" | wc -l) Markdown files"
    echo "Documents from the vault will be processed and indexed"
else
    echo "Warning: Vault directory is empty. No documents will be indexed."
    echo "You can copy documents to the container with:"
    echo "  docker cp ./path/to/docs/. obelisk-rag:/app/vault/"
fi

# Use absolute paths and configure Python environment
cd /app
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
export LOG_LEVEL=DEBUG

echo "Starting server directly with foreground execution"
echo "Command: python -m src.obelisk.cli.commands rag serve --host 0.0.0.0 --port 8000"

# Execute directly in foreground with explicit host and port
exec python -m src.obelisk.cli.commands rag serve --host 0.0.0.0 --port 8000
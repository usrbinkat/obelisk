#!/bin/bash
set -e

echo "Starting Obelisk RAG service..."

# Check if vault directory exists in the volume
if [ "$(ls -A /app/vault)" ]; then
    echo "Vault directory contains $(find /app/vault -type f -name "*.md" | wc -l) Markdown files"
    echo "Documents from the vault will be processed and indexed"
else
    echo "Warning: Vault directory is empty. No documents will be indexed."
    echo "You can copy documents to the container with:"
    echo "  docker cp ./path/to/docs/. obelisk-rag:/app/vault/"
fi

# Start the server with or without watch flag based on environment variable
if [ "$WATCH_DOCS" = "true" ]; then
    echo "Starting server with document watching enabled"
    exec python -m obelisk.rag.cli serve --watch
else
    echo "Starting server without document watching"
    exec python -m obelisk.rag.cli serve
fi
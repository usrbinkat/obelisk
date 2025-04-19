#!/bin/bash
set -e

# Make sure obelisk-rag container is running
if ! docker ps | grep -q obelisk-rag; then
    echo "Error: obelisk-rag container is not running"
    echo "Start it with: docker-compose up -d obelisk-rag"
    exit 1
fi

# Copy all docs from ./vault to the container
echo "Copying documentation from ./vault to obelisk-rag container..."
docker cp ./vault/. obelisk-rag:/app/vault/

# Count the markdown files copied
DOC_COUNT=$(find ./vault -name "*.md" | wc -l)
echo "Copied $DOC_COUNT markdown files to the RAG system"
echo "The documents will be automatically indexed by the RAG service"
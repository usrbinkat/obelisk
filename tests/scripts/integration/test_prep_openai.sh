#!/bin/bash

# Script to prepare environment for OpenAI integration testing
# This script handles the long-running commands that would timeout in AI assistants

set -e

echo "=== Starting test preparation steps ==="

# Build containers
echo "Building containers..."
docker-compose build

# Pull necessary images
echo "Pulling container images..."
docker-compose pull

# Start Ollama for model downloading
echo "Starting Ollama service..."
docker-compose up -d ollama

# Pull required models
echo "Pulling Llama3 model (this may take several minutes)..."
docker-compose exec ollama ollama pull llama3

echo "Pulling embedding model (this may take several minutes)..."
docker-compose exec ollama ollama pull mxbai-embed-large

echo "=== Test preparation completed successfully ==="

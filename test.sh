#!/bin/bash
# One-shot test script to rebuild the entire Obelisk Docker stack from scratch
set -e

echo "=== Obelisk Docker Stack Rebuild Test ==="
echo "Starting at: $(date)"

# Step 1: Clean up everything (containers, volumes, images)
echo "Step 1: Cleaning up all containers, volumes, and images..."
task clean-all-purge || { echo "Clean failed"; exit 1; }

# Step 2: Pull required base images
echo "Step 2: Pulling required base images..."
docker compose -f deployments/docker/compose/dev.yaml pull || { echo "Pull failed"; exit 1; }

# Step 3: Build all custom images
echo "Step 3: Building all custom images..."
docker compose -f deployments/docker/compose/dev.yaml build || { echo "Build failed"; exit 1; }

# Step 4: Start the entire stack (detached mode)
echo "Step 4: Starting the entire stack..."
docker compose -f deployments/docker/compose/dev.yaml up -d || { echo "Startup failed"; exit 1; }

# Step 5: Verify services are running
echo "Step 5: Verifying services are running..."
sleep 15 # Give some time for services to start
docker compose -f deployments/docker/compose/dev.yaml ps

# Step 6: Run the init-service to verify initialization
echo "Step 6: Running initialization service..."
docker compose -f deployments/docker/compose/dev.yaml stop init-service
docker compose -f deployments/docker/compose/dev.yaml start init-service

# Step 7: Wait for initialization to complete
echo "Step 7: Waiting for initialization to complete..."
echo "Tailing initialization logs (will wait up to 3 minutes)..."
timeout 180 docker compose -f deployments/docker/compose/dev.yaml logs -f init-service || true

# Step 8: Verify obelisk-rag service is ready
echo "Step 8: Verifying obelisk-rag service is ready..."
docker compose -f deployments/docker/compose/dev.yaml restart obelisk-rag
sleep 10
docker compose -f deployments/docker/compose/dev.yaml logs obelisk-rag --tail=20

# Step 9: Copy documentation files to the RAG service
echo "Step 9: Copying documentation files to the RAG service..."
docker cp vault/chatbot/. obelisk-rag:/app/vault/
docker cp vault/index.md obelisk-rag:/app/vault/
docker compose -f deployments/docker/compose/dev.yaml logs obelisk-rag --tail=10

echo "=== Stack rebuild and initialization completed ==="
echo "Test completed at: $(date)"
echo "Use 'docker compose -f deployments/docker/compose/dev.yaml ps' to see running services"
echo "Access services at:"
echo "  - Documentation: http://localhost:8000"
echo "  - RAG API: http://localhost:8001"
echo "  - Chat UI: http://localhost:8080"
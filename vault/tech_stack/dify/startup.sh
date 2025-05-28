#!/bin/bash
# Dify Quick Start Script
# Automates the deployment of Dify with existing services

set -e

echo "======================================"
echo "Dify Quick Start Deployment"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create necessary directories
echo -e "\n${YELLOW}Step 1: Creating directories...${NC}"
mkdir -p nginx
mkdir -p backups

# Step 2: Check if nginx configs exist
echo -e "\n${YELLOW}Step 2: Checking nginx configuration...${NC}"
if [ ! -f nginx/nginx.conf ] || [ ! -f nginx/proxy.conf ]; then
    echo "Nginx configuration files not found!"
    echo "Please create nginx/nginx.conf and nginx/proxy.conf from the provided templates."
    exit 1
fi
echo -e "${GREEN}✓ Nginx configs found${NC}"

# Step 3: Generate SECRET_KEY if not exists in .env
echo -e "\n${YELLOW}Step 3: Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    # You would copy the template here
    echo "Please create .env file from the provided template."
    exit 1
fi

# Check if SECRET_KEY is set
if ! grep -q "^SECRET_KEY=.+" .env; then
    echo "Generating SECRET_KEY..."
    SECRET_KEY=$(openssl rand -base64 42)
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    echo -e "${GREEN}✓ SECRET_KEY generated${NC}"
fi

# Step 4: Stop conflicting services
echo -e "\n${YELLOW}Step 4: Stopping Open-WebUI (if running)...${NC}"
docker-compose stop open-webui 2>/dev/null || true

# Step 5: Pull Dify images
echo -e "\n${YELLOW}Step 5: Pulling Dify images...${NC}"
docker-compose pull dify_api dify_worker dify_web dify_nginx dify_db dify_redis dify_sandbox dify_ssrf_proxy

# Step 6: Start Dify infrastructure
echo -e "\n${YELLOW}Step 6: Starting Dify infrastructure...${NC}"
echo "Starting databases..."
docker-compose up -d dify_db dify_redis

# Wait for databases to be ready
echo "Waiting for databases to initialize..."
sleep 10

# Check database health
until docker exec dify-db pg_isready > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL ready${NC}"

until docker exec dify-redis redis-cli -a "${DIFY_REDIS_PASSWORD:-difyai123456}" ping > /dev/null 2>&1; do
    echo "Waiting for Redis..."
    sleep 2
done
echo -e "${GREEN}✓ Redis ready${NC}"

# Step 7: Start remaining Dify services
echo -e "\n${YELLOW}Step 7: Starting Dify services...${NC}"
docker-compose up -d dify_sandbox dify_ssrf_proxy
docker-compose up -d dify_api dify_worker
docker-compose up -d dify_web dify_nginx

# Step 8: Wait for services to be ready
echo -e "\n${YELLOW}Step 8: Waiting for services to be ready...${NC}"
sleep 10

# Check if Dify API is responding
echo "Checking Dify API..."
attempts=0
max_attempts=30
until curl -s http://localhost:8080/console/api/health > /dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [ $attempts -eq $max_attempts ]; then
        echo "Dify API failed to start. Check logs with: docker logs dify-api"
        exit 1
    fi
    echo "Waiting for Dify API... (attempt $attempts/$max_attempts)"
    sleep 5
done
echo -e "${GREEN}✓ Dify API ready${NC}"

# Step 9: Display next steps
echo -e "\n${GREEN}======================================"
echo "Dify Deployment Complete!"
echo "======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Navigate to http://localhost:8080/install"
echo "2. Set up your admin account"
echo "3. Configure model providers:"
echo "   - Go to Settings → Model Providers → OpenAI-API-compatible"
echo "   - Base URL: http://litellm:4000"
echo "   - API Key: sk-c8b0734639e032001a5626a8"
echo ""
echo "To check service health, run:"
echo "  ./health-check.sh"
echo ""
echo "To view logs:"
echo "  docker logs dify-api"
echo "  docker logs dify-worker"
echo ""
echo "For troubleshooting, see the migration guide."

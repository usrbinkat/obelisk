#!/bin/bash
# Dify Health Check Script
# Verifies all services are running correctly

echo "======================================"
echo "Dify Integration Health Check"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local check_command=$2
    
    echo -n "Checking $service_name... "
    
    if eval $check_command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Function to check container status
check_container() {
    local container_name=$1
    
    echo -n "Checking container $container_name... "
    
    if docker ps | grep -q $container_name; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not Running${NC}"
        return 1
    fi
}

echo ""
echo "1. Checking Docker Containers"
echo "------------------------------"
check_container "milvus-standalone"
check_container "milvus-etcd"
check_container "milvus-minio"
check_container "litellm"
check_container "dify-api"
check_container "dify-worker"
check_container "dify-web"
check_container "dify-nginx"
check_container "dify-db"
check_container "dify-redis"
check_container "dify-sandbox"
check_container "tika"

echo ""
echo "2. Checking Service Health"
echo "------------------------------"
check_service "Milvus" "curl -s http://localhost:19530/v1/vector/collections/list"
check_service "LiteLLM" "curl -s http://localhost:4000/health"
check_service "Dify API" "curl -s http://localhost:8080/console/api/health"
check_service "Dify Web" "curl -s http://localhost:8080/"
check_service "Tika" "curl -s http://localhost:9998/tika"

echo ""
echo "3. Checking Service Connectivity"
echo "------------------------------"

# Check if Dify can connect to Milvus
echo -n "Dify → Milvus connection... "
if docker exec dify-api curl -s http://milvus:19530 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check if Dify can connect to LiteLLM
echo -n "Dify → LiteLLM connection... "
if docker exec dify-api curl -s http://litellm:4000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check if Dify can connect to Tika
echo -n "Dify → Tika connection... "
if docker exec dify-api curl -s http://tika:9998/tika > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo "4. Checking Database Connectivity"
echo "------------------------------"

# Check PostgreSQL
echo -n "Dify PostgreSQL... "
if docker exec dify-db pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check Redis
echo -n "Dify Redis... "
if docker exec dify-redis redis-cli -a "${DIFY_REDIS_PASSWORD:-difyai123456}" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo "5. Checking Configuration"
echo "------------------------------"

# Check if .env file exists
echo -n "Environment file (.env)... "
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Not found (using defaults)${NC}"
fi

# Check if nginx config exists
echo -n "Nginx configuration... "
if [ -f nginx/nginx.conf ] && [ -f nginx/proxy.conf ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Missing${NC}"
fi

echo ""
echo "6. Recent Logs Check"
echo "------------------------------"

# Check for errors in Dify API logs
echo -n "Dify API errors (last 50 lines)... "
error_count=$(docker logs dify-api 2>&1 | tail -50 | grep -i error | wc -l)
if [ $error_count -eq 0 ]; then
    echo -e "${GREEN}✓ No errors${NC}"
else
    echo -e "${YELLOW}⚠ Found $error_count error(s)${NC}"
fi

# Check for errors in Milvus logs
echo -n "Milvus errors (last 50 lines)... "
error_count=$(docker logs milvus-standalone 2>&1 | tail -50 | grep -i error | wc -l)
if [ $error_count -eq 0 ]; then
    echo -e "${GREEN}✓ No errors${NC}"
else
    echo -e "${YELLOW}⚠ Found $error_count error(s)${NC}"
fi

echo ""
echo "======================================"
echo "Health Check Complete"
echo "======================================"

# Summary
echo ""
echo "To view detailed logs for any service:"
echo "  docker logs <container-name>"
echo ""
echo "To restart a service:"
echo "  docker-compose restart <service-name>"
echo ""
echo "For more help, see the migration guide."

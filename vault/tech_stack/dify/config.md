# Key Configuration Notes for Dify Integration

## Critical Configuration Differences

### 1. Milvus Connection
**Important**: Unlike Open-WebUI, Dify services must use Docker service names, not localhost:
```yaml
# Correct for Dify:
MILVUS_URI=http://milvus:19530

# NOT this:
MILVUS_URI=http://localhost:19530  # Will fail!
```

### 2. LiteLLM Integration
Dify connects to LiteLLM through the OpenAI-compatible API interface:
- Configure in Dify UI, not just environment variables
- Base URL: `http://litellm:4000` (use Docker service name)
- API Key: `sk-c8bxxxxxxxxxxxxx`
- Models appear as OpenAI-compatible models in Dify

### 3. Network Architecture
Dify uses two networks for security:
- `ollama-net`: General service communication
- `ssrf_proxy_network`: Isolated network for SSRF protection

All services that need to communicate must be on the same network.

### 4. Storage Volumes
Dify separates storage concerns:
```
dify_storage: Application file storage
dify_postgres_data: Database persistence  
dify_redis_data: Cache persistence
```

Your existing Milvus volumes remain unchanged.

### 5. Authentication Flow
Unlike Open-WebUI's simple token system:
- Dify requires initial admin setup at `/install`
- Supports multiple authentication methods (local, OAuth, SSO)
- API keys are generated per application, not globally

## Service Dependencies

### Startup Order Matters:
1. Infrastructure: `etcd` → `minio` → `milvus`
2. Dify Infrastructure: `dify_db` → `dify_redis`
3. Dify Services: `dify_sandbox` → `dify_api` → `dify_worker` → `dify_web`
4. Frontend: `dify_nginx`

### Health Checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Dify API: `http://localhost:8080/console/api/health`
- Milvus: `http://localhost:19530/v1/vector/collections/list`

## Environment Variable Hierarchy

Dify loads configuration in this order:
1. Default values (hardcoded)
2. `.env` file
3. Environment variables in docker-compose
4. Database-stored settings (via UI)

**Note**: Some settings can only be changed via UI after initial setup.

## API Compatibility

### OpenAI-Compatible Endpoints:
- Chat Completions: `/v1/chat/completions`
- Embeddings: `/v1/embeddings`
- Models List: `/v1/models`

### Dify-Specific APIs:
- Apps: `/console/api/apps`
- Datasets: `/console/api/datasets`
- Workflows: `/console/api/workflows`

## Performance Tuning

### For Production:
```yaml
# Increase workers
dify_worker:
  deploy:
    replicas: 3

# Increase API threads
dify_api:
  environment:
    GUNICORN_WORKERS: 4
    SERVER_WORKER_AMOUNT: 8
```

### Milvus Optimization:
- Collection shards: Based on data volume
- Index type: IVF_FLAT or HNSW for better performance
- Consistency level: Adjust based on requirements

## Common Pitfalls to Avoid

1. **Don't use localhost/127.0.0.1 in service configurations**
   - Always use Docker service names

2. **Don't skip the /install step**
   - Required for initial database setup

3. **Don't mix authentication tokens**
   - LiteLLM tokens ≠ Dify API keys

4. **Don't ignore SSRF proxy**
   - Required for secure external API calls

5. **Don't modify volumes while services are running**
   - Stop services before volume operations

## Monitoring and Debugging

### Key Log Files to Watch:
```bash
# API errors
docker logs dify-api -f

# Background job issues  
docker logs dify-worker -f

# Vector indexing problems
docker logs milvus-standalone -f

# Model routing issues
docker logs litellm -f
```

### Performance Metrics:
- Dify API: Response times at `/console/api/health`
- Milvus: Collection statistics via API
- Redis: Memory usage via `INFO memory`

## Security Considerations

1. **Change all default passwords**:
   - `DIFY_POSTGRES_PASSWORD`
   - `DIFY_REDIS_PASSWORD`
   - `SANDBOX_API_KEY`
   - `SECRET_KEY` (must be unique)

2. **Network isolation**:
   - SSRF proxy prevents internal network scanning
   - Sandbox isolates code execution

3. **API security**:
   - Always use API keys for production
   - Enable rate limiting
   - Configure CORS appropriately

## Backup Strategy

### Daily Backups Should Include:
```bash
# Milvus data
docker exec milvus-standalone tar -czf /tmp/milvus-backup.tar.gz /var/lib/milvus

# Dify database
docker exec dify-db pg_dump -U postgres dify > dify-backup.sql

# Application storage
tar -czf dify-storage-backup.tar.gz ./volumes/dify_storage
```

## Migration Validation

### Verify successful migration:
1. ✓ All containers running
2. ✓ Dify UI accessible at http://localhost:8080
3. ✓ Can create and query knowledge bases
4. ✓ LiteLLM models appear in Dify
5. ✓ Documents index in Milvus
6. ✓ RAG queries return results

## Getting Help

- Dify Logs: Primary debugging source
- Health Check Script: Quick diagnostics
- Dify Docs: https://docs.dify.ai
- Community: GitHub Issues

Remember: Dify is more complex than Open-WebUI but offers significantly more enterprise features. The initial setup investment pays off in capabilities.

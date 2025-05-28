# Migration Guide: Open-WebUI to Dify

## Overview
This guide walks through migrating from Open-WebUI to Dify while maintaining all existing integrations with Milvus, LiteLLM, and other services.

## Pre-Migration Checklist

1. **Backup existing data**:
   ```bash
   # Backup Milvus data
   docker exec milvus-standalone /bin/bash -c "cd /var/lib/milvus && tar -czf /tmp/milvus-backup.tar.gz ."
   docker cp milvus-standalone:/tmp/milvus-backup.tar.gz ./backups/
   
   # Backup existing volumes
   cp -r ./volumes ./volumes-backup-$(date +%Y%m%d)
   ```

2. **Stop Open-WebUI service**:
   ```bash
   docker-compose stop open-webui
   ```

## Migration Steps

### Step 1: Create Nginx Configuration
```bash
mkdir -p nginx
```

Create `nginx/nginx.conf` and `nginx/proxy.conf` files with the provided configurations.

### Step 2: Update Environment Variables
1. Copy the provided `.env` template
2. Update the following critical values:
   - `SECRET_KEY` - Generate new: `openssl rand -base64 42`
   - `DIFY_ADMIN_EMAIL` - Your admin email
   - `DIFY_ADMIN_PASSWORD` - Strong admin password
   - OpenAI API keys if using OpenAI

### Step 3: Deploy Dify
```bash
# Pull new images
docker-compose pull dify_api dify_worker dify_web dify_nginx

# Start Dify services
docker-compose up -d dify_db dify_redis dify_sandbox dify_ssrf_proxy
docker-compose up -d dify_api dify_worker dify_web dify_nginx
```

### Step 4: Initialize Dify
1. Navigate to http://localhost:8080/install
2. Set up your admin account
3. Configure initial workspace

### Step 5: Configure Model Providers

#### Configure LiteLLM Integration:
1. Go to Settings → Model Providers → OpenAI-API-compatible
2. Configure:
   - Model Name: `gpt-4o` (or your model)
   - Base URL: `http://litellm:4000`
   - API Key: `sk-c8b0734639e032001a5626a8`
   - Model Type: `Chat`
   - Max context length: `4096`

#### Configure Embedding Model:
1. Same provider (OpenAI-API-compatible)
2. Add embedding model:
   - Model Name: `text-embedding-3-large`
   - Model Type: `Text Embedding`

### Step 6: Verify Milvus Integration
1. Create a new Knowledge Base in Dify
2. Upload a test document
3. Verify it's indexed in Milvus:
   ```bash
   # Check Milvus collections
   curl http://localhost:19530/v1/vector/collections/list
   ```

### Step 7: Test RAG Functionality
1. Create a new App in Dify
2. Enable "Knowledge Base" context
3. Select your created knowledge base
4. Test queries against your documents

## Post-Migration Tasks

### Data Migration (if needed)
If you have existing documents in Open-WebUI:
1. Export documents from Open-WebUI
2. Re-import into Dify Knowledge Base
3. Verify indexing completion

### API Migration
Dify provides OpenAI-compatible APIs:
- Base URL: `http://localhost:8080/v1`
- Use Dify API keys from Settings → API Access

### User Migration
- Dify supports SSO, OAuth, and multi-user management
- Create user accounts via Settings → Members
- Configure authentication methods as needed

## Rollback Plan
If issues occur:
```bash
# Stop Dify services
docker-compose stop dify_api dify_worker dify_web dify_nginx

# Restart Open-WebUI
docker-compose start open-webui
```

## Troubleshooting

### Common Issues

1. **Milvus Connection Failed**
   - Check: `docker logs milvus-standalone`
   - Verify MILVUS_URI is set to `http://milvus:19530` (not localhost)

2. **LiteLLM Integration Issues**
   - Test LiteLLM directly: `curl http://localhost:4000/v1/models`
   - Verify API key matches configuration

3. **Document Processing Fails**
   - Check Tika service: `curl http://localhost:9998/tika`
   - Verify ETL_TYPE=tika in environment

4. **Authentication Issues**
   - Clear browser cookies
   - Check SECRET_KEY hasn't changed
   - Verify database connection

### Performance Optimization

1. **Increase Worker Processes**:
   ```yaml
   dify_worker:
     deploy:
       replicas: 3
   ```

2. **Tune Milvus for Production**:
   - Adjust index parameters
   - Configure appropriate shard/replica counts

3. **Enable Redis Persistence**:
   ```yaml
   command: redis-server --requirepass ${DIFY_REDIS_PASSWORD} --appendonly yes
   ```

## Feature Comparison

| Feature | Open-WebUI | Dify |
|---------|------------|------|
| Milvus Support | ✓ | ✓ Native |
| LiteLLM Integration | ✓ | ✓ Via OpenAI-compatible |
| Multi-tenancy | Limited | ✓ Full |
| SSO/OAuth | Limited | ✓ Enterprise |
| API Access | Basic | ✓ Comprehensive |
| Workflow Builder | ✗ | ✓ Visual |
| Agent Capabilities | Basic | ✓ Advanced |
| Monitoring | Basic | ✓ Built-in |

## Support Resources

- Dify Documentation: https://docs.dify.ai
- Dify GitHub: https://github.com/langgenius/dify
- Community Forum: https://community.dify.ai

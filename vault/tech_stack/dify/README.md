# Dify - Enterprise Chat UI for Obelisk

## What is Dify?

Dify is an open-source LLM application development platform that we're using as our enterprise chat UI. It replaces Open-WebUI with a more sophisticated system that includes visual workflow building, native vector database support, and enterprise features like multi-tenancy and RBAC.

## Accessing Dify

### First Time Setup
1. Navigate to http://localhost:8080/install
2. Create your admin account with email and password
3. Set your workspace name (e.g., "Obelisk RAG Platform")

### Regular Login
- URL: http://localhost:8080
- Use the email/password you created during setup
- After login, you'll see the main dashboard with Apps, Knowledge, and Tools sections

## Understanding Dify's Interface

### Main Navigation
- **Studio**: Where you create and manage AI applications
  - Apps: Chat interfaces, agents, and workflows
  - Knowledge: Document collections for RAG
  - Tools: Custom functions and integrations
  
- **Explore**: Pre-built application templates

- **Settings**: System configuration
  - Model Providers: Configure LLMs and embeddings
  - Members: User management
  - API Access: Generate API keys

## How Dify Works in Our Stack

### Service Architecture

Dify consists of multiple services working together:

```
User Browser
     │
     ▼
[nginx:8080] ─── Routes traffic to appropriate service
     │
     ├──→ [dify_web:3000] ─── React frontend (what you see)
     │
     └──→ [dify_api:5001] ─── Backend API
              │
              ├──→ [dify_worker] ─── Processes documents, embeddings
              ├──→ [dify_db] ─── Stores app configs, users
              ├──→ [dify_redis] ─── Caches data, job queue
              └──→ [dify_sandbox] ─── Executes code safely
```

### Network Communication

In our Docker Compose setup, services communicate using Docker's internal DNS:

- **Internal Communication**: Services use container names (e.g., `http://dify_api:5001`)
- **External Access**: Only through nginx on port 8080
- **Vector Database**: Dify talks to Milvus at `http://milvus:19530`
- **LLM Proxy**: Dify connects to LiteLLM at `http://litellm:4000`

Important: Never use `localhost` or `127.0.0.1` in configurations - always use service names!

## Setting Up Models

### Configure LiteLLM Connection

1. Go to Settings → Model Providers
2. Click "OpenAI-API-compatible"
3. Configure:
   - Model Name: `gpt-4o` (or any model in LiteLLM)
   - Model Type: `Chat`
   - Base URL: `http://litellm:4000`
   - API Key: `sk-c8b0734639e032001a5626a8`
   - Max Tokens: `4096`
   - Click "Save"

4. Add embedding model:
   - Model Name: `text-embedding-3-large`
   - Model Type: `Text Embedding`
   - Same Base URL and API Key
   - Click "Save"

### Available Models
Any model configured in LiteLLM is available, including:
- Local Ollama models (llama3, mxbai-embed-large)
- OpenAI models (if API key configured)
- Any other LiteLLM-supported provider

## Creating Your First RAG Application

### Step 1: Create a Knowledge Base
1. Navigate to Studio → Knowledge
2. Click "Create Knowledge"
3. Name it (e.g., "Technical Documentation")
4. Settings to note:
   - Embedding Model: Select `text-embedding-3-large`
   - Vector Database: Automatically uses Milvus
   - Retrieval Setting: Default is Semantic Search

### Step 2: Upload Documents
1. Click into your Knowledge Base
2. Click "Add file" or drag documents
3. Supported formats: PDF, TXT, MD, DOCX, HTML, and more
4. Processing happens automatically via Tika
5. Watch the status - it will show "Indexing" then "Available"

### Step 3: Create a Chat Application
1. Go to Studio → Create App
2. Choose "Chat App"
3. Configure:
   - Name: "Obelisk Assistant"
   - Model: Select your configured model (e.g., `gpt-4o`)
   - Context: Enable and select your Knowledge Base
   - System Prompt: Customize for your use case

### Step 4: Test Your App
1. Click "Preview" to test in the interface
2. Ask questions about your uploaded documents
3. Adjust retrieval settings if needed:
   - Top K: Number of chunks to retrieve (default: 3)
   - Score Threshold: Minimum similarity score

## How Dify Stores Data

### Vector Storage (Milvus)
- Collections named: `Dify_<dataset_id>`
- Each document is chunked and embedded
- Chunks stored with metadata for retrieval

### Application Data (PostgreSQL)
- User accounts and permissions
- Application configurations
- Knowledge base metadata
- Conversation histories

### Cache and Queue (Redis)
- Session data
- Background job queue
- Embedding cache

### File Storage
- Local: `/app/api/storage` (mounted as `dify_storage` volume)
- Contains uploaded documents and generated files

## API Access

### Getting API Keys
1. Settings → API Access
2. Create new API key with descriptive name
3. Copy immediately (shown only once)

### Using the API
```bash
# Chat completion
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-app-id",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# List available apps
curl http://localhost:8080/v1/apps \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Monitoring and Debugging

### View Logs
```bash
# API server logs
docker logs -f dify-api

# Background job processing
docker logs -f dify-worker

# See what's happening with vector storage
docker logs -f milvus-standalone
```

### Common Issues and Solutions

**"Failed to connect to Milvus"**
- Check: Is Milvus running? `docker ps | grep milvus`
- Fix: Ensure MILVUS_URI uses `http://milvus:19530` not localhost

**"Model not found"**
- Check: Is LiteLLM configured correctly in UI?
- Fix: Verify Base URL is `http://litellm:4000` and API key matches

**"Document processing stuck"**
- Check: Worker logs `docker logs dify-worker`
- Fix: Restart worker `docker-compose restart dify_worker`

## Advanced Features

### Workflows
Beyond simple chat, Dify supports visual workflow building:
1. Create Workflow app type
2. Drag and drop nodes:
   - LLM nodes for processing
   - Knowledge Retrieval for RAG
   - Conditional logic
   - HTTP requests
   - Code execution

### Agents
Create autonomous agents that can:
- Use multiple tools
- Make decisions
- Access knowledge bases
- Execute multi-step tasks

### Team Collaboration
1. Settings → Members → Invite Member
2. Assign roles:
   - Admin: Full access
   - Editor: Create/modify apps
   - Viewer: Read-only access

## Backup and Maintenance

### What to Backup
```bash
# Dify application data
docker exec dify-db pg_dump -U postgres dify > dify-backup.sql

# Vector data (Milvus)
# Milvus data is in milvus_data volume

# Uploaded files
cp -r ./volumes/dify_storage ./backup/
```

### Updating Dify
```bash
# Pull latest images
docker-compose pull dify_api dify_worker dify_web

# Restart services
docker-compose up -d dify_api dify_worker dify_web
```

## Integration with Obelisk Components

### Using with Obelisk-RAG
Both Dify and obelisk-rag use the same Milvus instance but different collections:
- Dify: `Dify_*` collections
- Obelisk-RAG: Custom named collections

They can coexist without interference.

### Shared Services
- **Milvus**: Both systems store vectors here
- **LiteLLM**: Both route LLM calls through this proxy
- **Tika**: Shared document processing service

## Tips for Production Use

1. **Change Default Passwords**: Update all passwords in `.env`
2. **Configure HTTPS**: Add SSL certificates to nginx
3. **Set Resource Limits**: Define memory/CPU limits in docker-compose
4. **Enable Monitoring**: Export metrics to Prometheus
5. **Regular Backups**: Automate database and file backups

## Getting Help

- **Dify Issues**: Check container logs first
- **Integration Issues**: Verify service names and network connectivity
- **Performance Issues**: Monitor Milvus and PostgreSQL metrics
- **UI Issues**: Check browser console and dify_web logs

Remember: Dify is a complex system with many moving parts. When troubleshooting, follow the data flow: Web UI → API → Worker → Databases → Vector Store.

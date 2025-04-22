# Obelisk Hack Directory

This directory contains various test and utility scripts for the Obelisk project.

## test_init.py

This script validates that the container initialization process has completed successfully. It performs the following checks:

1. **Service Health Checks**: Verifies that Ollama, LiteLLM, and Obelisk-RAG services are running and responding
2. **Model Availability**: Confirms that required Ollama models (mxbai-embed-large, llama3) are downloaded
3. **Authentication**: Tests LiteLLM authentication with generated tokens
4. **Token Registration**: Automatically registers tokens with LiteLLM API if needed
5. **Generation Tests**: Verifies that LiteLLM can generate responses
6. **OpenWebUI Integration**: Tests the OpenWebUI API if available
7. **RAG Functionality**: Validates the end-to-end RAG pipeline

### Usage

```bash
# Run the validation script
python3 hack/test_init.py
```

The script will output detailed logs of its verification process and exit with code 0 if all checks pass or a non-zero code if issues are detected.

### Environment Variables

The script uses these environment variables (with defaults if not specified):

- `OLLAMA_API_URL`: URL for Ollama API (default: http://localhost:11434)
- `LITELLM_API_URL`: URL for LiteLLM API (default: http://localhost:4000)
- `MILVUS_HOST`: Hostname for Milvus (default: localhost)
- `MILVUS_PORT`: Port for Milvus (default: 19530)
- `OBELISK_RAG_API_URL`: URL for Obelisk RAG API (default: http://localhost:8001)
- `OPENWEBUI_API_URL`: URL for OpenWebUI API (default: http://localhost:8080)
- `OPENWEBUI_TOKEN`: OpenWebUI authentication token (if different from LiteLLM token)

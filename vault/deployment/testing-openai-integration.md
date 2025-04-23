---
title: Testing OpenAI Integration
date: 2025-04-22
---

# Testing OpenAI Integration in Obelisk

This guide provides a comprehensive testing methodology for validating the OpenAI integration feature in Obelisk. This feature allows the system to use OpenAI models when an API key is available, while gracefully falling back to local Ollama models when it's not.

> **⚠️ IMPORTANT NOTE FOR AI-ASSISTED TESTING ⚠️**  
> When using Claude Code or similar AI assistants for testing procedures:
> 
> Several commands in this testing workflow exceed the 2-minute execution time limit imposed by AI assistants:
> - `task clean-all-purge` (or alternative cleanup commands)
> - `docker-compose build`
> - `docker-compose pull`
> - Ollama model pulling (can take 5-10 minutes per model)
> 
> **Recommendation**: Run these commands manually BEFORE asking the AI to assist with testing:
> ```bash
> # Run these commands manually first
> task clean-all-purge  # or alternative cleanup commands
> docker-compose build
> docker-compose pull
> 
> # For quick model pull (optional but helpful)
> docker-compose up -d ollama
> docker-compose exec ollama ollama pull llama3
> docker-compose exec ollama ollama pull mxbai-embed-large
> ```
> 
> After these commands complete, you can engage the AI assistant for the remaining testing steps.

## Architecture and Integration Points

The OpenAI integration allows Obelisk to use either OpenAI models or local Ollama models, dynamically selecting the appropriate option based on configuration and API key availability.

### Key Components

1. **LiteLLM Proxy**: Routes requests to either OpenAI or Ollama based on:
   - Environment variables (OPENAI_API_KEY, USE_OPENAI)
   - Availability of models
   - Fallback configuration

2. **OpenWebUI**: Provides user interface for interacting with models through either:
   - Direct connection to LiteLLM proxy
   - Connection to Ollama

3. **Initialization Scripts**: Configure the system during startup:
   - Token generation and distribution
   - Model configuration and registration
   - Service configuration

## Testing Prerequisites

- Docker and Docker Compose installed
- Git clone of the Obelisk repository
- At least 16GB RAM and 50GB disk space
- Internet connection for downloading models
- (Optional) Valid OpenAI API key for full testing

### Verifying Container Versions

Before testing, you can verify you're using the recommended container versions:

```bash
# Run the container version checker script
cd /workspaces/obelisk
chmod +x hack/check_container_versions.sh
./hack/check_container_versions.sh
```

This script checks the latest stable versions of all container images used in Obelisk, including:
- PostgreSQL
- MinIO
- Ollama
- Milvus
- Apache Tika
- LiteLLM
- etcd
- Open WebUI

## Testing Methodology

This methodology focuses on validating both functionality and fallback behavior, ensuring the system works correctly in all scenarios.

### 1. Environment Preparation

There are two approaches for preparing the test environment: manual step-by-step or using the automated preparation script.

#### Option A: Using the Automated Preparation Script 

The repository includes a script to automate the preparation steps that would otherwise time out in AI assistants:

```bash
# Run the test preparation task (will clean, build, pull images, and download models)
task test-prep-openai

# (Optional) To test with OpenAI API key
export OPENAI_API_KEY="your-openai-api-key" 
export USE_OPENAI=true

# (Optional) To test fallback behavior
# export USE_OPENAI=true
# Do not set OPENAI_API_KEY
```

This automated script handles:
- Cleaning the environment via `task clean-all-purge`
- Building all containers with `docker-compose build`
- Pulling required container images with `docker-compose pull`
- Starting Ollama and downloading required models

#### Option B: Manual Step-by-Step Preparation

If you prefer to perform steps individually:

```bash
# Clean any existing environment
task clean-all-purge  # or use alternative docker-compose commands

# Build the containers
docker-compose build

# Pull required images
docker-compose pull

# Start ollama to download models
docker-compose up -d ollama
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull mxbai-embed-large

# (Optional) To test with OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"
export USE_OPENAI=true

# (Optional) To test fallback behavior
# export USE_OPENAI=true
# Do not set OPENAI_API_KEY
```

### 2. Running Tests

#### Starting Services and Initialization

After preparing the environment, you need to start the services in the correct order and run the initialization process:

```bash
# Start infrastructure services
docker-compose up -d etcd minio milvus

# Wait for milvus to be fully initialized
sleep 10

# Start AI services
docker-compose up -d litellm_db litellm

# Wait for litellm to be ready
sleep 5

# Run initialization service (this will run and exit when complete)
docker-compose up init-service

# Verify initialization was successful
docker-compose logs init-service | grep "Initialization complete"
docker-compose exec ollama ollama list
```

Make sure the initialization was successful before proceeding. You should see "Initialization complete" in the logs and both `llama3` and `mxbai-embed-large` models in the Ollama list.

#### Running the Test Script

After successful initialization, run Obelisk's automated tests:

```bash
# Run the comprehensive OpenAI integration test
./hack/test_openai_integration.sh
```

This script automates the testing workflow:
1. Validates system initialization
2. Tests OpenAI API directly (if key available)
3. Retrieves LiteLLM token from container
4. Tests LiteLLM API with authentication
5. Tests generation capabilities with appropriate model selection
6. Tests OpenWebUI accessibility and API functionality
7. Provides a comprehensive test summary

You can also run individual tests:

```bash
# IMPORTANT: Always use 'poetry run' to execute Python scripts to ensure all dependencies are available
# Direct execution with 'python' will likely fail with "ModuleNotFoundError: No module named 'requests'" or other missing dependencies

# Test initialization
poetry run python hack/test_init.py

# Test LiteLLM integration with OpenAI
LITELLM_TOKEN=$(docker-compose exec -T litellm grep LITELLM_API_TOKEN /app/tokens/api_tokens.env | cut -d= -f2 | tr -d ' \t\n\r')
OPENAI_API_KEY="$OPENAI_API_KEY" \
LITELLM_API_TOKEN="$LITELLM_TOKEN" \
LITELLM_API_URL="http://localhost:4000" \
poetry run python hack/test_litellm_openai.py

# Run end-to-end testing
OPENAI_API_KEY="$OPENAI_API_KEY" \
LITELLM_API_TOKEN="$LITELLM_TOKEN" \
LITELLM_API_URL="http://localhost:4000" \
OPENWEBUI_API_URL="http://localhost:8080" \
poetry run python hack/test_e2e_openai.py
```

### 3. Manual Verification

After automated testing, perform these manual validations:

#### Check LiteLLM API and Models

```bash
# Get LiteLLM token
LITELLM_TOKEN=$(docker-compose exec -T litellm grep LITELLM_API_TOKEN /app/tokens/api_tokens.env | cut -d= -f2 | tr -d ' \t\n\r')

# List available models
curl -s -H "Authorization: Bearer ${LITELLM_TOKEN}" http://localhost:4000/models | jq

# Test completion with appropriate model
MODEL="gpt-4o"  # If OpenAI API key available
# MODEL="llama3"  # If no OpenAI API key

curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LITELLM_TOKEN}" \
  -d '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "Say hello in one word"}],
    "max_tokens": 10
  }' | jq
```

#### Test OpenWebUI Integration

- Access OpenWebUI in browser: http://localhost:8080/
- Navigate to Settings > LiteLLM/OpenAI API Settings
- Verify the API URL is set to http://litellm:4000
- Start a new chat and test responses
- Ensure model selection includes appropriate models based on your configuration

#### Verify Fallback Behavior

If you have an OpenAI API key, test both with and without the key:

```bash
# Test with OpenAI API key
export OPENAI_API_KEY="your-key"
export USE_OPENAI=true
./hack/test_openai_integration.sh

# Test fallback behavior
unset OPENAI_API_KEY
export USE_OPENAI=true
./hack/test_openai_integration.sh
```

## Key Testing Focus Areas

When testing the OpenAI integration, pay particular attention to these areas:

### 1. Model Registration and Availability

- **With OpenAI API Key**:
  - Both OpenAI models (gpt-4o) and Ollama models (llama3) should be available
  - Model aliases should work correctly (e.g., both "gpt-4o" and "openai/gpt-4o")

- **Without OpenAI API Key**:
  - Only Ollama models should be available
  - System should not show errors related to missing OpenAI models

### 2. Authentication and Tokens

- Token format should be clean (no whitespace, newlines, or "Bearer " prefix)
- LiteLLM should accept the token and provide access to models
- Tokens should be properly shared between services

### 3. API Functionality

- LiteLLM API should respond correctly to requests
- OpenWebUI should connect to LiteLLM API successfully
- Chat completions should work with authentication

### 4. Fallback Mechanism

- With OpenAI API key: OpenAI models should be used
- Without OpenAI API key: System should fallback to Ollama models
- No errors should occur during fallback

## Troubleshooting Common Issues

### Authentication Problems

- **Symptom**: "Unauthorized" or 401 errors
- **Check**:
  ```bash
  # Verify token format
  LITELLM_TOKEN=$(docker-compose exec -T litellm grep LITELLM_API_TOKEN /app/tokens/api_tokens.env | cut -d= -f2 | tr -d ' \t\n\r')
  echo "Token: $LITELLM_TOKEN"
  ```
- **Solution**: If token has whitespace or "Bearer " prefix, clean it before using

### Model Registration Issues

- **Symptom**: OpenAI models not appearing in model list
- **Check**:
  ```bash
  # Check LiteLLM logs for model registration
  docker-compose logs litellm | grep -i "model registration"
  docker-compose exec litellm cat /app/config/litellm_config.yaml
  ```
- **Solution**: Verify OpenAI API key is passed correctly in environment variables

### OpenWebUI API Authentication

- **Note**: OpenWebUI's chat completions API requiring authentication (403/401) is normal
- **Solution**: Access through the web interface at http://localhost:8080

### Initialization Failures

- **Check**: 
  ```bash
  docker-compose logs init-service
  ```
- **Solution**: Look for specific errors in token generation, model pulling, or configuration

## Conclusion

By following this testing methodology, you can thoroughly validate the OpenAI integration in Obelisk. Remember to test both with and without an OpenAI API key to ensure the fallback mechanism works correctly.

For additional help or to report issues, please refer to the main project documentation or submit a detailed issue report to the project repository.
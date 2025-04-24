#!/bin/bash
# Service configuration for Obelisk
# Handles configuration of all services in the stack

set -e

echo "Service Configuration"
echo "===================="

# Configuration sources
TOKEN_FILE="/app/tokens/api_tokens.env"
CONFIG_DIR="/app/config"

# Load tokens if available
if [ -f "$TOKEN_FILE" ]; then
  source "$TOKEN_FILE"
fi

# Ensure config directory exists
mkdir -p "$CONFIG_DIR"

# Configure LiteLLM
function configure_litellm() {
  echo "Configuring LiteLLM service..."
  
  # Determine if OpenAI should be used
  USE_OPENAI_CONFIG=false
  
  # Check for API key and use flag
  if [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI}" = "true" ]; then
    USE_OPENAI_CONFIG=true
    echo "OpenAI configuration enabled"
  fi
  
  echo "LiteLLM configuration complete"
  
  # Function to wait for LiteLLM API to be available
  wait_for_litellm_api() {
    local retry_count=0
    local max_retries=30
    local wait_time=2
    local api_token="${LITELLM_API_TOKEN:-sk-1234}"
    
    echo "Waiting for LiteLLM API to be available..."
    
    while [ $retry_count -lt $max_retries ]; do
      # First try with authorization header (preferred method)
      if curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${api_token}" "http://litellm:4000/models" | grep -q "200"; then
        echo "LiteLLM API is available (authenticated with API token)"
        return 0
      fi
      
      # Second option: try the /health endpoint with master key
      if curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "http://litellm:4000/health" | grep -q "200"; then
        echo "LiteLLM API is available (authenticated with master key)"
        return 0
      fi
      
      # Third option: try other endpoints that might not require auth
      if curl -s -o /dev/null -w "%{http_code}" "http://litellm:4000/v1/models" | grep -q "200"; then
        echo "LiteLLM API is available (v1 endpoint)"
        return 0
      fi
      
      # Alternative: check if the server is at least running (will return 401 if running but requires auth)
      if curl -s -o /dev/null -w "%{http_code}" "http://litellm:4000/health" | grep -q "401"; then
        echo "LiteLLM API is available (requires authentication)"
        return 0
      fi
      
      echo "LiteLLM API not ready yet, retrying in ${wait_time}s... (${retry_count}/${max_retries})"
      sleep $wait_time
      retry_count=$((retry_count + 1))
    done
    
    echo "ERROR: Timed out waiting for LiteLLM API to become available after $((max_retries * wait_time)) seconds"
    return 1
  }
  
  # Function to register models via API
  register_models_via_api() {
    echo "Registering models via LiteLLM API..."
    
    # Use master key for model registration which requires admin privileges
    local api_token="${LITELLM_MASTER_KEY:-sk-1234}"
    local api_base="http://litellm:4000"
    
    # First, wait for the API to be available
    wait_for_litellm_api
    
    # Register Ollama models
    echo "Registering Ollama models with LiteLLM API..."
    
    # Register Llama3
    curl -s -X POST "${api_base}/model/new" \
      -H "Authorization: Bearer ${api_token}" \
      -H "Content-Type: application/json" \
      -d '{
        "model_name": "ollama/llama3",
        "litellm_params": {
          "model": "ollama/llama3",
          "api_base": "http://ollama:11434",
          "drop_params": true
        }
      }'
    echo ""
    
    # Register Llama3 alias
    curl -s -X POST "${api_base}/model/new" \
      -H "Authorization: Bearer ${api_token}" \
      -H "Content-Type: application/json" \
      -d '{
        "model_name": "llama3",
        "litellm_params": {
          "model": "ollama/llama3",
          "api_base": "http://ollama:11434",
          "drop_params": true
        }
      }'
    echo ""
    
    # Register MXBai embedding model
    curl -s -X POST "${api_base}/model/new" \
      -H "Authorization: Bearer ${api_token}" \
      -H "Content-Type: application/json" \
      -d '{
        "model_name": "ollama/mxbai-embed-large",
        "litellm_params": {
          "model": "ollama/mxbai-embed-large",
          "api_base": "http://ollama:11434",
          "drop_params": true
        }
      }'
    echo ""
    
    # Register OpenAI models if enabled
    if [ "$USE_OPENAI_CONFIG" = true ] && [ -n "${OPENAI_API_KEY}" ]; then
      echo "Registering OpenAI models with LiteLLM API..."
      
      # Register GPT-4o
      curl -s -X POST "${api_base}/model/new" \
        -H "Authorization: Bearer ${api_token}" \
        -H "Content-Type: application/json" \
        -d '{
          "model_name": "openai/gpt-4o",
          "litellm_params": {
            "model": "openai/gpt-4o",
            "api_key": "'${OPENAI_API_KEY}'",
            "drop_params": true
          }
        }'
      echo ""
      
      # Register GPT-4o alias
      curl -s -X POST "${api_base}/model/new" \
        -H "Authorization: Bearer ${api_token}" \
        -H "Content-Type: application/json" \
        -d '{
          "model_name": "gpt-4o",
          "litellm_params": {
            "model": "openai/gpt-4o",
            "api_key": "'${OPENAI_API_KEY}'",
            "drop_params": true
          }
        }'
      echo ""
      
      # Register Embedding model
      curl -s -X POST "${api_base}/model/new" \
        -H "Authorization: Bearer ${api_token}" \
        -H "Content-Type: application/json" \
        -d '{
          "model_name": "openai/text-embedding-3-large",
          "litellm_params": {
            "model": "openai/text-embedding-3-large",
            "api_key": "'${OPENAI_API_KEY}'",
            "drop_params": true
          }
        }'
      echo ""
      
      # Register Embedding model alias
      curl -s -X POST "${api_base}/model/new" \
        -H "Authorization: Bearer ${api_token}" \
        -H "Content-Type: application/json" \
        -d '{
          "model_name": "text-embedding-3-large",
          "litellm_params": {
            "model": "openai/text-embedding-3-large",
            "api_key": "'${OPENAI_API_KEY}'",
            "drop_params": true
          }
        }'
      echo ""
      
      # Setup fallbacks if OpenAI is enabled
      echo "Setting up model fallbacks..."
      
      # Register fallbacks
      curl -s -X POST "${api_base}/router/set" \
        -H "Authorization: Bearer ${api_token}" \
        -H "Content-Type: application/json" \
        -d '{
          "router_settings": {
            "fallbacks": [
              {
                "model": "openai/gpt-4o",
                "fallback_model": "ollama/llama3"
              },
              {
                "model": "gpt-4o",
                "fallback_model": "ollama/llama3"
              },
              {
                "model": "openai/text-embedding-3-large",
                "fallback_model": "ollama/mxbai-embed-large"
              },
              {
                "model": "text-embedding-3-large",
                "fallback_model": "ollama/mxbai-embed-large"
              }
            ]
          }
        }'
      echo ""
    fi
    
    echo "Model registration via API complete"
  }
  
  # Process any pending model registrations from previous stages
  function process_pending_model_registrations() {
    echo "Checking for pending model registrations..."
    
    # Check for pending model registrations
    PENDING_MODELS_DIR="/app/config/pending_models"
    if [ -d "$PENDING_MODELS_DIR" ] && [ "$(ls -A $PENDING_MODELS_DIR 2>/dev/null)" ]; then
      echo "Found pending model registrations, processing..."
      
      # Wait for LiteLLM API to be available first
      wait_for_litellm_api
      
      # Process each pending model registration
      for model_file in "$PENDING_MODELS_DIR"/*.json; do
        model_name=$(basename "$model_file" .json)
        echo "Registering pending model: $model_name"
        
        # Register the model
        curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/model/new" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -H "Content-Type: application/json" \
          -d @"$model_file"
        echo ""
        
        # Remove the pending registration file
        rm "$model_file"
      done
      
      echo "Completed processing pending model registrations"
    else
      echo "No pending model registrations found"
    fi
  }
  
  # Check for pending token registrations
  function process_pending_token_registrations() {
    echo "Checking for pending token registrations..."
    
    TOKEN_REG_FILE="/app/config/.token_registration_pending"
    if [ -f "$TOKEN_REG_FILE" ]; then
      echo "Found pending token registration, processing..."
      
      # Wait for LiteLLM API to be available first
      wait_for_litellm_api
      
      # Read token from file
      TOKEN=$(cat "$TOKEN_REG_FILE")
      
      # Register the token
      echo "Registering pending token with LiteLLM API..."
      curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/key/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
        -d "{
          \"key_name\": \"obelisk-init-token\",
          \"key\": \"$TOKEN\",
          \"metadata\": {\"description\": \"Obelisk initialization token (delayed registration)\"},
          \"models\": [\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"],
          \"tpm\": 100000,
          \"rpm\": 5000
        }"
      echo ""
      
      # Remove the pending registration file
      rm "$TOKEN_REG_FILE"
      
      echo "Completed processing pending token registration"
    else
      echo "No pending token registrations found"
    fi
    
    # Also check for the alternate token registration file
    TOKEN_REG_NEEDED_FILE="/app/config/.token_registration_needed"
    if [ -f "$TOKEN_REG_NEEDED_FILE" ]; then
      echo "Found token registration needed marker, processing..."
      
      # Wait for LiteLLM API to be available first
      wait_for_litellm_api
      
      # Read token from file
      TOKEN=$(cat "$TOKEN_REG_NEEDED_FILE")
      
      # Register the token
      echo "Registering token with LiteLLM API..."
      curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/key/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
        -d "{
          \"key_name\": \"obelisk-init-token\",
          \"key\": \"$TOKEN\",
          \"metadata\": {\"description\": \"Obelisk initialization token (verify retry)\"},
          \"models\": [\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"],
          \"tpm\": 100000,
          \"rpm\": 5000
        }"
      echo ""
      
      # Remove the pending registration file
      rm "$TOKEN_REG_NEEDED_FILE"
      
      echo "Completed processing token registration"
    fi
  }
  
  # Check for pending OpenAI model registrations
  function process_pending_openai_registrations() {
    echo "Checking for pending OpenAI model registrations..."
    
    OPENAI_REG_FILE="/app/config/.openai_registration_pending"
    if [ -f "$OPENAI_REG_FILE" ]; then
      echo "Found pending OpenAI model registration, processing..."
      
      # Wait for LiteLLM API to be available first
      wait_for_litellm_api
      
      # Source the OpenAI registration info
      source "$OPENAI_REG_FILE"
      
      # Register the OpenAI models
      if [ -n "$OPENAI_API_KEY" ]; then
        echo "Registering OpenAI models with LiteLLM API..."
        
        # Register GPT-4o model
        curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/model/new" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -H "Content-Type: application/json" \
          -d '{
            "model_name": "openai/'"${OPENAI_COMPLETION_MODEL}"'",
            "litellm_params": {
              "model": "openai/'"${OPENAI_COMPLETION_MODEL}"'",
              "api_key": "'"${OPENAI_API_KEY}"'",
              "drop_params": true
            }
          }'
        echo ""
        
        # Register alias without provider prefix
        curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/model/new" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -H "Content-Type: application/json" \
          -d '{
            "model_name": "'"${OPENAI_COMPLETION_MODEL}"'",
            "litellm_params": {
              "model": "openai/'"${OPENAI_COMPLETION_MODEL}"'",
              "api_key": "'"${OPENAI_API_KEY}"'",
              "drop_params": true
            }
          }'
        echo ""
        
        # Register embedding model
        curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/model/new" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -H "Content-Type: application/json" \
          -d '{
            "model_name": "openai/'"${OPENAI_EMBEDDING_MODEL}"'",
            "litellm_params": {
              "model": "openai/'"${OPENAI_EMBEDDING_MODEL}"'",
              "api_key": "'"${OPENAI_API_KEY}"'",
              "drop_params": true
            }
          }'
        echo ""
        
        # Register embedding model alias
        curl -s -X POST "${LITELLM_API_URL:-http://litellm:4000}/model/new" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -H "Content-Type: application/json" \
          -d '{
            "model_name": "'"${OPENAI_EMBEDDING_MODEL}"'",
            "litellm_params": {
              "model": "openai/'"${OPENAI_EMBEDDING_MODEL}"'",
              "api_key": "'"${OPENAI_API_KEY}"'",
              "drop_params": true
            }
          }'
        echo ""
        
        echo "OpenAI models registration complete"
      fi
      
      # Remove the pending registration file
      rm "$OPENAI_REG_FILE"
      
      echo "Completed processing pending OpenAI model registrations"
    else
      echo "No pending OpenAI model registrations found"
    fi
  }
  
  # Process all pending registrations
  process_pending_token_registrations
  process_pending_openai_registrations
  process_pending_model_registrations
  
  # Register models via API (config file no longer needed)
  register_models_via_api
}

# Configure OpenWebUI
function configure_openwebui() {
  echo "Configuring OpenWebUI service..."
  
  # Create configuration for OpenWebUI if needed
  # OpenWebUI is primarily configured via environment variables in docker-compose.yaml
  # but we can set up additional configuration here if needed
  
  # Ensure configuration directories exist
  mkdir -p "$CONFIG_DIR/openwebui"
  
  # Always create these files regardless of token presence
  echo "Setting up OpenWebUI configuration..."
  
  # Determine model configuration
  OLLAMA_MODELS="llama3,mxbai-embed-large"
  
  # Default to always including OpenAI models through LiteLLM - we manage
  # this through token permissions at LiteLLM level
  OPENAI_MODELS="gpt-4o,text-embedding-3-large"
  
  # Create configurations
  echo "Creating OpenWebUI configurations..."
  
  # Create the environment file with appropriate configuration
  cat > "$CONFIG_DIR/openwebui/openai.env" << EOF
# OpenWebUI API configuration
# Generated at: $(date)
OPENAI_API_KEY=${LITELLM_API_TOKEN:-sk-1234}
OPENAI_API_BASE_URL=http://litellm:4000
OLLAMA_MODELS=${OLLAMA_MODELS}
OPENAI_MODELS=${OPENAI_MODELS}
OPENAI_USE_KEY=true
EOF
  
  # Create a JSON config file that OpenWebUI can load
  # This file contains model configurations that can be used by OpenWebUI
  cat > "$CONFIG_DIR/openwebui/models.json" << EOF
{
  "models": [
    {
      "name": "llama3",
      "type": "ollama",
      "endpoint": "http://ollama:11434"
    },
    {
      "name": "mxbai-embed-large",
      "type": "embedding",
      "endpoint": "http://ollama:11434"
    },
    {
      "name": "gpt-4o",
      "type": "openai",
      "endpoint": "http://litellm:4000"
    },
    {
      "name": "text-embedding-3-large",
      "type": "embedding",
      "endpoint": "http://litellm:4000"
    }
  ]
}
EOF

  # Create default model credentials file
  cat > "$CONFIG_DIR/openwebui/model_credentials.json" << EOF
{
  "credentials": {
    "openai": {
      "key": "${LITELLM_API_TOKEN:-sk-1234}",
      "endpoint": "http://litellm:4000"
    }
  }
}
EOF

  echo "OpenWebUI configuration complete"
}

# Configure Obelisk-RAG
function configure_obelisk_rag() {
  echo "Configuring Obelisk-RAG service..."
  
  # Determine provider settings based on OpenAI availability
  EMBEDDING_PROVIDER="ollama"
  EMBEDDING_MODEL="mxbai-embed-large"
  COMPLETION_PROVIDER="ollama"
  COMPLETION_MODEL="llama3"
  
  # Update to OpenAI if key is available and USE_OPENAI is true
  if [ -n "${OPENAI_API_KEY}" ] && [ "${USE_OPENAI:-false}" = "true" ]; then
    EMBEDDING_PROVIDER="openai"
    EMBEDDING_MODEL="${OPENAI_EMBEDDING_MODEL:-text-embedding-3-large}"
    COMPLETION_PROVIDER="openai"
    COMPLETION_MODEL="${OPENAI_COMPLETION_MODEL:-gpt-4o}"
    echo "OpenAI providers enabled for RAG"
  fi
  
  # Create or update Obelisk-RAG configuration
  cat > "$CONFIG_DIR/rag_config.yaml" << EOF
# Obelisk-RAG Configuration
# Generated at: $(date)

embedding:
  provider: ${EMBEDDING_PROVIDER}
  model: ${EMBEDDING_MODEL}
  openai_api_key: ${OPENAI_API_KEY:-}
  openai_model: ${OPENAI_EMBEDDING_MODEL:-text-embedding-3-large}

completion:
  provider: ${COMPLETION_PROVIDER}
  model: ${COMPLETION_MODEL}
  openai_api_key: ${OPENAI_API_KEY:-}
  openai_model: ${OPENAI_COMPLETION_MODEL:-gpt-4o}

storage:
  type: milvus
  host: milvus
  port: 19530
  collection: documents

retrieve:
  top_k: 5

litellm:
  api_base: http://litellm:4000
  api_key: ${LITELLM_API_TOKEN:-sk-1234}
EOF

  echo "Obelisk-RAG configuration complete"
}

# Configure Milvus
function configure_milvus() {
  echo "Configuring Milvus service..."
  
  # Check if Milvus is available
  # This might involve creating collections or other setup tasks
  
  echo "Milvus configuration complete"
}

# Token permissions verification function (at global level)
function verify_token_permissions() {
  echo "========================================"
  echo "Verifying API token permissions..."
  
  # Wait for LiteLLM API to be available
  LITELLM_API_URL="${LITELLM_API_URL:-http://litellm:4000}"
  
  # Define retry parameters for API connectivity check
  local max_retries=10
  local retry_count=0
  local wait_time=3
  local api_available=false
    
  echo "Waiting for LiteLLM API to be available..."
  while [ $retry_count -lt $max_retries ]; do
    # Try multiple ways to check if API is available
    if curl -s --connect-timeout 2 -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "$LITELLM_API_URL/health" > /dev/null 2>&1; then
      echo "LiteLLM API is available (authenticated with master key)"
      api_available=true
      break
    elif curl -s --connect-timeout 2 "$LITELLM_API_URL/v1/models" > /dev/null 2>&1; then
      echo "LiteLLM API is available (v1 endpoint)"
      api_available=true
      break
    elif curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" "$LITELLM_API_URL/health" | grep -q "401"; then
      echo "LiteLLM API is available (requires authentication)"
      api_available=true
      break
    fi
      
    echo "Waiting for LiteLLM API to be available... (attempt $((retry_count+1)) of $max_retries)"
    sleep $wait_time
    retry_count=$((retry_count + 1))
  done
  
  if [ "$api_available" = false ]; then
    echo "ERROR: LiteLLM API did not become available for token verification"
    echo "Token verification will be skipped"
    return 1
  fi
  
  # Get the current API token
  local api_token="${LITELLM_API_TOKEN:-}"
  if [ -f "$TOKEN_FILE" ]; then
    source "$TOKEN_FILE"
    api_token="${LITELLM_API_TOKEN:-$api_token}"
  fi
  
  if [ -z "$api_token" ]; then
    echo "No API token found, skipping permission verification"
    return 1
  fi
  
  echo "Using API token: ${api_token:0:5}... for verification"
  
  # Check what models the token can see
  local models_response=$(curl -s -H "Authorization: Bearer $api_token" "$LITELLM_API_URL/models")
  echo "Current models accessible to token: $(echo "$models_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ')"
  
  # If the response only has "*" or doesn't have our specific models, update the permissions
  if echo "$models_response" | grep -q "\"id\":\"\\*\"" || ! (echo "$models_response" | grep -q "llama3" && echo "$models_response" | grep -q "mxbai-embed-large"); then
    echo "API token needs specific model permissions, updating..."
    
    # Determine which models to include
    local model_list="[\"llama3\", \"mxbai-embed-large\"]"
    
    # Add OpenAI models if they should be available
    if [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI:-false}" = "true" ]; then
      model_list="[\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"]"
      echo "Including OpenAI models in token permissions"
    fi
    
    # Update token permissions to use specific models instead of wildcard
    local update_response=$(curl -s -X POST "$LITELLM_API_URL/key/update" \
      -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
      -H "Content-Type: application/json" \
      -d "{
        \"key\": \"$api_token\",
        \"models\": $model_list
      }")
    
    echo "Token update response: $update_response"
    
    # Verify the update was successful
    local verify_response=$(curl -s -H "Authorization: Bearer $api_token" "$LITELLM_API_URL/models")
    if ! echo "$verify_response" | grep -q "\"id\":\"\\*\"" && (echo "$verify_response" | grep -q "llama3" && echo "$verify_response" | grep -q "mxbai-embed-large"); then
      echo "✓ API token permissions successfully updated"
      echo "Updated models accessible to token: $(echo "$verify_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ')"
    else
      echo "! WARNING: Token permissions update may not have been successful"
      echo "Models still accessible: $(echo "$verify_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ')"
    fi
  else
    echo "✓ API token permissions already correctly set - has access to specific models"
    echo "Models accessible: $(echo "$models_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ')"
  fi
  
  echo "Token permissions verification complete"
  echo "========================================"
}

# Main execution
configure_litellm
configure_openwebui
configure_obelisk_rag
configure_milvus

echo "Service configuration complete"

# Run final token permission verification as the last step
# This ensures all models are registered before updating token permissions
verify_token_permissions
#!/bin/bash
# Register models with LiteLLM dynamically
# This ensures models are properly configured for routing

set -e

echo "LiteLLM Model Registration"
echo "========================="

# Configuration
LITELLM_API_URL="${LITELLM_API_URL:-http://litellm:4000}"
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-sk-1234}"
TOKEN_FILE="${TOKEN_FILE:-/app/tokens/api_tokens.env}"

# Load tokens if available
if [ -f "$TOKEN_FILE" ]; then
  source "$TOKEN_FILE"
fi

# Function to register a model with LiteLLM
register_model() {
  local model_name="$1"
  local model_config="$2"
  
  echo "Registering model: $model_name"
  
  # Check if model already exists
  local exists=$(curl -s -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    "$LITELLM_API_URL/v1/models" | jq -r ".data[] | select(.id == \"$model_name\") | .id" 2>/dev/null)
  
  if [ -n "$exists" ]; then
    echo "Model $model_name already registered"
    return 0
  fi
  
  # Register the model
  local response=$(curl -s -X POST "$LITELLM_API_URL/model/new" \
    -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    -H "Content-Type: application/json" \
    -d "$model_config")
  
  if echo "$response" | grep -q "model_id"; then
    echo "Successfully registered $model_name"
  else
    echo "Failed to register $model_name: $response"
    return 1
  fi
}

# Function to wait for LiteLLM
wait_for_litellm() {
  echo "Waiting for LiteLLM to be ready..."
  local retries=0
  local max_retries=30
  
  while [ $retries -lt $max_retries ]; do
    if curl -s "$LITELLM_API_URL/health" >/dev/null 2>&1; then
      echo "LiteLLM is ready"
      return 0
    fi
    echo "Waiting for LiteLLM... (attempt $((retries + 1))/$max_retries)"
    sleep 2
    retries=$((retries + 1))
  done
  
  echo "Error: LiteLLM not available after $max_retries attempts"
  return 1
}

# Main registration function
register_all_models() {
  # Wait for LiteLLM
  if ! wait_for_litellm; then
    echo "Failed to connect to LiteLLM"
    exit 1
  fi
  
  echo "Registering Ollama models..."
  
  # Register llama3
  register_model "llama3" '{
    "model_name": "llama3",
    "litellm_params": {
      "model": "ollama/llama3",
      "api_base": "http://ollama:11434"
    }
  }'
  
  # Register mxbai-embed-large
  register_model "mxbai-embed-large" '{
    "model_name": "mxbai-embed-large",
    "litellm_params": {
      "model": "ollama/mxbai-embed-large",
      "api_base": "http://ollama:11434"
    }
  }'
  
  # Register OpenAI models if API key is available
  if [ -n "${OPENAI_API_KEY}" ]; then
    echo "Registering OpenAI models..."
    
    # Register gpt-4o
    register_model "gpt-4o" "{
      \"model_name\": \"gpt-4o\",
      \"litellm_params\": {
        \"model\": \"gpt-4o\",
        \"api_key\": \"os.environ/OPENAI_API_KEY\"
      }
    }"
    
    # Register text-embedding-3-large
    register_model "text-embedding-3-large" "{
      \"model_name\": \"text-embedding-3-large\",
      \"litellm_params\": {
        \"model\": \"text-embedding-3-large\",
        \"api_key\": \"os.environ/OPENAI_API_KEY\"
      }
    }"
    
    echo "OpenAI models registered"
  else
    echo "No OpenAI API key found, skipping OpenAI models"
  fi
  
  # List all registered models
  echo ""
  echo "Currently registered models:"
  curl -s -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    "$LITELLM_API_URL/v1/models" | jq -r '.data[].id' 2>/dev/null || echo "Failed to list models"
}

# Run registration
register_all_models

echo "Model registration complete"
#!/bin/bash
# Ollama model management for Obelisk
# Handles downloading and configuring required models

set -e

echo "Ollama Model Management"
echo "======================="

# Configuration
EMBEDDING_MODEL="mxbai-embed-large"
GENERATION_MODEL="llama3"
OLLAMA_API="http://ollama:11434/api"
OLLAMA_API_URL="${OLLAMA_API_URL:-http://ollama:11434}"  # Make sure this is set for LiteLLM registration

# Function to check if model is already pulled
function check_model() {
  local model_name=$1
  echo "Checking if model '$model_name' is available..."
  
  # Get all models from Ollama API
  local response=$(curl -s "$OLLAMA_API/tags")
  
  # Check if model exists in the list (handling both with and without tags)
  if echo "$response" | grep -q "\"name\":\"$model_name\"\\|\"name\":\"$model_name:"; then
    echo "Model '$model_name' is already available"
    return 0
  else
    echo "Model '$model_name' needs to be pulled"
    return 1
  fi
}

# Function to pull a model using Ollama API
function pull_model() {
  local model_name=$1
  echo "Pulling model '$model_name'..."
  
  # Pull the model using Ollama API
  curl -s "$OLLAMA_API/pull" -d "{\"name\":\"$model_name\"}" > /dev/null
  
  # Wait for model to become available (pulling can take time)
  local MAX_RETRIES=60
  local RETRY_INTERVAL=10
  local retries=0
  
  while [ $retries -lt $MAX_RETRIES ]; do
    if check_model "$model_name"; then
      echo "Successfully pulled model '$model_name'"
      
      # Register model with LiteLLM if available
      if [ -n "$LITELLM_API_URL" ]; then
        # Try to register with LiteLLM API but don't block on it
        echo "Attempting to register model with LiteLLM API..."
        
        # Format model information based on its type
        local model_type="completion"
        if [[ "$model_name" == *"embed"* ]]; then
          model_type="embedding"
        fi
        
        # Create a temporary file for the JSON payload to ensure proper formatting
        TEMP_JSON_FILE=$(mktemp)
        cat > "$TEMP_JSON_FILE" << EOF
{
  "model_name": "$model_name",
  "litellm_params": {
    "model": "ollama/$model_name",
    "api_base": "$OLLAMA_API_URL",
    "drop_params": true
  }
}
EOF
        
        # Non-blocking check for LiteLLM availability with authentication
        if curl -s --connect-timeout 2 -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "$LITELLM_API_URL/health" > /dev/null 2>&1 || \
           curl -s --connect-timeout 2 -H "Authorization: Bearer ${LITELLM_API_TOKEN:-sk-1234}" "$LITELLM_API_URL/models" > /dev/null 2>&1 || \
           curl -s --connect-timeout 2 "$LITELLM_API_URL/v1/models" > /dev/null 2>&1 || \
           curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" "$LITELLM_API_URL/health" | grep -q "401"; then
          echo "LiteLLM API is available, registering model..."
          
          # Send the properly formatted JSON with master key (admin privileges)
          curl -s -X POST "$LITELLM_API_URL/model/new" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
            -d @"$TEMP_JSON_FILE"
            
          # Check if model registration was successful
          if [ $? -eq 0 ]; then
            echo "Model '$model_name' registered with LiteLLM API successfully"
          else
            echo "Warning: Failed to register model '$model_name' with LiteLLM API"
          fi
        else
          echo "LiteLLM API not immediately available - model will be registered during service configuration"
          
          # Store model info for later registration
          mkdir -p "/app/config/pending_models"
          
          # Store the model details for later registration
          cp "$TEMP_JSON_FILE" "/app/config/pending_models/${model_name}.json"
        fi
        
        # Clean up temp file
        rm "$TEMP_JSON_FILE"
      fi
      
      return 0
    fi
    
    echo "Model not yet available, waiting... (retry $retries of $MAX_RETRIES)"
    sleep $RETRY_INTERVAL
    retries=$((retries + 1))
  done
  
  echo "Failed to pull model '$model_name' after $MAX_RETRIES retries"
  return 1
}

# Main function to manage models
function manage_models() {
  echo "Managing Ollama models..."
  
  # Wait for Ollama service to be available
  echo "Waiting for Ollama API to be available..."
  until curl -s -f "$OLLAMA_API/version" > /dev/null; do
    echo "Ollama API not yet available, waiting..."
    sleep 5
  done
  
  # Check and pull embedding model
  if ! check_model "$EMBEDDING_MODEL"; then
    pull_model "$EMBEDDING_MODEL"
  fi
  
  # Check and pull generation model
  if ! check_model "$GENERATION_MODEL"; then
    pull_model "$GENERATION_MODEL"
  fi
  
  echo "Model management complete"
}

# Execute model management
manage_models
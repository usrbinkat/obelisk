#!/bin/bash
# Master initialization controller for Obelisk container startup
# Manages the startup sequence, token generation, and model management

set -e

echo "Obelisk Container Initialization"
echo "================================"
echo "Starting initialization sequence at $(date)"

# Script locations
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TOKEN_SCRIPT="${SCRIPT_DIR}/generate-tokens.sh"
MODELS_SCRIPT="${SCRIPT_DIR}/download-models.sh"
CONFIG_SCRIPT="${SCRIPT_DIR}/configure-services.sh"

# Initialization steps
function check_dependencies() {
  echo "Checking service dependencies..."
  # TODO: Add dependency checks for required services
}

function generate_tokens() {
  echo "Generating and propagating authentication tokens..."
  # Source token script when it exists
  if [ -f "$TOKEN_SCRIPT" ]; then
    source "$TOKEN_SCRIPT"
  else
    echo "Warning: Token generation script not found"
  fi
}

function configure_models() {
  echo "Configuring and downloading required models..."
  # Source models script when it exists
  if [ -f "$MODELS_SCRIPT" ]; then
    source "$MODELS_SCRIPT"
  else
    echo "Warning: Model configuration script not found"
  fi
}

function configure_services() {
  echo "Configuring services..."
  # Source config script when it exists
  if [ -f "$CONFIG_SCRIPT" ]; then
    source "$CONFIG_SCRIPT"
  else
    echo "Warning: Service configuration script not found"
  fi
}

function verify_initialization() {
  echo "Verifying initialization..."
  
  # Check if token file exists
  if [ ! -f "/app/tokens/api_tokens.env" ]; then
    echo "Error: Token file not found. Initialization may have failed."
    return 1
  fi
  
  # Check if Ollama API is accessible
  if ! curl -s "$OLLAMA_API_URL/api/tags" > /dev/null; then
    echo "Error: Ollama API is not accessible. Initialization may have failed."
    return 1
  fi
  
  # Check if LiteLLM API is accessible with the generated token
  # First source the token file to get the token value
  source "/app/tokens/api_tokens.env"
  
  # Check LiteLLM authentication
  if ! curl -s -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models" > /dev/null; then
    echo "Warning: LiteLLM API authentication failed. Token may not be registered."
    
    # Try to register the token
    echo "Attempting to register token with LiteLLM API..."
    curl -s -X POST "$LITELLM_API_URL/key/generate" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
      -d "{
          \"key\": \"$LITELLM_API_TOKEN\",
          \"metadata\": {\"description\": \"Obelisk initialization token (verification)\"}
      }" > /dev/null
      
    # Check again
    if ! curl -s -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models" > /dev/null; then
      echo "Error: LiteLLM API authentication still failed after token registration."
      return 1
    fi
  fi
  
  # All checks passed
  echo "Verification completed successfully"
  return 0
}

# Main initialization sequence
check_dependencies
generate_tokens
configure_models
configure_services
verify_initialization

echo "Initialization complete at $(date)"
echo "================================"
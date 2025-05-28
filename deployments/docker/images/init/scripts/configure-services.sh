#!/bin/bash
# Service configuration for Obelisk
# Model registration is handled by register-litellm-models.sh

set -e

echo "Service Configuration"
echo "===================="

# Configuration sources with environment variable fallbacks
TOKEN_FILE="${TOKEN_FILE:-/app/tokens/api_tokens.env}"
CONFIG_DIR="${CONFIG_DIR:-/app/config}"

# Load tokens from file if available, otherwise use environment
if [ -f "$TOKEN_FILE" ]; then
  echo "Loading tokens from $TOKEN_FILE"
  source "$TOKEN_FILE"
elif [ -n "$LITELLM_API_TOKEN" ]; then
  echo "Using tokens from environment variables"
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
  
  # Model registration is handled by register-litellm-models.sh
  echo "Model registration will be handled by dedicated script"
}

# Configure Milvus - No longer needed since we're using updated schema
function configure_milvus() {
  echo "Milvus configuration skipped - using updated Obelisk schema"
}

# Main execution
configure_litellm
configure_milvus

echo "Service configuration complete"
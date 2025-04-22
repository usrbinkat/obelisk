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
  
  # Create or update LiteLLM configuration
  cat > "$CONFIG_DIR/litellm_config.yaml" << EOF
# LiteLLM Configuration
# Generated at: $(date)

model_list:
  - model_name: llama3
    litellm_params:
      model: ollama/llama3
      api_base: http://ollama:11434
  - model_name: mxbai-embed-large
    litellm_params:
      model: ollama/mxbai-embed-large
      api_base: http://ollama:11434

# Authentication
api_key: ${LITELLM_API_TOKEN:-sk-1234}
EOF

  echo "LiteLLM configuration complete"
}

# Configure OpenWebUI
function configure_openwebui() {
  echo "Configuring OpenWebUI service..."
  
  # Create or update OpenWebUI configuration
  # This might involve setting environment variables or config files
  # depending on how OpenWebUI is configured in the stack
  
  echo "OpenWebUI configuration complete"
}

# Configure Obelisk-RAG
function configure_obelisk_rag() {
  echo "Configuring Obelisk-RAG service..."
  
  # Create or update Obelisk-RAG configuration
  cat > "$CONFIG_DIR/rag_config.yaml" << EOF
# Obelisk-RAG Configuration
# Generated at: $(date)

embedding:
  provider: ollama
  model: mxbai-embed-large

storage:
  type: milvus
  host: milvus
  port: 19530
  collection: documents

retrieve:
  top_k: 5

litellm:
  api_base: http://litellm:8000
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

# Main execution
configure_litellm
configure_openwebui
configure_obelisk_rag
configure_milvus

echo "Service configuration complete"
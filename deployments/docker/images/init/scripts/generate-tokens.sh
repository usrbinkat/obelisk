#!/bin/bash
# Token generation and management for Obelisk services
# Handles creation and propagation of authentication tokens

set -e

echo "Token Generation and Management"
echo "==============================="

# Configuration with environment variable fallbacks
# File takes precedence if it exists, otherwise use environment variable
TOKEN_FILE="${TOKEN_FILE:-/app/tokens/api_tokens.env}"
CONFIG_DIR="${CONFIG_DIR:-/app/config}"

# Check if token file already exists and has tokens
if [ -f "$TOKEN_FILE" ] && grep -q "LITELLM_API_TOKEN=" "$TOKEN_FILE" 2>/dev/null; then
  echo "Loading existing tokens from $TOKEN_FILE"
  source "$TOKEN_FILE"
  LITELLM_TOKEN="${LITELLM_API_TOKEN}"
else
  # Generate new tokens if not found
  LITELLM_TOKEN="${LITELLM_API_TOKEN:-sk-$(openssl rand -hex 12)}"
fi

# Ensure directories exist
mkdir -p "$(dirname "$TOKEN_FILE")" "$CONFIG_DIR"

# Generate tokens
function generate_tokens() {
  echo "Generating authentication tokens..."
  
  # Create tokens file
  cat > "$TOKEN_FILE" << EOF
# Generated tokens for Obelisk services
# Generated at: $(date)
# These tokens are used for service authentication

# LiteLLM API token (sk-prefixed)
LITELLM_API_TOKEN=$LITELLM_TOKEN
EOF

  echo "Tokens generated and saved to $TOKEN_FILE"
}

# Handle OpenAI API key
function handle_openai_api_key() {
  echo "Checking OpenAI API key..."
  
  # If OPENAI_API_KEY is set in environment, add it to tokens file
  if [ -n "${OPENAI_API_KEY}" ]; then
    echo "OpenAI API key found in environment"
    
    # Add to tokens file for other services
    cat >> "$TOKEN_FILE" << EOF

# OpenAI API configuration
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_ORG_ID=${OPENAI_ORG_ID:-}
USE_OPENAI=${USE_OPENAI:-true}
OPENAI_EMBEDDING_MODEL=${OPENAI_EMBEDDING_MODEL:-text-embedding-3-large}
OPENAI_COMPLETION_MODEL=${OPENAI_COMPLETION_MODEL:-gpt-4o}
EOF

    # Validate key if curl is available
    if command -v curl &> /dev/null; then
      echo "Validating OpenAI API key..."
      # Simple validation to check if key might be valid (just checks models endpoint)
      if curl -s -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models | grep -q "data"; then
        echo "OpenAI API key validation successful"
        
        # Model registration will be handled by LiteLLM registration script
        echo "OpenAI model registration will be handled by dedicated script"
        
        # Even if LiteLLM was not available, we continue with initialization
      else
        echo "Warning: OpenAI API key validation failed. Key may be invalid or rate limited."
      fi
    fi
  else
    echo "No OpenAI API key found. Ollama models will be used exclusively."
    
    # Set the USE_OPENAI flag to false in the tokens file
    cat >> "$TOKEN_FILE" << EOF

# OpenAI API configuration (disabled)
USE_OPENAI=false
EOF
  fi
}

# Propagate tokens to services
function propagate_tokens() {
  echo "Propagating tokens to services..."
  
  # Register with LiteLLM API if it's available
  if [ -n "$LITELLM_API_URL" ]; then
    echo "Registering token with LiteLLM API..."
    # Non-blocking check for LiteLLM service availability
    # Reduced wait time (15 seconds max) to avoid long blocking
    MAX_RETRIES=3
    RETRY_INTERVAL=5
    retries=0
    LITELLM_AVAILABLE=false
    
    while [ $retries -lt $MAX_RETRIES ]; do
      # Try multiple ways to check if the API is available (with and without auth)
      # Option 1: Try master key with health endpoint
      if curl -s -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "$LITELLM_API_URL/health" > /dev/null 2>&1; then
        echo "LiteLLM API is available (authenticated with master key)"
        LITELLM_AVAILABLE=true
        break
      # Option 2: Try v1/models endpoint (may not require auth)
      elif curl -s "$LITELLM_API_URL/v1/models" > /dev/null 2>&1; then
        echo "LiteLLM API is available (v1 endpoint)"
        LITELLM_AVAILABLE=true
        break
      # Option 3: Check if API returns 401 (means it's running but needs auth)
      elif curl -s -o /dev/null -w "%{http_code}" "$LITELLM_API_URL/health" | grep -q "401"; then
        echo "LiteLLM API is available (requires authentication)"
        LITELLM_AVAILABLE=true
        break
      fi
      
      echo "Checking if LiteLLM API is available... (attempt $((retries+1)) of $MAX_RETRIES)"
      sleep $RETRY_INTERVAL
      retries=$((retries + 1))
    done
    
    if [ "$LITELLM_AVAILABLE" = false ]; then
      echo "LiteLLM API not immediately available - will continue initialization and register tokens later"
      # Create a marker file to indicate token registration is needed
      mkdir -p "$CONFIG_DIR"
      echo "$LITELLM_TOKEN" > "$CONFIG_DIR/.token_registration_pending"
      # Continue with initialization regardless
    else
      # Register token with LiteLLM API with proper JSON formatting
      # Create a temporary file for the JSON payload to ensure proper formatting
      
      # Determine which models to include based on OpenAI availability
      TOKEN_MODELS="[\"llama3\", \"mxbai-embed-large\"]"
      if [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI:-false}" = "true" ]; then
        TOKEN_MODELS="[\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"]"
        echo "Including OpenAI models in token permissions"
      fi
      
      TEMP_JSON_FILE=$(mktemp)
      cat > "$TEMP_JSON_FILE" << EOF
{
  "key_name": "obelisk-init-token",
  "key": "$LITELLM_TOKEN",
  "metadata": {"description": "Obelisk initialization token"},
  "models": $TOKEN_MODELS,
  "aliases": {},
  "tpm": 100000,
  "rpm": 5000
}
EOF
      
      # Register the token
      # First try with the key/generate endpoint
      RESPONSE=$(curl -s -X POST "$LITELLM_API_URL/key/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
        -d @"$TEMP_JSON_FILE")
      
      REG_RESULT=$?
      echo "Token registration response: $RESPONSE"
      
      # If the response contains "error", try the alternative auth_check endpoint
      if echo "$RESPONSE" | grep -q "error"; then
        echo "Token registration using key/generate failed, trying alternative method..."
        # Some versions of LiteLLM use the /admin/auth_check endpoint instead
        curl -s -X POST "$LITELLM_API_URL/admin/auth_check" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
          -d "{\"api_key\": \"$LITELLM_TOKEN\", \"allow\": true}" > /dev/null
      fi
      
      # Remove temporary file
      rm "$TEMP_JSON_FILE"
      
      if [ $REG_RESULT -eq 0 ]; then
        echo "Token registered with LiteLLM API successfully"
        
        # Verify token was registered by checking if it works
        if curl -s -H "Authorization: Bearer $LITELLM_TOKEN" "$LITELLM_API_URL/models" > /dev/null; then
          echo "Token verified to be working with LiteLLM API"
        else
          echo "Warning: Token registration verification failed"
          echo "Attempting token registration again with alternative method..."
          
          # Try alternative registration method
          # Determine which models to include based on OpenAI availability
          RETRY_TOKEN_MODELS="[\"llama3\", \"mxbai-embed-large\"]"
          if [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI:-false}" = "true" ]; then
            RETRY_TOKEN_MODELS="[\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"]"
          fi
          
          curl -s -X POST "$LITELLM_API_URL/key/generate" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
            -d "{\"key\":\"$LITELLM_TOKEN\",\"metadata\":{\"description\":\"Obelisk initialization token (retry)\"},\"models\":$RETRY_TOKEN_MODELS}" > /dev/null
            
          if curl -s -H "Authorization: Bearer $LITELLM_TOKEN" "$LITELLM_API_URL/models" > /dev/null; then
            echo "Token verified after second registration attempt"
          else
            echo "Warning: Token registration still failed after retry"
          fi
        fi
      else
        echo "Warning: Failed to register token with LiteLLM API"
      fi
    fi
  else
    echo "LiteLLM API URL not set, skipping token registration"
  fi
  
  # Even if LiteLLM was not available, we can continue with initialization
}

# Main execution
generate_tokens
handle_openai_api_key
propagate_tokens

echo "Token management complete"
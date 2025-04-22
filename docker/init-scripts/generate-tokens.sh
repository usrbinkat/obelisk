#!/bin/bash
# Token generation and management for Obelisk services
# Handles creation and propagation of authentication tokens

set -e

echo "Token Generation and Management"
echo "==============================="

# Configuration
TOKEN_FILE="/app/tokens/api_tokens.env"
LITELLM_TOKEN="sk-$(openssl rand -hex 12)"
OPENWEBUI_TOKEN="$(openssl rand -base64 32)"

# Ensure token directory exists
mkdir -p "$(dirname "$TOKEN_FILE")"

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

# OpenWebUI authentication token
OPENWEBUI_AUTH_TOKEN=$OPENWEBUI_TOKEN
EOF

  echo "Tokens generated and saved to $TOKEN_FILE"
}

# Propagate tokens to services
function propagate_tokens() {
  echo "Propagating tokens to services..."
  
  # Register with LiteLLM API if it's available
  if [ -n "$LITELLM_API_URL" ]; then
    echo "Registering token with LiteLLM API..."
    # Wait for LiteLLM service to be available
    MAX_RETRIES=30
    RETRY_INTERVAL=5
    retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
      if curl -s "$LITELLM_API_URL/health" > /dev/null 2>&1; then
        echo "LiteLLM API is available"
        break
      fi
      
      echo "Waiting for LiteLLM API to be available... (retry $retries of $MAX_RETRIES)"
      sleep $RETRY_INTERVAL
      retries=$((retries + 1))
    done
    
    if [ $retries -eq $MAX_RETRIES ]; then
      echo "Warning: LiteLLM API did not become available. Token registration skipped."
    else
      # Register token with LiteLLM API with proper JSON formatting
      # Create a temporary file for the JSON payload to ensure proper formatting
      TEMP_JSON_FILE=$(mktemp)
      cat > "$TEMP_JSON_FILE" << EOF
{
  "key": "$LITELLM_TOKEN",
  "metadata": {"description": "Obelisk initialization token"}
}
EOF
      
      # Register the token
      curl -s -X POST "$LITELLM_API_URL/key/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
        -d @"$TEMP_JSON_FILE" > /dev/null
      
      REG_RESULT=$?
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
          curl -s -X POST "$LITELLM_API_URL/key/generate" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
            -d "{\"key\":\"$LITELLM_TOKEN\",\"metadata\":{\"description\":\"Obelisk initialization token (retry)\"}}" > /dev/null
            
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
}

# Main execution
generate_tokens
propagate_tokens

echo "Token management complete"
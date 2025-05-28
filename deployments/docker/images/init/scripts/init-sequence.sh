#!/bin/bash
# Master initialization controller for Obelisk container startup
# Manages the startup sequence, token generation, and model management

set -e

echo "Obelisk Container Initialization"
echo "================================"
echo "Starting initialization sequence at $(date)"

sleep 20

# Script locations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
TOKEN_SCRIPT="${SCRIPT_DIR}/generate-tokens.sh"
MODELS_SCRIPT="${SCRIPT_DIR}/download-models.sh"
CONFIG_SCRIPT="${SCRIPT_DIR}/configure-services.sh"
LITELLM_REGISTRATION_SCRIPT="${SCRIPT_DIR}/register-litellm-models.sh"

# Initialization steps
function check_dependencies() {
	echo "Checking service dependencies..."
	
	# Check LiteLLM is ready
	local litellm_retries=0
	while [ $litellm_retries -lt 10 ]; do
		if curl -s -f http://litellm:4000/health >/dev/null 2>&1 || curl -s http://litellm:4000/v1/models -H "Authorization: Bearer sk-1234" >/dev/null 2>&1; then
			echo "✓ LiteLLM is ready"
			break
		fi
		echo "Waiting for LiteLLM... (attempt $((litellm_retries + 1))/10)"
		sleep 3
		litellm_retries=$((litellm_retries + 1))
	done
	
	# Check Ollama is ready
	local ollama_retries=0
	while [ $ollama_retries -lt 10 ]; do
		if curl -s -f http://ollama:11434/api/tags >/dev/null 2>&1; then
			echo "✓ Ollama is ready"
			break
		fi
		echo "Waiting for Ollama... (attempt $((ollama_retries + 1))/10)"
		sleep 3
		ollama_retries=$((ollama_retries + 1))
	done
	
	# Check Milvus is ready
	local milvus_retries=0
	while [ $milvus_retries -lt 10 ]; do
		if curl -s -f http://milvus:19530/v1/vector/collections >/dev/null 2>&1; then
			echo "✓ Milvus is ready"
			break
		fi
		echo "Waiting for Milvus... (attempt $((milvus_retries + 1))/10)"
		sleep 3
		milvus_retries=$((milvus_retries + 1))
	done
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

function register_litellm_models() {
	echo "Registering models with LiteLLM..."
	# Run the LiteLLM model registration script
	if [ -f "$LITELLM_REGISTRATION_SCRIPT" ]; then
		chmod +x "$LITELLM_REGISTRATION_SCRIPT"
		"$LITELLM_REGISTRATION_SCRIPT"
	else
		echo "Warning: LiteLLM model registration script not found"
	fi
}


function verify_initialization() {
	echo "Verifying initialization..."
	local verification_warnings=0

	# Check if token file exists
	if [ ! -f "/app/tokens/api_tokens.env" ]; then
		echo "Error: Token file not found. Initialization may have failed."
		return 1
	fi

	# Source token file to get token values
	source "/app/tokens/api_tokens.env"

	# Check for OpenAI API key and print status
	if [ -n "${OPENAI_API_KEY}" ]; then
		echo "OpenAI API key found, OpenAI integration will be enabled"
		echo "OpenAI completion model: ${OPENAI_COMPLETION_MODEL:-gpt-4o}"
		echo "OpenAI embedding model: ${OPENAI_EMBEDDING_MODEL:-text-embedding-3-large}"

		# Store OpenAI configuration for later use in model registration
		mkdir -p "/app/config"
		cat >"/app/config/.openai_registration_pending" <<EOF
OPENAI_API_KEY="${OPENAI_API_KEY}"
OPENAI_EMBEDDING_MODEL="${OPENAI_EMBEDDING_MODEL:-text-embedding-3-large}"
OPENAI_COMPLETION_MODEL="${OPENAI_COMPLETION_MODEL:-gpt-4o}"
EOF
	else
		echo "No OpenAI API key found. Ollama models will be used exclusively."
	fi

	# Check if Ollama API is accessible
	if ! curl -s "$OLLAMA_API_URL/api/tags" >/dev/null; then
		echo "Warning: Ollama API is not accessible. Some features may be limited."
		verification_warnings=$((verification_warnings + 1))
	else
		echo "Ollama API is accessible"
	fi

	# Check LiteLLM API with non-blocking approach
	# This is now a warning rather than an error
	echo "Checking LiteLLM API accessibility..."

	# Try multiple ways to check if API is available
	if curl -s --connect-timeout 2 -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "$LITELLM_API_URL/health" >/dev/null 2>&1; then
		echo "LiteLLM API is accessible (authenticated with master key)"

		# Check if token works
		if curl -s --connect-timeout 2 -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models" >/dev/null 2>&1; then
			echo "LiteLLM API token authentication successful"

			# Extra check for token permissions (models vs wildcard "*")
			local models_response=$(curl -s -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models")
			if echo "$models_response" | grep -q "\"id\":\"\\*\""; then
				echo "Warning: API token only has wildcard access. Token permissions will be fixed in final step."
				verification_warnings=$((verification_warnings + 1))
			else
				echo "API token has specific model permissions. Good!"
			fi
		else
			echo "Warning: LiteLLM API token authentication failed. Will attempt registration during service configuration."
			verification_warnings=$((verification_warnings + 1))

			# Mark token for registration in next phase
			mkdir -p "/app/config"
			echo "$LITELLM_API_TOKEN" >"/app/config/.token_registration_needed"
		fi
	elif curl -s --connect-timeout 2 "$LITELLM_API_URL/v1/models" >/dev/null 2>&1; then
		echo "LiteLLM API is accessible (v1 endpoint)"
		verification_warnings=$((verification_warnings + 1))
	elif curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" "$LITELLM_API_URL/health" | grep -q "401"; then
		echo "LiteLLM API is accessible (requires authentication)"

		# Mark token for registration in next phase
		mkdir -p "/app/config"
		echo "$LITELLM_API_TOKEN" >"/app/config/.token_registration_needed"
		verification_warnings=$((verification_warnings + 1))
	else
		echo "Warning: LiteLLM API is not accessible. Token verification skipped."
		verification_warnings=$((verification_warnings + 1))
		# We don't return error - the LiteLLM container might still be starting up
	fi

	# All critical checks passed, report warnings
	if [ $verification_warnings -gt 0 ]; then
		echo "Verification completed with $verification_warnings warnings"
	else
		echo "Verification completed successfully"
	fi
	return 0
}

# Function to check if we need to verify token permissions one final time
function final_token_permission_check() {
	echo "=========================================="
	echo "Running final token permission check..."

	# Source token file to get token values if it exists
	if [ -f "/app/tokens/api_tokens.env" ]; then
		source "/app/tokens/api_tokens.env"
	else
		echo "Token file not found, skipping final token check"
		return 1
	fi

	# Check if LiteLLM API is accessible
	if ! curl -s --connect-timeout 2 -H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" "$LITELLM_API_URL/health" >/dev/null 2>&1; then
		echo "LiteLLM API not accessible, skipping final token check"
		return 1
	fi

	# Check if the API token has the correct permissions
	echo "Checking token permissions on models endpoint..."

	local models_response=$(curl -s -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models")
	echo "Raw models response: $models_response"

	# Check if we have OpenAI models when they should be available
	local needs_update=false
	if echo "$models_response" | grep -q "\"id\":\"\\*\""; then
		echo "Token has wildcard permissions, needs update"
		needs_update=true
	elif [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI:-false}" = "true" ]; then
		# Check if OpenAI models are present when they should be
		if ! (echo "$models_response" | grep -q "gpt-4o") || ! (echo "$models_response" | grep -q "text-embedding-3-large"); then
			echo "OpenAI models missing from token permissions, needs update"
			needs_update=true
		fi
	fi
	
	if [ "$needs_update" = true ]; then
		echo "API token needs permission update. Running one final update..."

		# Force a token permission update
		local model_list="[\"llama3\", \"mxbai-embed-large\"]"

		# Add OpenAI models if they should be available
		if [ -n "${OPENAI_API_KEY}" ] || [ "${USE_OPENAI:-false}" = "true" ]; then
			model_list="[\"llama3\", \"mxbai-embed-large\", \"gpt-4o\", \"text-embedding-3-large\"]"
		fi

		# Update permissions
		echo "Sending token update request with model_list: $model_list"
		local update_response=$(curl -v -X POST "$LITELLM_API_URL/key/update" \
			-H "Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-1234}" \
			-H "Content-Type: application/json" \
			-d "{\"key\": \"$LITELLM_API_TOKEN\", \"models\": $model_list}")

		echo "Update response: $update_response"

		# Verify the update worked
		local verify_response=$(curl -s -H "Authorization: Bearer $LITELLM_API_TOKEN" "$LITELLM_API_URL/models")
		echo "New models response: $verify_response"

		echo "Final permission update complete"
	else
		echo "API token permissions are already correctly set"
	fi
}

# Main initialization sequence
check_dependencies
generate_tokens
configure_models
configure_services
register_litellm_models  # Register models with LiteLLM
verify_initialization

# Final token permission check as the very last step
# This ensures permissions are set correctly even if missed in earlier steps
final_token_permission_check

echo "Initialization complete at $(date)"
echo "================================"

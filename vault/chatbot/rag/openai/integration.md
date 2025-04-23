# OpenAI Model Integration

This document covers integrating OpenAI models with Obelisk's RAG system.

## Supported Models

Obelisk RAG supports the following OpenAI models for embedding and completion tasks:

### Model Datasheets

| Feature                     | GPT-4o                                | GPT-4.1                              | text-embedding-3-large                 |
| --------------------------- | ------------------------------------- | ------------------------------------ | -------------------------------------- |
| **Description**             | Fast, intelligent, flexible GPT model | Flagship GPT model for complex tasks | Most capable embedding model           |
| **Use in Obelisk**          | Completion generation                 | Completion generation                | Document and query embedding           |
| **Pricing (per 1M tokens)** | $2.50 input / $10.00 output           | $2.00 input / $8.00 output           | $0.13                                  |
| **Context Window**          | 128,000 tokens                        | 1,047,576 tokens                     | N/A                                    |
| **Max Output Tokens**       | 16,384                                | 32,768                               | N/A                                    |
| **Knowledge Cutoff**        | Sep 30, 2023                          | May 31, 2024                         | Not applicable                         |
| **Dimensions**              | N/A                                   | N/A                                  | 3,072                                  |
| **Rate Limits (TPM)**       | Tier 1: 30,000<br>Tier 2: 450,000     | Tier 1: 30,000<br>Tier 2: 450,000    | Tier 1: 1,000,000<br>Tier 2: 1,000,000 |

## Configuration

When an OpenAI API key is detected in the environment, Obelisk RAG can optionally use these models instead of local Ollama models, providing enhanced performance and capabilities especially for development environments without GPU access.

### Environment Variables

To enable OpenAI models, set the following environment variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
OPENAI_ORG_ID=your_org_id                      # For enterprise users
USE_OPENAI=true                                # Force using OpenAI (defaults to true when key exists)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # Default embedding model
OPENAI_COMPLETION_MODEL=gpt-4o                 # Default completion model
EMBEDDING_PROVIDER=openai                      # Set embedding provider (ollama or openai)
COMPLETION_PROVIDER=openai                     # Set completion provider (ollama or openai)
```

### Docker Compose Usage

When using docker-compose, you can provide the OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key docker-compose up
```

## Technical Implementation

The OpenAI integration is implemented through several components:

### 1. LiteLLM Configuration

LiteLLM acts as a middleware layer that can route requests to either OpenAI or Ollama models. The configuration in `litellm-config.yaml` includes:

- OpenAI model definitions (gpt-4o, text-embedding-3-large)
- Model aliases for simpler referencing
- Fallback mechanisms to ensure graceful degradation to Ollama models when needed
- Prioritized embedding model list

```yaml
# Model routing with fallbacks
fallbacks: [
  {
    "model": "openai/gpt-4o",
    "fallback_model": "ollama/llama3"
  },
  {
    "model": "openai/text-embedding-3-large", 
    "fallback_model": "ollama/mxbai-embed-large"
  }
]
```

### 2. Initialization Process

During container initialization:

1. The `generate-tokens.sh` script checks for an OpenAI API key and adds it to the shared tokens file
2. The `configure-services.sh` script creates configurations for LiteLLM and Obelisk-RAG based on the presence of the API key
3. Models are automatically prioritized based on availability

### 3. Fallback Mechanism

If the OpenAI API is unavailable or rate-limited:

1. LiteLLM will automatically route requests to the specified fallback model (Ollama)
2. This ensures system reliability even when external API services are unavailable
3. No code changes are needed as the fallback is handled at the routing layer

## Testing the Integration

1. Start the Obelisk stack with your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key docker-compose up
   ```

2. Access the OpenWebUI interface at http://localhost:8080

3. Create a new chat and select LiteLLM as the provider

4. In the model dropdown, you should see OpenAI models (gpt-4o)

5. Test embedding functionality by creating a new RAG collection and uploading a document

## Troubleshooting

### API Key Issues

If your OpenAI API key is invalid or has insufficient permissions:

1. Check the logs in the `litellm` container for API-related errors
2. Verify the key works using our testing script:
   ```bash
   poetry run python /workspaces/obelisk/hack/test_litellm_openai.py
   ```
3. Ensure your OpenAI account has billing enabled for API access

### Fallback Issues

If fallback to Ollama models isn't working:

1. Verify Ollama models are downloaded and available
2. Check the fallback configuration in `config/litellm_config.yaml`
3. Examine the logs for routing-related errors

## Limitations

- Embedding caching is not yet implemented (planned for future releases)
- Rate limiting for OpenAI API is not currently enforced
- Cost optimization features are not yet available

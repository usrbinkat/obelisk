# Open WebUI Configuration

Open WebUI provides a powerful interface for interacting with AI models through Ollama. This guide explains how to configure and customize it for use with Obelisk.

## Basic Configuration

Open WebUI is configured through environment variables in the `docker-compose.yaml` file:

```yaml
open-webui:
  environment:
    - MODEL_DOWNLOAD_DIR=/models
    - OLLAMA_API_BASE_URL=http://ollama:11434
    - OLLAMA_API_URL=http://ollama:11434
    - LOG_LEVEL=debug
```

These settings establish connection to the Ollama service and configure basic behavior.

## User Interface Features

Open WebUI provides several key features:

### Chat Interface

The main chat interface allows:

- Conversational interactions with AI models
- Code highlighting and formatting
- File attachment and reference
- Conversation history and management

### Model Selection

Users can select from available models with options for:

- Parameter adjustment (temperature, top_p, etc.)
- Context length configuration
- Model-specific presets

### Prompt Templates

Create and manage prompt templates to:

- Define consistent AI behavior
- Create specialized assistants for different tasks
- Share templates with your team

## Advanced Configuration

### Custom Branding

To customize the Open WebUI appearance for your Obelisk deployment:

1. Mount a custom assets volume:

```yaml
open-webui:
  volumes:
    - ./custom-webui-assets:/app/public/custom
```

2. Create the following files:
   - `custom-webui-assets/logo.png` - Main logo
   - `custom-webui-assets/logo-dark.png` - Logo for dark mode
   - `custom-webui-assets/favicon.png` - Browser tab icon
   - `custom-webui-assets/background.png` - Login page background

### Authentication

Enable authentication for multi-user setups:

```yaml
open-webui:
  environment:
    - ENABLE_USER_AUTH=true
    - DEFAULT_USER_EMAIL=admin@example.com
    - DEFAULT_USER_PASSWORD=strongpassword
```

### API Integration

Open WebUI can be integrated with other services via its API:

```yaml
open-webui:
  environment:
    - ENABLE_API=true
    - API_KEY=your-secure-api-key
```

This allows programmatic access to model interactions.

## Persistent Data

Open WebUI stores its data in Docker volumes:

- `data`: Conversations, user settings, and app data
- `open-webui`: Configuration files
- `models`: Shared with Ollama for model storage

These volumes persist across container restarts and updates.

## Customizing for Documentation Support

To optimize Open WebUI for documentation support:

1. Create a specialized preset:
   - Navigate to Settings > Presets
   - Create a new preset named "Documentation Helper"
   - Configure with appropriate temperature (0.3-0.5) and parameters
   - Set system prompt to documentation-specific instructions

2. Create documentation-focused prompt templates:
   - "Explain this concept"
   - "How do I configure X"
   - "Troubleshoot this error"

3. Enable RAG (Retrieval Augmented Generation):
   - Upload documentation files through the interface
   - Enable "Knowledge Base" feature
   - Configure vector storage settings

## Troubleshooting

Common issues and solutions:

1. **Connection errors**:
   - Verify network settings in docker-compose
   - Check that Ollama service is running

2. **Authentication problems**:
   - Reset password using the API
   - Check environment variables for auth settings

3. **Performance issues**:
   - Adjust interface settings for slower devices
   - Configure page size and context window appropriately

## Resources

- [Open WebUI GitHub Repository](https://github.com/open-webui/open-webui)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
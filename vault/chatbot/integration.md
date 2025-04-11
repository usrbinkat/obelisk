# Integrating AI Chat with Documentation

Learn how to effectively integrate the AI chatbot capabilities with your Obelisk documentation site.

## Basic Integration

The Obelisk stack includes Ollama and Open WebUI running alongside your documentation server. Users can access:

- Documentation site: `http://localhost:8000`
- Chat interface: `http://localhost:8080`

This separation allows flexible deployment options while keeping the services connected through a shared Docker network.

## Advanced Integration Options

### Embedding Chat in Documentation

To embed the chat interface directly within your documentation pages:

1. Create a custom HTML template by modifying `vault/overrides/main.html`:

```html
{% extends "base.html" %}

{% block content %}
  {{ super() }}
  
  <!-- Chat button in corner -->
  <div class="chat-launcher">
    <button class="chat-button" onclick="toggleChat()">
      <span class="material-icons">chat</span>
    </button>
  </div>
  
  <!-- Chat iframe container -->
  <div id="chat-container" class="hidden">
    <div class="chat-header">
      <span>Obelisk AI Assistant</span>
      <button onclick="toggleChat()">×</button>
    </div>
    <iframe id="chat-frame" src="http://localhost:8080"></iframe>
  </div>
{% endblock %}

{% block extrahead %}
  {{ super() }}
  <style>
    .chat-launcher {
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 999;
    }
    .chat-button {
      background: var(--md-primary-fg-color);
      color: white;
      border: none;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      cursor: pointer;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    #chat-container {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 400px;
      height: 600px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.2);
      z-index: 1000;
      display: flex;
      flex-direction: column;
    }
    .hidden {
      display: none !important;
    }
    .chat-header {
      padding: 10px;
      background: var(--md-primary-fg-color);
      color: white;
      border-radius: 10px 10px 0 0;
      display: flex;
      justify-content: space-between;
    }
    #chat-frame {
      flex: 1;
      border: none;
      border-radius: 0 0 10px 10px;
    }
  </style>
  <script>
    function toggleChat() {
      const container = document.getElementById('chat-container');
      container.classList.toggle('hidden');
    }
  </script>
{% endblock %}
```

2. Add custom CSS in `vault/stylesheets/extra.css` if needed

3. Update the JavaScript in `vault/javascripts/extra.js` to handle chat functionality

### Training on Documentation Content

For more contextual responses about your documentation:

1. Extract your documentation content:

```bash
# Create a training data directory
mkdir -p ~/obelisk-training-data

# Use a script to extract content from markdown files
find /workspaces/obelisk/vault -name "*.md" -exec sh -c 'cat "$1" >> ~/obelisk-training-data/docs.txt' sh {} \;
```

2. Create a new Modelfile with your documentation context:

```
FROM mistral

# Include documentation context
SYSTEM You are an AI assistant for the Obelisk documentation system. 
SYSTEM You specialize in helping users understand how to use Obelisk to convert their Obsidian vaults to MkDocs Material Theme sites.
SYSTEM You should give concise, helpful answers based on the official documentation.

# Reference documentation content
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
```

3. Build a custom model:

```bash
docker exec -it ollama ollama create obelisk-docs -f /path/to/Modelfile
```

## Security Considerations

When integrating AI chat with your documentation:

1. **Access Control**:
   - Consider securing the chat interface with authentication
   - Limit network access to the Ollama API

2. **Content Filtering**:
   - Configure model parameters to avoid harmful outputs
   - Set appropriate system prompts to guide model behavior

3. **Privacy**:
   - Be aware that conversations may be stored in the `data` volume
   - Configure data retention policies in Open WebUI

4. **Deployment**:
   - For public deployments, consider using a reverse proxy
   - Implement rate limiting to prevent abuse

## Best Practices

For effective documentation-chat integration:

1. **Clear Distinction**: Make it obvious when users are interacting with AI vs. reading documentation
2. **Contextual Linking**: Have the AI provide links to relevant documentation pages
3. **Feedback Loop**: Collect user feedback on AI responses to improve over time
4. **Fallbacks**: Provide easy ways for users to access human help when AI can't solve a problem
5. **Monitoring**: Track usage patterns to identify documentation gaps
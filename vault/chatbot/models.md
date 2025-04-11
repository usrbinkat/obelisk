# AI Models Configuration

This guide explains how to configure and use AI models with the Ollama and Open WebUI integration in Obelisk.

## Model Management

### Pulling Models

Models can be pulled through the Open WebUI interface or directly using Ollama:

```bash
# Using Ollama CLI
docker exec -it ollama ollama pull mistral

# List available models
docker exec -it ollama ollama list
```

### Model Storage

Models are stored in persistent Docker volumes:

- `models`: Shared volume for model files
- `ollama`: Ollama-specific configuration and model registry

This ensures your models persist between container restarts.

## Recommended Models

Here are some recommended models to use with the Obelisk chatbot integration:

| Model | Size | Description | Command |
| ----- | ---- | ----------- | ------- |
| Llama 2 | 7B | Meta's general purpose model | `ollama pull llama2` |
| Mistral | 7B | High-performance open model | `ollama pull mistral` |
| Phi-2 | 2.7B | Microsoft's compact model | `ollama pull phi` |
| Gemma | 7B | Google's lightweight model | `ollama pull gemma:7b` |
| CodeLlama | 7B | Code-specialized model | `ollama pull codellama` |

For documentation-specific tasks, consider models that excel at knowledge retrieval and explanation.

## Custom Model Configuration

You can create custom model configurations using Modelfiles:

1. Create a Modelfile:

```
FROM mistral
SYSTEM You are a helpful documentation assistant for the Obelisk project.
```

2. Build the custom model:

```bash
docker exec -it ollama ollama create obelisk-assistant -f Modelfile
```

3. Use the custom model in Open WebUI.

## Hardware Requirements

Model performance depends on available hardware:

- **7B models**: Minimum 8GB VRAM (GPU) or 16GB RAM (CPU)
- **13B models**: Minimum 16GB VRAM (GPU) or 32GB RAM (CPU)
- **70B models**: Minimum 80GB VRAM (GPU) or distributed setup

For optimal performance, use GPU acceleration with the NVIDIA Container Toolkit.

## Quantization Options

Ollama supports various quantization levels to balance performance and resource usage:

| Quantization | Quality | Memory Usage | Example |
| ------------ | ------- | ------------ | ------- |
| F16 | Highest | Highest | `ollama pull mistral:latest` |
| Q8_0 | High | Medium | `ollama pull mistral:8b-q8_0` |
| Q4_K_M | Medium | Low | `ollama pull mistral:8b-q4_k_m` |
| Q4_0 | Lowest | Lowest | `ollama pull mistral:8b-q4_0` |

Choose quantization based on your hardware capabilities and quality requirements.

## Troubleshooting

Common issues and solutions:

1. **Out of memory errors**:
   - Try a smaller model or higher quantization level
   - Reduce context length in Open WebUI settings

2. **Slow responses**:
   - Ensure GPU acceleration is properly configured
   - Check for other processes using GPU resources

3. **Model not found**:
   - Verify the model was pulled correctly
   - Check network connectivity to model repositories

For more troubleshooting, consult the [Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md).
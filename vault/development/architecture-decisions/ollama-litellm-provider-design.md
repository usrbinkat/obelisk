# Ollama-LiteLLM Provider Architecture Design Document

> **Status**: Implemented and Refined (PR #39, May 2025)  
> **Purpose**: Design document for the dual-provider architecture with LiteLLM API gateway  
> **Originally**: TASK.ollama-litellm-provider-architecture.md  
> **Note**: Updated to reflect the refined architecture where all completions route through the OpenAI-compatible LiteLLM API while maintaining both providers for different capabilities

## Executive Summary

This document presents a comprehensive architectural design for integrating Ollama and LiteLLM as model providers in the Obelisk RAG system. Based on deep technical research of both libraries, this design addresses long-term maintainability, operational excellence, and optimal user experience while preserving the local-first philosophy of Obelisk.

**Key Research Findings:**
- LiteLLM SDK uses stateless `completion()` and `embedding()` functions with automatic provider detection via model name prefixes
- Ollama-python provides unique model management operations (`pull`, `push`, `create`, `delete`) and hardware configuration options not available through LiteLLM
- LiteLLM adds minimal overhead through parameter mapping, prompt formatting, and response normalization (tracked via `litellm_overhead_latency_metric`)
- The LiteLLM Proxy Server offers enterprise features (routing strategies, rate limiting, observability) beyond the SDK capabilities

**Refined Architecture (Current Implementation):**
- All chat completions are routed through the OpenAI-compatible LiteLLM API endpoint
- Provider factory pattern maintains both LiteLLMProvider and OllamaProvider classes
- OllamaProvider is used for hardware tuning and model management operations
- LiteLLMProvider handles all completion requests, even for local Ollama models
- This approach unifies the completion API while preserving hardware control capabilities

## Table of Contents

1. [Technical Context](#technical-context)
2. [Architecture Overview](#architecture-overview)
3. [Provider Capabilities Analysis](#provider-capabilities-analysis)
4. [Design Decisions](#design-decisions)
5. [Implementation Architecture](#implementation-architecture)
6. [Operational Considerations](#operational-considerations)
7. [Migration Strategy](#migration-strategy)
8. [Future Roadmap](#future-roadmap)

## Technical Context

### Obelisk's Core Mission
Obelisk is a local-first RAG system designed to transform Obsidian vaults into AI-powered documentation sites. The architecture must prioritize:
- Local model performance and control
- Hardware optimization capabilities
- Minimal operational overhead
- Cloud provider flexibility when needed

### Current State
- **LiteLLM Provider**: Implemented with direct `completion()` and `embedding()` calls
- **Ollama Provider**: Uses `langchain-ollama` for direct server access
- **OpenAI Provider**: Fallback option for cloud deployments
- **Configuration**: Environment-based with provider selection support

## Architecture Overview

### Unified API with Dual-Provider Support

The refined architecture routes all completions through LiteLLM's OpenAI-compatible API while maintaining both providers for their unique capabilities:

```mermaid
graph TD
    A[User Request] --> B[Provider Factory]
    B --> C{Request Type}
    
    C -->|Completions/Chat| D[LiteLLM Provider]
    C -->|Hardware Config| E[Ollama Provider]
    C -->|Model Management| E
    
    D --> F[LiteLLM API Gateway :4000]
    F --> G[Ollama Backend]
    F --> H[OpenAI Backend]
    F --> I[Anthropic Backend]
    F --> J[Other Backends]
    
    E --> K[Direct Ollama API :11434]
    
    G --> L[Local Models]
    K --> L
```

**Key Architecture Points:**
- All completion requests go through LiteLLM API (port 4000)
- Ollama provider retained for hardware tuning and model operations
- Provider factory intelligently selects based on operation type
- Unified OpenAI-compatible interface for all completions

### Provider Selection Logic (Refined)

```python
class RefinedProviderSelector:
    """Provider selection based on operation type, not model."""
    
    def select_provider(self, operation_type: str, **kwargs) -> ProviderType:
        """
        Select provider based on operation type:
        - All completions/chat -> LiteLLM API
        - Hardware config/model management -> Direct Ollama
        """
        if operation_type in ["completion", "chat", "embedding"]:
            # ALL completions go through LiteLLM API
            return ProviderType.LITELLM
            
        elif operation_type in ["model_pull", "model_push", "model_create", 
                                "model_delete", "hardware_config"]:
            # Model management and hardware ops use direct Ollama
            return ProviderType.OLLAMA
            
        else:
            # Default to LiteLLM for unknown operations
            return ProviderType.LITELLM
    
    def get_completion_url(self, model_name: str) -> str:
        """All completions use LiteLLM API endpoint."""
        return "http://litellm:4000/v1/chat/completions"
```

## Provider Capabilities Analysis

### Ollama Direct Access (via ollama-python)

#### Strengths
1. **Performance**
   - Zero proxy overhead (direct HTTP connection to Ollama server)
   - Native streaming without buffering
   - Direct API access without abstraction layers
   - Optimal for high-throughput local workloads

2. **Model Management** (Unique to Direct Access)
   - `pull()`: Download models with streaming progress tracking
   - `push()`: Upload models to registries with progress updates
   - `create()`: Create custom models with quantization options, templates, and parameters
   - `delete()`: Remove local models
   - `list()`: Retrieve all available models
   - `copy()`: Duplicate models with new names
   - `show()`: Display detailed model information (Modelfile, template, parameters)
   - `create_blob()`: Upload binary blobs for model creation

3. **Hardware Control** (via Options)
   - `num_gpu`: Number of GPUs to use
   - `main_gpu`: Specify primary GPU
   - `num_thread`: CPU thread count
   - `low_vram`: Enable low VRAM usage mode
   - `numa`: NUMA support
   - `num_ctx`: Context window size
   - `num_batch`: Batch size for processing

4. **Advanced Features**
   - Process monitoring via `ps()` method
   - Both synchronous (`Client`) and asynchronous (`AsyncClient`) interfaces
   - Type-safe API with Pydantic models
   - Direct multimodal support (images with text)
   - Structured output control (JSON format)

#### Limitations
- No built-in retry mechanisms
- No automatic fallback to other providers
- Limited to Ollama-compatible models
- No unified telemetry/monitoring

### LiteLLM SDK and Proxy

#### SDK Strengths
1. **Provider Abstraction**
   - 100+ LLM providers through unified interface
   - Automatic provider detection via model prefixes (e.g., "ollama/llama3", "azure/gpt-4")
   - Standardized request/response formats
   - Stateless architecture with `completion()` and `embedding()` functions
   - Async support via `acompletion()` and `aembedding()`

2. **Reliability Features**
   - Built-in retry mechanisms with `max_retries` parameter
   - Router class for advanced features (when initialized)
   - Rate limit handling
   - Exponential backoff support

3. **Integration Simplicity**
   - Direct function calls without client instantiation
   - Configuration via environment variables, direct parameters, or global settings
   - Automatic parameter mapping for different providers
   - OpenAI-compatible response format

#### Proxy Server Additional Features
1. **Advanced Routing Strategies**
   - `simple-shuffle`: Random model selection
   - `least-busy`: Routes to model with fewest ongoing calls
   - `usage-based-routing`: Based on TPM/RPM
   - `latency-based-routing`: Lowest latency selection
   - `tag-filtering`: Request routing based on tags

2. **Enterprise Features**
   - Virtual key management with RPM/TPM limits
   - Budget tracking per user/key/model/team
   - Custom pricing configuration
   - Authentication (API keys, JWT, OAuth2)
   - Admin UI for management

3. **Observability**
   - Prometheus metrics (`/metrics` endpoint)
   - Integration with Langfuse, OpenTelemetry, Datadog
   - Detailed latency tracking: `litellm_overhead_latency_metric`
   - Spend logs and transaction history

#### Limitations
- No model management operations (pull, push, create, delete)
- No hardware-specific configurations (GPU allocation, memory settings)
- Added latency from parameter mapping and response normalization
- Ollama function calling adapted to JSON format (not native)

## Design Decisions

### 1. Unified API with Dual Provider Support (Refined)

**Decision**: Route all completions through LiteLLM API while maintaining both provider classes.

**Rationale**:
- Provides consistent OpenAI-compatible API for all completions
- Preserves Ollama's unique hardware tuning capabilities
- Simplifies client integration (single endpoint)
- Enables unified monitoring and observability
- Maintains flexibility for provider-specific operations

**Implementation**:
- All completion requests -> LiteLLM API (port 4000)
- Hardware config/model management -> Direct Ollama (port 11434)
- Provider factory selects based on operation type, not model

### 2. Operation-Based Provider Selection (Refined)

**Decision**: Select provider based on operation type, not model name.

**Rationale**:
- Clear separation of concerns between providers
- Consistent API surface for all completions
- Preserves hardware control where needed
- Simplifies client code (no model-based routing logic)

**Implementation**:
```python
# Completion operations - ALWAYS use LiteLLM API
response = await rag_service.query("What is RAG?", model="llama3")
# Routes to: http://litellm:4000/v1/chat/completions

# Hardware configuration - Direct Ollama
await ollama_provider.configure_hardware({
    "num_gpu": 2,
    "num_thread": 8,
    "gpu_memory_fraction": 0.9
})
# Uses: http://ollama:11434 directly

# Model management - Direct Ollama
await ollama_provider.pull_model("llama3:70b")
# Uses: http://ollama:11434/api/pull
```

### 3. Unified Configuration Model

**Decision**: Single configuration system with provider-specific sections.

**Rationale**:
- Simplifies configuration management
- Enables easy provider switching
- Supports environment-based deployment

**Structure**:
```yaml
# config.yaml
providers:
  default: smart  # smart, ollama, litellm
  
  ollama:
    url: http://localhost:11434
    default_model: llama3
    hardware:
      num_gpu: -1  # Use all available GPUs
      num_thread: 8
  
  litellm:
    api_base: http://litellm:4000
    api_key: ${LITELLM_API_KEY}
    retry_config:
      num_retries: 3
      retry_after: 5
    router_settings:
      routing_strategy: usage-based-routing-v2
  
  fallback_chain:
    - ollama
    - litellm
    - openai
```

### 4. Feature-Based Provider Capabilities

**Decision**: Expose provider capabilities through a unified interface.

**Rationale**:
- Allows feature detection at runtime
- Enables graceful degradation
- Supports future provider additions

**Implementation**:
```python
class ProviderCapabilities:
    """Runtime capability detection for providers."""
    
    supports_streaming: bool = True
    supports_model_management: bool = False
    supports_hardware_config: bool = False
    supports_retry: bool = False
    supports_fallback: bool = False
    supports_load_balancing: bool = False
    
    @classmethod
    def for_provider(cls, provider_type: ProviderType) -> "ProviderCapabilities":
        if provider_type == ProviderType.OLLAMA:
            return cls(
                supports_streaming=True,
                supports_model_management=True,
                supports_hardware_config=True,
                supports_retry=False,
                supports_fallback=False,
                supports_load_balancing=False
            )
        elif provider_type == ProviderType.LITELLM:
            return cls(
                supports_streaming=True,
                supports_model_management=False,
                supports_hardware_config=False,
                supports_retry=True,
                supports_fallback=True,
                supports_load_balancing=True
            )
```

## Implementation Architecture

### 1. Provider Factory Enhancement

```python
class EnhancedProviderFactory:
    """Enhanced factory with smart provider selection and capability detection."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.selector = SmartProviderSelector()
        self._provider_cache: Dict[str, ModelProvider] = {}
    
    def get_provider(
        self, 
        model: Optional[str] = None,
        provider_hint: Optional[ProviderType] = None,
        **kwargs
    ) -> ModelProvider:
        """Get appropriate provider with smart selection."""
        # Allow explicit provider selection
        if provider_hint:
            provider_type = provider_hint
        else:
            # Smart selection based on model and config
            provider_type = self.selector.select_provider(
                model or self.config.get("default_model"),
                {**self.config, **kwargs}
            )
        
        # Cache providers for reuse
        cache_key = f"{provider_type}:{model}"
        if cache_key not in self._provider_cache:
            provider = self._create_provider(provider_type)
            self._provider_cache[cache_key] = provider
        
        return self._provider_cache[cache_key]
```

### 2. Extended Ollama Provider

```python
from ollama import AsyncClient, Client
from typing import AsyncIterator

class ExtendedOllamaProvider(OllamaProvider):
    """Enhanced Ollama provider with additional operational features."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.hardware_config = config.get("hardware", {})
        self._model_cache: Dict[str, bool] = {}
        # Initialize both sync and async clients
        self.client = Client(host=self.api_base)
        self.async_client = AsyncClient(host=self.api_base)
    
    async def ensure_model(self, model: str) -> None:
        """Ensure model is available locally, pulling if necessary."""
        if model in self._model_cache:
            return
        
        try:
            # Check if model exists using ollama-python API
            models_response = await self.async_client.list()
            model_names = [m['name'] for m in models_response.get('models', [])]
            
            if model in model_names:
                self._model_cache[model] = True
                return
            
            # Pull model with progress tracking
            logger.info(f"Model {model} not found locally, pulling...")
            async for progress in await self.async_client.pull(model, stream=True):
                if progress.get("status") == "downloading":
                    percent = progress.get("completed", 0) / progress.get("total", 1) * 100
                    logger.info(f"Downloading {model}: {percent:.1f}%")
            
            self._model_cache[model] = True
            logger.info(f"Model {model} ready for use")
            
        except Exception as e:
            raise ModelNotFoundError(f"Failed to ensure model {model}: {e}")
    
    def get_hardware_options(self, model: str) -> Dict[str, Any]:
        """Get hardware-specific options for model using ollama-python Options."""
        from ollama import Options
        
        base_options = Options(
            num_gpu=self.hardware_config.get("num_gpu", -1),
            num_thread=self.hardware_config.get("num_thread"),
            num_batch=self.hardware_config.get("num_batch", 512),
            main_gpu=self.hardware_config.get("main_gpu", 0),
            low_vram=self.hardware_config.get("low_vram", False),
            numa=self.hardware_config.get("numa", False),
            num_ctx=self.hardware_config.get("num_ctx", 2048)
        )
        
        # Model-specific overrides
        model_config = self.hardware_config.get("model_overrides", {}).get(model, {})
        for key, value in model_config.items():
            setattr(base_options, key, value)
        
        return base_options
    
    async def pull_model_with_progress(self, model: str) -> None:
        """Pull a model with detailed progress tracking."""
        async for response in await self.async_client.pull(model, stream=True):
            yield response
    
    async def create_custom_model(self, name: str, modelfile: str) -> None:
        """Create a custom model from a Modelfile."""
        await self.async_client.create(name=name, modelfile=modelfile)
    
    def list_running_models(self) -> List[Dict[str, Any]]:
        """List currently running models using ps()."""
        return self.client.ps()
```

### 3. Enhanced LiteLLM Provider with Monitoring

```python
class MonitoredLiteLLMProvider(LiteLLMProvider):
    """LiteLLM provider with enhanced monitoring and fallback."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.metrics = ProviderMetrics()
        self.fallback_chain = config.get("fallback_chain", [])
    
    async def completion_with_fallback(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Any:
        """Execute completion with automatic fallback on failure."""
        primary_error = None
        
        # Try primary model
        try:
            start_time = time.time()
            response = await self._try_completion(model, messages, **kwargs)
            self.metrics.record_success(model, time.time() - start_time)
            return response
        except Exception as e:
            primary_error = e
            self.metrics.record_failure(model, str(e))
        
        # Try fallback models
        for fallback_model in self.fallback_chain:
            if fallback_model == model:
                continue
                
            try:
                logger.warning(f"Falling back from {model} to {fallback_model}")
                start_time = time.time()
                response = await self._try_completion(fallback_model, messages, **kwargs)
                self.metrics.record_fallback_success(model, fallback_model, time.time() - start_time)
                return response
            except Exception as e:
                self.metrics.record_fallback_failure(fallback_model, str(e))
                continue
        
        # All attempts failed
        raise primary_error or Exception("All models in fallback chain failed")
```

## Operational Considerations

### 1. Ollama Configuration and Tuning

Based on research of Ollama's environment configuration, the following options are available for optimization:

#### Core Configuration Variables
```yaml
# Essential Ollama environment variables
OLLAMA_HOST: "0.0.0.0:11434"              # Bind address (default: 127.0.0.1:11434)
OLLAMA_MODELS: "/opt/models"               # Model storage path
OLLAMA_KEEP_ALIVE: "5m"                    # Model memory retention (default: 5m, use -1 for infinite)
OLLAMA_LOAD_TIMEOUT: "10m"                 # Model load timeout (default: 5m)
OLLAMA_NUM_PARALLEL: "4"                   # Parallel request handling (default: auto)
OLLAMA_MAX_LOADED_MODELS: "2"              # Maximum concurrent models in memory
OLLAMA_MAX_QUEUE: "512"                    # Request queue size
OLLAMA_DEBUG: "1"                          # Debug logging (0=INFO, 1=DEBUG, 2=TRACE)
```

#### GPU and Performance Configuration
```yaml
# NVIDIA GPU Configuration
CUDA_VISIBLE_DEVICES: "0,1"                # GPU device selection
OLLAMA_GPU_OVERHEAD: "1073741824"          # Reserve 1GB VRAM per GPU

# AMD GPU Configuration  
HIP_VISIBLE_DEVICES: "0"                   # AMD GPU selection
HSA_OVERRIDE_GFX_VERSION: "11.0.0"         # Override AMD GPU architecture

# Advanced Performance
OLLAMA_FLASH_ATTENTION: "true"             # Enable Flash Attention optimization
OLLAMA_KV_CACHE_TYPE: "f16"                # KV cache quantization (f16, q8_0, q4_0)
OLLAMA_SCHED_SPREAD: "true"                # Spread models across all GPUs
OLLAMA_MULTIUSER_CACHE: "true"             # Optimize for multi-user scenarios
OLLAMA_CONTEXT_LENGTH: "8192"              # Default context length
```

#### Hardware-Specific Options (via ollama-python Options class)
```python
# Available hardware control options
num_gpu: int = -1          # Number of GPUs (-1 = all available)
main_gpu: int = 0          # Primary GPU for compute
num_thread: int = None     # CPU threads (None = auto)
num_batch: int = 512       # Batch size for prompt processing
num_ctx: int = 2048        # Context window size
low_vram: bool = False     # Low VRAM mode
f16_kv: bool = True        # Use FP16 for key/value cache
use_mmap: bool = True      # Memory-mapped model loading
use_mlock: bool = False    # Lock model in RAM
numa: bool = False         # NUMA optimization
```

### 2. Current Deployment Architecture

Our implementation leverages both LiteLLM proxy server and SDK integration:

#### Docker Compose Stack (Current)
```yaml
# deployments/docker/compose/dev.yaml
services:
  # LiteLLM Proxy Server with database backend
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - DATABASE_URL=postgresql://postgres:postgres@litellm_db:5432/postgres
      - STORE_MODEL_IN_DB=true
      # Bootstrap models configuration
      - MODEL_NAME_1=llama3
      - MODEL_1=ollama/llama3
      - MODEL_API_BASE_1=http://ollama:11434
    depends_on:
      - litellm_db
      - ollama
  
  # Direct Ollama server for local models
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=24h  # Keep models loaded for development
  
  # Obelisk RAG service can use both providers
  obelisk-rag:
    environment:
      - OLLAMA_URL=http://ollama:11434
      - LITELLM_API_URL=http://litellm:4000
      - LITELLM_API_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - MODEL_PROVIDER=${MODEL_PROVIDER:-ollama}  # Configurable
```

### 3. Monitoring and Observability

```python
class ProviderMetrics:
    """Comprehensive metrics for provider monitoring."""
    
    def __init__(self):
        self.request_count = Counter('provider_requests_total', 'Total requests', ['provider', 'model'])
        self.request_duration = Histogram('provider_request_duration_seconds', 'Request duration', ['provider', 'model'])
        self.error_count = Counter('provider_errors_total', 'Total errors', ['provider', 'model', 'error_type'])
        self.fallback_count = Counter('provider_fallbacks_total', 'Total fallbacks', ['from_model', 'to_model'])
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics for dashboards."""
        return {
            "requests_per_minute": self._calculate_rpm(),
            "average_latency": self._calculate_avg_latency(),
            "error_rate": self._calculate_error_rate(),
            "fallback_rate": self._calculate_fallback_rate(),
            "model_usage": self._get_model_usage_stats()
        }
```

### 4. Health Checks and Readiness

```python
class ProviderHealthCheck:
    """Unified health checking for all providers."""
    
    async def check_all_providers(self) -> Dict[str, bool]:
        """Check health of all configured providers."""
        results = {}
        
        # Check Ollama
        if self.ollama_enabled:
            results["ollama"] = await self._check_ollama()
        
        # Check LiteLLM
        if self.litellm_enabled:
            results["litellm"] = await self._check_litellm()
        
        # Check specific models
        for model in self.critical_models:
            results[f"model:{model}"] = await self._check_model_availability(model)
        
        return results
    
    async def _check_ollama(self) -> bool:
        """Check Ollama server health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
```

### 5. Performance Optimization

```python
class ProviderOptimizer:
    """Runtime optimization for provider selection."""
    
    def __init__(self):
        self.latency_tracker = LatencyTracker()
        self.cost_tracker = CostTracker()
        self.availability_tracker = AvailabilityTracker()
    
    def get_optimal_provider(
        self,
        model: str,
        optimization_goal: str = "latency"
    ) -> ProviderType:
        """Select optimal provider based on runtime metrics."""
        if optimization_goal == "latency":
            return self._optimize_for_latency(model)
        elif optimization_goal == "cost":
            return self._optimize_for_cost(model)
        elif optimization_goal == "availability":
            return self._optimize_for_availability(model)
        else:
            return self._default_selection(model)
```

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. Audit current provider usage patterns
2. Document all provider-specific code
3. Create comprehensive test suite
4. Set up monitoring infrastructure

### Phase 2: Implementation (Weeks 2-3)
1. Implement enhanced provider factories
2. Add smart selection logic
3. Extend provider capabilities
4. Update configuration system

### Phase 3: Testing (Week 4)
1. Unit test all provider paths
2. Integration test with real services
3. Performance benchmarking
4. Load testing with both providers

### Phase 4: Rollout (Week 5)
1. Deploy to development environment
2. Gradual rollout to production
3. Monitor metrics and performance
4. Fine-tune selection algorithms

### Rollback Plan
```python
class ProviderRollback:
    """Emergency rollback to single provider mode."""
    
    def force_single_provider(self, provider: ProviderType):
        """Force all requests through a single provider."""
        logger.warning(f"EMERGENCY: Forcing all requests through {provider}")
        self.config["provider_mode"] = "forced"
        self.config["forced_provider"] = provider
        self.clear_provider_cache()
```

## Future Roadmap

### Near Term (3 months)
1. **Model Management UI**
   - Web interface for Ollama model management
   - Download progress visualization
   - Model configuration editor

2. **Advanced Routing**
   - ML-based provider selection
   - Predictive model availability
   - Cost optimization algorithms

3. **Enhanced Monitoring**
   - Grafana dashboards
   - Prometheus metrics export
   - Alert configuration

### Medium Term (6 months)
1. **Provider Plugins**
   - Plugin architecture for custom providers
   - Community provider marketplace
   - Provider testing framework

2. **Edge Deployment**
   - Lightweight provider for edge devices
   - Offline fallback mechanisms
   - Sync capabilities

3. **Multi-Model Orchestration**
   - Chain multiple models
   - Ensemble predictions
   - A/B testing framework

### Long Term (12 months)
1. **Federated Learning**
   - Distributed model training
   - Privacy-preserving inference
   - Model versioning

2. **Custom Model Support**
   - Fine-tuning pipeline
   - Model compression
   - Deployment automation

## Implementation Considerations

Based on extensive research of both libraries, several key considerations emerge:

### Performance Optimization
- **Direct Ollama Access**: Eliminates LiteLLM's overhead (parameter mapping, prompt formatting, response normalization)
- **Async Operations**: Use `acompletion()` and `aembedding()` for concurrent requests
- **Connection Pooling**: LiteLLM uses `httpx` internally for efficient connection management
- **Model Caching**: Pre-load frequently used models to avoid initialization overhead

### Integration Best Practices
1. **Model Naming Convention**:
   - Use prefixes for explicit routing: `ollama/llama3`, `azure/gpt-4`
   - Unprefixed local models default to direct Ollama
   - Cloud models automatically route through LiteLLM

2. **Configuration Hierarchy**:
   - Direct parameters > Provider config > Environment variables
   - Use explicit configuration for production deployments
   - Leverage environment variables for development

3. **Error Handling**:
   - Wrap all provider calls in try-except blocks
   - Implement provider-specific error mapping
   - Use fallback chains for critical operations

### Feature Parity Considerations
**Features exclusive to direct Ollama access**:
- Model management operations (pull, push, create, delete)
- Hardware configuration (GPU allocation, memory settings)
- Process monitoring (`ps()`)
- Binary blob management
- Custom model creation from Modelfiles

**Features gained through LiteLLM**:
- Unified interface for 100+ providers
- Automatic retry mechanisms
- Built-in fallback support
- Cost tracking and budgeting
- Request routing strategies

### Proxy vs SDK Deployment
Our current architecture leverages both approaches:

1. **LiteLLM Proxy Server (Current Stack)**:
   - Provides OpenAI-compatible endpoint at port 4000
   - Manages model registry in PostgreSQL database
   - Enables virtual key management and authentication
   - Supports dynamic model registration via API
   - Used by OpenWebUI and can be accessed by any OpenAI client

2. **Direct SDK Integration (Provider Classes)**:
   - Used within Obelisk RAG Python code
   - Enables fine-grained control over provider selection
   - Supports both direct Ollama and LiteLLM routing
   - Allows for custom provider implementations

## Current Implementation Status

### What's Implemented
1. **Provider Factory Pattern**: Both LiteLLMProvider and OllamaProvider classes exist
2. **LiteLLM Proxy Server**: Running in Docker stack on port 4000
3. **Basic Integration**: RAG service can use both providers
4. **Environment Configuration**: Provider selection via MODEL_PROVIDER env var

### What Needs Refinement (Today's Work)
1. **Unified API Gateway**: Route ALL completions through LiteLLM API
2. **Remove Direct Ollama Imports**: Replace with LiteLLM API calls for completions
3. **Preserve Hardware Control**: Keep OllamaProvider for tuning operations
4. **Update Provider Factory**: Select based on operation type, not model

### Migration Path
```python
# Before (mixed routing)
if model.startswith("gpt"):
    provider = litellm_provider
else:
    provider = ollama_provider
response = await provider.completion(messages)

# After (unified API)
# All completions through LiteLLM
response = await litellm_client.chat.completions.create(
    model=model,  # LiteLLM handles routing
    messages=messages
)

# Hardware ops still direct
if need_hardware_tuning:
    ollama_provider.configure_gpu(settings)
```

## Deployment Architecture

For comprehensive deployment patterns across different platforms and environments, please refer to the companion document: [deployment-architecture.md](../deployment/deployment-architecture.md)

This deployment guide covers:
- Docker deployment patterns with Milvus vector database
- Kubernetes production architectures with GPU support
- Apple Silicon optimization strategies
- Platform-specific performance tuning
- High availability and disaster recovery patterns

## Conclusion

The refined architecture provides an elegant solution that unifies the API surface while preserving essential capabilities:

1. **Unified API Surface**: All completions through OpenAI-compatible LiteLLM endpoint
2. **Hardware Control**: Direct Ollama access for GPU tuning and model management
3. **Operational Simplicity**: Single endpoint for all chat/completion operations
4. **Provider Flexibility**: LiteLLM automatically routes to appropriate backend
5. **Future Ready**: Easy to add new providers without changing client code

This approach reduces complexity for API consumers while maintaining the flexibility needed for hardware optimization and model management. The dual-provider pattern with operation-based selection ensures we get the best of both worlds: unified API access and direct hardware control.

### Research Summary

This design document is based on comprehensive research of:

1. **LiteLLM SDK Architecture**: Stateless design with automatic provider detection via model name prefixes
2. **Ollama-python Capabilities**: Unique model management operations and hardware control options
3. **Performance Characteristics**: LiteLLM overhead tracked via metrics, not fixed latency
4. **Deployment Patterns**: Multi-platform support across Docker, Kubernetes, and native installations
5. **2025 Best Practices**: GPU optimization, intelligent routing, and cloud-native patterns

The architecture decisions reflect the current state of both libraries while maintaining flexibility for future enhancements.

## Appendix: Code Examples

### Example 1: Smart Provider Usage
```python
# Automatic provider selection based on model name
rag_service = RAGService()

# Local model - uses direct Ollama
response = await rag_service.query("What is machine learning?", model="llama3")

# Cloud model - uses LiteLLM
response = await rag_service.query("What is machine learning?", model="gpt-4")

# Explicit provider prefix - uses LiteLLM with Ollama backend
response = await rag_service.query(
    "What is machine learning?",
    model="ollama/llama3"  # LiteLLM routes to Ollama
)

# Force provider selection
response = await rag_service.query(
    "What is machine learning?",
    model="llama3",
    provider_hint=ProviderType.LITELLM,  # Override smart selection
    force_proxy=True
)

# Hardware-specific configuration for Ollama
response = await rag_service.query(
    "What is machine learning?",
    model="llama3",
    options={
        "num_gpu": 2,
        "num_ctx": 4096,
        "num_thread": 8
    }  # Automatically uses direct Ollama with hardware options
)
```

### Example 2: Provider Capability Detection
```python
provider = factory.get_provider("gpt-4")
capabilities = provider.get_capabilities()

if capabilities.supports_streaming:
    async for chunk in provider.stream_completion(messages):
        print(chunk, end="")
else:
    response = await provider.completion(messages)
    print(response)
```

### Example 3: Direct LiteLLM SDK Usage
```python
import litellm
import asyncio

# Configure LiteLLM with automatic provider detection
async def use_litellm_directly():
    # Direct completion call - provider detected from model name
    response = litellm.completion(
        model="ollama/llama3",  # Routes to Ollama
        messages=[{"role": "user", "content": "Hello"}],
        max_retries=3,
        api_base="http://localhost:11434"  # Optional Ollama base URL
    )
    
    # Async completion with different provider
    async_response = await litellm.acompletion(
        model="gpt-4",  # Routes to OpenAI
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7
    )
    
    # Embedding with automatic provider routing
    embedding = litellm.embedding(
        model="ollama/mxbai-embed-large",
        input=["This is a test sentence"]
    )
    
    return response, async_response, embedding

# Using Router for advanced features
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "primary-llm",
            "litellm_params": {
                "model": "ollama/llama3",
                "api_base": "http://localhost:11434"
            }
        },
        {
            "model_name": "fallback-llm",
            "litellm_params": {
                "model": "gpt-3.5-turbo"
            }
        }
    ],
    routing_strategy="least-busy",
    fallbacks=[{"primary-llm": ["fallback-llm"]}]
)

# Router automatically handles fallbacks and load balancing
response = await router.acompletion(
    model="primary-llm",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Example 4: Operational Monitoring
```python
# Health check endpoint with provider details
@app.get("/health/providers")
async def health_check():
    health = ProviderHealthCheck()
    results = await health.check_all_providers()
    
    # Include latency metrics from LiteLLM
    metrics = {
        "litellm_overhead_ms": request.headers.get("x-litellm-overhead-duration-ms"),
        "providers": results
    }
    
    if all(results.values()):
        return {"status": "healthy", **metrics}
    else:
        return {"status": "degraded", **metrics}, 503

# Prometheus metrics endpoint
@app.get("/metrics/providers")
async def metrics():
    # LiteLLM exposes metrics when using proxy
    return {
        "provider_metrics": provider_metrics.export_metrics(),
        "litellm_metrics": {
            "overhead_latency": "litellm_overhead_latency_metric",
            "request_latency": "litellm_request_total_latency_metric",
            "llm_api_latency": "litellm_llm_api_latency_metric"
        }
    }
```
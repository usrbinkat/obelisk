"""
Concrete model provider implementations for the Obelisk RAG system.

This module contains the actual implementations of different model providers,
including LiteLLM, Ollama, and OpenAI providers.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import httpx

try:
    import litellm
    from litellm import completion, embedding
    LITELLM_AVAILABLE = True
    # TODO: Import acompletion, aembedding when implementing async support
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None

try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ChatOllama = None
    OllamaEmbeddings = None

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None
    OpenAIEmbeddings = None

from .models import (
    ModelProvider, ProviderType, ProviderFactory,
    ProviderNotAvailableError, ModelNotFoundError
)

logger = logging.getLogger(__name__)


class LiteLLMProvider(ModelProvider):
    """
    LiteLLM-based model provider implementation.
    
    This provider uses LiteLLM to access multiple model providers through
    a unified interface, supporting automatic fallback and provider routing.
    """
    
    provider_type = ProviderType.LITELLM
    
    def initialize(self) -> None:
        """Initialize the LiteLLM provider."""
        if not LITELLM_AVAILABLE:
            raise ProviderNotAvailableError(
                "LiteLLM is not installed. Install with: pip install litellm"
            )
        
        # Configure LiteLLM settings
        self.api_base = self.config.get("litellm_api_base", "http://litellm:4000")
        self.api_key = self.config.get("litellm_api_key", os.getenv("LITELLM_API_KEY"))
        
        # Set up LiteLLM configuration
        if self.api_key:
            litellm.api_key = self.api_key
        
        # Configure LiteLLM proxy settings if using proxy
        if self.api_base:
            litellm.api_base = self.api_base
        
        # Configure LiteLLM settings
        if self.config.get("debug", False):
            litellm.set_verbose = True
        
        # Set retry and timeout configuration
        if hasattr(litellm, 'num_retries'):
            litellm.num_retries = self.config.get("num_retries", 3)
        if hasattr(litellm, 'request_timeout'):
            litellm.request_timeout = self.config.get("request_timeout", 600)
        
        # Test connection
        if not self.health_check():
            logger.warning("LiteLLM provider initialized but health check failed")
        
        self._initialized = True
        logger.info(f"LiteLLM provider initialized with base URL: {self.api_base}")
    
    def get_llm(self, model: Optional[str] = None, **kwargs) -> Any:
        """
        Get an LLM instance through LiteLLM.
        
        Returns a simplified wrapper that uses LiteLLM directly.
        """
        from langchain.llms.base import LLM
        from langchain.callbacks.manager import CallbackManagerForLLMRun
        
        model_name = model or self.config.get("llm_model", "gpt-3.5-turbo")
        api_base = self.api_base
        api_key = self.api_key
        config = self.config
        
        class LiteLLMLLM(LLM):
            """Direct LiteLLM wrapper for LangChain compatibility."""
            
            model: str = model_name
            temperature: float = kwargs.get("temperature", 0.7)
            max_tokens: Optional[int] = kwargs.get("max_tokens")
            
            @property
            def _llm_type(self) -> str:
                return "litellm"
            
            def _call(
                self,
                prompt: str,
                stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any,
            ) -> str:
                """Call LiteLLM completion API directly."""
                # Build kwargs for LiteLLM
                call_kwargs = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "api_base": api_base,
                    "api_key": api_key,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stop": stop,
                }
                
                # Add retry configuration
                if config:
                    call_kwargs["num_retries"] = config.get("num_retries", 3)
                    call_kwargs["request_timeout"] = config.get("request_timeout", 600)
                
                # Remove None values
                call_kwargs = {k: v for k, v in call_kwargs.items() if v is not None}
                
                try:
                    response = completion(**call_kwargs)
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"LiteLLM completion error: {e}")
                    raise
            
            async def _acall(
                self,
                prompt: str,
                stop: Optional[List[str]] = None,
                run_manager: Optional[Any] = None,
                **kwargs: Any,
            ) -> str:
                """Async call - currently uses sync implementation."""
                # TODO: Use litellm.acompletion when implementing full async support
                return self._call(prompt, stop, run_manager, **kwargs)
            
            @property
            def _identifying_params(self) -> Dict[str, Any]:
                """Return model parameters for caching/identification."""
                return {
                    "model": model_name,
                    "api_base": api_base,
                    "temperature": kwargs.get("temperature", 0.7),
                }
        
        return LiteLLMLLM()
    
    def get_embeddings(self, model: Optional[str] = None, **kwargs) -> Any:
        """
        Get an embeddings instance through LiteLLM.
        
        Returns a simplified LangChain-compatible embeddings wrapper.
        """
        from langchain.embeddings.base import Embeddings
        
        model_name = model or self.config.get("embedding_model", "text-embedding-3-small")
        
        class LiteLLMEmbeddings(Embeddings):
            """Simplified embeddings wrapper for LiteLLM."""
            
            def __init__(self, api_base: str, api_key: Optional[str], model: str):
                self.api_base = api_base
                self.api_key = api_key
                self.model = model
            
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents using LiteLLM."""
                try:
                    # Debug logging
                    logger.debug(f"LiteLLM embed_documents called with {len(texts)} texts")
                    logger.debug(f"First text sample: {texts[0][:100] if texts else 'empty'}...")
                    logger.debug(f"Input type: {type(texts)}, first element type: {type(texts[0]) if texts else 'N/A'}")
                    
                    # LiteLLM's embedding function handles batching internally
                    response = embedding(
                        model=self.model,
                        input=texts,
                        api_base=self.api_base,
                        api_key=self.api_key
                    )
                    return [data["embedding"] for data in response.data]
                except Exception as e:
                    logger.error(f"LiteLLM embedding error: {e}")
                    logger.error(f"Input was: type={type(texts)}, len={len(texts) if hasattr(texts, '__len__') else 'N/A'}")
                    if texts and hasattr(texts, '__iter__'):
                        logger.error(f"First element: type={type(texts[0])}, value={texts[0][:100] if hasattr(texts[0], '__getitem__') else texts[0]}")
                    raise
            
            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return self.embed_documents([text])[0]
            
            async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
                """Async embed documents - currently uses sync method."""
                # TODO: Use litellm.aembedding when available
                return self.embed_documents(texts)
            
            async def aembed_query(self, text: str) -> List[float]:
                """Async embed query - currently uses sync method."""
                # TODO: Use litellm.aembedding when available
                return self.embed_query(text)
        
        return LiteLLMEmbeddings(
            api_base=self.api_base,
            api_key=self.api_key,
            model=model_name
        )
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List available models from LiteLLM."""
        try:
            # LiteLLM supports model names with provider prefixes
            # This allows automatic routing to the correct provider
            return {
                "llm": [
                    # OpenAI models
                    "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo",
                    # Anthropic models
                    "claude-2", "claude-instant-1", "claude-3-opus", "claude-3-sonnet",
                    # Local models via Ollama (use prefix)
                    "ollama/llama3", "ollama/mistral", "ollama/mixtral",
                    # Azure OpenAI (use prefix)
                    "azure/gpt-4", "azure/gpt-35-turbo",
                    # Google models
                    "gemini-pro", "palm-2",
                    # Cohere models
                    "command", "command-light"
                ],
                "embedding": [
                    # OpenAI embeddings
                    "text-embedding-3-small", "text-embedding-3-large",
                    "text-embedding-ada-002",
                    # Local embeddings via Ollama
                    "ollama/mxbai-embed-large", "ollama/nomic-embed-text",
                    # Cohere embeddings
                    "embed-english-v3.0", "embed-multilingual-v3.0"
                ]
            }
        except Exception as e:
            logger.error(f"Error listing LiteLLM models: {e}")
            return {"llm": [], "embedding": []}
    
    def health_check(self) -> bool:
        """Check if LiteLLM is accessible."""
        try:
            # Use a minimal model that should work with most providers
            # If model includes provider prefix, use it directly
            test_model = self.config.get("llm_model", "gpt-3.5-turbo")
            
            response = completion(
                model=test_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                api_base=self.api_base,
                api_key=self.api_key,
                num_retries=1  # Don't retry health checks
            )
            return True
        except Exception as e:
            logger.debug(f"LiteLLM health check failed: {e}")
            return False


class OllamaProvider(ModelProvider):
    """
    Direct Ollama provider implementation.
    
    This provider connects directly to Ollama for local model inference,
    bypassing any proxy layers for maximum performance with local models.
    """
    
    provider_type = ProviderType.OLLAMA
    
    def initialize(self) -> None:
        """Initialize the Ollama provider."""
        if not OLLAMA_AVAILABLE:
            raise ProviderNotAvailableError(
                "Ollama integration not installed. Install with: pip install langchain-ollama"
            )
        
        self.api_base = self.config.get("ollama_url", "http://ollama:11434")
        self.default_llm_model = self.config.get("ollama_model", "llama3")
        self.default_embedding_model = self.config.get("embedding_model", "mxbai-embed-large")
        
        # Test connection
        if not self.health_check():
            logger.warning("Ollama provider initialized but health check failed")
        
        self._initialized = True
        logger.info(f"Ollama provider initialized with URL: {self.api_base}")
    
    def get_llm(self, model: Optional[str] = None, **kwargs) -> Any:
        """Get an Ollama LLM instance."""
        model_name = model or self.default_llm_model
        
        # Extract temperature to avoid duplicate argument
        temperature = kwargs.pop("temperature", 0.7)
        
        return ChatOllama(
            model=model_name,
            base_url=self.api_base,
            temperature=temperature,
            **kwargs
        )
    
    def get_embeddings(self, model: Optional[str] = None, **kwargs) -> Any:
        """Get an Ollama embeddings instance."""
        model_name = model or self.default_embedding_model
        
        return OllamaEmbeddings(
            model=model_name,
            base_url=self.api_base,
            **kwargs
        )
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List available models from Ollama."""
        try:
            # Query Ollama API for available models
            response = httpx.get(f"{self.api_base}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                # Separate embedding models (common convention)
                embedding_models = [m for m in models if "embed" in m.lower()]
                llm_models = [m for m in models if "embed" not in m.lower()]
                return {"llm": llm_models, "embedding": embedding_models}
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
        
        return {"llm": [], "embedding": []}
    
    def health_check(self) -> bool:
        """Check if Ollama is accessible."""
        try:
            response = httpx.get(f"{self.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class OpenAIProvider(ModelProvider):
    """
    Direct OpenAI provider implementation.
    
    This provider connects directly to OpenAI's API for cloud-based
    model inference with the latest GPT models.
    """
    
    provider_type = ProviderType.OPENAI
    
    def initialize(self) -> None:
        """Initialize the OpenAI provider."""
        if not OPENAI_AVAILABLE:
            raise ProviderNotAvailableError(
                "OpenAI integration not installed. Install with: pip install langchain-openai"
            )
        
        self.api_key = self.config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
        if not self.api_key:
            raise ProviderNotAvailableError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        self.default_llm_model = self.config.get("openai_model", "gpt-3.5-turbo")
        self.default_embedding_model = self.config.get("openai_embedding_model", "text-embedding-3-small")
        
        self._initialized = True
        logger.info("OpenAI provider initialized")
    
    def get_llm(self, model: Optional[str] = None, **kwargs) -> Any:
        """Get an OpenAI LLM instance."""
        model_name = model or self.default_llm_model
        
        # Extract temperature to avoid duplicate argument
        temperature = kwargs.pop("temperature", 0.7)
        
        return ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            temperature=temperature,
            **kwargs
        )
    
    def get_embeddings(self, model: Optional[str] = None, **kwargs) -> Any:
        """Get an OpenAI embeddings instance."""
        model_name = model or self.default_embedding_model
        
        return OpenAIEmbeddings(
            model=model_name,
            api_key=self.api_key,
            **kwargs
        )
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List commonly available OpenAI models."""
        return {
            "llm": [
                "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k", "gpt-4-32k"
            ],
            "embedding": [
                "text-embedding-3-small", "text-embedding-3-large",
                "text-embedding-ada-002"
            ]
        }
    
    def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            # Test with a minimal embedding request
            embeddings = self.get_embeddings()
            embeddings.embed_query("test")
            return True
        except Exception:
            return False


# Register all providers with the factory
ProviderFactory.register_provider(ProviderType.LITELLM, LiteLLMProvider)
ProviderFactory.register_provider(ProviderType.OLLAMA, OllamaProvider)
ProviderFactory.register_provider(ProviderType.OPENAI, OpenAIProvider)


# Direct factory for creating model providers
class ModelProviderFactory:
    """Factory for creating model provider instances."""
    
    @staticmethod
    def create(provider_type: Union[ProviderType, str], config: Dict[str, Any]) -> ModelProvider:
        """
        Create a provider instance.
        
        Args:
            provider_type: The type of provider (litellm, ollama, openai)
            config: Configuration dictionary
            
        Returns:
            Initialized model provider instance
        """
        return ProviderFactory.create_provider(provider_type, config)
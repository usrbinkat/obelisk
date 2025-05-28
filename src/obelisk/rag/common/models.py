"""
Model abstraction layer for the Obelisk RAG system.

This module provides a common interface for different model providers,
abstracting away the specific implementation details and allowing for
seamless switching between providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported model provider types."""
    LITELLM = "litellm"
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for a model instance."""
    model_name: str
    provider: ProviderType
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    retry_attempts: int = 3
    additional_params: Optional[Dict[str, Any]] = None


class ModelProvider(ABC):
    """
    Abstract base class for model providers.
    
    This class defines the interface that all model providers must implement,
    ensuring consistent behavior across different provider implementations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the model provider.
        
        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config
        self._initialized = False
        self.initialize()
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the provider connection and resources.
        
        This method should set up any necessary connections, authenticate
        with the provider, and prepare the provider for use.
        """
        pass
    
    @abstractmethod
    def get_llm(self, model: Optional[str] = None, **kwargs) -> Any:
        """
        Get a language model instance.
        
        Args:
            model: Optional model name override
            **kwargs: Additional model-specific parameters
            
        Returns:
            A configured LLM instance compatible with LangChain
        """
        pass
    
    @abstractmethod
    def get_embeddings(self, model: Optional[str] = None, **kwargs) -> Any:
        """
        Get an embeddings model instance.
        
        Args:
            model: Optional model name override
            **kwargs: Additional model-specific parameters
            
        Returns:
            A configured embeddings instance compatible with LangChain
        """
        pass
    
    @abstractmethod
    def list_available_models(self) -> Dict[str, List[str]]:
        """
        List available models from the provider.
        
        Returns:
            Dictionary with 'llm' and 'embedding' keys containing lists of model names
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.
        
        Returns:
            True if the provider is healthy, False otherwise
        """
        pass
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information or None if not found
        """
        return None
    
    def estimate_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate the number of tokens in a text for a given model.
        
        Args:
            text: Text to estimate tokens for
            model: Model name to use for estimation
            
        Returns:
            Estimated number of tokens
        """
        # Simple character-based estimation as default
        # Providers can override with more accurate methods
        return len(text) // 4
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(initialized={self._initialized})"


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available or accessible."""
    pass


class ModelNotFoundError(ProviderError):
    """Raised when a requested model is not found."""
    pass


class ProviderFactory:
    """
    Factory class for creating model provider instances.
    
    This class manages the registration and instantiation of different
    model provider implementations.
    """
    
    _providers: Dict[ProviderType, type] = {}
    
    @classmethod
    def register_provider(cls, provider_type: ProviderType, provider_class: type) -> None:
        """
        Register a provider implementation.
        
        Args:
            provider_type: The type of provider
            provider_class: The provider class implementation
        """
        if not issubclass(provider_class, ModelProvider):
            raise ValueError(f"{provider_class} must be a subclass of ModelProvider")
        cls._providers[provider_type] = provider_class
        logger.info(f"Registered provider: {provider_type.value}")
    
    @classmethod
    def create_provider(cls, provider_type: Union[ProviderType, str], config: Dict[str, Any]) -> ModelProvider:
        """
        Create a provider instance.
        
        Args:
            provider_type: The type of provider to create
            config: Configuration for the provider
            
        Returns:
            An initialized provider instance
            
        Raises:
            ValueError: If the provider type is not registered
        """
        if isinstance(provider_type, str):
            try:
                provider_type = ProviderType(provider_type)
            except ValueError:
                raise ValueError(f"Unknown provider type: {provider_type}")
        
        if provider_type not in cls._providers:
            raise ValueError(f"Provider {provider_type.value} not registered. "
                           f"Available providers: {list(cls._providers.keys())}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered provider types.
        
        Returns:
            List of registered provider type names
        """
        return [p.value for p in cls._providers.keys()]


def get_model_provider(config: Optional[Dict[str, Any]] = None) -> ModelProvider:
    """
    Get a model provider instance based on configuration.
    
    This is the main entry point for getting a model provider. It reads
    the configuration and returns an appropriate provider instance.
    
    Args:
        config: Optional configuration override
        
    Returns:
        An initialized model provider instance
    """
    if config is None:
        from .config import get_config
        config = get_config()
    
    provider_type = config.get("model_provider", "litellm")
    return ProviderFactory.create_provider(provider_type, config)
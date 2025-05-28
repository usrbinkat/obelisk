"""
Unit tests for model provider abstraction layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from src.obelisk.rag.common.models import (
    ModelProvider,
    ProviderType,
    ModelConfig,
    ProviderFactory,
    ProviderError,
    ProviderNotAvailableError,
    ModelNotFoundError,
    get_model_provider
)


class TestModelProvider:
    """Test the abstract ModelProvider base class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that ModelProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ModelProvider({})
    
    def test_concrete_provider_must_implement_abstract_methods(self):
        """Test that concrete providers must implement all abstract methods."""
        
        class IncompleteProvider(ModelProvider):
            def initialize(self):
                pass
            # Missing other required methods
        
        # Should fail because not all abstract methods are implemented
        with pytest.raises(TypeError):
            IncompleteProvider({})
    
    def test_provider_initialization(self):
        """Test that providers are properly initialized."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                self._initialized = True
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        config = {"test_key": "test_value"}
        provider = TestProvider(config)
        
        assert provider.config == config
        assert provider._initialized is True
    
    def test_default_methods(self):
        """Test default method implementations."""
        
        class MinimalProvider(ModelProvider):
            def initialize(self):
                self._initialized = True
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        provider = MinimalProvider({})
        
        # Test default get_model_info returns None
        assert provider.get_model_info("test-model") is None
        
        # Test default token estimation
        test_text = "This is a test string"
        estimated_tokens = provider.estimate_tokens(test_text)
        assert estimated_tokens == len(test_text) // 4
        
        # Test string representation
        assert "MinimalProvider(initialized=True)" in str(provider)


class TestProviderType:
    """Test the ProviderType enum."""
    
    def test_provider_types(self):
        """Test that all expected provider types exist."""
        assert ProviderType.LITELLM.value == "litellm"
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.OPENAI.value == "openai"
    
    def test_provider_type_from_string(self):
        """Test creating ProviderType from string."""
        assert ProviderType("litellm") == ProviderType.LITELLM
        assert ProviderType("ollama") == ProviderType.OLLAMA
        assert ProviderType("openai") == ProviderType.OPENAI
        
        with pytest.raises(ValueError):
            ProviderType("invalid_provider")


class TestModelConfig:
    """Test the ModelConfig dataclass."""
    
    def test_model_config_creation(self):
        """Test creating a ModelConfig instance."""
        config = ModelConfig(
            model_name="gpt-4",
            provider=ProviderType.OPENAI,
            api_key="test_key",
            temperature=0.5
        )
        
        assert config.model_name == "gpt-4"
        assert config.provider == ProviderType.OPENAI
        assert config.api_key == "test_key"
        assert config.temperature == 0.5
        assert config.max_tokens is None  # Default value
        assert config.timeout == 30  # Default value
    
    def test_model_config_defaults(self):
        """Test ModelConfig default values."""
        config = ModelConfig(
            model_name="llama3",
            provider=ProviderType.OLLAMA
        )
        
        assert config.api_base is None
        assert config.api_key is None
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.additional_params is None


class TestProviderFactory:
    """Test the ProviderFactory class."""
    
    def setup_method(self):
        """Reset the factory before each test."""
        # Clear any registered providers
        ProviderFactory._providers.clear()
    
    def test_register_provider(self):
        """Test registering a provider."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                pass
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        # Register the provider
        ProviderFactory.register_provider(ProviderType.LITELLM, TestProvider)
        
        # Verify it was registered
        assert ProviderType.LITELLM in ProviderFactory._providers
        assert ProviderFactory._providers[ProviderType.LITELLM] == TestProvider
    
    def test_register_invalid_provider(self):
        """Test that only ModelProvider subclasses can be registered."""
        
        class NotAProvider:
            pass
        
        with pytest.raises(ValueError, match="must be a subclass of ModelProvider"):
            ProviderFactory.register_provider(ProviderType.LITELLM, NotAProvider)
    
    def test_create_provider(self):
        """Test creating a provider instance."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                self._initialized = True
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        # Register and create
        ProviderFactory.register_provider(ProviderType.LITELLM, TestProvider)
        config = {"test": "config"}
        
        # Test with ProviderType enum
        provider = ProviderFactory.create_provider(ProviderType.LITELLM, config)
        assert isinstance(provider, TestProvider)
        assert provider.config == config
        
        # Test with string
        provider2 = ProviderFactory.create_provider("litellm", config)
        assert isinstance(provider2, TestProvider)
    
    def test_create_unregistered_provider(self):
        """Test creating a provider that hasn't been registered."""
        with pytest.raises(ValueError, match="Provider litellm not registered"):
            ProviderFactory.create_provider(ProviderType.LITELLM, {})
    
    def test_create_invalid_provider_type(self):
        """Test creating a provider with invalid type."""
        with pytest.raises(ValueError, match="Unknown provider type: invalid"):
            ProviderFactory.create_provider("invalid", {})
    
    def test_list_providers(self):
        """Test listing registered providers."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                pass
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        # Initially empty
        assert ProviderFactory.list_providers() == []
        
        # Register providers
        ProviderFactory.register_provider(ProviderType.LITELLM, TestProvider)
        ProviderFactory.register_provider(ProviderType.OLLAMA, TestProvider)
        
        providers = ProviderFactory.list_providers()
        assert "litellm" in providers
        assert "ollama" in providers
        assert len(providers) == 2


class TestGetModelProvider:
    """Test the get_model_provider function."""
    
    def setup_method(self):
        """Reset the factory before each test."""
        ProviderFactory._providers.clear()
    
    @patch('src.obelisk.rag.common.config.get_config')
    def test_get_model_provider_with_default_config(self, mock_get_config):
        """Test getting a model provider with default configuration."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                self._initialized = True
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        # Register provider
        ProviderFactory.register_provider(ProviderType.LITELLM, TestProvider)
        
        # Mock config
        mock_config = {"model_provider": "litellm", "test": "value"}
        mock_get_config.return_value = mock_config
        
        # Get provider
        provider = get_model_provider()
        
        assert isinstance(provider, TestProvider)
        assert provider.config == mock_config
        mock_get_config.assert_called_once()
    
    def test_get_model_provider_with_custom_config(self):
        """Test getting a model provider with custom configuration."""
        
        class TestProvider(ModelProvider):
            def initialize(self):
                self._initialized = True
            
            def get_llm(self, model=None, **kwargs):
                return Mock()
            
            def get_embeddings(self, model=None, **kwargs):
                return Mock()
            
            def list_available_models(self):
                return {"llm": [], "embedding": []}
            
            def health_check(self):
                return True
        
        # Register provider
        ProviderFactory.register_provider(ProviderType.OLLAMA, TestProvider)
        
        # Custom config
        custom_config = {"model_provider": "ollama", "custom": "value"}
        
        # Get provider with custom config
        provider = get_model_provider(custom_config)
        
        assert isinstance(provider, TestProvider)
        assert provider.config == custom_config


class TestProviderExceptions:
    """Test provider exception classes."""
    
    def test_provider_error(self):
        """Test base ProviderError exception."""
        error = ProviderError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_provider_not_available_error(self):
        """Test ProviderNotAvailableError exception."""
        error = ProviderNotAvailableError("Provider not available")
        assert str(error) == "Provider not available"
        assert isinstance(error, ProviderError)
    
    def test_model_not_found_error(self):
        """Test ModelNotFoundError exception."""
        error = ModelNotFoundError("Model not found")
        assert str(error) == "Model not found"
        assert isinstance(error, ProviderError)
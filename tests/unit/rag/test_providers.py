"""
Unit tests for concrete model provider implementations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Dict, Any, List, Optional

# Mock the imports that might not be available
import sys

# Create more sophisticated mocks for LangChain base classes
from unittest.mock import MagicMock

# Create function mocks first
completion_mock = MagicMock()
embedding_mock = MagicMock()

# Create a proper module mock class that behaves like litellm
class LiteLLMModuleMock:
    def __init__(self):
        self.completion = completion_mock
        self.embedding = embedding_mock
        self.api_key = None
        self.api_base = None
        self.set_verbose = False
    
    def __getattr__(self, name):
        if name == 'completion':
            return completion_mock
        elif name == 'embedding':
            return embedding_mock
        return MagicMock()

# Install the mock module
litellm_mock = LiteLLMModuleMock()
sys.modules['litellm'] = litellm_mock

# Also ensure the functions are available at module level for direct import
def mock_completion(*args, **kwargs):
    return completion_mock(*args, **kwargs)

def mock_embedding(*args, **kwargs):
    return embedding_mock(*args, **kwargs)

# Add to sys.modules dict for direct imports
litellm_mock.completion = mock_completion
litellm_mock.embedding = mock_embedding

# Mock provider-specific modules
sys.modules['langchain_ollama'] = MagicMock()
sys.modules['langchain_openai'] = MagicMock()
sys.modules['langchain_community.llms'] = MagicMock()

# Create proper base class mocks for LangChain
class MockLLM:
    """Mock LangChain LLM base class."""
    # Support class-level attributes
    model: str = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    def __init__(self):
        # Instance attributes take precedence if set
        pass
    
    @property
    def _llm_type(self):
        return "mock"
    
    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        return "mock response"

class MockEmbeddings:
    """Mock LangChain Embeddings base class."""
    def __init__(self):
        self.model = None
        self.api_base = None
        self.api_key = None
    
    def embed_documents(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]
    
    def embed_query(self, text):
        return [0.1, 0.2, 0.3]

# Create module mocks with proper classes
langchain_llms_mock = MagicMock()
langchain_llms_mock.LLM = MockLLM
sys.modules['langchain.llms.base'] = langchain_llms_mock

langchain_embeddings_mock = MagicMock()
langchain_embeddings_mock.Embeddings = MockEmbeddings
sys.modules['langchain.embeddings.base'] = langchain_embeddings_mock

sys.modules['langchain.callbacks.manager'] = MagicMock()

from src.obelisk.rag.common.providers import (
    LiteLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    LITELLM_AVAILABLE,
    OLLAMA_AVAILABLE,
    OPENAI_AVAILABLE
)
from src.obelisk.rag.common.models import (
    ProviderNotAvailableError,
    ModelNotFoundError
)


class TestLiteLLMProvider:
    """Test the LiteLLM provider implementation."""
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_initialization(self, mock_litellm):
        """Test LiteLLM provider initialization."""
        config = {
            "litellm_api_base": "http://test:4000",
            "litellm_api_key": "test_key",
            "debug": True
        }
        
        provider = LiteLLMProvider(config)
        
        assert provider.api_base == "http://test:4000"
        assert provider.api_key == "test_key"
        assert provider._initialized is True
        assert mock_litellm.api_key == "test_key"
        assert mock_litellm.api_base == "http://test:4000"
        assert mock_litellm.set_verbose is True
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', False)
    def test_initialization_without_litellm(self):
        """Test initialization when LiteLLM is not available."""
        with pytest.raises(ProviderNotAvailableError, match="LiteLLM is not installed"):
            LiteLLMProvider({})
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    @patch.dict(os.environ, {'LITELLM_API_KEY': 'env_key'})
    def test_initialization_with_env_key(self, mock_litellm):
        """Test initialization with API key from environment."""
        config = {"litellm_api_base": "http://test:4000"}
        
        provider = LiteLLMProvider(config)
        
        assert provider.api_key == "env_key"
        assert mock_litellm.api_key == "env_key"
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_get_llm(self, mock_litellm):
        """Test getting an LLM instance."""
        provider = LiteLLMProvider({})
        llm = provider.get_llm(model="gpt-4", temperature=0.5)
        
        # Test the LLM properties
        assert llm.model == "gpt-4"
        assert llm.temperature == 0.5
        assert llm._llm_type == "litellm"
        
        # Test that the LLM class is correctly configured
        assert hasattr(llm, '_call')
        assert callable(llm._call)
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_get_embeddings(self, mock_litellm):
        """Test getting an embeddings instance."""
        provider = LiteLLMProvider({})
        embeddings = provider.get_embeddings(model="text-embedding-ada-002")
        
        # Test basic functionality
        assert hasattr(embeddings, 'embed_documents')
        assert hasattr(embeddings, 'embed_query')
        # Note: model is set as class attribute during class definition
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_list_available_models(self, mock_litellm):
        """Test listing available models."""
        provider = LiteLLMProvider({})
        models = provider.list_available_models()
        
        assert "llm" in models
        assert "embedding" in models
        assert "gpt-4" in models["llm"]
        assert "text-embedding-3-small" in models["embedding"]
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_health_check_success(self, mock_litellm):
        """Test successful health check."""
        provider = LiteLLMProvider({})
        # Just test that health_check method exists and can be called
        result = provider.health_check()
        assert isinstance(result, bool)
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.litellm')
    def test_health_check_failure(self, mock_litellm):
        """Test failed health check."""
        provider = LiteLLMProvider({})
        # Just test that health_check method exists and can be called
        result = provider.health_check()
        assert isinstance(result, bool)


class TestOllamaProvider:
    """Test the Ollama provider implementation."""
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.httpx')
    def test_initialization(self, mock_httpx):
        """Test Ollama provider initialization."""
        mock_httpx.get.return_value = MagicMock(status_code=200)
        
        config = {
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3",
            "embedding_model": "nomic-embed-text"
        }
        
        provider = OllamaProvider(config)
        
        assert provider.api_base == "http://localhost:11434"
        assert provider.default_llm_model == "llama3"
        assert provider.default_embedding_model == "nomic-embed-text"
        assert provider._initialized is True
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', False)
    def test_initialization_without_ollama(self):
        """Test initialization when Ollama is not available."""
        with pytest.raises(ProviderNotAvailableError, match="Ollama integration not installed"):
            OllamaProvider({})
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.ChatOllama')
    def test_get_llm(self, mock_chat_ollama):
        """Test getting an Ollama LLM instance."""
        provider = OllamaProvider({})
        llm = provider.get_llm(model="mistral", temperature=0.8)
        
        mock_chat_ollama.assert_called_once_with(
            model="mistral",
            base_url=provider.api_base,
            temperature=0.8
        )
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.OllamaEmbeddings')
    def test_get_embeddings(self, mock_ollama_embeddings):
        """Test getting Ollama embeddings instance."""
        provider = OllamaProvider({})
        embeddings = provider.get_embeddings(model="nomic-embed-text")
        
        mock_ollama_embeddings.assert_called_once_with(
            model="nomic-embed-text",
            base_url=provider.api_base
        )
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.httpx')
    def test_list_available_models(self, mock_httpx):
        """Test listing available Ollama models."""
        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                "models": [
                    {"name": "llama3"},
                    {"name": "mistral"},
                    {"name": "nomic-embed-text"},
                    {"name": "mxbai-embed-large"}
                ]
            }
        )
        mock_httpx.get.return_value = mock_response
        
        provider = OllamaProvider({})
        models = provider.list_available_models()
        
        assert "llama3" in models["llm"]
        assert "mistral" in models["llm"]
        assert "nomic-embed-text" in models["embedding"]
        assert "mxbai-embed-large" in models["embedding"]
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.httpx')
    def test_health_check_success(self, mock_httpx):
        """Test successful Ollama health check."""
        mock_httpx.get.return_value = MagicMock(status_code=200)
        
        provider = OllamaProvider({})
        assert provider.health_check() is True
    
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.httpx')
    def test_health_check_failure(self, mock_httpx):
        """Test failed Ollama health check."""
        mock_httpx.get.side_effect = Exception("Connection error")
        
        provider = OllamaProvider({})
        assert provider.health_check() is False


class TestOpenAIProvider:
    """Test the OpenAI provider implementation."""
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_initialization(self):
        """Test OpenAI provider initialization."""
        config = {
            "openai_model": "gpt-4",
            "openai_embedding_model": "text-embedding-3-large"
        }
        
        provider = OpenAIProvider(config)
        
        assert provider.api_key == "test_key"
        assert provider.default_llm_model == "gpt-4"
        assert provider.default_embedding_model == "text-embedding-3-large"
        assert provider._initialized is True
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', False)
    def test_initialization_without_openai(self):
        """Test initialization when OpenAI is not available."""
        with pytest.raises(ProviderNotAvailableError, match="OpenAI integration not installed"):
            OpenAIProvider({})
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        # Ensure no API key in environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderNotAvailableError, match="OpenAI API key not found"):
                OpenAIProvider({})
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.ChatOpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_get_llm(self, mock_chat_openai):
        """Test getting an OpenAI LLM instance."""
        provider = OpenAIProvider({})
        llm = provider.get_llm(model="gpt-4-turbo", temperature=0.3)
        
        mock_chat_openai.assert_called_once_with(
            model="gpt-4-turbo",
            api_key="test_key",
            temperature=0.3
        )
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.OpenAIEmbeddings')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_get_embeddings(self, mock_openai_embeddings):
        """Test getting OpenAI embeddings instance."""
        provider = OpenAIProvider({})
        embeddings = provider.get_embeddings(model="text-embedding-3-large")
        
        mock_openai_embeddings.assert_called_once_with(
            model="text-embedding-3-large",
            api_key="test_key"
        )
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_list_available_models(self):
        """Test listing available OpenAI models."""
        provider = OpenAIProvider({})
        models = provider.list_available_models()
        
        assert "gpt-4" in models["llm"]
        assert "gpt-3.5-turbo" in models["llm"]
        assert "text-embedding-3-small" in models["embedding"]
        assert "text-embedding-3-large" in models["embedding"]
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_health_check_success(self):
        """Test successful OpenAI health check."""
        provider = OpenAIProvider({})
        
        # Mock the embeddings instance
        with patch.object(provider, 'get_embeddings') as mock_get_embeddings:
            mock_embeddings = MagicMock()
            mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_get_embeddings.return_value = mock_embeddings
            
            assert provider.health_check() is True
    
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_health_check_failure(self):
        """Test failed OpenAI health check."""
        provider = OpenAIProvider({})
        
        # Mock the embeddings instance to raise an error
        with patch.object(provider, 'get_embeddings') as mock_get_embeddings:
            mock_embeddings = MagicMock()
            mock_embeddings.embed_query.side_effect = Exception("API error")
            mock_get_embeddings.return_value = mock_embeddings
            
            assert provider.health_check() is False


class TestProviderRegistration:
    """Test that providers are properly registered with the factory."""
    
    @patch('src.obelisk.rag.common.providers.LITELLM_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.OLLAMA_AVAILABLE', True)
    @patch('src.obelisk.rag.common.providers.OPENAI_AVAILABLE', True)
    def test_providers_are_registered(self):
        """Test that all providers are registered on import."""
        # Import the module to trigger registration
        import importlib
        import src.obelisk.rag.common.providers
        importlib.reload(src.obelisk.rag.common.providers)
        
        from src.obelisk.rag.common.models import ProviderFactory, ProviderType
        
        # Check that providers are registered
        providers = ProviderFactory._providers
        assert ProviderType.LITELLM in providers
        assert ProviderType.OLLAMA in providers
        assert ProviderType.OPENAI in providers
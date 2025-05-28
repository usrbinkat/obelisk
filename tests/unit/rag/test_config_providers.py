"""
Unit tests for provider-related configuration.
"""

import pytest
import os
from unittest.mock import patch
from typing import Dict, Any

from src.obelisk.rag.common.config import RAGConfig, get_config, set_config


class TestRAGConfigProviderSupport:
    """Test RAG configuration support for model providers."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_provider_config(self):
        """Test default provider configuration values without environment variables."""
        config = RAGConfig()
        
        # Model provider settings
        assert config.get("model_provider") == "litellm"
        assert config.get("enable_fallback") is True
        assert config.get("fallback_providers") == ["ollama", "openai"]
        
        # LiteLLM settings
        assert config.get("litellm_api_base") == "http://litellm:4000"
        assert config.get("litellm_api_key") is None
        
        # Ollama settings
        assert config.get("ollama_url") == "http://localhost:11434"
        assert config.get("ollama_model") == "llama3"
        
        # OpenAI settings
        assert config.get("openai_api_key") is None
        assert config.get("openai_model") == "gpt-4o"
        assert config.get("openai_embedding_model") == "text-embedding-3-large"
        
        # Model preferences
        assert config.get("llm_model") == "gpt-4o"
        assert config.get("embedding_model") == "text-embedding-3-large"
        
        # Advanced settings
        assert config.get("model_temperature") == 0.7
        assert config.get("model_max_tokens") is None
        assert config.get("model_timeout") == 30
        assert config.get("model_retry_attempts") == 3
    
    def test_custom_provider_config(self):
        """Test custom provider configuration."""
        custom_config = {
            "model_provider": "openai",
            "openai_api_key": "test_key",
            "openai_model": "gpt-4",
            "llm_model": "gpt-4",
            "model_temperature": 0.5
        }
        
        config = RAGConfig(custom_config)
        
        assert config.get("model_provider") == "openai"
        assert config.get("openai_api_key") == "test_key"
        assert config.get("openai_model") == "gpt-4"
        assert config.get("llm_model") == "gpt-4"
        assert config.get("model_temperature") == 0.5
    
    @patch.dict(os.environ, {
        "MODEL_PROVIDER": "ollama",
        "ENABLE_FALLBACK": "false",
        "LITELLM_API_BASE": "http://custom:5000",
        "LITELLM_API_KEY": "env_litellm_key",
        "OLLAMA_URL": "http://custom-ollama:11434",
        "OLLAMA_MODEL": "mistral",
        "OPENAI_API_KEY": "env_openai_key",
        "OPENAI_MODEL": "gpt-4-turbo",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
        "LLM_MODEL": "mistral",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "MODEL_TEMPERATURE": "0.3",
        "MODEL_MAX_TOKENS": "2000",
        "MODEL_TIMEOUT": "60",
        "MODEL_RETRY_ATTEMPTS": "5"
    })
    def test_env_variable_loading(self):
        """Test loading provider configuration from environment variables."""
        config = RAGConfig()
        
        # Model provider settings
        assert config.get("model_provider") == "ollama"
        assert config.get("enable_fallback") is False
        
        # LiteLLM settings
        assert config.get("litellm_api_base") == "http://custom:5000"
        assert config.get("litellm_api_key") == "env_litellm_key"
        
        # Ollama settings
        assert config.get("ollama_url") == "http://custom-ollama:11434"
        assert config.get("ollama_model") == "mistral"
        
        # OpenAI settings
        assert config.get("openai_api_key") == "env_openai_key"
        assert config.get("openai_model") == "gpt-4-turbo"
        assert config.get("openai_embedding_model") == "text-embedding-3-large"
        
        # Model preferences
        assert config.get("llm_model") == "mistral"
        assert config.get("embedding_model") == "nomic-embed-text"
        
        # Advanced settings
        assert config.get("model_temperature") == 0.3
        assert config.get("model_max_tokens") == 2000
        assert config.get("model_timeout") == 60
        assert config.get("model_retry_attempts") == 5
    
    @patch.dict(os.environ, {
        "MODEL_PROVIDER": "litellm",
        "LITELLM_API_KEY": "env_key"
    })
    def test_config_priority(self):
        """Test configuration priority: custom > env > default."""
        custom_config = {
            "model_provider": "openai",  # Should override env
            "litellm_api_key": "custom_key",  # Should override env
            "ollama_url": "http://custom:11434"  # Should override default
        }
        
        config = RAGConfig(custom_config)
        
        # Custom overrides env
        assert config.get("model_provider") == "openai"
        assert config.get("litellm_api_key") == "custom_key"
        
        # Custom overrides default
        assert config.get("ollama_url") == "http://custom:11434"
        
        # Default is used when no override
        assert config.get("ollama_model") == "llama3"
    
    def test_get_and_set_provider_config(self):
        """Test getting and setting provider configuration values."""
        config = RAGConfig()
        
        # Test get with default
        assert config.get("nonexistent_key", "default_value") == "default_value"
        
        # Test set
        config.set("model_provider", "ollama")
        assert config.get("model_provider") == "ollama"
        
        config.set("custom_provider_setting", "custom_value")
        assert config.get("custom_provider_setting") == "custom_value"
    
    def test_global_config_functions(self):
        """Test global configuration functions."""
        # Get default config
        config = get_config()
        assert isinstance(config, RAGConfig)
        
        # Set new values
        set_config({
            "model_provider": "openai",
            "openai_api_key": "test_key"
        })
        
        # Verify changes
        assert get_config().get("model_provider") == "openai"
        assert get_config().get("openai_api_key") == "test_key"
    
    def test_boolean_env_parsing(self):
        """Test parsing boolean values from environment variables."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("yes", True),
            ("Yes", True),
            ("YES", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("no", False),
            ("No", False),
            ("NO", False),
            ("0", False),
            ("anything_else", False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"ENABLE_FALLBACK": env_value}):
                config = RAGConfig()
                assert config.get("enable_fallback") == expected, f"Failed for env_value: {env_value}"
    
    def test_all_provider_configs_compatible(self):
        """Test that all provider configurations can coexist."""
        config = RAGConfig({
            "model_provider": "litellm",
            "litellm_api_base": "http://litellm:4000",
            "litellm_api_key": "litellm_key",
            "ollama_url": "http://ollama:11434",
            "ollama_model": "llama3",
            "openai_api_key": "openai_key",
            "openai_model": "gpt-4",
            "llm_model": "llama3",
            "embedding_model": "mxbai-embed-large"
        })
        
        # All settings should be accessible
        assert config.get("litellm_api_base") == "http://litellm:4000"
        assert config.get("ollama_url") == "http://ollama:11434"
        assert config.get("openai_api_key") == "openai_key"
        
        # Provider selection should work
        assert config.get("model_provider") == "litellm"
        assert config.get("fallback_providers") == ["ollama", "openai"]
"""
Configuration management for the Obelisk RAG system.

This module provides the configuration management for the RAG system,
including default settings and configuration loading from different sources.
"""

import os
from typing import Dict, Any, Optional


class RAGConfig:
    """Configuration class for the RAG system."""
    
    DEFAULT_CONFIG = {
        # Paths and file locations
        "vault_dir": "./vault",
        
        # Milvus Vector Database
        "milvus_host": "milvus",
        "milvus_port": 19530,
        "milvus_user": "default",
        "milvus_password": "Milvus",
        # Note: Open-WebUI prefixes collections with "open_webui_" internally
        # If duplicate prefix issues occur (open_webui_open_webui_...), revisit this
        "milvus_collection": "open_webui_obelisk_rag",
        
        # Model provider configuration
        "model_provider": "litellm",  # Options: 'litellm', 'ollama', 'openai'
        "enable_fallback": True,
        "fallback_providers": ["ollama", "openai"],
        "force_litellm_proxy": True,  # Force all completions through LiteLLM
        
        # LiteLLM settings (primary provider)
        "litellm_api_base": "http://litellm:4000",
        "litellm_api_key": None,  # Will be loaded from env
        
        # Ollama settings (for hardware tuning operations only)
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        
        # OpenAI settings (accessed via LiteLLM)
        "openai_api_key": None,  # Will be loaded from env
        "openai_model": "gpt-4o",
        "openai_embedding_model": "text-embedding-3-large",
        
        # Model preferences (provider-agnostic)
        "llm_model": "gpt-4o",  # Default LLM model name
        "embedding_model": "text-embedding-3-large",  # Default embedding model
        "embedding_dim": 3072,  # Dimension for text-embedding-3-large
        
        # Processing settings
        "chunk_size": 2500,
        "chunk_overlap": 500,
        "retrieve_top_k": 5,
        
        # API settings
        "api_host": "0.0.0.0",
        "api_port": 8000,
        
        # Advanced settings
        "model_temperature": 0.7,
        "model_max_tokens": None,
        "model_timeout": 30,
        "model_retry_attempts": 3,
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with optional custom config."""
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Override with environment variables
        self._load_from_env()
        
        # Override with provided config
        if config:
            self.config.update(config)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            # Paths
            "VAULT_DIR": "vault_dir",
            
            # Milvus configuration
            "MILVUS_HOST": "milvus_host",
            "MILVUS_PORT": "milvus_port",
            "MILVUS_USER": "milvus_user",
            "MILVUS_PASSWORD": "milvus_password",
            "MILVUS_COLLECTION": "milvus_collection",
            
            # Model provider
            "MODEL_PROVIDER": "model_provider",
            "ENABLE_FALLBACK": "enable_fallback",
            "FORCE_LITELLM_PROXY": "force_litellm_proxy",
            
            # LiteLLM
            "LITELLM_API_BASE": "litellm_api_base",
            "LITELLM_API_KEY": "litellm_api_key",
            
            # Ollama
            "OLLAMA_URL": "ollama_url",
            "OLLAMA_MODEL": "ollama_model",
            
            # OpenAI
            "OPENAI_API_KEY": "openai_api_key",
            "OPENAI_MODEL": "openai_model",
            "OPENAI_EMBEDDING_MODEL": "openai_embedding_model",
            
            # Model preferences
            "LLM_MODEL": "llm_model",
            "EMBEDDING_MODEL": "embedding_model",
            "EMBEDDING_DIM": "embedding_dim",
            
            # Processing
            "CHUNK_SIZE": "chunk_size",
            "CHUNK_OVERLAP": "chunk_overlap",
            "RETRIEVE_TOP_K": "retrieve_top_k",
            
            # API
            "API_HOST": "api_host",
            "API_PORT": "api_port",
            
            # Advanced
            "MODEL_TEMPERATURE": "model_temperature",
            "MODEL_MAX_TOKENS": "model_max_tokens",
            "MODEL_TIMEOUT": "model_timeout",
            "MODEL_RETRY_ATTEMPTS": "model_retry_attempts",
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert to appropriate type based on default
                default_value = self.config[config_key]
                if isinstance(default_value, bool):
                    value = value.lower() in ("true", "yes", "1")
                elif isinstance(default_value, int):
                    value = int(value)
                elif isinstance(default_value, float):
                    value = float(value)
                elif default_value is None:
                    # Try to infer type from key name or value
                    if any(keyword in config_key for keyword in ["timeout", "port", "max_tokens", "retry_attempts", "top_k"]):
                        try:
                            value = int(value)
                        except ValueError:
                            pass  # Keep as string
                    elif any(keyword in config_key for keyword in ["temperature"]):
                        try:
                            value = float(value)
                        except ValueError:
                            pass  # Keep as string
                
                self.config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value


# Create a default config instance
default_config = RAGConfig()


def get_config() -> RAGConfig:
    """Get the default configuration instance."""
    return default_config


def set_config(config: Dict[str, Any]) -> None:
    """Update the default configuration with new values."""
    for key, value in config.items():
        default_config.set(key, value)
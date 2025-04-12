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
        "chroma_dir": "./.obelisk/vectordb",
        
        # Ollama settings
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        "embedding_model": "mxbai-embed-large",
        
        # Processing settings
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "retrieve_top_k": 3,
        
        # API settings
        "api_host": "0.0.0.0",
        "api_port": 8000,
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
            "VAULT_DIR": "vault_dir",
            "CHROMA_DIR": "chroma_dir",
            "OLLAMA_URL": "ollama_url",
            "OLLAMA_MODEL": "ollama_model",
            "EMBEDDING_MODEL": "embedding_model",
            "CHUNK_SIZE": "chunk_size",
            "CHUNK_OVERLAP": "chunk_overlap",
            "RETRIEVE_TOP_K": "retrieve_top_k",
            "API_HOST": "api_host",
            "API_PORT": "api_port",
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert to appropriate type based on default
                default_value = self.config[config_key]
                if isinstance(default_value, int):
                    value = int(value)
                elif isinstance(default_value, float):
                    value = float(value)
                elif isinstance(default_value, bool):
                    value = value.lower() in ("true", "yes", "1")
                
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
"""Tests for the Obelisk RAG configuration system."""

import os
import pytest
from unittest.mock import patch

from obelisk.rag.config import RAGConfig, get_config


def test_default_config():
    """Test that the default configuration has expected values."""
    config = RAGConfig()
    
    # Check default values
    assert config.get("vault_dir") == "./vault"
    assert config.get("chroma_dir") == "./.obelisk/vectordb"
    assert config.get("ollama_url") == "http://localhost:11434"
    assert config.get("ollama_model") == "llama3"
    assert config.get("embedding_model") == "mxbai-embed-large"
    assert config.get("chunk_size") == 1000
    assert config.get("chunk_overlap") == 200
    assert config.get("retrieve_top_k") == 3


def test_config_override():
    """Test that configuration can be overridden."""
    custom_config = {
        "vault_dir": "/custom/path",
        "chunk_size": 2000
    }
    
    config = RAGConfig(custom_config)
    
    # Check that values were overridden
    assert config.get("vault_dir") == "/custom/path"
    assert config.get("chunk_size") == 2000
    
    # Check that other values remain defaults
    assert config.get("chroma_dir") == "./.obelisk/vectordb"
    assert config.get("ollama_url") == "http://localhost:11434"


@patch.dict(os.environ, {
    "VAULT_DIR": "/env/path",
    "CHUNK_SIZE": "3000",
    "RETRIEVE_TOP_K": "5"
})
def test_config_env_override():
    """Test that configuration can be overridden by environment variables."""
    config = RAGConfig()
    
    # Check that environment variables take precedence
    assert config.get("vault_dir") == "/env/path"
    assert config.get("chunk_size") == 3000
    assert config.get("retrieve_top_k") == 5
    
    # Check that other values remain defaults
    assert config.get("chroma_dir") == "./.obelisk/vectordb"
    assert config.get("ollama_url") == "http://localhost:11434"


def test_get_config():
    """Test that get_config returns a RAGConfig instance."""
    config = get_config()
    assert isinstance(config, RAGConfig)
    
    # Verify it has the default values
    assert config.get("vault_dir") == "./vault"
    assert config.get("chroma_dir") == "./.obelisk/vectordb"


def test_config_set():
    """Test that configuration values can be set after initialization."""
    config = RAGConfig()
    
    # Set a value
    config.set("vault_dir", "/new/path")
    
    # Check that it was updated
    assert config.get("vault_dir") == "/new/path"
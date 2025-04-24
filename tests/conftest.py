"""
Common test fixtures for the Obelisk test suite.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_vault(temp_dir):
    """Create a sample vault with test content."""
    vault_dir = os.path.join(temp_dir, "vault")
    os.makedirs(vault_dir, exist_ok=True)
    
    # Create a sample markdown file
    md_content = """---
title: Test Document
date: 2025-04-24
---

# Test Document

This is a sample document for testing.

## Section 1

Content in section 1.

## Section 2

Content in section 2.
"""
    with open(os.path.join(vault_dir, "test.md"), "w") as f:
        f.write(md_content)
    
    return vault_dir

@pytest.fixture
def vector_db_dir(temp_dir):
    """Create a temporary directory for vector database."""
    vector_db_dir = os.path.join(temp_dir, "vectordb")
    os.makedirs(vector_db_dir, exist_ok=True)
    return vector_db_dir

@pytest.fixture
def mock_rag_config(sample_vault, vector_db_dir):
    """Create a mock RAG configuration for testing."""
    from src.obelisk.rag.common.config import RAGConfig
    
    return RAGConfig({
        "vault_dir": sample_vault,
        "chroma_dir": vector_db_dir,
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        "embedding_model": "mxbai-embed-large",
        "chunk_size": 500,
        "chunk_overlap": 100,
        "retrieve_top_k": 2,
        "api_host": "localhost",
        "api_port": 8001
    })
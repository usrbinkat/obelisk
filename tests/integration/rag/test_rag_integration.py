"""
Integration tests for the Obelisk RAG system.

These tests verify that all components of the restructured RAG system
work together correctly in the src-layout pattern.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

from langchain.schema.document import Document
from src.obelisk.rag.service.coordinator import RAGService
from src.obelisk.rag.common.config import RAGConfig
from src.obelisk.rag.document.processor import DocumentProcessor
from src.obelisk.rag.embedding.service import EmbeddingService
from src.obelisk.rag.storage.store import VectorStorage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_vault(temp_dir):
    """Create a test vault with sample markdown files."""
    # Create test vault directory
    vault_dir = os.path.join(temp_dir, "vault")
    os.makedirs(vault_dir, exist_ok=True)
    
    # Document template
    doc_template = """---
title: {title}
date: 2025-04-24
tags: {tags}
---

# {title}

{description}

## {section1_title}

{section1_content}

## {section2_title}

{section2_content}
"""
    
    # Create multiple test documents
    test_documents = [
        {
            "filename": "obelisk_intro.md",
            "title": "Introduction to Obelisk",
            "tags": "obelisk, introduction, overview",
            "description": "Obelisk is a tool that transforms Obsidian vaults into MkDocs Material Theme sites with AI integration.",
            "section1_title": "Core Features",
            "section1_content": "Obelisk provides seamless conversion of Obsidian features including wiki links, callouts, and comments.",
            "section2_title": "Architecture",
            "section2_content": "Obelisk consists of a Python package for conversion, a documentation content structure, and a container architecture."
        },
        {
            "filename": "rag_overview.md",
            "title": "RAG System Overview",
            "tags": "rag, vector, embedding",
            "description": "The Retrieval-Augmented Generation (RAG) system provides context-aware responses by retrieving relevant documents.",
            "section1_title": "Components",
            "section1_content": "The RAG system includes document processing, embedding generation, vector storage, and query processing.",
            "section2_title": "Vector Search",
            "section2_content": "Documents are embedded into vector space, allowing for semantic similarity search using ChromaDB or Milvus."
        },
        {
            "filename": "vector_db.md",
            "title": "Vector Database Integration",
            "tags": "vector, database, chromadb, milvus",
            "description": "Vector databases store and retrieve document embeddings for semantic search capabilities.",
            "section1_title": "ChromaDB",
            "section1_content": "ChromaDB is the default vector database used for local development and smaller deployments.",
            "section2_title": "Milvus",
            "section2_content": "Milvus integration is planned for larger deployments requiring more scalability and performance."
        }
    ]
    
    # Write the documents to the vault directory
    for doc in test_documents:
        with open(os.path.join(vault_dir, doc["filename"]), "w") as f:
            f.write(doc_template.format(**doc))
    
    # Create a subdirectory with additional documents
    advanced_dir = os.path.join(vault_dir, "advanced")
    os.makedirs(advanced_dir, exist_ok=True)
    
    # Create a document in the subdirectory
    with open(os.path.join(advanced_dir, "configuration.md"), "w") as f:
        f.write(doc_template.format(
            title="Advanced Configuration",
            tags="configuration, setup",
            description="Configure Obelisk for different deployment scenarios and requirements.",
            section1_title="Environment Variables",
            section1_content="Obelisk can be configured using environment variables for various settings.",
            section2_title="Configuration Files",
            section2_content="YAML configuration files provide a declarative way to configure Obelisk components."
        ))
    
    return vault_dir


@pytest.fixture
def config(temp_dir, test_vault):
    """Create a test configuration."""
    return RAGConfig({
        "vault_dir": test_vault,
        "chroma_dir": os.path.join(temp_dir, "vectordb"),
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        "embedding_model": "mxbai-embed-large",
        "chunk_size": 500,
        "chunk_overlap": 100,
        "retrieve_top_k": 2
    })


@pytest.fixture
def mock_ollama_chat():
    """Create a mock ChatOllama."""
    with patch('src.obelisk.rag.service.coordinator.ChatOllama') as mock:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is a mock response from the model."
        mock_instance.invoke.return_value = mock_response
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ollama_embeddings():
    """Create a mock OllamaEmbeddings."""
    with patch('src.obelisk.rag.embedding.service.OllamaEmbeddings') as mock:
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(10)]
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chroma():
    """Create a mock Chroma."""
    with patch('src.obelisk.rag.storage.store.Chroma') as mock:
        mock_instance = MagicMock()
        
        # Configure mock methods
        mock_instance.add_documents.return_value = None
        mock_instance._collection = MagicMock()
        mock_instance._collection.count.return_value = 0
        mock_instance.similarity_search_by_vector.return_value = [
            Document(page_content="Sample Document content", metadata={"source": "sample.md"})
        ]
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def service(config, mock_ollama_chat, mock_ollama_embeddings, mock_chroma):
    """Create a RAG service with real components but mocked dependencies."""
    return RAGService(config)


def test_end_to_end_flow(service, test_vault, mock_chroma, mock_ollama_embeddings, mock_ollama_chat):
    """Test the end-to-end flow of the RAG system."""
    # Process the vault
    count = service.process_vault()
    
    # Verify that documents were processed (4 documents in test_vault)
    assert count > 0
    
    # Verify that the embedding service was called
    mock_ollama_embeddings.embed_documents.assert_called()
    
    # Verify that the storage service was called
    mock_chroma.add_documents.assert_called()
    
    # Query the system
    query_text = "What is Obelisk?"
    result = service.query(query_text)
    
    # Verify that the embedding service was called
    mock_ollama_embeddings.embed_query.assert_called_with(query_text)
    
    # Verify that the storage service was called
    mock_chroma.similarity_search_by_vector.assert_called()
    
    # Verify that the LLM was called
    mock_ollama_chat.invoke.assert_called()
    
    # Check the result format
    assert "query" in result
    assert "context" in result
    assert "response" in result
    assert result["query"] == query_text
    assert result["response"] == "This is a mock response from the model."
    assert len(result["context"]) > 0


def test_src_layout_imports(test_vault, temp_dir):
    """Test that the src-layout pattern imports work correctly."""
    # This test explicitly verifies that the imports in the src-layout pattern work
    
    # 1. Create a configuration
    config = RAGConfig({
        "vault_dir": test_vault,
        "chroma_dir": os.path.join(temp_dir, "vectordb"),
        "ollama_url": "http://mock-ollama",
        "ollama_model": "mock-model"
    })
    
    # 2. Instantiate each component to verify import paths
    with patch('src.obelisk.rag.embedding.service.OllamaEmbeddings'):
        embedding_service = EmbeddingService(config)
        assert embedding_service is not None
        
        with patch('src.obelisk.rag.storage.store.Chroma'):
            storage_service = VectorStorage(embedding_service=embedding_service, config=config)
            assert storage_service is not None
            
            document_processor = DocumentProcessor(config)
            assert document_processor is not None
            
            with patch('src.obelisk.rag.service.coordinator.ChatOllama'):
                rag_service = RAGService(config)
                assert rag_service is not None


def test_recursive_document_processing(service, test_vault, mock_chroma):
    """Test that documents in subdirectories are processed correctly."""
    # Configure the mock to track which files are processed
    processed_files = []
    
    def side_effect(docs):
        nonlocal processed_files
        for doc in docs:
            if "source" in doc.metadata:
                processed_files.append(doc.metadata["source"])
        return None
    
    mock_chroma.add_documents.side_effect = side_effect
    
    # Process the vault
    service.process_vault()
    
    # Verify that files in subdirectories were processed
    assert any("advanced/configuration.md" in path for path in processed_files)
"""Tests for the Obelisk RAG embedding service."""

import os
import pytest
from unittest.mock import MagicMock, patch

from langchain.schema.document import Document
from obelisk.rag.embedding import EmbeddingService
from obelisk.rag.config import RAGConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    return RAGConfig({
        "ollama_url": "http://localhost:11434",
        "embedding_model": "mxbai-embed-large"
    })


@pytest.fixture
def mock_ollama_embeddings():
    """Create a mock OllamaEmbeddings object."""
    with patch('obelisk.rag.embedding.OllamaEmbeddings') as mock:
        mock_instance = MagicMock()
        # Define mock behavior for embed_documents and embed_query
        mock_instance.embed_documents.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ]
        mock_instance.embed_query.return_value = [0.7, 0.8, 0.9]
        
        # Make the constructor return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def embedding_service(config, mock_ollama_embeddings):
    """Create an embedding service with a mocked OllamaEmbeddings."""
    return EmbeddingService(config)


def test_service_initialization(embedding_service, config):
    """Test that the embedding service initializes correctly."""
    assert embedding_service.config == config
    assert embedding_service.model_name == "mxbai-embed-large"
    assert embedding_service.ollama_url == "http://localhost:11434"
    assert embedding_service.embeddings_model is not None


def test_embed_documents(embedding_service, mock_ollama_embeddings):
    """Test embedding documents."""
    # Create some test documents
    docs = [
        Document(page_content="This is a test document", metadata={}),
        Document(page_content="This is another test document", metadata={})
    ]
    
    # Process the documents
    result_docs = embedding_service.embed_documents(docs)
    
    # Check that the mock was called with the expected arguments
    mock_ollama_embeddings.embed_documents.assert_called_once_with(
        ["This is a test document", "This is another test document"]
    )
    
    # We no longer store embeddings in metadata directly for better serialization
    # Instead, we just check that the embedding function was called
    # and the documents were processed and returned
    assert result_docs == docs


def test_embed_query(embedding_service, mock_ollama_embeddings):
    """Test embedding a query string."""
    query = "What is Obelisk?"
    embedding = embedding_service.embed_query(query)
    
    # Check that the mock was called with the expected arguments
    mock_ollama_embeddings.embed_query.assert_called_once_with(query)
    
    # Check that the correct embedding was returned
    assert embedding == [0.7, 0.8, 0.9]


def test_empty_documents(embedding_service, mock_ollama_embeddings):
    """Test handling of empty document list."""
    result = embedding_service.embed_documents([])
    
    # The method should return the empty list without calling the model
    assert result == []
    mock_ollama_embeddings.embed_documents.assert_not_called()


def test_error_handling(embedding_service, mock_ollama_embeddings):
    """Test error handling for embedding generation."""
    # Set up the mock to raise an exception
    mock_ollama_embeddings.embed_documents.side_effect = Exception("Test error")
    
    # Create a test document
    docs = [Document(page_content="This will cause an error", metadata={})]
    
    # Process the document - should not raise an exception
    result_docs = embedding_service.embed_documents(docs)
    
    # Should return the original documents
    assert result_docs == docs
"""Unit tests for the Obelisk RAG embedding service."""

import os
import pytest
from unittest.mock import MagicMock, patch, Mock

from langchain.schema.document import Document
from src.obelisk.rag.embedding.service import EmbeddingService
from src.obelisk.rag.common.config import RAGConfig
from src.obelisk.rag.common.models import ModelProvider


@pytest.fixture
def config():
    """Create a test configuration."""
    return RAGConfig({
        "model_provider": "ollama",
        "ollama_url": "http://localhost:11434",
        "embedding_model": "mxbai-embed-large"
    })


@pytest.fixture
def mock_provider():
    """Create a mock ModelProvider."""
    provider = Mock(spec=ModelProvider)
    
    # Create a mock embeddings instance
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]
    mock_embeddings.embed_query.return_value = [0.7, 0.8, 0.9]
    
    # Make provider.get_embeddings return the mock embeddings
    provider.get_embeddings.return_value = mock_embeddings
    
    return provider


@pytest.fixture
def embedding_service(config, mock_provider):
    """Create an embedding service with a mocked provider."""
    # Pass the mock provider directly to avoid creating a real one
    return EmbeddingService(config, provider=mock_provider)


def test_service_initialization(embedding_service, config, mock_provider):
    """Test that the embedding service initializes correctly."""
    assert embedding_service.config == config
    assert embedding_service.model_name == "mxbai-embed-large"
    assert embedding_service.provider == mock_provider
    assert embedding_service.embeddings_model is not None
    
    # Verify that the provider's get_embeddings was called with the correct model
    mock_provider.get_embeddings.assert_called_once_with(
        model="mxbai-embed-large"
    )


def test_embed_documents(embedding_service):
    """Test embedding documents."""
    # Create some test texts
    texts = [
        "This is a test document",
        "This is another test document"
    ]
    
    # Process the texts
    embeddings = embedding_service.embed_documents(texts)
    
    # Check that the mock was called with the expected arguments
    embedding_service.embeddings_model.embed_documents.assert_called_once_with(texts)
    
    # Check we got embeddings back
    assert len(embeddings) == 2
    # Mock returns 3-element arrays
    assert all(len(emb) == 3 for emb in embeddings)


def test_embed_query(embedding_service):
    """Test embedding a query string."""
    query = "What is Obelisk?"
    embedding = embedding_service.embed_query(query)
    
    # Check that the mock was called with the expected arguments
    embedding_service.embeddings_model.embed_query.assert_called_once_with(query)
    
    # Check that the correct embedding was returned
    assert embedding == [0.7, 0.8, 0.9]


def test_empty_documents(embedding_service):
    """Test handling of empty document list."""
    result = embedding_service.embed_documents([])
    
    # The method should return the empty list without calling the model
    assert result == []
    embedding_service.embeddings_model.embed_documents.assert_not_called()


def test_error_handling(embedding_service):
    """Test error handling for embedding generation."""
    # Set up the mock to raise an exception
    embedding_service.embeddings_model.embed_documents.side_effect = Exception("Test error")
    
    # Create test texts
    texts = ["This will cause an error"]
    
    # Process the texts - should not raise an exception
    embeddings = embedding_service.embed_documents(texts)
    
    # Should return empty list on error
    assert embeddings == []


def test_service_with_auto_provider():
    """Test that the service creates a provider automatically when none is provided."""
    with patch('src.obelisk.rag.embedding.service.ModelProviderFactory') as mock_factory:
        # Create a mock provider
        mock_provider = Mock(spec=ModelProvider)
        mock_embeddings = MagicMock()
        mock_provider.get_embeddings.return_value = mock_embeddings
        mock_factory.create.return_value = mock_provider
        
        # Create service without passing a provider
        config = RAGConfig({
            "model_provider": "litellm",
            "embedding_model": "text-embedding-ada-002"
        })
        service = EmbeddingService(config)
        
        # Verify ModelProviderFactory.create was called
        mock_factory.create.assert_called_once()
        
        # Verify the service has the auto-created provider
        assert service.provider == mock_provider
        assert service.embeddings_model == mock_embeddings
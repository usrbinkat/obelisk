"""Tests for the Obelisk RAG vector storage service."""

import os
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from langchain.schema.document import Document
from obelisk.rag.storage import VectorStorage
from obelisk.rag.config import RAGConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test configuration with temporary directory."""
    return RAGConfig({
        "ollama_url": "http://localhost:11434",
        "embedding_model": "mxbai-embed-large",
        "chroma_dir": temp_dir,
        "retrieve_top_k": 2
    })


@pytest.fixture
def mock_chroma():
    """Create a mock Chroma instance."""
    with patch('obelisk.rag.storage.Chroma') as mock:
        mock_instance = MagicMock()
        
        # Configure mock methods
        mock_instance.add_documents.return_value = None
        mock_instance.similarity_search.return_value = [
            Document(page_content="Test result 1", metadata={"score": 0.9}),
            Document(page_content="Test result 2", metadata={"score": 0.8})
        ]
        mock_instance.similarity_search_by_vector.return_value = [
            Document(page_content="Test vector result 1", metadata={"score": 0.95}),
            Document(page_content="Test vector result 2", metadata={"score": 0.85})
        ]
        mock_instance._collection = MagicMock()
        mock_instance._collection.count.return_value = 42
        
        # Make the constructor return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    mock_service = MagicMock()
    mock_service.embeddings_model = MagicMock()
    return mock_service


@pytest.fixture
def storage_service(config, mock_chroma, mock_embedding_service):
    """Create a storage service with mocked dependencies."""
    return VectorStorage(embedding_service=mock_embedding_service, config=config)


def test_service_initialization(storage_service, config, temp_dir):
    """Test that the storage service initializes correctly."""
    assert storage_service.config == config
    assert storage_service.db_path == temp_dir
    assert storage_service.embedding_service is not None
    assert storage_service.store is not None
    
    # Check directory was created
    assert os.path.exists(temp_dir)


def test_add_documents(storage_service, mock_chroma):
    """Test adding documents to the vector store."""
    # Create some test documents
    docs = [
        Document(page_content="Test document 1", metadata={}),
        Document(page_content="Test document 2", metadata={})
    ]
    
    # Add the documents
    storage_service.add_documents(docs)
    
    # Check that the mock was called correctly
    mock_chroma.add_documents.assert_called_once_with(docs)
    mock_chroma.persist.assert_called_once()


def test_search(storage_service, mock_chroma):
    """Test searching the vector store."""
    query = "Test query"
    results = storage_service.search(query)
    
    # Check that the mock was called correctly
    mock_chroma.similarity_search.assert_called_once_with(query, k=2)
    
    # Check results
    assert len(results) == 2
    assert results[0].page_content == "Test result 1"
    assert results[1].page_content == "Test result 2"


def test_search_with_embedding(storage_service, mock_chroma):
    """Test searching with a pre-computed embedding."""
    embedding = [0.1, 0.2, 0.3]
    results = storage_service.search_with_embedding(embedding)
    
    # Check that the mock was called correctly
    mock_chroma.similarity_search_by_vector.assert_called_once_with(embedding, k=2)
    
    # Check results
    assert len(results) == 2
    assert results[0].page_content == "Test vector result 1"
    assert results[1].page_content == "Test vector result 2"


def test_delete_documents(storage_service, mock_chroma):
    """Test deleting documents from the vector store."""
    ids = ["doc1", "doc2"]
    storage_service.delete_documents(ids)
    
    # Check that the mock was called correctly
    mock_chroma.delete.assert_called_once_with(ids)
    mock_chroma.persist.assert_called_once()


def test_get_collection_stats(storage_service, mock_chroma):
    """Test getting statistics about the vector store."""
    stats = storage_service.get_collection_stats()
    
    # Check that the mock was called correctly
    mock_chroma._collection.count.assert_called_once()
    
    # Check stats
    assert stats["count"] == 42
    assert stats["path"] == storage_service.db_path


def test_error_handling(storage_service, mock_chroma):
    """Test error handling in the storage service."""
    # Configure the mock to raise an exception
    mock_chroma.similarity_search.side_effect = Exception("Test error")
    
    # Test search with error
    results = storage_service.search("query that causes error")
    
    # Should return empty list
    assert results == []
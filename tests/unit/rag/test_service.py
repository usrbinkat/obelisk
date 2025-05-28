"""Unit tests for the Obelisk RAG service integration."""

import os
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, Mock

from langchain.schema.document import Document
from src.obelisk.rag.service.coordinator import RAGService
from src.obelisk.rag.common.config import RAGConfig
from src.obelisk.rag.common.models import ModelProvider


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test configuration."""
    return RAGConfig({
        "model_provider": "ollama",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        "llm_model": "llama3",
        "embedding_model": "mxbai-embed-large",
        "chroma_dir": os.path.join(temp_dir, "vectordb"),
        "vault_dir": temp_dir,
        "retrieve_top_k": 2
    })


@pytest.fixture
def mock_provider():
    """Create a mock ModelProvider."""
    provider = Mock(spec=ModelProvider)
    
    # Create mock LLM instance
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "This is a mock response from the model."
    mock_llm.invoke.return_value = mock_response
    
    # Create mock embeddings instance
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    # Configure provider to return our mocks
    provider.get_llm.return_value = mock_llm
    provider.get_embeddings.return_value = mock_embeddings
    
    return provider


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    with patch('src.obelisk.rag.service.coordinator.EmbeddingService') as mock:
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Make the constructor return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service."""
    with patch('src.obelisk.rag.service.coordinator.VectorStorage') as mock:
        mock_instance = MagicMock()
        mock_instance.search_with_embedding.return_value = [
            Document(page_content="Relevant document 1", metadata={"source": "doc1.md"}),
            Document(page_content="Relevant document 2", metadata={"source": "doc2.md"})
        ]
        mock_instance.get_collection_stats.return_value = {
            "count": 42,
            "path": "/path/to/vectordb"
        }
        
        # Make the constructor return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_document_processor():
    """Create a mock document processor."""
    with patch('src.obelisk.rag.service.coordinator.DocumentProcessor') as mock:
        mock_instance = MagicMock()
        mock_instance.process_directory.return_value = [
            Document(page_content="Test document", metadata={"source": "test.md"})
            for _ in range(10)
        ]
        
        # Make the constructor return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def service(config, mock_provider, mock_embedding_service, 
            mock_storage_service, mock_document_processor):
    """Create a RAG service with mocked components."""
    # Patch EmbeddingService to pass the provider along
    mock_embedding_service.provider = mock_provider
    
    return RAGService(config, provider=mock_provider)


def test_service_initialization(service, config):
    """Test that the service initializes correctly."""
    assert service.config == config
    assert service.embedding_service is not None
    assert service.storage_service is not None
    assert service.document_processor is not None
    assert service.llm is not None
    assert service.watcher is None


def test_process_vault(service, mock_document_processor):
    """Test processing all documents in the vault."""
    count = service.process_vault()
    
    # Check that the document processor was called
    mock_document_processor.process_directory.assert_called_once()
    
    # Count should be 10 (from our mock)
    assert count == 10


def test_query_with_context(service, mock_embedding_service, mock_storage_service):
    """Test querying the system with results."""
    query_text = "What is Obelisk?"
    result = service.query(query_text)
    
    # Check that services were called with correct arguments
    mock_embedding_service.embed_query.assert_called_once_with(query_text)
    mock_storage_service.search_with_embedding.assert_called_once()
    service.llm.invoke.assert_called_once()
    
    # Check result format
    assert result["query"] == query_text
    assert result["response"] == "This is a mock response from the model."
    assert len(result["context"]) == 2
    assert result["no_context"] is False


def test_query_without_context(service, mock_embedding_service, mock_storage_service):
    """Test querying the system with no results."""
    # Configure mock to return empty results
    mock_storage_service.search_with_embedding.return_value = []
    
    query_text = "Query with no relevant documents"
    result = service.query(query_text)
    
    # Check result format for no-context case
    assert result["query"] == query_text
    assert result["response"] == "This is a mock response from the model."
    assert result["context"] == []
    assert result["no_context"] is True


def test_get_stats(service, mock_storage_service):
    """Test getting system statistics."""
    stats = service.get_stats()
    
    # Check stats
    assert stats["document_count"] == 42
    assert stats["vector_db_path"] == "/path/to/vectordb"
    assert stats["model_provider"] == "ollama"
    assert stats["llm_model"] == "llama3"
    assert stats["embedding_model"] == "mxbai-embed-large"
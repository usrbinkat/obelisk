"""Unit tests for the Obelisk RAG Milvus vector storage service."""

import pytest
from unittest.mock import MagicMock, patch

from langchain.schema.document import Document
from src.obelisk.rag.storage.store import VectorStorage
from src.obelisk.rag.common.config import RAGConfig


@pytest.fixture
def config():
    """Create a test configuration for Milvus."""
    return RAGConfig({
        "milvus_host": "milvus",
        "milvus_port": 19530,
        "milvus_user": "default",
        "milvus_password": "Milvus",
        "milvus_collection": "test_obelisk_rag",
        "embedding_dim": 3072,
        "retrieve_top_k": 5
    })


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    mock_service = MagicMock()
    
    # Mock embed_documents to return 3072-dimensional vectors
    mock_service.embed_documents.return_value = [
        [0.1] * 3072,  # Mock embedding for doc 1
        [0.2] * 3072   # Mock embedding for doc 2
    ]
    
    # Mock embed_query to return a 3072-dimensional vector
    mock_service.embed_query.return_value = [0.3] * 3072
    
    return mock_service


@pytest.fixture
def mock_milvus():
    """Create mock Milvus objects."""
    with patch('src.obelisk.rag.storage.store.connections') as mock_connections, \
         patch('src.obelisk.rag.storage.store.Collection') as mock_collection_class, \
         patch('src.obelisk.rag.storage.store.utility') as mock_utility:
        
        # Mock connections
        mock_connections.connect.return_value = None
        
        # Mock utility
        mock_utility.has_collection.return_value = True
        
        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.insert.return_value = MagicMock(primary_keys=["id1", "id2"])
        mock_collection.flush.return_value = None
        mock_collection.load.return_value = None
        mock_collection.num_entities = 42
        
        # Mock search results
        mock_hit1 = MagicMock()
        mock_hit1.entity.get.side_effect = lambda key, default=None: {
            "content": "Test result 1",
            "metadata": {"source": "test1.md"},
            "doc_id": "test1.md"
        }.get(key, default)
        
        mock_hit2 = MagicMock()
        mock_hit2.entity.get.side_effect = lambda key, default=None: {
            "content": "Test result 2",
            "metadata": {"source": "test2.md"},
            "doc_id": "test2.md"
        }.get(key, default)
        
        # Configure search to return results directly
        mock_collection.search.return_value = [[mock_hit1, mock_hit2]]
        
        # Make Collection constructor return our mock
        mock_collection_class.return_value = mock_collection
        
        yield {
            "connections": mock_connections,
            "collection_class": mock_collection_class,
            "collection": mock_collection,
            "utility": mock_utility
        }


@pytest.fixture
def storage_service(config, mock_milvus, mock_embedding_service):
    """Create a storage service with mocked dependencies."""
    return VectorStorage(embedding_service=mock_embedding_service, config=config)


def test_service_initialization(storage_service, config, mock_milvus):
    """Test that the storage service initializes correctly."""
    assert storage_service.config == config
    assert storage_service.milvus_host == "milvus"
    assert storage_service.milvus_port == 19530
    assert storage_service.collection_name == "test_obelisk_rag"
    assert storage_service.embedding_dim == 3072
    
    # Check Milvus connection was made
    mock_milvus["connections"].connect.assert_called_once_with(
        alias="default",
        host="milvus",
        port=19530,
        user="default",
        password="Milvus"
    )
    
    # Check collection was loaded
    mock_milvus["collection"].load.assert_called_once()


def test_add_documents(storage_service, mock_milvus, mock_embedding_service):
    """Test adding documents to the Milvus vector store."""
    # Create test documents
    docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.md"}),
        Document(page_content="Test document 2", metadata={"source": "test2.md"})
    ]
    
    # Add the documents
    with patch('uuid.uuid4', side_effect=["id1", "id2"]):
        ids = storage_service.add_documents(docs)
    
    # Check embeddings were generated
    mock_embedding_service.embed_documents.assert_called_once_with(
        ["Test document 1", "Test document 2"]
    )
    
    # Check Milvus insert was called with correct data
    mock_milvus["collection"].insert.assert_called_once()
    insert_args = mock_milvus["collection"].insert.call_args[0][0]
    
    # Verify the structure (5 lists: ids, embeddings, contents, metadatas, doc_ids)
    assert len(insert_args) == 5
    assert insert_args[0] == ["id1", "id2"]  # IDs
    assert len(insert_args[1]) == 2  # Embeddings
    assert insert_args[2] == ["Test document 1", "Test document 2"]  # Contents
    assert len(insert_args[3]) == 2  # Metadatas
    assert insert_args[4] == ["test1.md", "test2.md"]  # Doc IDs
    
    # Check flush was called
    mock_milvus["collection"].flush.assert_called_once()
    
    # Check return value
    assert ids == ["id1", "id2"]


def test_search(storage_service, mock_milvus, mock_embedding_service):
    """Test searching the Milvus vector store."""
    query = "Test query"
    results = storage_service.search(query, k=2)
    
    # Check embedding was generated for query
    mock_embedding_service.embed_query.assert_called_once_with(query)
    
    # Check search was called with correct parameters
    mock_milvus["collection"].search.assert_called_once()
    search_kwargs = mock_milvus["collection"].search.call_args.kwargs
    
    # Verify search parameters
    assert len(search_kwargs["data"][0]) == 3072  # Embedding dimension
    assert search_kwargs["limit"] == 2
    assert search_kwargs["anns_field"] == "embedding"
    
    # Check results
    assert len(results) == 2
    assert results[0].page_content == "Test result 1"
    assert results[0].metadata["source"] == "test1.md"
    assert results[1].page_content == "Test result 2"
    assert results[1].metadata["source"] == "test2.md"


def test_search_with_embedding(storage_service, mock_milvus):
    """Test searching with a pre-computed embedding."""
    embedding = [0.5] * 3072  # 3072-dimensional embedding
    results = storage_service.search_with_embedding(embedding, k=3)
    
    # Check search was called with the provided embedding
    mock_milvus["collection"].search.assert_called_once()
    search_args = mock_milvus["collection"].search.call_args
    
    assert search_args[1]["data"][0] == embedding
    assert search_args[1]["limit"] == 3
    
    # Check results
    assert len(results) == 2


def test_search_with_wrong_dimension(storage_service, mock_milvus):
    """Test searching with wrong embedding dimension."""
    wrong_embedding = [0.5] * 1024  # Wrong dimension
    results = storage_service.search_with_embedding(wrong_embedding)
    
    # Should return empty results due to dimension mismatch
    assert results == []
    
    # Search should not have been called
    mock_milvus["collection"].search.assert_not_called()


def test_delete_documents(storage_service, mock_milvus):
    """Test deleting documents from the vector store."""
    ids = ["doc1", "doc2"]
    storage_service.delete_documents(ids)
    
    # Check delete was called with correct expression
    mock_milvus["collection"].delete.assert_called_once_with("id in ['doc1', 'doc2']")
    
    # Check flush was called
    mock_milvus["collection"].flush.assert_called_once()


def test_get_collection_stats(storage_service, mock_milvus):
    """Test getting statistics about the vector store."""
    stats = storage_service.get_collection_stats()
    
    # Check stats
    assert stats["count"] == 42
    assert stats["collection"] == "test_obelisk_rag"
    assert stats["host"] == "milvus:19530"
    assert stats["dimension"] == 3072
    assert stats["index_type"] == "HNSW"


def test_drop_collection(storage_service, mock_milvus):
    """Test dropping the collection."""
    # Set up has_collection to return True
    mock_milvus["utility"].has_collection.return_value = True
    
    # Drop the collection
    storage_service.drop_collection()
    
    # Check drop was called
    mock_milvus["collection"].drop.assert_called_once()


def test_error_handling_search(storage_service, mock_milvus, mock_embedding_service):
    """Test error handling during search."""
    # Configure the mock to raise an exception
    mock_milvus["collection"].search.side_effect = Exception("Milvus error")
    
    # Test search with error
    results = storage_service.search("query that causes error")
    
    # Should return empty list
    assert results == []


def test_error_handling_add_documents(storage_service, mock_milvus, mock_embedding_service):
    """Test error handling during document addition."""
    # Configure the mock to raise an exception
    mock_milvus["collection"].insert.side_effect = Exception("Insert error")
    
    docs = [Document(page_content="Test", metadata={})]
    
    # Test add with error
    ids = storage_service.add_documents(docs)
    
    # Should return empty list
    assert ids == []


def test_no_embedding_service(storage_service):
    """Test behavior when no embedding service is provided."""
    storage_service.embedding_service = None
    
    # Try to add documents without embedding service
    docs = [Document(page_content="Test", metadata={})]
    ids = storage_service.add_documents(docs)
    
    # Should return empty list
    assert ids == []
    
    # Try to search without embedding service
    results = storage_service.search("query")
    
    # Should return empty list
    assert results == []


def test_storage_initialization_creates_new_collection(config, mock_milvus, mock_embedding_service):
    """Test storage initialization when collection doesn't exist."""
    # Set up has_collection to return False
    mock_milvus["utility"].has_collection.return_value = False
    
    # Create storage service
    storage = VectorStorage(embedding_service=mock_embedding_service, config=config)
    
    # Check collection was created with correct schema
    mock_milvus["collection_class"].assert_called_once()
    call_args = mock_milvus["collection_class"].call_args
    
    # Verify collection parameters
    assert call_args[1]["name"] == "test_obelisk_rag"
    assert call_args[1]["consistency_level"] == "Strong"
    
    # Check index was created
    mock_milvus["collection"].create_index.assert_called_once()
    index_args = mock_milvus["collection"].create_index.call_args
    assert index_args[0][0] == "embedding"
    assert index_args[0][1]["index_type"] == "HNSW"
    assert index_args[0][1]["metric_type"] == "IP"
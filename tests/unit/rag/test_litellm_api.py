"""Unit tests for the LiteLLM API module."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import json
import time

from fastapi.testclient import TestClient
from fastapi import FastAPI
from langchain.schema.document import Document

from src.obelisk.rag.api.litellm import setup_litellm_api, router
from src.obelisk.rag.common.config import RAGConfig
from src.obelisk.rag.common.models import ProviderType


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service with LiteLLM provider."""
    with patch('src.obelisk.rag.api.litellm.get_service') as mock_get_service:
        mock_service = MagicMock()
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.list_available_models.return_value = {
            "llm": ["gpt-3.5-turbo", "gpt-4", "claude-2"],
            "embedding": ["text-embedding-ada-002", "text-embedding-3-small"]
        }
        mock_provider.health_check.return_value = True
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is a response from LiteLLM provider."
        mock_llm.invoke.return_value = mock_response
        mock_provider.get_llm.return_value = mock_llm
        
        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_provider.get_embeddings.return_value = mock_embeddings
        
        # Mock RAG query
        mock_service.query.return_value = {
            "query": "What is Obelisk?",
            "context": [
                Document(page_content="Obelisk is a RAG tool", metadata={"source": "doc1.md"}),
                Document(page_content="It uses LiteLLM for model abstraction", metadata={"source": "doc2.md"})
            ],
            "response": "Obelisk is a RAG tool that uses LiteLLM for model abstraction.",
            "no_context": False
        }
        
        mock_service.provider = mock_provider
        mock_service.config = RAGConfig()
        mock_get_service.return_value = mock_service
        yield mock_service


@pytest.fixture
def app(mock_rag_service):
    """Create a FastAPI app with LiteLLM endpoints."""
    app = FastAPI()
    setup_litellm_api(app)
    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_chat_completion_direct_model(client, mock_rag_service):
    """Test chat completion with direct model (non-RAG)."""
    response = client.post(
        "/v1/litellm/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "temperature": 0.5,
            "max_tokens": 100
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "chat.completion"
    assert data["model"] == "gpt-3.5-turbo"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert data["choices"][0]["message"]["content"] == "This is a response from LiteLLM provider."
    assert data["choices"][0]["finish_reason"] == "stop"
    assert "usage" in data
    
    # Verify LLM was called with correct parameters
    mock_rag_service.provider.get_llm.assert_called_once_with(
        model="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=100,
        top_p=1.0
    )


def test_chat_completion_rag_model(client, mock_rag_service):
    """Test chat completion with RAG-enabled model."""
    response = client.post(
        "/v1/litellm/chat/completions",
        json={
            "model": "rag-gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "What is Obelisk?"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "chat.completion"
    assert data["model"] == "rag-gpt-3.5-turbo"
    assert len(data["choices"]) == 1
    
    # Check that response includes RAG content and sources
    content = data["choices"][0]["message"]["content"]
    assert "Obelisk is a RAG tool" in content
    assert "Sources:" in content
    assert "doc1.md" in content
    assert "doc2.md" in content
    
    # Verify query was called
    mock_rag_service.query.assert_called_once_with("What is Obelisk?")


def test_chat_completion_no_user_message(client):
    """Test chat completion with no user message."""
    response = client.post(
        "/v1/litellm/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
        }
    )
    
    assert response.status_code == 400
    assert "No user message found" in response.json()["detail"]


def test_list_models(client, mock_rag_service):
    """Test listing available models."""
    response = client.get("/v1/litellm/models")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "list"
    assert len(data["data"]) > 0
    
    # Check LLM models
    llm_models = [m for m in data["data"] if not m["id"].startswith("embedding-") and not m["id"].startswith("rag-")]
    assert len(llm_models) == 3
    assert any(m["id"] == "gpt-3.5-turbo" for m in llm_models)
    assert all(m["owned_by"] == "litellm" for m in llm_models)
    
    # Check embedding models
    embedding_models = [m for m in data["data"] if m["id"].startswith("embedding-")]
    assert len(embedding_models) == 2
    assert any(m["id"] == "embedding-text-embedding-ada-002" for m in embedding_models)
    
    # Check RAG models
    rag_models = [m for m in data["data"] if m["id"].startswith("rag-")]
    assert len(rag_models) == 3
    assert any(m["id"] == "rag-gpt-3.5-turbo" for m in rag_models)
    assert all(m["owned_by"] == "litellm-rag" for m in rag_models)


def test_create_embeddings(client, mock_rag_service):
    """Test creating embeddings."""
    response = client.post(
        "/v1/litellm/embeddings",
        json={
            "model": "text-embedding-ada-002",
            "input": ["Hello world", "How are you?"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "list"
    assert len(data["data"]) == 2
    assert data["model"] == "text-embedding-ada-002"
    
    # Check embeddings
    for i, embedding_data in enumerate(data["data"]):
        assert embedding_data["object"] == "embedding"
        assert embedding_data["index"] == i
        assert embedding_data["embedding"] == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    # Check usage
    assert "usage" in data
    assert data["usage"]["prompt_tokens"] > 0
    assert data["usage"]["total_tokens"] > 0
    
    # Verify embeddings were called
    assert mock_rag_service.provider.get_embeddings.called
    assert mock_rag_service.provider.get_embeddings.return_value.embed_query.call_count == 2


def test_create_embeddings_single_string(client, mock_rag_service):
    """Test creating embeddings with single string input."""
    response = client.post(
        "/v1/litellm/embeddings",
        json={
            "model": "embedding-text-embedding-3-small",  # Test with prefix
            "input": "Single text to embed"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["data"]) == 1
    assert data["model"] == "text-embedding-3-small"  # Prefix should be removed
    
    # Verify correct model was requested
    mock_rag_service.provider.get_embeddings.assert_called_with(
        model="text-embedding-3-small"
    )


def test_health_check_healthy(client, mock_rag_service):
    """Test health check when provider is healthy."""
    response = client.get("/v1/litellm/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["provider"] == "litellm"
    assert "timestamp" in data
    
    # Verify health check was called
    mock_rag_service.provider.health_check.assert_called_once()


def test_health_check_unhealthy(client, mock_rag_service):
    """Test health check when provider is unhealthy."""
    mock_rag_service.provider.health_check.return_value = False
    
    response = client.get("/v1/litellm/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "unhealthy"
    assert data["provider"] == "litellm"
    assert "timestamp" in data


def test_health_check_error(client):
    """Test health check when there's an error."""
    with patch('src.obelisk.rag.api.litellm.get_service') as mock_get_service:
        mock_get_service.side_effect = Exception("Service initialization failed")
        
        response = client.get("/v1/litellm/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "error"
        assert data["provider"] == "litellm"
        assert data["error"] == "Service initialization failed"
        assert "timestamp" in data


def test_error_handling_chat_completion(client):
    """Test error handling in chat completion."""
    with patch('src.obelisk.rag.api.litellm.get_service') as mock_get_service:
        mock_get_service.side_effect = Exception("Provider not available")
        
        response = client.post(
            "/v1/litellm/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        
        assert response.status_code == 500
        assert "Provider not available" in response.json()["detail"]


def test_error_handling_embeddings(client):
    """Test error handling in embeddings."""
    with patch('src.obelisk.rag.api.litellm.get_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.provider.get_embeddings.side_effect = Exception("Embedding model not found")
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/v1/litellm/embeddings",
            json={
                "model": "unknown-model",
                "input": "Test text"
            }
        )
        
        assert response.status_code == 500
        assert "Embedding model not found" in response.json()["detail"]
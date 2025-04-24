"""Unit tests for the Ollama API proxy."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.obelisk.rag.api.ollama import setup_ollama_proxy
from src.obelisk.rag.common.config import RAGConfig


@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    return FastAPI()


@pytest.fixture
def mock_service():
    """Create a mock RAG service."""
    service = MagicMock()
    service.config = RAGConfig({
        "ollama_url": "http://mock-ollama:11434"
    })
    return service


@pytest.fixture
def mock_httpx_client():
    """Create a mock HTTPX client."""
    with patch("src.obelisk.rag.api.ollama.httpx.AsyncClient") as mock:
        # Use AsyncMock for async methods
        mock_client = AsyncMock()
        
        # Configure mock response for generate
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = json.dumps({
            "model": "llama3",
            "response": "This is a test response"
        }).encode()
        mock_response.json.return_value = {
            "model": "llama3",
            "response": "This is a test response"
        }
        
        # Set up the async context manager
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value=mock_response)
        mock.return_value = mock_client
        
        yield mock_client


@pytest.fixture
def client(app, mock_service, mock_httpx_client):
    """Create a test client with the app configured."""
    setup_ollama_proxy(app, mock_service)
    return TestClient(app)


def test_ollama_api_proxy_generate(client, mock_httpx_client):
    """Test the Ollama API proxy for generate endpoint."""
    request_body = {
        "model": "llama3",
        "prompt": "What is Obelisk?"
    }
    
    # Make a request to the proxy
    response = client.post("/api/generate", json=request_body)
    
    # Check the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["model"] == "llama3"
    assert response_data["response"] == "This is a test response"
    
    # Check that the request was forwarded to Ollama
    mock_httpx_client.request.assert_called_once()
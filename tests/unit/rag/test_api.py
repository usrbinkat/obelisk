"""Unit tests for the Obelisk RAG API endpoints."""

import pytest
from unittest.mock import MagicMock, patch
import json
import time

from fastapi.testclient import TestClient
from fastapi import FastAPI
from langchain.schema.document import Document

from src.obelisk.rag.api.openai import setup_openai_api, router as openai_router
from src.obelisk.rag.common.config import RAGConfig


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service."""
    with patch('src.obelisk.rag.api.openai.service') as mock:
        mock.query.return_value = {
            "query": "What is Obelisk?",
            "context": [
                Document(page_content="Obelisk is a RAG tool", metadata={"source": "doc1.md"}),
                Document(page_content="Obelisk can process markdown files", metadata={"source": "doc2.md"})
            ],
            "response": "Obelisk is a RAG (Retrieval Augmented Generation) tool that can process markdown files.",
            "no_context": False
        }
        
        mock.config = RAGConfig()
        yield mock


@pytest.fixture
def app(mock_rag_service):
    """Create a FastAPI app with the OpenAI-compatible endpoints."""
    app = FastAPI()
    setup_openai_api(app)
    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_chat_completion_endpoint(client, mock_rag_service):
    """Test the chat completion endpoint."""
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "llama3",
            "messages": [
                {"role": "user", "content": "What is Obelisk?"}
            ],
            "temperature": 0.7
        }
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Parse response body
    data = response.json()
    
    # Check response format
    assert data["object"] == "chat.completion"
    assert data["model"] == "llama3"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "Obelisk is a RAG" in data["choices"][0]["message"]["content"]
    
    # Check sources
    assert "sources" in data
    assert len(data["sources"]) == 2
    assert "doc1.md" in data["sources"][0]["source"]
    assert "doc2.md" in data["sources"][1]["source"]


def test_chat_completion_no_user_message(client):
    """Test the chat completion endpoint with no user message."""
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "llama3",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."}
            ],
            "temperature": 0.7
        }
    )
    
    # Should return a 400 error
    assert response.status_code == 400
    assert "No user messages found" in response.json()["detail"]
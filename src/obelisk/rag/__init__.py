"""
Obelisk RAG - Retrieval Augmented Generation system.

This module provides RAG capabilities for Obelisk, allowing the integration
of document content with AI models through vector search and LLM integration.
"""

__version__ = "0.1.0"

# Import the main components for easier access
from src.obelisk.rag.common.config import RAGConfig, get_config, set_config
from src.obelisk.rag.document.processor import DocumentProcessor
from src.obelisk.rag.embedding.service import EmbeddingService
from src.obelisk.rag.storage.store import VectorStorage
from src.obelisk.rag.service.coordinator import RAGService
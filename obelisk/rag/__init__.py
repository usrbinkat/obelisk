"""
Obelisk RAG - Retrieval Augmented Generation for Obelisk documentation.

This module provides RAG capabilities for Obelisk, allowing the integration
of documentation content with AI models through Ollama.
"""

__version__ = "0.1.0"

from obelisk.rag.config import RAGConfig, get_config, set_config
from obelisk.rag.document import DocumentProcessor
from obelisk.rag.embedding import EmbeddingService
from obelisk.rag.storage import VectorStorage
from obelisk.rag.service import RAGService
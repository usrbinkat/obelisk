"""
Embedding generation for the Obelisk RAG system.

This module provides embedding generation capabilities using configurable model providers.
It handles the conversion of text chunks to vector embeddings.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain.schema.document import Document

from src.obelisk.rag.common.config import get_config
from src.obelisk.rag.common.models import get_model_provider, ModelProvider
from src.obelisk.rag.common.providers import ModelProviderFactory, ProviderType

# Set up logging
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from text."""
    
    def __init__(self, config=None, provider: Optional[ModelProvider] = None):
        """Initialize the embedding service.
        
        Args:
            config: Optional configuration dictionary
            provider: Optional pre-initialized model provider
        """
        self.config = config or get_config()
        
        # Force LiteLLM for all embeddings when force_litellm_proxy is True
        if provider:
            self.provider = provider
        elif self.config.get("force_litellm_proxy", True):
            # Always use LiteLLM for embeddings (unified API)
            self.provider = ModelProviderFactory.create(
                ProviderType.LITELLM, 
                self.config
            )
        else:
            # Fallback to configured provider (for backward compatibility)
            self.provider = get_model_provider(self.config)
        
        # Get embedding model from config
        self.model_name = self.config.get("embedding_model")
        
        # Debug info
        provider_type = "litellm" if self.config.get("force_litellm_proxy", True) else self.config.get("model_provider", "litellm")
        logger.info(f"Embedding service using provider: {provider_type}")
        logger.info(f"Embedding model: {self.model_name!r}")
        
        # Initialize the embedding model through the provider
        self.embeddings_model = self.provider.get_embeddings(
            model=self.model_name
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
            
        try:
            # Generate embeddings using the provider
            embeddings = self.embeddings_model.embed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query string."""
        try:
            return self.embeddings_model.embed_query(query)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
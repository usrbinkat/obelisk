"""
Embedding generation for the Obelisk RAG system.

This module provides embedding generation capabilities using Ollama.
It handles the conversion of text chunks to vector embeddings.
"""

import logging
from typing import List, Dict, Any

from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings

from obelisk.rag.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from text."""
    
    def __init__(self, config=None):
        """Initialize the embedding service."""
        self.config = config or get_config()
        self.model_name = self.config.get("embedding_model")
        self.ollama_url = self.config.get("ollama_url")
        
        # Debug info
        logger.info(f"Embedding model: {self.model_name!r}")
        logger.info(f"Ollama URL: {self.ollama_url!r}")
        
        # Initialize the embedding model with explicit string values
        # This ensures we never pass None to the model parameter
        model_name = self.model_name or "mxbai-embed-large"
        ollama_url = self.ollama_url or "http://ollama:11434"
        
        self.embeddings_model = OllamaEmbeddings(
            model=model_name,
            base_url=ollama_url
        )
    
    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """Generate embeddings for a list of documents."""
        if not documents:
            return documents
        
        # Ensure we have valid Document objects
        valid_docs = []
        for doc in documents:
            if not isinstance(doc, Document) or not hasattr(doc, 'metadata'):
                logger.warning(f"Invalid document encountered: {type(doc)}")
                continue
            valid_docs.append(doc)
        
        if not valid_docs:
            logger.warning("No valid documents to embed")
            return documents
            
        try:
            # Extract text from documents
            texts = [doc.page_content for doc in valid_docs]
            
            # Generate embeddings - no need to store in metadata
            # just proceed with the model embedding call to ensure
            # the model is working correctly
            try:
                self.embeddings_model.embed_documents(texts)
            except Exception as embed_err:
                logger.error(f"Error during embedding: {embed_err}")
                # Continue anyway - the vector store will handle embeddings
            
            # Return the original documents without modification
            return documents
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return documents
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query string."""
        try:
            return self.embeddings_model.embed_query(query)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
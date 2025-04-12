"""
Vector storage for the Obelisk RAG system.

This module provides vector database storage using ChromaDB.
It handles the storage and retrieval of document embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from langchain.schema.document import Document
from langchain_chroma import Chroma  # Updated import path
from langchain_community.vectorstores.utils import filter_complex_metadata  # For metadata filtering
from langchain_ollama import OllamaEmbeddings

# Set up logging
logger = logging.getLogger(__name__)

from obelisk.rag.config import get_config


class VectorStorage:
    """Vector database storage using ChromaDB."""
    
    def __init__(self, embedding_service=None, config=None):
        """Initialize the vector storage."""
        self.config = config or get_config()
        self.db_path = self.config.get("chroma_dir")
        self.embedding_service = embedding_service
        
        # Create directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize the vector store
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize the vector store with ChromaDB."""
        if self.embedding_service:
            embeddings_model = self.embedding_service.embeddings_model
        else:
            # Create embeddings model if not provided
            embeddings_model = OllamaEmbeddings(
                model=self.config.get("embedding_model"),
                base_url=self.config.get("ollama_url")
            )
        
        # Initialize Chroma (it will automatically load existing DB or create new one)
        self.store = Chroma(
            persist_directory=self.db_path,
            embedding_function=embeddings_model
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        try:
            # Input validation
            if not documents or not all(isinstance(doc, Document) for doc in documents):
                logger.warning("Invalid document format received")
                return
                
            # Filter out complex metadata (like date objects) that ChromaDB can't handle
            filtered_documents = []
            for doc in documents:
                try:
                    # Create a dictionary with filtered metadata
                    filtered_metadata = {}
                    for key, value in doc.metadata.items():
                        # Only include primitive types
                        if isinstance(value, (str, int, float, bool)):
                            filtered_metadata[key] = value
                    
                    # Create a new document with filtered metadata
                    filtered_doc = Document(
                        page_content=doc.page_content,
                        metadata=filtered_metadata
                    )
                    filtered_documents.append(filtered_doc)
                except Exception as doc_err:
                    logger.error(f"Error processing document: {doc_err}")
                    # Skip this document and continue with others
            
            if filtered_documents:
                # Add documents to the vector store (no need to call persist - Chroma does this automatically)
                self.store.add_documents(filtered_documents)
                logger.info(f"Added {len(filtered_documents)} documents to vector store")
            else:
                logger.warning("No valid documents to add to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
    
    def search(self, query: str, k: int = None) -> List[Document]:
        """Search the vector store for relevant documents."""
        if k is None:
            k = self.config.get("retrieve_top_k")
        
        try:
            return self.store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def search_with_embedding(self, embedding: List[float], k: int = None) -> List[Document]:
        """Search using a pre-computed embedding."""
        if k is None:
            k = self.config.get("retrieve_top_k")
        
        try:
            return self.store.similarity_search_by_vector(embedding, k=k)
        except Exception as e:
            logger.error(f"Error searching vector store with embedding: {e}")
            return []
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store."""
        try:
            self.store.delete(ids)
            # No need to call persist() - Chroma automatically persists changes
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            count = self.store._collection.count()
            return {
                "count": count,
                "path": self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {
                "count": 0,
                "path": self.db_path,
                "error": str(e)
            }
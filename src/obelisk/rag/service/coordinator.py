"""
Main RAG service for the Obelisk system.

This module provides the core RAG functionality, connecting all components
together to provide a complete document retrieval and generation system.
"""

import logging
from typing import List, Dict, Any, Optional, Union

from langchain.schema.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama

from src.obelisk.rag.common.config import get_config, RAGConfig
from src.obelisk.rag.document.processor import DocumentProcessor
from src.obelisk.rag.document.watcher import start_watcher
from src.obelisk.rag.embedding.service import EmbeddingService
from src.obelisk.rag.storage.store import VectorStorage

# Set up logging
logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service that connects all components."""
    
    def __init__(self, config=None):
        """Initialize the RAG service."""
        self.config = config or get_config()
        
        # Initialize component services
        self.embedding_service = EmbeddingService(self.config)
        self.storage_service = VectorStorage(
            embedding_service=self.embedding_service,
            config=self.config
        )
        self.document_processor = DocumentProcessor(self.config)
        
        # Register services with the document processor
        self.document_processor.register_services(
            self.embedding_service,
            self.storage_service
        )
        
        # Get model parameters with fallbacks
        ollama_model = self.config.get("ollama_model") or "llama3"
        ollama_url = self.config.get("ollama_url") or "http://ollama:11434"
        
        logger.info(f"LLM model: {ollama_model!r}")
        logger.info(f"Ollama URL: {ollama_url!r}")
        
        # Initialize LLM
        self.llm = ChatOllama(
            model=ollama_model,
            base_url=ollama_url
        )
        
        # Document watcher (will be started if needed)
        self.watcher = None
    
    def start_document_watcher(self) -> None:
        """Start watching for document changes."""
        if self.watcher is None:
            self.watcher = start_watcher(self.document_processor)
            logger.info(f"Started document watcher for directory: {self.config.get('vault_dir')}")
    
    def stop_document_watcher(self) -> None:
        """Stop the document watcher."""
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            logger.info("Stopped document watcher")
    
    def process_vault(self) -> int:
        """Process all markdown files in the vault."""
        chunks = self.document_processor.process_directory()
        return len(chunks)
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a query using RAG.
        
        This method:
        1. Embeds the query
        2. Retrieves relevant documents
        3. Generates a response using the LLM with context
        
        Returns a dictionary containing:
        - query: The original query
        - context: The retrieved documents
        - response: The LLM's generated response
        """
        # Get query embedding
        query_embedding = self.embedding_service.embed_query(query_text)
        
        # Retrieve relevant documents
        docs = self.storage_service.search_with_embedding(
            query_embedding, 
            k=self.config.get("retrieve_top_k")
        )
        
        if not docs:
            # Fallback to direct query if no documents found
            logger.warning(f"No documents found for query: {query_text}")
            response = self.llm.invoke(query_text)
            return {
                "query": query_text,
                "context": [],
                "response": response.content,
                "no_context": True
            }
        
        # Format context for the LLM
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # Generate prompt with context
        prompt = f"""Answer the following question based on the provided context. If the context does not contain relevant information, just say so - do not make up an answer.

Context:
{context_text}

Question: {query_text}

Answer:"""
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        return {
            "query": query_text,
            "context": docs,
            "response": response.content,
            "no_context": False
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        db_stats = self.storage_service.get_collection_stats()
        
        return {
            "document_count": db_stats.get("count", 0),
            "vector_db_path": db_stats.get("path"),
            "ollama_model": self.config.get("ollama_model"),
            "embedding_model": self.config.get("embedding_model"),
            "vault_directory": self.config.get("vault_dir")
        }
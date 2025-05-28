"""
Main RAG service for the Obelisk system.

This module provides the core RAG functionality, connecting all components
together to provide a complete document retrieval and generation system.
"""

import logging
from typing import List, Dict, Any, Optional, Union

from langchain.schema.document import Document
from langchain_core.language_models.chat_models import BaseChatModel

from src.obelisk.rag.common.config import get_config, RAGConfig
from src.obelisk.rag.common.models import get_model_provider, ModelProvider
from src.obelisk.rag.common.providers import ModelProviderFactory, ProviderType
from src.obelisk.rag.document.processor import DocumentProcessor
from src.obelisk.rag.document.watcher import start_watcher
from src.obelisk.rag.embedding.service import EmbeddingService
from src.obelisk.rag.storage.store import VectorStorage

# Set up logging
logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service that connects all components."""
    
    def __init__(self, config=None, provider: Optional[ModelProvider] = None):
        """Initialize the RAG service.
        
        Args:
            config: Optional configuration dictionary
            provider: Optional pre-initialized model provider
        """
        self.config = config or get_config()
        
        # Use provided provider or create one based on config
        if provider:
            self.provider = provider
        else:
            # Default to LiteLLM provider for all completions
            if self.config.get("force_litellm_proxy", True):
                self.provider = ModelProviderFactory.create(
                    ProviderType.LITELLM,
                    self.config
                )
            else:
                # Fallback to configured provider
                self.provider = get_model_provider(self.config)
        
        # Initialize component services with shared provider
        self.embedding_service = EmbeddingService(self.config, provider=self.provider)
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
        
        # Get model parameters
        self.llm_model = self.config.get("llm_model") or self.config.get("ollama_model") or "gpt-4o"
        provider_type = "litellm" if self.config.get("force_litellm_proxy", True) else self.config.get("model_provider", "litellm")
        
        logger.info(f"RAG service using provider: {provider_type}")
        logger.info(f"LLM model: {self.llm_model!r}")
        
        # Initialize LLM through provider
        self.llm = self.provider.get_llm(model=self.llm_model)
        
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
    
    def query(
        self, 
        query_text: str,
        model: Optional[str] = None,
        provider_type: Optional[ProviderType] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a query using RAG.
        
        This method:
        1. Embeds the query
        2. Retrieves relevant documents
        3. Generates a response using the LLM with context
        
        Args:
            query_text: The query text
            model: Optional model override
            provider_type: Optional provider type override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
        
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
        
        # Get the LLM to use (with optional provider override)
        if provider_type and provider_type != self.provider.provider_type:
            # Create a temporary provider for this request
            temp_provider = ModelProviderFactory.create(provider_type, self.config)
            llm = temp_provider.get_llm(
                model=model or self.llm_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Use the default provider with optional parameters
            llm = self.provider.get_llm(
                model=model or self.llm_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        if not docs:
            # Fallback to direct query if no documents found
            logger.warning(f"No documents found for query: {query_text}")
            response = llm.invoke(query_text)
            # Handle both string and object responses
            response_text = response.content if hasattr(response, 'content') else str(response)
            return {
                "query": query_text,
                "context": [],
                "response": response_text,
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
        response = llm.invoke(prompt)
        # Handle both string and object responses
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "query": query_text,
            "context": docs,
            "response": response_text,
            "no_context": False
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        db_stats = self.storage_service.get_collection_stats()
        
        # Get model info from provider config
        llm_model = self.config.get("llm_model") or self.config.get("ollama_model")
        provider_type = self.config.get("model_provider", "litellm")
        
        return {
            "document_count": db_stats.get("count", 0),
            "vector_db_path": db_stats.get("path"),
            "model_provider": provider_type,
            "llm_model": llm_model,
            "embedding_model": self.config.get("embedding_model"),
            "vault_directory": self.config.get("vault_dir")
        }
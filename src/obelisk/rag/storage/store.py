"""
Vector storage for the Obelisk RAG system using Milvus.

This module provides vector database storage using Milvus.
It handles the storage and retrieval of document embeddings
with support for high-dimensional vectors (3072 dims for OpenAI text-embedding-3-large).
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
import numpy as np

from langchain.schema.document import Document
from pymilvus import (
    connections, 
    Collection, 
    CollectionSchema, 
    FieldSchema, 
    DataType, 
    utility,
    MilvusException
)

# Set up logging
logger = logging.getLogger(__name__)

from src.obelisk.rag.common.config import get_config


class VectorStorage:
    """Vector database storage using Milvus."""
    
    def __init__(self, embedding_service=None, config=None):
        """Initialize the vector storage with Milvus."""
        self.config = config or get_config()
        self.embedding_service = embedding_service
        
        # Milvus configuration
        self.milvus_host = self.config.get("milvus_host", "milvus")
        self.milvus_port = self.config.get("milvus_port", 19530)
        self.milvus_user = self.config.get("milvus_user", "default")
        self.milvus_password = self.config.get("milvus_password", "Milvus")
        self.collection_name = self.config.get("milvus_collection", "obelisk_rag")
        
        # Embedding dimension (3072 for OpenAI text-embedding-3-large)
        self.embedding_dim = self.config.get("embedding_dim", 3072)
        
        # Connect to Milvus and initialize collection
        self._connect()
        self._init_collection()
    
    def _connect(self):
        """Connect to Milvus server."""
        try:
            connections.connect(
                alias="default",
                host=self.milvus_host,
                port=self.milvus_port,
                user=self.milvus_user,
                password=self.milvus_password
            )
            logger.info(f"Connected to Milvus at {self.milvus_host}:{self.milvus_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _init_collection(self):
        """Initialize Milvus collection with schema."""
        try:
            # Define collection schema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=65535),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
                FieldSchema(name="data", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=255)
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="Obelisk RAG embeddings"
            )
            
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                logger.info(f"Loading existing collection: {self.collection_name}")
                self.collection = Collection(self.collection_name)
                self.collection.load()
            else:
                logger.info(f"Creating new collection: {self.collection_name}")
                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema,
                    consistency_level="Strong"
                )
                
                # Create HNSW index for high performance similarity search
                index_params = {
                    "metric_type": "IP",  # Inner Product for normalized embeddings
                    "index_type": "HNSW",
                    "params": {"M": 16, "efConstruction": 256}
                }
                self.collection.create_index("vector", index_params)
                logger.info("Created HNSW index on vector field")
                
                # Load collection into memory
                self.collection.load()
                logger.info(f"Collection {self.collection_name} loaded into memory")
                
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        if not documents:
            logger.warning("No documents provided to add")
            return []
            
        try:
            # Generate embeddings if service is available
            if self.embedding_service:
                texts = [doc.page_content for doc in documents]
                embeddings = self.embedding_service.embed_documents(texts)
            else:
                logger.error("No embedding service available")
                return []
            
            # Prepare data for insertion
            ids = []
            contents = []
            metadatas = []
            doc_ids = []
            
            for doc in documents:
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                ids.append(doc_id)
                contents.append(doc.page_content)
                
                # Filter metadata to ensure JSON compatibility
                filtered_metadata = {}
                for key, value in doc.metadata.items():
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        filtered_metadata[key] = value
                    else:
                        filtered_metadata[key] = str(value)
                
                metadatas.append(filtered_metadata)
                doc_ids.append(filtered_metadata.get("source", "unknown"))
            
            # Insert data into Milvus
            # Order must match schema: id, vector, data, metadata, doc_id
            entities = [
                ids,        # id
                embeddings, # vector
                contents,   # data
                metadatas,  # metadata
                doc_ids     # doc_id
            ]
            
            insert_result = self.collection.insert(entities)
            
            # Flush to ensure data persistence
            self.collection.flush()
            
            logger.info(f"Added {len(documents)} documents to Milvus collection")
            return insert_result.primary_keys
            
        except Exception as e:
            logger.error(f"Error adding documents to Milvus: {e}")
            return []
    
    def search(self, query: str, k: int = None) -> List[Document]:
        """Search the vector store for relevant documents."""
        if k is None:
            k = self.config.get("retrieve_top_k", 5)
        
        try:
            # Generate query embedding
            if self.embedding_service:
                query_embedding = self.embedding_service.embed_query(query)
            else:
                logger.error("No embedding service available for query")
                return []
            
            return self.search_with_embedding(query_embedding, k)
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def search_with_embedding(self, embedding: List[float], k: int = None) -> List[Document]:
        """Search using a pre-computed embedding."""
        if k is None:
            k = self.config.get("retrieve_top_k", 5)
        
        try:
            # Ensure embedding is the right dimension
            if len(embedding) != self.embedding_dim:
                logger.error(f"Embedding dimension mismatch: got {len(embedding)}, expected {self.embedding_dim}")
                return []
            
            # Define search parameters
            search_params = {
                "metric_type": "IP",
                "params": {"ef": 128}
            }
            
            # Perform search
            results = self.collection.search(
                data=[embedding],
                anns_field="vector",
                param=search_params,
                limit=k,
                output_fields=["data", "metadata", "doc_id"]
            )
            
            # Convert results to LangChain Documents
            documents = []
            for hits in results:
                for hit in hits:
                    doc = Document(
                        page_content=hit.entity.get("data"),
                        metadata=hit.entity.get("metadata", {})
                    )
                    documents.append(doc)
            
            logger.info(f"Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching with embedding: {e}")
            return []
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store by IDs."""
        try:
            expr = f"id in {ids}"
            self.collection.delete(expr)
            self.collection.flush()
            logger.info(f"Deleted {len(ids)} documents from Milvus")
        except Exception as e:
            logger.error(f"Error deleting documents from Milvus: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            # Get collection statistics
            stats = self.collection.num_entities
            
            return {
                "count": stats,
                "collection": self.collection_name,
                "host": f"{self.milvus_host}:{self.milvus_port}",
                "dimension": self.embedding_dim,
                "index_type": "HNSW"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "count": 0,
                "collection": self.collection_name,
                "error": str(e)
            }
    
    def drop_collection(self):
        """Drop the entire collection (use with caution!)."""
        try:
            if utility.has_collection(self.collection_name):
                self.collection.drop()
                logger.info(f"Dropped collection: {self.collection_name}")
            else:
                logger.warning(f"Collection {self.collection_name} does not exist")
        except Exception as e:
            logger.error(f"Error dropping collection: {e}")
            raise
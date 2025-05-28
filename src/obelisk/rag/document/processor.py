"""
Document processing for the Obelisk RAG system.

This module handles the processing of markdown files, including:
- Loading and parsing markdown content
- Extracting metadata from YAML frontmatter
- Chunking text into appropriate segments
- Monitoring file changes in the vault
"""

import os
import glob
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.obelisk.rag.common.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process markdown documents for the RAG system."""
    
    def __init__(self, config=None):
        """Initialize the document processor."""
        self.config = config or get_config()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("chunk_size"),
            chunk_overlap=self.config.get("chunk_overlap"),
            separators=["\n## ", "\n### ", "\n#### ", "\n- ", "\n* ", "\n1. ", "\n```", "\n", " ", ""]
        )
        
        # These will be set when registered
        self.embedding_service = None
        self.storage_service = None
    
    def register_services(self, embedding_service, storage_service):
        """Register the embedding and storage services."""
        self.embedding_service = embedding_service
        self.storage_service = storage_service
    
    def process_file(self, file_path: str) -> List[Document]:
        """Process a single markdown file."""
        if not file_path.endswith('.md'):
            return []
        
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a Document object
            doc = Document(
                page_content=content,
                metadata={"source": file_path}
            )
            
            # Add additional metadata
            self._extract_metadata(doc)
            
            # Split the document
            chunks = self.text_splitter.split_documents([doc])
            
            # Process with services if available
            if self.embedding_service and self.storage_service and chunks:
                try:
                    # Store the documents directly - storage service will handle embeddings
                    self.storage_service.add_documents(chunks)
                except Exception as service_err:
                    logger.error(f"Error in embedding/storage services for {file_path}: {service_err}")
                    # Continue processing without embedding/storage
            
            logger.info(f"Processed {file_path}: generated {len(chunks)} chunks")
            return chunks
        except IOError as io_err:
            logger.error(f"IO error processing {file_path}: {io_err}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
            return []
    
    def process_directory(self, directory: str = None) -> List[Document]:
        """Process all markdown files in a directory."""
        if directory is None:
            directory = self.config.get("vault_dir")
        
        all_chunks = []
        for md_file in glob.glob(f"{directory}/**/*.md", recursive=True):
            chunks = self.process_file(md_file)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def _extract_metadata(self, doc: Document) -> None:
        """Extract metadata from document content."""
        try:
            # Proper YAML frontmatter extraction
            content = doc.page_content
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    frontmatter_str = content[3:end_idx].strip()
                    doc.page_content = content[end_idx+3:].strip()
                    
                    # Parse frontmatter using YAML parser
                    try:
                        frontmatter = yaml.safe_load(frontmatter_str)
                        if isinstance(frontmatter, dict):
                            # Add all metadata from frontmatter
                            for key, value in frontmatter.items():
                                doc.metadata[key] = value
                    except yaml.YAMLError as yaml_err:
                        logger.warning(f"Failed to parse YAML frontmatter: {yaml_err}")
                        # Fallback to simple line parsing if YAML parsing fails
                        for line in frontmatter_str.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                doc.metadata[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            # Continue processing without metadata rather than failing
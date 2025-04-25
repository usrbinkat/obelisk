"""Unit tests for the Obelisk RAG document processor."""

import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.obelisk.rag.document.processor import DocumentProcessor
from src.obelisk.rag.common.config import RAGConfig


# Path to the test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
SAMPLE_MD_PATH = os.path.join(TEST_DATA_DIR, "sample.md")


@pytest.fixture(scope="function")
def setup_test_data():
    """Create test data directory and sample file if it doesn't exist."""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Create a sample markdown file for testing if it doesn't exist
    if not os.path.exists(SAMPLE_MD_PATH):
        with open(SAMPLE_MD_PATH, "w") as f:
            f.write("""---
title: Sample Document
date: 2025-04-11
tags: test, sample
---

# Sample Document

This is a sample markdown document for testing the document processor.

## Section 1

This is the content of section 1.

### Subsection 1.1

This is a subsection of section 1.

## Section 2

This is the content of section 2.

### Subsection 2.1

This is a subsection of section 2.

### Subsection 2.2

This is another subsection of section 2.
""")


@pytest.fixture
def config(setup_test_data):
    """Create a test configuration."""
    return RAGConfig({
        "vault_dir": TEST_DATA_DIR,
        "chunk_size": 500,
        "chunk_overlap": 100
    })


@pytest.fixture
def processor(config):
    """Create a document processor with test configuration."""
    return DocumentProcessor(config)


def test_processor_initialization(processor, config):
    """Test that the processor initializes correctly."""
    assert processor.config == config
    assert processor.text_splitter is not None
    assert processor.embedding_service is None
    assert processor.storage_service is None


def test_process_file(processor):
    """Test processing a single markdown file."""
    chunks = processor.process_file(SAMPLE_MD_PATH)
    
    # Check that chunks were generated
    assert len(chunks) > 0
    
    # Check that metadata was added
    for chunk in chunks:
        assert "source" in chunk.metadata
        assert chunk.metadata["source"] == SAMPLE_MD_PATH


def test_extract_metadata(processor):
    """Test extraction of metadata from frontmatter."""
    chunks = processor.process_file(SAMPLE_MD_PATH)
    
    # Check the first chunk for metadata
    first_chunk = chunks[0]
    assert "title" in first_chunk.metadata
    assert first_chunk.metadata["title"] == "Sample Document"
    assert "date" in first_chunk.metadata
    # Check date - could be string or datetime object depending on YAML parser
    assert str(first_chunk.metadata["date"]) == "2025-04-11"
    assert "tags" in first_chunk.metadata
    assert first_chunk.metadata["tags"] == "test, sample"
    
    # Verify content doesn't include frontmatter
    assert "---" not in first_chunk.page_content
    assert first_chunk.page_content.startswith("# Sample Document")


def test_process_directory(processor):
    """Test processing all markdown files in a directory."""
    chunks = processor.process_directory()
    
    # Check that chunks were generated
    assert len(chunks) > 0
    
    # Check that the right file was processed
    assert any(chunk.metadata["source"] == SAMPLE_MD_PATH for chunk in chunks)


def test_service_integration(processor):
    """Test integration with embedding and storage services."""
    # Create mock services
    mock_embedding_service = MagicMock()
    mock_storage_service = MagicMock()
    
    # Register the services
    processor.register_services(mock_embedding_service, mock_storage_service)
    
    # Process a file
    processor.process_file(SAMPLE_MD_PATH)
    
    # Verify the services were called
    mock_embedding_service.embed_documents.assert_called_once()
    mock_storage_service.add_documents.assert_called_once()
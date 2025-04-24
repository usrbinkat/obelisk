"""Unit tests for the Obelisk RAG document watcher."""

import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.obelisk.rag.document.watcher import MarkdownWatcher, start_watcher
from src.obelisk.rag.common.config import RAGConfig


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def sample_vault(temp_dir):
    """Create a sample vault with test content."""
    vault_dir = temp_dir / "vault"
    vault_dir.mkdir(exist_ok=True)
    
    # Create a sample markdown file
    md_content = """---
title: Test Document
date: 2025-04-24
---

# Test Document

This is a sample document for testing.
"""
    with open(vault_dir / "test.md", "w") as f:
        f.write(md_content)
    
    return vault_dir


@pytest.fixture
def mock_document_processor():
    """Create a mock document processor."""
    processor = MagicMock()
    processor.process_file.return_value = ["Test chunk"]
    processor.config = RAGConfig({
        "vault_dir": "/mock/vault"
    })
    return processor


def test_markdown_watcher_initialization(mock_document_processor):
    """Test that the MarkdownWatcher initializes correctly."""
    watcher = MarkdownWatcher(mock_document_processor)
    
    assert watcher.processor == mock_document_processor
    assert watcher.watched_extensions == {".md", ".markdown"}


def test_on_created(mock_document_processor):
    """Test the on_created event handler."""
    watcher = MarkdownWatcher(mock_document_processor)
    
    # Create a mock event
    event = MagicMock()
    event.src_path = "/mock/vault/test.md"
    event.is_directory = False
    
    # Call the handler
    watcher.on_created(event)
    
    # Check that the processor was called
    mock_document_processor.process_file.assert_called_once_with("/mock/vault/test.md")


def test_on_modified(mock_document_processor):
    """Test the on_modified event handler."""
    watcher = MarkdownWatcher(mock_document_processor)
    
    # Create a mock event
    event = MagicMock()
    event.src_path = "/mock/vault/test.md"
    event.is_directory = False
    
    # Call the handler
    watcher.on_modified(event)
    
    # Check that the processor was called
    mock_document_processor.process_file.assert_called_once_with("/mock/vault/test.md")


def test_start_watcher(mock_document_processor):
    """Test the start_watcher function."""
    with patch("src.obelisk.rag.document.watcher.Observer") as mock_observer:
        mock_instance = MagicMock()
        mock_observer.return_value = mock_instance
        
        # Call the function
        observer = start_watcher(mock_document_processor)
        
        # Check that the observer was created and started
        mock_observer.assert_called_once()
        mock_instance.schedule.assert_called_once()
        mock_instance.start.assert_called_once()
        
        # Check that the observer was returned
        assert observer == mock_instance
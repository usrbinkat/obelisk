"""Unit tests for the Obelisk RAG CLI commands."""

import pytest
import json
from unittest.mock import patch, MagicMock
from argparse import Namespace
import os
import tempfile

from src.obelisk.cli.rag import handle_rag_command, handle_index, handle_query, handle_stats, handle_config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service."""
    with patch('src.obelisk.cli.rag.RAGService') as mock:
        mock_instance = MagicMock()
        
        # Configure mock methods
        mock_instance.process_vault.return_value = 10
        mock_instance.process_directory.return_value = 10
        mock_instance.query.return_value = {
            "query": "What is Obelisk?",
            "context": [
                MagicMock(page_content="Obelisk is a RAG tool", metadata={"source": "doc1.md"}),
                MagicMock(page_content="Obelisk can process markdown files", metadata={"source": "doc2.md"})
            ],
            "response": "Obelisk is a RAG tool that can process markdown files.",
            "no_context": False
        }
        mock_instance.get_stats.return_value = {
            "document_count": 42,
            "vector_db_path": "/path/to/vectordb",
            "ollama_model": "llama3",
            "embedding_model": "mxbai-embed-large",
            "vault_directory": "/path/to/vault"
        }
        
        # Configure the constructor to return our mock instance
        mock.return_value = mock_instance
        
        yield mock_instance


def test_handle_index_directory(mock_rag_service, temp_dir):
    """Test handle_index with a directory."""
    # Setup args
    args = Namespace()
    args.vault = temp_dir
    
    # Call the function
    handle_index(args)
    
    # Verify that the service was created with the correct config
    # and the process_vault method was called
    mock_rag_service.process_vault.assert_called_once()


def test_handle_index_file(mock_rag_service, temp_dir):
    """Test handle_index with a file."""
    # Create a test file
    test_file = os.path.join(temp_dir, "test.md")
    with open(test_file, "w") as f:
        f.write("# Test\n\nThis is a test file.")
    
    # Setup args
    args = Namespace()
    args.vault = test_file
    
    # Call the function
    handle_index(args)
    
    # Verify that the document processor process_file method was called with the correct path
    mock_rag_service.document_processor.process_file.assert_called_once_with(test_file)


def test_handle_query(mock_rag_service):
    """Test handle_query."""
    # Setup args
    args = Namespace()
    args.query_text = "What is Obelisk?"
    args.json = False
    args.model = "llama3"
    args.temperature = 0.7
    
    # Call the function
    with patch('builtins.print') as mock_print:
        handle_query(args)
    
    # Verify that the service was created and the query method was called
    mock_rag_service.query.assert_called_once_with("What is Obelisk?")
    
    # Check that the output was printed
    mock_print.assert_any_call("\nQUERY:")
    mock_print.assert_any_call("What is Obelisk?")
    mock_print.assert_any_call("\nRESPONSE:")
    mock_print.assert_any_call("Obelisk is a RAG tool that can process markdown files.")
    mock_print.assert_any_call("\nSOURCES:")


def test_handle_query_json(mock_rag_service):
    """Test handle_query with JSON output."""
    # Setup args
    args = Namespace()
    args.query_text = "What is Obelisk?"
    args.json = True
    args.model = "llama3"
    args.temperature = 0.7
    
    # Call the function
    with patch('builtins.print') as mock_print:
        with patch('json.dumps') as mock_json_dumps:
            mock_json_dumps.return_value = '{"json": "output"}'
            handle_query(args)
    
    # Verify that the service was created and the query method was called
    mock_rag_service.query.assert_called_once_with("What is Obelisk?")
    
    # Check that the JSON output was printed
    mock_print.assert_called_once_with('{"json": "output"}')


def test_handle_stats(mock_rag_service):
    """Test handle_stats."""
    # Setup args
    args = Namespace()
    args.json = False
    
    # Call the function
    with patch('builtins.print') as mock_print:
        handle_stats(args)
    
    # Verify that the service was created and the get_stats method was called
    mock_rag_service.get_stats.assert_called_once()
    
    # Check that the output was printed
    mock_print.assert_any_call("\nRAG SYSTEM STATISTICS:")
    mock_print.assert_any_call("Document Count: 42")
    mock_print.assert_any_call("Vector DB Path: /path/to/vectordb")
    mock_print.assert_any_call("Ollama Model: llama3")
    mock_print.assert_any_call("Embedding Model: mxbai-embed-large")
    mock_print.assert_any_call("Vault Directory: /path/to/vault")


def test_handle_stats_json(mock_rag_service):
    """Test handle_stats with JSON output."""
    # Setup args
    args = Namespace()
    args.json = True
    
    # Call the function
    with patch('builtins.print') as mock_print:
        handle_stats(args)
    
    # Verify that the service was created and the get_stats method was called
    mock_rag_service.get_stats.assert_called_once()
    
    # Check that the JSON output was printed
    mock_print.assert_called_once()
    # Ensure it's valid JSON by parsing it
    call_args = mock_print.call_args[0][0]
    json.loads(call_args)  # This will raise an exception if it's not valid JSON


@patch('src.obelisk.cli.rag.get_config')
@patch('src.obelisk.cli.rag.set_config')
def test_handle_config_set(mock_set_config, mock_get_config):
    """Test handle_config with set operation."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.config = {"key1": "value1", "key2": "value2"}
    mock_get_config.return_value = mock_config
    
    # Setup args
    args = Namespace()
    args.set_config = "key3=value3"
    args.show = False
    
    # Call the function
    with patch('builtins.print') as mock_print:
        handle_config(args)
    
    # Verify that set_config was called with the correct arguments
    mock_set_config.assert_called_once_with({"key3": "value3"})
    
    # Check that the output was printed
    mock_print.assert_called_once_with("Set key3 = value3")


@patch('src.obelisk.cli.rag.get_config')
def test_handle_config_show(mock_get_config):
    """Test handle_config with show operation."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.config = {"key1": "value1", "key2": "value2"}
    mock_get_config.return_value = mock_config
    
    # Setup args
    args = Namespace()
    args.set_config = None
    args.show = True
    
    # Call the function
    with patch('builtins.print') as mock_print:
        handle_config(args)
    
    # Check that the output was printed
    mock_print.assert_any_call("\nCURRENT CONFIGURATION:")
    mock_print.assert_any_call("key1 = value1")
    mock_print.assert_any_call("key2 = value2")
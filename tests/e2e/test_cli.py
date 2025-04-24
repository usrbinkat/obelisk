"""
End-to-end tests for the Obelisk CLI.

These tests verify that the CLI commands work correctly
with the new src-layout pattern.
"""

import pytest
import subprocess
import tempfile
import os
import shutil
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

import src.obelisk


@pytest.fixture
def test_env():
    """Create a temporary environment with test files."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create a temporary vault directory
    vault_dir = os.path.join(temp_dir, "vault")
    os.makedirs(vault_dir, exist_ok=True)
    
    # Create a sample document
    with open(os.path.join(vault_dir, "test.md"), "w") as f:
        f.write("""---
title: Test Document
date: 2025-04-24
---

# Test Document

This is a test document for the CLI.

## Section 1

Content for testing the src-layout CLI.

## Section 2

More content for testing.
""")
    
    # Create a vector database directory
    vector_db_dir = os.path.join(temp_dir, "vectordb")
    os.makedirs(vector_db_dir, exist_ok=True)
    
    # Create an output directory
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Return the paths
    yield {
        "temp_dir": temp_dir,
        "vault_dir": vault_dir,
        "vector_db_dir": vector_db_dir,
        "output_dir": output_dir
    }
    
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.mark.skipif(
    os.environ.get("SKIP_CLI_TESTS") == "1", 
    reason="CLI tests disabled"
)
def test_cli_version():
    """Test the CLI version command with src-layout."""
    # Run the CLI version command
    result = subprocess.run(
        ["python", "-m", "src.obelisk", "--version"],
        capture_output=True,
        text=True
    )
    
    # Verify output contains version information
    assert result.returncode == 0
    # Output format is "Obelisk 0.1.0" - no need to check for the word "version"
    assert src.obelisk.__version__ in result.stdout
    assert f"Obelisk {src.obelisk.__version__}" in result.stdout


@pytest.mark.skipif(
    os.environ.get("SKIP_CLI_TESTS") == "1", 
    reason="CLI tests disabled"
)
def test_cli_help():
    """Test the CLI help command with src-layout."""
    # Run the CLI help command
    result = subprocess.run(
        ["python", "-m", "src.obelisk", "--help"],
        capture_output=True,
        text=True
    )
    
    # Verify output contains help information
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "positional arguments:" in result.stdout.lower()
    assert "options:" in result.stdout.lower()
    assert "rag" in result.stdout.lower()


@pytest.mark.skipif(
    os.environ.get("SKIP_CLI_TESTS") == "1" or os.environ.get("SKIP_OLLAMA_TESTS") == "1", 
    reason="CLI tests or Ollama tests disabled"
)
def test_cli_rag_index(test_env):
    """Test the CLI RAG index command."""
    # Skip with a message if not running in environment with Ollama
    if os.environ.get("TEST_OLLAMA_URL") is None:
        pytest.skip("Skipping test that requires Ollama")
    
    with patch("src.obelisk.rag.service.coordinator.ChatOllama"):
        with patch("src.obelisk.rag.embedding.service.OllamaEmbeddings"):
            # Run the CLI RAG index command with minimal processing
            process_result = subprocess.run(
                [
                    "python", "-m", "src.obelisk", "rag", "index",
                    "--vault", test_env["vault_dir"]
                ],
                capture_output=True,
                text=True
            )
            
            # Verify index command output
            assert process_result.returncode == 0
            assert "index" in process_result.stdout.lower()


@pytest.mark.skipif(
    os.environ.get("SKIP_CLI_TESTS") == "1" or os.environ.get("SKIP_OLLAMA_TESTS") == "1", 
    reason="CLI tests or Ollama tests disabled"
)
def test_cli_rag_stats(test_env):
    """Test the CLI RAG stats command."""
    # Skip with a message if not running in environment with Ollama
    if os.environ.get("TEST_OLLAMA_URL") is None:
        pytest.skip("Skipping test that requires Ollama")
    
    with patch("src.obelisk.rag.service.coordinator.ChatOllama"):
        with patch("src.obelisk.rag.embedding.service.OllamaEmbeddings"):
            with patch("src.obelisk.rag.storage.store.Chroma"):
                # Run the CLI RAG stats command
                stats_result = subprocess.run(
                    [
                        "python", "-m", "src.obelisk", "rag", "stats"
                    ],
                    capture_output=True,
                    text=True
                )
                
                # Verify stats command output
                assert stats_result.returncode == 0
                assert "statistics" in stats_result.stdout.lower()


@pytest.mark.skipif(
    os.environ.get("SKIP_CLI_TESTS") == "1" or os.environ.get("SKIP_OLLAMA_TESTS") == "1", 
    reason="CLI tests or Ollama tests disabled"
)
def test_cli_rag_query(test_env):
    """Test the CLI RAG query command."""
    # Skip with a message if not running in environment with Ollama
    if os.environ.get("TEST_OLLAMA_URL") is None:
        pytest.skip("Skipping test that requires Ollama")
    
    # Setup mocks for the chain of dependencies
    with patch("src.obelisk.rag.service.coordinator.ChatOllama") as mock_chat:
        with patch("src.obelisk.rag.embedding.service.OllamaEmbeddings"):
            with patch("src.obelisk.rag.storage.store.Chroma"):
                # Configure mock to return a response
                mock_response = MagicMock()
                mock_response.content = "This is a test response from the mocked model."
                mock_chat.return_value.invoke.return_value = mock_response
                
                # Index the vault first to setup document store
                subprocess.run(
                    [
                        "python", "-m", "src.obelisk", "rag", "index",
                        "--vault", test_env["vault_dir"]
                    ],
                    capture_output=True,
                    text=True
                )
                
                # Run the query command
                query_result = subprocess.run(
                    [
                        "python", "-m", "src.obelisk", "rag", "query",
                        "What is in the test document?"
                    ],
                    capture_output=True,
                    text=True
                )
                
                # Verify query command output
                assert query_result.returncode == 0
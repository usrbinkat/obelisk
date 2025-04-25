"""Unit tests for the Obelisk CLI commands."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from argparse import Namespace

from src.obelisk.cli.commands import main, add_rag_subparsers


@pytest.fixture
def mock_argparse():
    """Mock argparse components."""
    mock_parser = MagicMock()
    mock_subparsers = MagicMock()
    mock_parser.add_subparsers.return_value = mock_subparsers
    mock_rag_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_rag_parser
    
    return {
        "parser": mock_parser,
        "subparsers": mock_subparsers,
        "rag_parser": mock_rag_parser
    }


def test_add_rag_subparsers(mock_argparse):
    """Test adding RAG subparsers to the argument parser."""
    # Call the function
    add_rag_subparsers(mock_argparse["rag_parser"])
    
    # Verify that the rag parser's add_subparsers method was called
    mock_argparse["rag_parser"].add_subparsers.assert_called_once()


@patch('src.obelisk.cli.commands.argparse.ArgumentParser')
@patch('src.obelisk.cli.commands.add_rag_subparsers')
@patch('src.obelisk.cli.rag.handle_rag_command')
def test_main_with_rag_command(mock_handle_rag, mock_add_rag, mock_argparse):
    """Test the main function with RAG command."""
    # Setup mocks
    mock_parser = MagicMock()
    mock_argparse.return_value = mock_parser
    
    # Setup args
    args = Namespace()
    args.command = "rag"
    args.rag_command = "index"
    mock_parser.parse_args.return_value = args
    
    # Call the function
    with patch.object(sys, 'argv', ['obelisk', 'rag', 'index']):
        main()
    
    # Verify that the rag command handler was called
    mock_handle_rag.assert_called_once_with(args)


@patch('src.obelisk.cli.commands.argparse.ArgumentParser')
def test_main_with_no_command(mock_argparse):
    """Test the main function with no command."""
    # Setup mocks
    mock_parser = MagicMock()
    mock_argparse.return_value = mock_parser
    
    # Setup args
    args = Namespace()
    args.command = None
    mock_parser.parse_args.return_value = args
    
    # Call the function
    with patch.object(sys, 'argv', ['obelisk']):
        with pytest.raises(SystemExit) as e:
            main()
    
    # Verify that the help was printed and the program exited
    mock_parser.print_help.assert_called_once()
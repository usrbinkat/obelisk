"""
Main command-line interface for Obelisk.
"""

import argparse
import logging
import sys
from typing import List

from src.obelisk import __version__

# Set up logging - this is the central logging configuration for all modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set specific logging levels for noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Obelisk - RAG system with vector storage and AI integration"
    )
    parser.add_argument(
        "--version", action="version", version=f"Obelisk {__version__}"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # RAG subcommand
    rag_parser = subparsers.add_parser("rag", help="RAG functionality")
    # We'll add rag subcommands in add_rag_subparsers function
    add_rag_subparsers(rag_parser)
    
    # Parse args and execute
    args = parser.parse_args()
    
    if args.command == "rag":
        # Handle RAG command
        from src.obelisk.cli.rag import handle_rag_command
        handle_rag_command(args)
    else:
        # If no command specified, show help
        parser.print_help()
        sys.exit(1)


def add_rag_subparsers(parser):
    """Add RAG-specific subparsers."""
    # Create subparsers for RAG commands
    subparsers = parser.add_subparsers(dest="rag_command", help="RAG command to run")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documents in the vault")
    index_parser.add_argument(
        "--vault", 
        help="Path to the vault directory"
    )
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument(
        "query_text", 
        help="The query text"
    )
    query_parser.add_argument(
        "--json", 
        action="store_true",
        help="Output results as JSON"
    )
    query_parser.add_argument(
        "--model",
        default="llama3",
        help="Model to use for the query (default: llama3)"
    )
    query_parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature setting for the model (default: 0.7)"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show system statistics")
    stats_parser.add_argument(
        "--json", 
        action="store_true",
        help="Output stats as JSON"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--set", 
        dest="set_config",
        help="Set a configuration value (format: key=value)"
    )
    config_parser.add_argument(
        "--show", 
        action="store_true",
        help="Show current configuration"
    )
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Start the RAG API server with OpenAI-compatible endpoint")
    server_parser.add_argument(
        "--host", 
        help="Host to bind server to"
    )
    server_parser.add_argument(
        "--port", 
        type=int,
        help="Port to bind server to"
    )
    server_parser.add_argument(
        "--watch", 
        action="store_true",
        help="Watch for document changes"
    )


if __name__ == "__main__":
    main()
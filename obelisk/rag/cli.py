"""
Command line interface for the Obelisk RAG system.

This module provides a CLI interface to the RAG system, allowing users
to index documents, query the system, and manage the service.
"""

import os
import sys
import json
import logging
import argparse
import textwrap
from typing import Dict, Any

from obelisk.rag.service import RAGService
from obelisk.rag.config import get_config, set_config, RAGConfig

# Set up logging - this is the central logging configuration for all RAG modules
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Obelisk RAG - Retrieval Augmented Generation for Obelisk documentation"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
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
    server_parser = subparsers.add_parser("serve", help="Start the RAG API server")
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
    
    return parser.parse_args()


def handle_index(args):
    """Handle the index command."""
    config = RAGConfig().config.copy()  # Start with default config
    vault_path = args.vault
    
    if vault_path:
        # Check if the path is a file or directory
        import os
        if os.path.isfile(vault_path):
            # For single file, use the parent directory as vault_dir
            parent_dir = os.path.dirname(vault_path)
            if parent_dir:
                config["vault_dir"] = parent_dir
            
            service = RAGService(RAGConfig(config))
            print(f"Indexing single file: {vault_path}")
            chunks = service.document_processor.process_file(vault_path)
            print(f"Indexed {len(chunks)} document chunks")
            return
        else:
            config["vault_dir"] = vault_path
    
    service = RAGService(RAGConfig(config))
    print(f"Indexing documents in {service.config.get('vault_dir')}...")
    count = service.process_vault()
    print(f"Indexed {count} document chunks")


def handle_query(args):
    """Handle the query command."""
    service = RAGService(get_config())
    result = service.query(args.query_text)
    
    if args.json:
        # For JSON output, convert documents to serializable format
        serializable_result = {
            "query": result["query"],
            "response": result["response"],
            "no_context": result["no_context"],
            "context": [
                {
                    "content": doc.page_content,
                    "metadata": {
                        k: v for k, v in doc.metadata.items() 
                        if not isinstance(v, (list, dict))
                    }
                }
                for doc in result["context"]
            ]
        }
        print(json.dumps(serializable_result, indent=2))
    else:
        # For human-readable output
        print("\nQUERY:")
        print(args.query_text)
        print("\nRESPONSE:")
        print(result["response"])
        
        if result["context"]:
            print("\nSOURCES:")
            for i, doc in enumerate(result["context"]):
                source = doc.metadata.get("source", "Unknown")
                print(f"{i+1}. {source}")


def handle_stats(args):
    """Handle the stats command."""
    service = RAGService(get_config())
    stats = service.get_stats()
    
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print("\nRAG SYSTEM STATISTICS:")
        print(f"Document Count: {stats['document_count']}")
        print(f"Vector DB Path: {stats['vector_db_path']}")
        print(f"Ollama Model: {stats['ollama_model']}")
        print(f"Embedding Model: {stats['embedding_model']}")
        print(f"Vault Directory: {stats['vault_directory']}")


def handle_config(args):
    """Handle the config command."""
    config = get_config()
    
    if args.set_config:
        # Parse and set configuration
        try:
            key, value = args.set_config.split("=", 1)
            set_config({key: value})
            print(f"Set {key} = {value}")
        except ValueError:
            print("Error: Config must be in format key=value")
            return
    
    if args.show or not args.set_config:
        # Show current configuration
        print("\nCURRENT CONFIGURATION:")
        for key, value in config.config.items():
            print(f"{key} = {value}")


def handle_serve(args):
    """Handle the serve command."""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        print("Error: FastAPI and uvicorn are required for API server")
        print("Install with: pip install fastapi uvicorn")
        return
    
    # Configure service
    config = {}
    if args.host:
        config["api_host"] = args.host
    if args.port:
        config["api_port"] = args.port
    
    # Initialize service
    service = RAGService(RAGConfig(config))
    
    # Index documents
    print(f"Indexing documents in {service.config.get('vault_dir')}...")
    count = service.process_vault()
    print(f"Indexed {count} document chunks")
    
    # Start document watcher if requested
    if args.watch:
        service.start_document_watcher()
        print("Document watcher started")
    
    # Define API models
    class QueryRequest(BaseModel):
        query: str
    
    class SourceInfo(BaseModel):
        content: str
        source: str
    
    class QueryResponse(BaseModel):
        query: str
        response: str
        sources: list[SourceInfo]
        no_context: bool = False
    
    # Create FastAPI app
    app = FastAPI(
        title="Obelisk RAG API",
        description="Retrieval Augmented Generation API for Obelisk documentation",
        version="0.1.0"
    )
    
    @app.get("/stats")
    def api_stats():
        """Get system statistics."""
        return service.get_stats()
    
    @app.post("/query", response_model=QueryResponse)
    def api_query(request: QueryRequest):
        """Process a query using RAG."""
        try:
            result = service.query(request.query)
            
            # Format response
            return {
                "query": result["query"],
                "response": result["response"],
                "sources": [
                    {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "source": doc.metadata.get("source", "Unknown")
                    }
                    for doc in result["context"]
                ],
                "no_context": result["no_context"]
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Start the server
    host = service.config.get("api_host")
    port = int(service.config.get("api_port"))
    
    print(f"Starting API server at http://{host}:{port}")
    print("API endpoints:")
    print(f"  GET  http://{host}:{port}/stats")
    print(f"  POST http://{host}:{port}/query")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(app, host=host, port=port)


def main():
    """Main entry point for the CLI."""
    try:
        args = parse_args()
        
        if args.command == "index":
            handle_index(args)
        elif args.command == "query":
            handle_query(args)
        elif args.command == "stats":
            handle_stats(args)
        elif args.command == "config":
            handle_config(args)
        elif args.command == "serve":
            handle_serve(args)
        else:
            print("Please specify a command. Use --help for more information.")
    except KeyboardInterrupt:
        print("\nOperation canceled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if os.environ.get("RAG_DEBUG"):
            # In debug mode, show the full traceback
            import traceback
            traceback.print_exc()
        else:
            # In normal mode, show a user-friendly message
            print(f"Error: {e}")
            print("For detailed error output, set the RAG_DEBUG environment variable")
        sys.exit(1)


if __name__ == "__main__":
    main()
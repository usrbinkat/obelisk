"""
RAG-specific CLI commands for Obelisk.
"""

import os
import sys
import json
import logging
import argparse
import textwrap
import time
import traceback
from typing import Dict, Any

# Import these conditionally in handle_serve to prevent dependency errors
# when running other commands
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel
    import uvicorn
    import httpx
    from src.obelisk.rag.api.openai import setup_openai_api
    from src.obelisk.rag.api.ollama import setup_ollama_proxy
except ImportError:
    # These imports are only required for 'serve' command and will be checked there
    pass

from src.obelisk.rag.service.coordinator import RAGService
from src.obelisk.rag.common.config import get_config, set_config, RAGConfig

# Set up logging
logger = logging.getLogger(__name__)


def handle_rag_command(args):
    """Handle RAG-specific CLI commands."""
    if args.rag_command == "index":
        handle_index(args)
    elif args.rag_command == "query":
        handle_query(args)
    elif args.rag_command == "stats":
        handle_stats(args)
    elif args.rag_command == "config":
        handle_config(args)
    elif args.rag_command == "serve":
        handle_serve(args)
    else:
        print("Please specify a RAG command. Use --help for more information.")
        sys.exit(1)


def handle_index(args):
    """Handle the index command."""
    config = RAGConfig().config.copy()  # Start with default config
    vault_path = args.vault
    
    if vault_path:
        # Check if the path is a file or directory
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
    
    # Set model config if provided
    if hasattr(args, 'model') and args.model:
        service.llm.model = args.model
    
    # Set temperature if provided
    if hasattr(args, 'temperature'):
        service.llm.temperature = args.temperature
    
    # Get query result
    result = service.query(args.query_text)
    
    # Format sources in a consistent way similar to the API
    sources = []
    if result["context"] and not result["no_context"]:
        sources = [
            {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "source": doc.metadata.get("source", "Unknown")
            }
            for doc in result["context"]
        ]
    
    if args.json:
        # For JSON output, format in OpenAI-compatible style with sources
        import time
        serializable_result = {
            "id": f"rag-chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": args.model if hasattr(args, 'model') and args.model else service.config.get("ollama_model", "llama3"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result["response"]
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(args.query_text.split()),  # Rough estimate
                "completion_tokens": len(result["response"].split()),  # Rough estimate
                "total_tokens": len(args.query_text.split()) + len(result["response"].split())  # Rough estimate
            },
            "sources": sources if sources else None
        }
        print(json.dumps(serializable_result, indent=2))
    else:
        # For human-readable output
        print("\nQUERY:")
        print(args.query_text)
        print("\nRESPONSE:")
        print(result["response"])
        
        if sources:
            print("\nSOURCES:")
            for i, source_info in enumerate(sources):
                print(f"{i+1}. {source_info['source']}")


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
        # Check if FastAPI and other dependencies are available
        if 'FastAPI' not in globals():
            print("Error: FastAPI and uvicorn are required for API server")
            print("Install with: pip install fastapi uvicorn")
            return
    except Exception as e:
        print(f"Error loading required packages: {e}")
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
    
    # Create FastAPI app
    app = FastAPI(
        title="Obelisk RAG API",
        description="Retrieval Augmented Generation API with OpenAI-compatible endpoints",
        version="0.1.0"
    )
    
    @app.get("/stats")
    def api_stats():
        """Get system statistics."""
        return service.get_stats()
    
    # Add OpenAI-compatible API endpoints and Ollama proxying
    try:
        # Setup OpenAI-compatible API endpoints
        setup_openai_api(app)
        print("OpenAI-compatible API endpoints configured at /v1/chat/completions")
        
        # Setup Ollama proxy
        setup_ollama_proxy(app, service)
        print("Ollama API proxy configured at /api/* and /ollama/api/*")
    except Exception as e:
        logger.error(f"Error setting up API endpoints: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Start the server
    host = service.config.get("api_host")
    port = int(service.config.get("api_port"))
    
    print(f"Starting API server at http://{host}:{port}")
    print("API endpoints:")
    print(f"  GET  http://{host}:{port}/stats")
    print(f"  POST http://{host}:{port}/v1/chat/completions")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(app, host=host, port=port)
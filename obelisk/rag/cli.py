"""
Command line interface for the Obelisk RAG system.

This module provides a CLI interface to the RAG system, allowing users
to index documents, query the system, and manage the service. The API 
implements an OpenAI-compatible interface (/v1/chat/completions) for
integration with tools and interfaces expecting the OpenAI API format.
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
        # Add imports for Ollama proxy
        import httpx
        from fastapi import Request
        from fastapi.responses import JSONResponse, StreamingResponse
        
        # Setup OpenAI-compatible endpoints
        from obelisk.rag.api import setup_openai_api
        setup_openai_api(app)
        print("OpenAI-compatible API endpoints configured at /v1/chat/completions")
        
        # Add Ollama proxy routes to handle requests expecting Ollama API format
        @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
        async def proxy_ollama_api(request: Request, path: str):
            """Proxy requests to Ollama API."""
            ollama_url = service.config.get("ollama_url")
            target_url = f"{ollama_url}/api/{path}"
            
            logger.info(f"Proxying request to Ollama API: {target_url}")
            
            # Get the request body
            body = await request.body()
            
            # Special handling for chat and generate endpoints - enhance with RAG
            if path in ["chat", "generate"] and request.method == "POST" and body:
                try:
                    # Parse the request body
                    data = json.loads(body)
                    
                    # Extract the prompt/messages
                    if path == "chat" and "messages" in data:
                        # Extract the last user message from chat history
                        logger.info(f"Chat messages received: {json.dumps(data.get('messages', []))}")
                        user_messages = [m for m in data.get("messages", []) if m.get("role") == "user"]
                        if user_messages:
                            query = user_messages[-1].get("content", "")
                            
                            # Process through our RAG pipeline
                            logger.info(f"Enhancing chat with RAG for query: {query}")
                            logger.info(f"Starting RAG query process...")
                            rag_result = service.query(query)
                            logger.info(f"RAG query completed with {len(rag_result.get('context', []))} context items")
                            
                            # If we found context, modify the prompt to include it
                            if rag_result["context"] and not rag_result["no_context"]:
                                logger.info(f"Found {len(rag_result['context'])} relevant context items")
                                context_text = "\n\n".join([
                                    f"Document {i+1}:\n{doc.page_content}" 
                                    for i, doc in enumerate(rag_result["context"])
                                ])
                                
                                logger.info(f"Context length: {len(context_text)} characters")
                                                                
                                # Insert a system message with context
                                system_msg = {
                                    "role": "system", 
                                    "content": f"Use the following information to answer the user's question. If the information doesn't contain the answer, say you don't know.\n\nContext from documentation:\n{context_text}"
                                }
                                
                                # Add system message at the beginning if not already there
                                if not any(m.get("role") == "system" for m in data.get("messages", [])):
                                    logger.info("Adding new system message with context")
                                    data["messages"].insert(0, system_msg)
                                else:
                                    # Update existing system message
                                    logger.info("Updating existing system message with context")
                                    for i, msg in enumerate(data["messages"]):
                                        if msg.get("role") == "system":
                                            data["messages"][i] = system_msg
                                            break
                                
                                # Update the body with the enhanced messages
                                logger.info("Updating request body with enhanced messages")
                                body = json.dumps(data).encode()
                                logger.info(f"New body size: {len(body)} bytes")
                            else:
                                logger.info("No relevant context found, using original request")
                    
                    elif path == "generate" and "prompt" in data:
                        # Extract the prompt
                        query = data.get("prompt", "")
                        logger.info(f"Generate prompt received: {query[:100]}...")
                        
                        # Process through our RAG pipeline
                        logger.info(f"Enhancing generate with RAG for query: {query}")
                        logger.info(f"Starting RAG query process for generate...")
                        rag_result = service.query(query)
                        logger.info(f"RAG query completed with {len(rag_result.get('context', []))} context items")
                        
                        # If we found context, modify the prompt to include it
                        if rag_result["context"] and not rag_result["no_context"]:
                            logger.info(f"Found {len(rag_result['context'])} relevant context items for generate")
                            context_text = "\n\n".join([
                                f"Document {i+1}:\n{doc.page_content}" 
                                for i, doc in enumerate(rag_result["context"])
                            ])
                            
                            logger.info(f"Context length for generate: {len(context_text)} characters")
                            
                            # Create a new prompt with context
                            new_prompt = f"""Use the following information to answer the question. If the information doesn't contain the answer, say you don't know.

Context from documentation:
{context_text}

Question: {query}

Answer:"""
                            
                            # Update the prompt in the data
                            logger.info("Updating prompt with context")
                            data["prompt"] = new_prompt
                            
                            # Update the body with the enhanced prompt
                            logger.info("Updating request body with enhanced prompt")
                            body = json.dumps(data).encode()
                            logger.info(f"New body size for generate: {len(body)} bytes")
                        else:
                            logger.info("No relevant context found for generate, using original request")
                
                except Exception as e:
                    logger.error(f"Error enhancing with RAG: {e}")
                    # Continue with the original request if there's an error
            
            # Forward the request to Ollama
            # Create a new headers dictionary, removing 'host' and updating 'content-length'
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
            headers["content-length"] = str(len(body))
            
            # Detailed logging
            logger.info(f"Request method: {request.method}")
            logger.info(f"Request headers: {headers}")
            logger.info(f"Request body length: {len(body)}")
            logger.info(f"Forwarding to target URL: {target_url}")
            
            try:
                # Use a longer timeout (120 seconds) for requests to Ollama
                logger.info("Starting request to Ollama...")
                async with httpx.AsyncClient(timeout=120.0) as client:
                    logger.info("Client created, sending request...")
                    response = await client.request(
                        method=request.method,
                        url=target_url,
                        headers=headers,
                        content=body,
                    )
                    logger.info(f"Received response from Ollama with status: {response.status_code}")
                    
                    content_type = response.headers.get("content-type", "")
                    logger.info(f"Response content type: {content_type}")
                    logger.info(f"Response headers: {dict(response.headers)}")
            except Exception as e:
                logger.error(f"Error during request to Ollama: {str(e)}")
                raise
            
            # Return the response from Ollama
            try:
                return JSONResponse(
                    content=response.json() if response.content else None,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except:
                # If not JSON, return raw content
                return StreamingResponse(
                    content=iter([response.content]),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        # Add route for /ollama/api/* which OpenWebUI uses
        @app.api_route("/ollama/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
        async def proxy_ollama_api_alt(request: Request, path: str):
            """Proxy requests to Ollama API (alternate path)."""
            ollama_url = service.config.get("ollama_url")
            target_url = f"{ollama_url}/api/{path}"
            
            logger.info(f"Proxying request to Ollama API (alt path): {target_url}")
            
            # Get the request body and forward to the standard proxy
            body = await request.body()
            
            # Forward the request to our main proxy endpoint
            # We reuse the code by calling our other route handler
            # This ensures consistent RAG enhancement for both routes
            forwarded_request = Request(
                scope=request.scope.copy(),
                receive=request._receive,
                send=request._send,
            )
            
            # Call our standard proxy with the appropriate path
            return await proxy_ollama_api(forwarded_request, path)
        
        print("Ollama API proxy configured at /api/* and /ollama/api/*")
        
        # Add manual route listing for debugging
        print("All registered routes:")
        for route in app.routes:
            print(f"  {', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'} {route.path}")
    except Exception as e:
        logger.error(f"Error setting up API endpoints: {str(e)}")
        import traceback
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
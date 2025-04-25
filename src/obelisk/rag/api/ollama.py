"""
Ollama API proxy for the Obelisk RAG system.

This module provides a proxy to the Ollama API, enhancing certain
endpoints with RAG capabilities.
"""

import json
import logging
from typing import Dict, Any
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# Set up logging
logger = logging.getLogger(__name__)


def setup_ollama_proxy(app: FastAPI, service):
    """
    Add Ollama proxy routes to the FastAPI app.
    
    This sets up routes that proxy requests to the Ollama API,
    and enhances certain requests with RAG capabilities.
    """
    # httpx is now imported at the module level
    
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
    
    logger.info("Ollama API proxy configured at /api/* and /ollama/api/*")
    
    # Add manual route listing for debugging
    logger.info("All registered routes:")
    for route in app.routes:
        logger.info(f"  {', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'} {route.path}")
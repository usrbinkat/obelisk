"""
OpenAI-compatible API interface for the Obelisk RAG system.

This module provides an OpenAI-compatible API for the RAG service,
allowing integration with tools like Open WebUI that expect 
the OpenAI API format.
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union

from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.obelisk.rag.service.coordinator import RAGService
from src.obelisk.rag.common.config import get_config
from src.obelisk.rag.common.providers import ModelProviderFactory, ProviderType

# Set up logging
logger = logging.getLogger(__name__)

# Service will be initialized lazily
_service = None

def get_service() -> RAGService:
    """Get or create the RAG service instance."""
    global _service
    if _service is None:
        _service = RAGService(get_config())
    return _service

# Create router
router = APIRouter()

# Define API models based on OpenAI's API schema
class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'system', 'assistant')")
    content: str = Field(..., description="The content of the message")

class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="The model to use for completion")
    messages: List[Message] = Field(..., description="The messages to generate completions for")
    temperature: Optional[float] = Field(0.7, description="The temperature for sampling")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")

class SourceInfo(BaseModel):
    content: str = Field(..., description="The content of the source document")
    source: str = Field(..., description="The source document identifier")

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"

class ChatCompletionResponseUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = "rag-chat-completion"
    object: str = "chat.completion"
    created: int = 0  # Will be filled with current timestamp
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: ChatCompletionResponseUsage
    sources: Optional[List[SourceInfo]] = Field(None, description="Source documents used in RAG")

@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    x_provider_override: Optional[str] = None
):
    """
    Create a chat completion with RAG enhancement.
    
    This endpoint provides an OpenAI-compatible API that:
    - Routes all completions through LiteLLM by default
    - Supports provider override via X-Provider-Override header
    - Enhances responses with RAG context
    """
    # Extract the query from the messages
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        error_msg = "No user messages found in the request"
        logger.error(f"400: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        query = user_messages[-1].content
        config = get_config()
        
        # Determine provider based on operation type and override
        if x_provider_override and x_provider_override.lower() == "ollama":
            # Special case: direct Ollama for hardware tuning operations
            provider_type = ProviderType.OLLAMA
            logger.info("Using direct Ollama provider due to X-Provider-Override header")
        else:
            # Default: all completions through LiteLLM
            provider_type = ProviderType.LITELLM
            logger.info(f"Using LiteLLM provider for model: {request.model}")
        
        # Process the query through RAG with the selected provider
        rag_result = get_service().query(
            query, 
            model=request.model,
            provider_type=provider_type,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Create sources information if available
        sources = None
        if rag_result["context"] and not rag_result["no_context"]:
            sources = [
                SourceInfo(
                    content=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    source=doc.metadata.get("source", "Unknown")
                )
                for doc in rag_result["context"]
            ]
            
        # Create the response
        response = ChatCompletionResponse(
            id=f"rag-chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=rag_result["response"]
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionResponseUsage(
                prompt_tokens=len(query.split()),  # Rough estimate
                completion_tokens=len(rag_result["response"].split()),  # Rough estimate
                total_tokens=len(query.split()) + len(rag_result["response"].split())
            ),
            sources=sources
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def setup_openai_api(app: FastAPI):
    """Add the OpenAI-compatible API endpoints to the FastAPI app."""
    app.include_router(router)
    
    # Print a detailed message
    logger.info(f"OpenAI-compatible API endpoints configured: POST /v1/chat/completions")
    
    # Log all the available routes for debugging
    for route in app.routes:
        logger.info(f"Available route: {route.methods} {route.path}")
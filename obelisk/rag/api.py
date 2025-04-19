"""
OpenAI-compatible API interface for the Obelisk RAG system.

This module provides an OpenAI-compatible API for the RAG service,
allowing integration with tools like Open WebUI that expect 
the OpenAI API format.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from obelisk.rag.service import RAGService
from obelisk.rag.config import get_config

# Set up logging
logger = logging.getLogger(__name__)

# Initialize service
service = RAGService(get_config())

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
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Create a chat completion with RAG enhancement.
    
    This endpoint mimics the OpenAI API format but uses the RAG system to
    enhance responses with relevant document context.
    """
    try:
        # Extract the query from the messages
        # Typically, we want the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user messages found in the request")
        
        query = user_messages[-1].content
        
        # Process the query through RAG
        rag_result = service.query(query)
        
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
        import time
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
                total_tokens=len(query.split()) + len(rag_result["response"].split())  # Rough estimate
            ),
            sources=sources
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def setup_openai_api(app: FastAPI):
    """Add the OpenAI-compatible API endpoints to the FastAPI app."""
    app.include_router(router)
    
    # Print a detailed message
    logger.info(f"OpenAI-compatible API endpoints configured: POST /v1/chat/completions")
    
    # Log all the available routes for debugging
    for route in app.routes:
        logger.info(f"Available route: {route.methods} {route.path}")
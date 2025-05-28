"""
LiteLLM integration for the Obelisk RAG system.

This module provides a unified API endpoint that uses the LiteLLM provider
to support multiple model providers (OpenAI, Anthropic, Cohere, etc.) through
a single interface. It provides OpenAI-compatible endpoints while leveraging
LiteLLM's model routing and fallback capabilities.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.obelisk.rag.service.coordinator import RAGService
from src.obelisk.rag.common.config import get_config
from src.obelisk.rag.common.models import ProviderType, get_model_provider

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1/litellm", tags=["litellm"])

# Service will be initialized lazily
_service = None

def get_service() -> RAGService:
    """Get or create the RAG service instance with LiteLLM provider."""
    global _service
    if _service is None:
        config = get_config()
        # Force LiteLLM provider for this API
        config.set("model_provider", ProviderType.LITELLM.value)
        _service = RAGService(config)
    return _service


# Request/Response models matching OpenAI API
class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")
    name: Optional[str] = Field(None, description="Optional name for the participant")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    top_p: Optional[float] = Field(1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty")
    user: Optional[str] = Field(None, description="Unique identifier for the user")


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str
    logprobs: Optional[Any] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    system_fingerprint: Optional[str] = None


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: List[Dict[str, Any]] = []
    root: str
    parent: Optional[str] = None


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    Create a chat completion using LiteLLM provider.
    
    This endpoint provides OpenAI-compatible chat completions while using
    LiteLLM as the backend, enabling support for multiple model providers.
    """
    # Extract the last user message for RAG query
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")
    
    try:
        service = get_service()
        query = user_messages[-1].content
        
        # Check if we should use RAG or direct model
        use_rag = request.model.startswith("rag-") or "rag" in request.model.lower()
        
        if use_rag:
            # Process through RAG
            rag_result = service.query(query)
            response_content = rag_result["response"]
            
            # Add context information if available
            if rag_result.get("context") and not rag_result.get("no_context"):
                sources = "\n\nSources:\n" + "\n".join([
                    f"- {doc.metadata.get('source', 'Unknown')}"
                    for doc in rag_result["context"]
                ])
                response_content += sources
        else:
            # Direct model query through LiteLLM provider
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            # Get LLM from provider with model override
            llm = service.provider.get_llm(
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p
            )
            
            # Convert messages to prompt (LangChain style)
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            response = llm.invoke(prompt)
            response_content = response.content
        
        # Estimate token usage (rough approximation)
        prompt_tokens = sum(len(msg.content.split()) * 1.3 for msg in request.messages)
        completion_tokens = len(response_content.split()) * 1.3
        
        # Build response
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=response_content),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )
        )
        
    except Exception as e:
        logger.error(f"Error in LiteLLM chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """
    List available models through LiteLLM provider.
    
    Returns both LLM and embedding models available through the configured
    LiteLLM provider.
    """
    try:
        service = get_service()
        available_models = service.provider.list_available_models()
        
        models = []
        timestamp = int(time.time())
        
        # Add LLM models
        for model_id in available_models.get("llm", []):
            models.append(ModelInfo(
                id=model_id,
                created=timestamp,
                owned_by="litellm",
                root=model_id,
                parent=None
            ))
        
        # Add embedding models with prefix
        for model_id in available_models.get("embedding", []):
            models.append(ModelInfo(
                id=f"embedding-{model_id}",
                created=timestamp,
                owned_by="litellm",
                root=model_id,
                parent=None
            ))
        
        # Add RAG-enabled models
        for model_id in available_models.get("llm", []):
            models.append(ModelInfo(
                id=f"rag-{model_id}",
                created=timestamp,
                owned_by="litellm-rag",
                root=model_id,
                parent=None
            ))
        
        return ModelListResponse(data=models)
        
    except Exception as e:
        logger.error(f"Error listing LiteLLM models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings")
async def create_embeddings(request: Dict[str, Any]):
    """
    Create embeddings using LiteLLM provider.
    
    This endpoint provides OpenAI-compatible embeddings generation.
    """
    try:
        service = get_service()
        
        # Extract input
        input_data = request.get("input", [])
        if isinstance(input_data, str):
            input_data = [input_data]
        
        model = request.get("model", "text-embedding-ada-002")
        
        # Remove 'embedding-' prefix if present
        if model.startswith("embedding-"):
            model = model[10:]
        
        # Get embeddings model from provider
        embeddings_model = service.provider.get_embeddings(model=model)
        
        # Generate embeddings
        embeddings = []
        for i, text in enumerate(input_data):
            embedding = embeddings_model.embed_query(text)
            embeddings.append({
                "object": "embedding",
                "embedding": embedding,
                "index": i
            })
        
        # Calculate usage
        total_tokens = sum(len(text.split()) * 1.3 for text in input_data)
        
        return {
            "object": "list",
            "data": embeddings,
            "model": model,
            "usage": {
                "prompt_tokens": int(total_tokens),
                "total_tokens": int(total_tokens)
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check health of LiteLLM provider."""
    try:
        service = get_service()
        is_healthy = service.provider.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "provider": "litellm",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": "litellm",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def setup_litellm_api(app):
    """Add LiteLLM API endpoints to the FastAPI app."""
    app.include_router(router)
    logger.info("LiteLLM API endpoints configured: /v1/litellm/*")
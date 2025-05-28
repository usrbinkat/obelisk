"""API interfaces for the Obelisk RAG system."""

from src.obelisk.rag.api.openai import setup_openai_api

# Unified API approach - all completions route through OpenAI-compatible endpoint
# which internally uses LiteLLM for routing to appropriate providers
__all__ = ["setup_openai_api"]

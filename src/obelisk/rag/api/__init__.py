"""API interfaces for the Obelisk RAG system."""

from src.obelisk.rag.api.openai import setup_openai_api
from src.obelisk.rag.api.ollama import setup_ollama_proxy
# Import will be implemented as part of the LiteLLM refactoring
# from src.obelisk.rag.api.litellm import setup_litellm_integration

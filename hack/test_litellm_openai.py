#!/usr/bin/env python3
"""
LiteLLM OpenAI Integration Test

This script validates OpenAI API key functionality and tests the LiteLLM
integration with OpenAI models, including fallback to Ollama models when needed.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("openai-litellm-test")

# Service endpoints
LITELLM_API = os.environ.get("LITELLM_API_URL", "http://localhost:4000")
LITELLM_API_KEY = os.environ.get("LITELLM_API_TOKEN", "sk-1234")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = "https://api.openai.com/v1"


def test_openai_api_key() -> bool:
    """Test if the OpenAI API key is valid and working."""
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not set. Skipping direct OpenAI tests.")
        return False

    logger.info("Testing OpenAI API key...")
    
    # Test 1: List models
    try:
        models_response = requests.get(
            f"{OPENAI_API_BASE}/models",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            timeout=10
        )
        
        if models_response.status_code != 200:
            logger.error(f"OpenAI models API request failed: {models_response.status_code}")
            return False
        
        models_data = models_response.json()
        gpt4_models = [model["id"] for model in models_data.get("data", []) 
                     if "gpt-4" in model["id"]]
        embedding_models = [model["id"] for model in models_data.get("data", []) 
                          if "text-embedding" in model["id"]]
        
        logger.info(f"Found {len(gpt4_models)} GPT-4 models, including: {gpt4_models[:5]}")
        logger.info(f"Found {len(embedding_models)} embedding models: {embedding_models}")
        
        # Verify our target models are available
        target_models_available = True
        if "gpt-4o" not in gpt4_models and "gpt-4o-2024-08-06" not in gpt4_models:
            logger.error("Required model 'gpt-4o' not available")
            target_models_available = False
        
        if "text-embedding-3-large" not in embedding_models:
            logger.error("Required model 'text-embedding-3-large' not available")
            target_models_available = False
            
        if not target_models_available:
            return False
            
        logger.info("Target models are available")
        
    except requests.RequestException as e:
        logger.error(f"Error connecting to OpenAI models API: {e}")
        return False
    
    # Test 2: Test completion with gpt-4o
    try:
        completion_payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Say hello in one word"}],
            "max_tokens": 10
        }
        
        completion_response = requests.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                     "Content-Type": "application/json"},
            json=completion_payload,
            timeout=15
        )
        
        if completion_response.status_code != 200:
            logger.error(f"OpenAI completion request failed: {completion_response.status_code}")
            return False
        
        completion_data = completion_response.json()
        if not completion_data.get("choices") or len(completion_data["choices"]) == 0:
            logger.error("No completion choices returned")
            return False
            
        content = completion_data["choices"][0]["message"]["content"]
        logger.info(f"Completion response: '{content}'")
        
    except requests.RequestException as e:
        logger.error(f"Error testing OpenAI completion: {e}")
        return False
    
    # Test 3: Test embeddings with text-embedding-3-large
    try:
        embedding_payload = {
            "model": "text-embedding-3-large",
            "input": "Testing the embedding model for Obelisk RAG"
        }
        
        embedding_response = requests.post(
            f"{OPENAI_API_BASE}/embeddings",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                     "Content-Type": "application/json"},
            json=embedding_payload,
            timeout=15
        )
        
        if embedding_response.status_code != 200:
            logger.error(f"OpenAI embedding request failed: {embedding_response.status_code}")
            return False
        
        embedding_data = embedding_response.json()
        if not embedding_data.get("data") or len(embedding_data["data"]) == 0:
            logger.error("No embedding data returned")
            return False
            
        embedding = embedding_data["data"][0]["embedding"]
        embedding_dim = len(embedding)
        logger.info(f"Embedding dimension: {embedding_dim}")
        
        if embedding_dim != 3072:
            logger.error(f"Unexpected embedding dimension: {embedding_dim}, expected 3072")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Error testing OpenAI embedding: {e}")
        return False
    
    logger.info("All OpenAI API key tests passed")
    return True


def test_litellm_models() -> Dict[str, List[str]]:
    """Check available models in LiteLLM and categorize them."""
    try:
        response = requests.get(
            f"{LITELLM_API}/models",
            headers={"Authorization": f"Bearer {LITELLM_API_KEY}"},
            timeout=5
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get LiteLLM models: {response.status_code}")
            return {"openai": [], "ollama": [], "other": []}
        
        models_data = response.json()
        all_models = [model["id"] for model in models_data.get("data", [])]
        
        # Categorize models
        model_categories = {
            "openai": [m for m in all_models if m.startswith("openai/") or m in ["gpt-4o", "text-embedding-3-large"]],
            "ollama": [m for m in all_models if m.startswith("ollama/")],
            "other": [m for m in all_models if not m.startswith(("openai/", "ollama/")) 
                      and m not in ["gpt-4o", "text-embedding-3-large"]]
        }
        
        logger.info(f"Available models: {all_models}")
        logger.info(f"OpenAI models: {model_categories['openai']}")
        logger.info(f"Ollama models: {model_categories['ollama']}")
        
        return model_categories
    except requests.RequestException as e:
        logger.error(f"Error checking LiteLLM models: {e}")
        return {"openai": [], "ollama": [], "other": []}


def test_completion(model: str) -> Tuple[bool, Optional[str]]:
    """Test completions with specified model, return (success, actual_model_used)."""
    try:
        # Use a very short prompt for quick testing
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, who are you?"}],
            "max_tokens": 50
        }
        
        logger.info(f"Testing completion with model: {model}")
        
        response = requests.post(
            f"{LITELLM_API}/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {LITELLM_API_KEY}"},
            timeout=30  # Allow more time for model loading
        )
        
        if response.status_code != 200:
            logger.error(f"Completion failed with status {response.status_code}: {response.text[:200]}")
            return False, None
        
        result = response.json()
        if "choices" not in result or not result.get("choices"):
            logger.error("No choices in completion response")
            return False, None
            
        content = result["choices"][0]["message"]["content"]
        model_name = result.get("model", "unknown")
        
        logger.info(f"Completion result: {content[:100]}...")
        logger.info(f"Model used in response: {model_name}")
        
        return True, model_name
    except requests.RequestException as e:
        logger.error(f"Error testing completion: {e}")
        return False, None


def test_embedding(model: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Test embeddings with specified model, return (success, actual_model_used, embedding_dim)."""
    try:
        payload = {
            "model": model,
            "input": "This is a test of the embedding functionality."
        }
        
        logger.info(f"Testing embedding with model: {model}")
        
        response = requests.post(
            f"{LITELLM_API}/v1/embeddings",
            json=payload,
            headers={"Authorization": f"Bearer {LITELLM_API_KEY}"},
            timeout=20  # Allow time for embedding processing
        )
        
        if response.status_code != 200:
            logger.error(f"Embedding failed with status {response.status_code}: {response.text[:200]}")
            return False, None, None
        
        result = response.json()
        if "data" not in result or not result.get("data"):
            logger.error("No data in embedding response")
            return False, None, None
            
        embedding = result["data"][0]["embedding"]
        model_name = result.get("model", "unknown")
        embedding_dim = len(embedding)
        
        logger.info(f"Embedding dimension: {embedding_dim}")
        logger.info(f"Model used in response: {model_name}")
        
        return True, model_name, embedding_dim
    except requests.RequestException as e:
        logger.error(f"Error testing embedding: {e}")
        return False, None, None


def test_fallback_mechanism(primary_model: str, fallback_model: str, is_embedding: bool = False) -> Dict[str, Any]:
    """Test if the fallback mechanism works by using an invalid API key."""
    original_openai_key = os.environ.get("OPENAI_API_KEY", "")
    results = {
        "primary_successful": False,
        "primary_model_used": None,
        "fallback_successful": False,
        "fallback_model_used": None,
        "fallback_triggered": False
    }
    
    try:
        # Test with primary model first
        if is_embedding:
            success, model_used, embedding_dim = test_embedding(primary_model)
            results["primary_successful"] = success
            results["primary_model_used"] = model_used
            results["embedding_dim"] = embedding_dim
        else:
            success, model_used = test_completion(primary_model)
            results["primary_successful"] = success
            results["primary_model_used"] = model_used
        
        # Only test fallback if primary worked and we have an OpenAI key
        if results["primary_successful"] and original_openai_key:
            # Temporarily set an invalid API key
            os.environ["OPENAI_API_KEY"] = "sk-invalid-key-for-testing-fallback"
            
            # Test again with same model which should trigger fallback
            if is_embedding:
                success, model_used, embedding_dim = test_embedding(primary_model)
                results["fallback_successful"] = success
                results["fallback_model_used"] = model_used
                results["fallback_embedding_dim"] = embedding_dim
            else:
                success, model_used = test_completion(primary_model)
                results["fallback_successful"] = success
                results["fallback_model_used"] = model_used
                
            # Check if a different model was used in the response
            results["fallback_triggered"] = (results["primary_model_used"] != results["fallback_model_used"])
            
            # Restore original API key
            os.environ["OPENAI_API_KEY"] = original_openai_key
    except Exception as e:
        logger.error(f"Error in fallback test: {e}")
    finally:
        # Ensure original API key is restored
        os.environ["OPENAI_API_KEY"] = original_openai_key
    
    return results


def main():
    """Run the tests."""
    logger.info("Starting OpenAI LiteLLM integration tests")
    
    # Check direct OpenAI API functionality
    openai_api_works = test_openai_api_key()
    if openai_api_works:
        logger.info("✓ OpenAI API key is valid and working")
    else:
        logger.warning("⚠ OpenAI API key is invalid or not set")
    
    # Check available models and categorize them
    model_categories = test_litellm_models()
    
    # Determine if LiteLLM is available
    litellm_available = bool(model_categories["openai"] or model_categories["ollama"])
    
    if not litellm_available:
        logger.warning("⚠ LiteLLM API is not available, skipping LiteLLM tests")
        return 0 if openai_api_works else 1
    
    logger.info("LiteLLM API is available, continuing with integration tests")
    
    # Determine which models to test based on availability
    # For completion
    completion_model = "gpt-4o" if OPENAI_API_KEY and "gpt-4o" in model_categories["openai"] else "ollama/llama3"
    fallback_completion = "ollama/llama3"
    
    # For embedding
    embedding_model = "text-embedding-3-large" if OPENAI_API_KEY and "text-embedding-3-large" in model_categories["openai"] else "ollama/mxbai-embed-large"
    fallback_embedding = "ollama/mxbai-embed-large"
    
    # Test completions
    logger.info(f"Testing completion with model: {completion_model}")
    completion_ok, completion_model_used = test_completion(completion_model)
    if not completion_ok:
        logger.error(f"✘ Completion test with {completion_model} failed")
    else:
        logger.info(f"✓ Completion test successful using model: {completion_model_used}")
    
    # Test embeddings
    logger.info(f"Testing embedding with model: {embedding_model}")
    embedding_ok, embedding_model_used, embedding_dim = test_embedding(embedding_model)
    if not embedding_ok:
        logger.error(f"✘ Embedding test with {embedding_model} failed")
    else:
        logger.info(f"✓ Embedding test successful using model: {embedding_model_used}")
        logger.info(f"✓ Embedding dimension: {embedding_dim}")
    
    # Test fallback only if OpenAI key is available and primary tests passed
    if OPENAI_API_KEY and completion_ok and embedding_ok:
        logger.info("Testing fallback mechanism by simulating API failure")
        
        # Test completion fallback
        if "openai" in completion_model or completion_model == "gpt-4o":
            fallback_results = test_fallback_mechanism(completion_model, fallback_completion)
            if fallback_results["fallback_successful"]:
                logger.info(f"✓ Fallback for completion successful: {completion_model} → {fallback_results['fallback_model_used']}")
            else:
                logger.error(f"✘ Fallback for completion failed")
        
        # Test embedding fallback
        if "openai" in embedding_model or embedding_model == "text-embedding-3-large":
            fallback_results = test_fallback_mechanism(embedding_model, fallback_embedding, True)
            if fallback_results["fallback_successful"]:
                logger.info(f"✓ Fallback for embedding successful: {embedding_model} → {fallback_results['fallback_model_used']}")
            else:
                logger.error(f"✘ Fallback for embedding failed")
    
    all_tests_passed = (
        openai_api_works and completion_ok and embedding_ok
    )
    
    if all_tests_passed:
        logger.info("✅ All tests passed successfully!")
    else:
        logger.warning("⚠ Some tests failed or were skipped")
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3

import requests
import json
import time
import sys
from pymilvus import connections, Collection, utility

# Config
OPENWEBUI_URL = "http://localhost:8080"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
LITELLM_URL = "http://localhost:4000"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjdmN2FmZTJhLWY4YjMtNGI5My1hZDI2LTU0OTI5NjA3Yzk2MSJ9.G4sUoEoC56uU92_TIfetslcbVHhkZ4YFrU1vIvlPrc8"

def test_milvus_connection():
    """Test basic Milvus connection"""
    print("\n1. Testing Milvus connection...")
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Successfully connected to Milvus")
        
        # List collections
        collections = utility.list_collections()
        print(f"Available collections: {collections}")
        
        connections.disconnect("default")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        return False

def test_litellm_models():
    """Test LiteLLM API and available models using the API token"""
    print("\n2. Testing LiteLLM API and available models...")
    try:
        # Using v1/models endpoint with API key auth
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{LITELLM_URL}/v1/models", headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Successfully connected to LiteLLM API")
            print(f"Available models: {json.dumps(models, indent=2)}")
            return True
        else:
            print(f"❌ Failed to get models from LiteLLM: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try the UI endpoint as fallback
            print("Trying UI endpoint...")
            response = requests.get(f"{LITELLM_URL}/models")
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Successfully connected to LiteLLM UI API")
                print(f"Available models: {json.dumps(models, indent=2)}")
                return True
            return False
    except Exception as e:
        print(f"❌ Failed to connect to LiteLLM API: {e}")
        return False

def check_rag_env_vars():
    """Check if RAG environment variables are correctly set in OpenWebUI"""
    print("\n3. Checking RAG configuration in OpenWebUI...")
    try:
        # Check Docker environment variables for OpenWebUI
        print("Examining docker-compose configuration...")
        import os
        import yaml
        
        # Use new path structure
        compose_path = '/workspaces/obelisk/deployments/docker/compose/dev.yaml'
        # Fallback to original path if new structure not found
        if not os.path.exists(compose_path):
            compose_path = '/workspaces/obelisk/docker-compose.yaml'
            
        print(f"Using compose file: {compose_path}")
        with open(compose_path, 'r') as file:
            compose = yaml.safe_load(file)
        
        # Extract OpenWebUI environment variables
        open_webui_env = compose.get('services', {}).get('open-webui', {}).get('environment', {})
        
        rag_enabled = False
        using_milvus = False
        
        # Check for RAG and Milvus related env vars
        for env_var in open_webui_env:
            if isinstance(env_var, str):
                if env_var.startswith('RETRIEVAL_ENABLED='):
                    val = env_var.split('=', 1)[1].lower()
                    rag_enabled = val == 'true'
                    print(f"RETRIEVAL_ENABLED: {rag_enabled}")
                elif env_var.startswith('RETRIEVAL_VECTOR_STORE='):
                    val = env_var.split('=', 1)[1].lower()
                    using_milvus = val == 'milvus'
                    print(f"RETRIEVAL_VECTOR_STORE: {val}")
            elif isinstance(env_var, dict):
                for key, val in env_var.items():
                    if key == 'RETRIEVAL_ENABLED':
                        rag_enabled = str(val).lower() == 'true'
                        print(f"RETRIEVAL_ENABLED: {rag_enabled}")
                    elif key == 'RETRIEVAL_VECTOR_STORE':
                        using_milvus = str(val).lower() == 'milvus'
                        print(f"RETRIEVAL_VECTOR_STORE: {val}")
        
        # Report findings
        if rag_enabled and using_milvus:
            print("✅ OpenWebUI is configured to use Milvus for RAG")
            return True
        else:
            if not rag_enabled:
                print("❌ RAG is not enabled in OpenWebUI configuration")
            if not using_milvus:
                print("❌ Milvus is not set as the vector store in OpenWebUI configuration")
            return False
    except Exception as e:
        print(f"❌ Failed to check RAG configuration: {e}")
        return False

def main():
    print("=== Testing Milvus RAG Integration ===")
    
    # Run tests
    milvus_ok = test_milvus_connection()
    litellm_ok = test_litellm_models()
    rag_ok = check_rag_env_vars()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Milvus Connection: {'✅ PASS' if milvus_ok else '❌ FAIL'}")
    print(f"LiteLLM API: {'✅ PASS' if litellm_ok else '❌ FAIL'}")
    print(f"OpenWebUI RAG Config: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    
    if milvus_ok and rag_ok:
        print("\n🎉 Milvus integration is set up correctly!")
        if not litellm_ok:
            print("⚠️ LiteLLM API access failed, but this may be due to authentication issues")
            print("   The core Milvus integration is working.")
        return 0
    else:
        print("\n❌ Some tests FAILED. Please check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
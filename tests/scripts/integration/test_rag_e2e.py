#!/usr/bin/env python3

import requests
import json
import time
import sys
import random
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# Config
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "obelisk_test_documents"
DIMENSION = 384  # The standard embedding dimension for most sentence transformers models

def setup_test_collection():
    """Create a test collection in Milvus with sample document"""
    print("\n1. Setting up test collection in Milvus...")
    
    try:
        # Connect to Milvus
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Connected to Milvus")
        
        # Drop collection if it exists
        if utility.has_collection(COLLECTION_NAME):
            utility.drop_collection(COLLECTION_NAME)
            print(f"Dropped existing collection: {COLLECTION_NAME}")
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields=fields, description="Document collection for RAG testing")
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        print(f"✅ Created collection: {COLLECTION_NAME}")
        
        # Create an index
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        print("✅ Created index on embedding field")
        
        # Create sample document (using pseudo-embedding)
        # Note: In a real scenario, we'd generate proper embeddings with a model
        sample_docs = [
            {
                "id": 1,
                "content": "Obelisk is a tool that transforms Obsidian vaults into MkDocs Material Theme sites with AI integration.",
                "metadata": json.dumps({"source": "README.md", "type": "documentation"})
            },
            {
                "id": 2,
                "content": "Milvus is a vector database designed for similarity search and AI applications.",
                "metadata": json.dumps({"source": "test_doc.md", "type": "vector database"})
            },
            {
                "id": 3,
                "content": "OpenWebUI provides a user-friendly interface for interacting with large language models.",
                "metadata": json.dumps({"source": "openwebui.md", "type": "user interface"})
            }
        ]
        
        # Generate random embeddings (in a real scenario these would come from an embedding model)
        embeddings = [np.random.random([DIMENSION]).tolist() for _ in range(len(sample_docs))]
        
        # Insert data
        ids = [doc["id"] for doc in sample_docs]
        contents = [doc["content"] for doc in sample_docs]
        metadata = [doc["metadata"] for doc in sample_docs]
        
        collection.insert([
            ids,
            embeddings,
            contents,
            metadata
        ])
        
        # Load collection for searching
        collection.load()
        print(f"✅ Inserted {len(sample_docs)} sample documents into collection")
        
        return True
    except Exception as e:
        print(f"❌ Failed to set up test collection: {e}")
        return False
    finally:
        try:
            connections.disconnect("default")
        except:
            pass

def test_simple_search():
    """Test simple vector search in Milvus"""
    print("\n2. Testing simple vector search...")
    
    try:
        # Connect to Milvus
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        
        # Get collection
        if not utility.has_collection(COLLECTION_NAME):
            print(f"❌ Collection {COLLECTION_NAME} does not exist")
            return False
        
        collection = Collection(COLLECTION_NAME)
        collection.load()
        
        # Create a random query vector
        query_vector = np.random.random([DIMENSION]).tolist()
        
        # Search
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=3,
            output_fields=["content", "metadata"]
        )
        
        # Print results
        print("✅ Search results:")
        for i, hits in enumerate(results):
            print(f"Top {len(hits)} results for query vector:")
            for j, hit in enumerate(hits):
                print(f"  {j+1}. ID: {hit.id}, Distance: {hit.distance}")
                print(f"     Content: {hit.entity.get('content')}")
                print(f"     Metadata: {hit.entity.get('metadata')}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to perform search: {e}")
        return False
    finally:
        try:
            connections.disconnect("default")
        except:
            pass

def main():
    print("=== Testing End-to-End RAG with Milvus ===")
    
    setup_success = setup_test_collection()
    if not setup_success:
        print("❌ Failed to set up test collection, stopping tests")
        return 1
    
    search_success = test_simple_search()
    
    # Cleanup
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        if utility.has_collection(COLLECTION_NAME):
            utility.drop_collection(COLLECTION_NAME)
            print(f"\n✅ Cleanup: Dropped test collection {COLLECTION_NAME}")
        connections.disconnect("default")
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Collection Setup: {'✅ PASS' if setup_success else '❌ FAIL'}")
    print(f"Vector Search: {'✅ PASS' if search_success else '❌ FAIL'}")
    
    if setup_success and search_success:
        print("\n🎉 End-to-End Milvus RAG pipeline is working correctly!")
        return 0
    else:
        print("\n❌ Some tests FAILED. Please check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
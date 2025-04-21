#!/usr/bin/env python3

import random
import numpy as np
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType

# Connect to Milvus
print("Connecting to Milvus...")
connections.connect("default", host="localhost", port="19530")

# Parameters
COLLECTION_NAME = "test_collection"
DIMENSION = 128

# Check if collection exists and drop if it does
if utility.has_collection(COLLECTION_NAME):
    print(f"Collection {COLLECTION_NAME} already exists, dropping it")
    utility.drop_collection(COLLECTION_NAME)

# Create collection schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000)
]
schema = CollectionSchema(fields)

# Create collection
print(f"Creating collection {COLLECTION_NAME}")
collection = Collection(name=COLLECTION_NAME, schema=schema)

# Generate some random data
num_entities = 10
print(f"Generating {num_entities} random vectors")

ids = [i for i in range(num_entities)]
texts = [f"This is test text for vector {i}" for i in range(num_entities)]
embeddings = [np.random.random([DIMENSION]).tolist() for _ in range(num_entities)]

# Insert data
print("Inserting data into Milvus...")
collection.insert([
    ids,
    embeddings,
    texts
])

# Create index
print("Creating index...")
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128}
}
collection.create_index(field_name="embedding", index_params=index_params)

# Load collection to memory
print("Loading collection...")
collection.load()

# Search for vectors
print("Performing search...")
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
top_k = 3
vector_to_search = np.random.random([DIMENSION]).tolist()

results = collection.search(
    data=[vector_to_search],
    anns_field="embedding",
    param=search_params,
    limit=top_k,
    output_fields=["text"]
)

# Print results
print("\nSearch Results:")
for hits in results:
    for hit in hits:
        print(f"ID: {hit.id}, Distance: {hit.distance}, Text: {hit.entity.get('text')}")

# Cleanup
print("\nDropping collection and disconnecting")
utility.drop_collection(COLLECTION_NAME)
connections.disconnect("default")
print("Test completed successfully!")

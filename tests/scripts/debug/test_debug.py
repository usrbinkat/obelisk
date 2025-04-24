from pathlib import Path
import sys

from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Test document processing
doc_path = "/workspaces/obelisk/tests/scripts/test_rag.md"
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Create a Document object
doc = Document(page_content=content, metadata={"source": doc_path})

# Print document for debugging
print(f"Original document: {type(doc)}")
print(f"Has metadata attribute: {hasattr(doc, 'metadata')}")
print(f"Metadata: {doc.metadata}")

# Split the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n#### ", "\n", " ", ""]
)
chunks = text_splitter.split_documents([doc])

# Print chunks for debugging
print(f"\nChunks count: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {type(chunk)}")
    print(f"Has metadata attribute: {hasattr(chunk, 'metadata')}")
    if hasattr(chunk, 'metadata'):
        print(f"Metadata: {chunk.metadata}")
    print(f"Content prefix: {chunk.page_content[:50]}...")
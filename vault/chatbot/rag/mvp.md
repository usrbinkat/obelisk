# RAG System MVP Implementation Roadmap

Based on our research and requirements, this document outlines a focused MVP roadmap for building a local-first RAG system that integrates with Obsidian vault and Ollama setup. This approach prioritizes key functionality while setting a foundation for future enhancements.

## Development Checklist

### Prerequisites
- [x] Pull required embedding and LLM models:
  ```bash
  ollama pull llama3
  ollama pull mxbai-embed-large
  ```
  > Completed on 2025-04-11. Models are available via Ollama Docker container. The embedding model is 669MB, and the LLM is 4.7GB.

### Phase 1: Project Setup & Dependencies
- [x] Create module structure in `obelisk/rag/`
  > Created initial file structure on 2025-04-11, but implementation needs testing and refinement.
- [x] Update `pyproject.toml` with RAG dependencies
  > Added dependencies on 2025-04-11 and updated with Poetry. Successfully installed langchain, langchain-community, langchain-ollama, chromadb, watchdog, fastapi, uvicorn, and pydantic.
- [ ] Create basic configuration system for RAG settings
  > Initial configuration class created but needs testing with actual environment.
- [ ] Add initial unit tests structure
  > Test directory structure created but no actual tests implemented yet.

### Phase 2: Document Processing Pipeline
- [ ] Implement document loader for Markdown files
- [ ] Create text splitter with appropriate chunk sizing
- [ ] Develop file change monitoring system
- [ ] Set up metadata extraction from documents
- [ ] Test document processing with sample files

### Phase 3: Embedding & Vector Storage
- [ ] Implement Ollama embedding integration
- [ ] Configure ChromaDB for vector storage
- [ ] Create persistence mechanism for embeddings
- [ ] Develop document indexing pipeline
- [ ] Build retrieval system for querying vectors

### Phase 4: RAG Pipeline & LLM Integration
- [ ] Create prompt templates for RAG
- [ ] Implement Ollama LLM integration
- [ ] Develop RAG chain with context injection
- [ ] Add configuration options for the pipeline
- [ ] Test end-to-end query with retrieved context

### Phase 5: User Interfaces
- [ ] Build command-line interface
- [ ] Develop simple API with FastAPI
- [ ] Create basic documentation for usage
- [ ] Implement endpoints for querying and reindexing
- [ ] Test interfaces with real documents

### Phase 6: Docker & Integration
- [ ] Create Dockerfile for RAG service
- [ ] Update docker-compose.yml to include RAG service
- [ ] Configure volumes and environment variables
- [ ] Test integration with existing Obelisk services
- [ ] Verify end-to-end functionality in containers

## Implementation Order

1. First Implementation Tasks:
   - [ ] Project structure setup
   - [ ] Configuration system
   - [ ] Basic document processing

2. Second Implementation Tasks:
   - [ ] Embedding generation with Ollama
   - [ ] Vector storage with ChromaDB
   - [ ] Simple retrieval mechanism

3. Third Implementation Tasks:
   - [ ] RAG pipeline with LangChain
   - [ ] LLM integration with Ollama
   - [ ] Testing with sample questions

4. Final Implementation Tasks:
   - [ ] CLI interface
   - [ ] API endpoints
   - [ ] Docker container setup
   - [ ] Integration with existing services

## MVP Core Components

### 1. Document Processing Pipeline

**MVP Implementation:**
- [ ] Simple directory monitor for the `./vault` folder using Watchdog
- [ ] LangChain markdown loader for processing files
- [ ] Basic chunking strategy with RecursiveCharacterTextSplitter

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class MarkdownHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            process_file(event.src_path)

def process_file(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    # Send to embedding pipeline
```

**Future Enhancements:**
- YAML frontmatter parsing
- Smart chunking based on markdown structure
- Git integration for version-aware processing

### 2. Embedding Generation

**MVP Implementation:**
- [ ] Use Ollama with mxbai-embed-large (already compatible)
- [ ] Simple sequential embedding of document chunks

```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434"
)

def embed_documents(chunks):
    for chunk in chunks:
        embedding = embeddings.embed_documents([chunk.page_content])[0]
        # Store embedding with document in vector store
```

**Future Enhancements:**
- Batch processing for performance
- Caching to avoid redundant embedding
- Alternative model support (Stella, BGE, etc.)

### 3. Vector Storage

**MVP Decision: Chroma**
- [ ] Set up Chroma for simple vector storage
- [ ] Configure persistence to disk with minimal setup
- [ ] Implement basic querying functionality

```python
from langchain_community.vectorstores import Chroma

def store_embeddings(chunks, embeddings_model):
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory="./chroma_db"
    )
    vector_store.persist()
    return vector_store
```

**Future Enhancement Path:**
- Migration to Milvus Lite if scale becomes an issue
- Advanced indexing configurations
- Metadata filtering capabilities

### 4. RAG Pipeline

**MVP Implementation:**
- [ ] Simple RetrievalQA chain with LangChain
- [ ] Basic prompt template for context insertion

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

prompt_template = """You are an assistant helping with questions about Obelisk documentation.
Use the following context to answer the question. If you don't know, say so.

Context:
{context}

Question: {question}
Answer: """

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

def create_qa_chain(vector_store, llm):
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain
```

**Future Enhancements:**
- Maximal Marginal Relevance retrieval
- Multi-query retrieval strategies
- Query reformulation techniques
- Citation and source tracking

### 5. LLM Integration

**MVP Implementation:**
- [ ] Ollama with Llama3 (8B or smaller quantized model)
- [ ] Simple streaming interface for responses

```python
from langchain_ollama import Ollama

def setup_llm():
    llm = Ollama(
        model="llama3",  # or llama3:8b
        temperature=0.1,
        base_url="http://localhost:11434"
    )
    return llm
```

**Future Enhancements:**
- Model switching capability (Phi-4, DeepSeek-R1)
- Performance optimizations based on hardware
- Custom prompt templates per model

### 6. User Interface

**MVP Implementation:**
- [ ] Simple CLI interface for direct interaction
- [ ] Basic FastAPI endpoint for integration with tools

```python
import argparse
from fastapi import FastAPI, Body
from pydantic import BaseModel

# CLI
def setup_cli():
    parser = argparse.ArgumentParser(description="Query your documentation")
    parser.add_argument("question", help="Your question about the documentation")
    return parser

# API
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/api/query")
async def query_docs(query: Query):
    response = qa_chain.run(query.question)
    return {"response": response}
```

**Future Enhancement:**
- OpenWebUI integration 
- Web interface with source citations
- Chat history and conversation state

## Technical Decisions for MVP

1. **Embedding Model**: mxbai-embed-large via Ollama
   - Rationale: Already integrated with Ollama, good performance, simple setup

2. **Vector Database**: Chroma
   - Rationale: Lowest complexity, well-integrated with LangChain, sufficient for thousands of documents

3. **LLM**: Llama3 (8B variant) via Ollama
   - Rationale: Good balance of quality and performance on average hardware

4. **Framework**: LangChain core components
   - Rationale: Reduces custom code, well-tested integration patterns

5. **UI Approach**: CLI first, simple API for integration
   - Rationale: Fastest path to functional system, defer UI complexity

## Project Structure

```
obelisk/
├── rag/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── document.py        # Document processing
│   ├── embedding.py       # Embedding generation
│   ├── storage.py         # Vector database interface
│   ├── pipeline.py        # RAG pipeline implementation
│   ├── api.py             # FastAPI interface
│   └── cli.py             # Command-line interface
├── tests/
│   └── rag/
│       ├── test_document.py
│       ├── test_embedding.py
│       └── test_pipeline.py
```

## Docker Composition (Simplified for MVP)

```yaml
version: "3.8"

services:
    ollama:
        image: ollama/ollama:latest
        ports:
            - "11434:11434"
        volumes:
            - ollama_data:/root/.ollama
        restart: unless-stopped

    openwebui:
        image: ghcr.io/open-webui/open-webui:latest
        depends_on:
            - ollama
        ports:
            - "8080:8080"
        environment:
            - OLLAMA_BASE_URL=http://ollama:11434
        restart: unless-stopped

    rag-api:
        build:
            context: .
            dockerfile: Dockerfile.rag
        ports:
            - "8000:8000"
        environment:
            - VAULT_DIR=/vault
            - OLLAMA_URL=http://ollama:11434
            - OLLAMA_MODEL=llama3
        volumes:
            - ./vault:/vault
            - rag_data:/app/data
        depends_on:
            - ollama
        restart: unless-stopped

volumes:
    ollama_data:
    rag_data:
```

## Example Implementation

```python
# rag_pipeline.py
import os
import glob
from typing import List, Dict, Any
import argparse
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, Ollama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn

# Configuration
VAULT_DIR = os.environ.get("VAULT_DIR", "./vault")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "mxbai-embed-large")
CHROMA_DIR = os.environ.get("CHROMA_DIR", "./chroma_db")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "200"))
RETRIEVE_TOP_K = int(os.environ.get("RETRIEVE_TOP_K", "3"))

# Initialize components
embeddings_model = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_URL
)

llm = Ollama(
    model=OLLAMA_MODEL,
    temperature=0.1,
    base_url=OLLAMA_URL
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# Global vector store
vector_store = None

def initialize_vector_store():
    """Initialize or load the vector store"""
    global vector_store
    if os.path.exists(CHROMA_DIR):
        print(f"Loading existing vector store from {CHROMA_DIR}")
        vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings_model
        )
    else:
        print(f"Creating new vector store at {CHROMA_DIR}")
        vector_store = Chroma(
            embedding_function=embeddings_model,
            persist_directory=CHROMA_DIR
        )
        # Process all existing documents
        process_all_files()

def process_file(file_path: str):
    """Process a single markdown file"""
    print(f"Processing file: {file_path}")
    try:
        loader = TextLoader(file_path)
        documents = loader.load()

        # Add source metadata
        for doc in documents:
            doc.metadata["source"] = file_path

        # Split into chunks
        chunks = text_splitter.split_documents(documents)

        # Add or update in vector store
        vector_store.add_documents(chunks)
        vector_store.persist()
        print(f"Added {len(chunks)} chunks from {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_all_files():
    """Process all markdown files in the vault directory"""
    print(f"Processing all files in {VAULT_DIR}")
    for md_file in glob.glob(f"{VAULT_DIR}/**/*.md", recursive=True):
        process_file(md_file)

# Create RAG chain
def create_qa_chain():
    """Create the question-answering chain"""
    prompt_template = """You are an assistant helping with questions about the Obelisk documentation.
Use ONLY the following context to answer the question. If the information isn't in the context, say you don't know.

Context:
{context}

Question: {question}
Answer: """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVE_TOP_K})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

# File watcher
class MarkdownHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            process_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            process_file(event.src_path)

def start_file_watcher():
    """Start watching for file changes in the vault directory"""
    event_handler = MarkdownHandler()
    observer = Observer()
    observer.schedule(event_handler, VAULT_DIR, recursive=True)
    observer.start()
    return observer

# CLI Interface
def run_cli():
    """Run the CLI interface"""
    initialize_vector_store()
    qa_chain = create_qa_chain()

    parser = argparse.ArgumentParser(description="Query your Obelisk documentation")
    parser.add_argument("question", help="Your question about the documentation")
    args = parser.parse_args()

    answer = qa_chain.run(args.question)
    print(f"\nQ: {args.question}\n")
    print(f"A: {answer}")

# API Interface
app = FastAPI(title="Obelisk RAG API")

class Query(BaseModel):
    question: str

@app.post("/api/query")
async def query_docs(query: Query):
    """API endpoint to query the documentation"""
    global qa_chain
    response = qa_chain.run(query.question)
    return {"response": response}

@app.post("/api/reindex")
async def reindex():
    """API endpoint to trigger reindexing of all documents"""
    process_all_files()
    return {"status": "success", "message": "Reindexing complete"}

# Main entry point
if __name__ == "__main__":
    # Check if running as CLI or API
    if len(os.sys.argv) > 1:
        # CLI mode
        run_cli()
    else:
        # API mode
        print("Starting Obelisk RAG API server...")
        initialize_vector_store()
        qa_chain = create_qa_chain()

        # Start file watcher
        observer = start_file_watcher()

        try:
            # Start API server
            uvicorn.run(app, host="0.0.0.0", port=8000)
        finally:
            observer.stop()
            observer.join()
```

## Dockerfile.rag

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock* /app/

# Poetry already installed in the devcontainer
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application
COPY . /app/

# Environment variables
ENV VAULT_DIR=/vault
ENV CHROMA_DIR=/app/data/chroma_db
ENV OLLAMA_URL=http://ollama:11434
ENV OLLAMA_MODEL=llama3
ENV EMBEDDING_MODEL=mxbai-embed-large

# Expose port
EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "-m", "obelisk.rag.api"]
```

By focusing on these core components, we can quickly build a functional MVP that demonstrates the power of local RAG while setting the foundation for all the advanced features in the future roadmap.

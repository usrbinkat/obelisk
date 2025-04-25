from langchain.schema.document import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_ollama import OllamaEmbeddings

# Create a test document
doc = Document(
    page_content="This is a test document",
    metadata={"source": "test.md", "title": "Test"}
)

# Create embeddings model
embeddings_model = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434"
)

# Try to add to Chroma directly
try:
    # Create a temporary Chroma DB
    db = Chroma(
        persist_directory="./.test_chroma",
        embedding_function=embeddings_model
    )
    
    # Try to add the document
    print("Adding document to Chroma...")
    docs = [doc]
    
    # Apply filtering
    filtered_docs = []
    for d in docs:
        # Create a dictionary with filtered metadata
        filtered_metadata = {}
        for key, value in d.metadata.items():
            # Only include primitive types
            if isinstance(value, (str, int, float, bool)):
                filtered_metadata[key] = value
        
        # Create a new document with filtered metadata
        filtered_doc = Document(
            page_content=d.page_content,
            metadata=filtered_metadata
        )
        filtered_docs.append(filtered_doc)
    
    db.add_documents(filtered_docs)
    print("Success!")
    
    # Try to query
    print("Testing query...")
    results = db.similarity_search("test", k=1)
    print(f"Found {len(results)} results")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
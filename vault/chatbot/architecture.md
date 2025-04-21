---
title: Architecture Diagram
date: 2025-04-21
---

# System Architecture

This page contains a comprehensive architecture diagram for the Obelisk system, showing how all components interact from the document processing pipeline through to the client applications.

## Full Architecture Diagram

```mermaid
flowchart TB
    %% STYLE: Optimized layout for vertical scrolling with better horizontal space utilization
    
    %% Document Processing Pipeline
    subgraph DocumentProcessing ["Document Processing Pipeline"]
        direction TB
        
        subgraph Reconciliation ["Document Reconciliation"]
            direction LR
            VaultDir["Vault Directory"]:::file --> DocReconciler["Document Object Reconciler"]:::process
            HashTable["Document Hash Table"]:::database --> DocReconciler
            
            %% Simplified reconciliation flow (horizontal layout)
            DocReconciler --> NewHash["New Document Hash"]:::process --> HashDecision{"Hash Exists?"}:::decision
            HashDecision -- "Yes" --> DiscardDoc["Discard Document"]:::process
            HashDecision -- "No" --> ProcessDoc["Process Document"]:::process
            
            DocReconciler -- "Delete" --> RemoveHash["Remove Hash & Vectors"]:::process
            DocReconciler -- "Change" --> UpdateHash["Update Vectors & Reprocess"]:::process
            VaultDir -. "Deleted Files" .-> DeletedDocs["Deleted Documents"]:::deleted
        end
        
        Reconciliation --> Encoder["Embedding Generation"]
        
        %% Embedding process (more compact)
        subgraph Encoder
            direction LR
            DocChunker["Document Chunker"]:::process --> MetadataGen["Metadata Generator"]:::process --> DocMetadata["Document Metadata"]:::data
            DocChunker --> VectorGen["Vector Generator"]:::process --> ChunkVectors["Chunk Vectors"]:::data
            VectorGen -. "Uses mxbai-embed-large" .-> ChunkVectors
        end
    end
    
    %% Storage and AI layers side by side
    subgraph MiddleLayers ["Data & AI Layers"]
        direction LR
        
        subgraph StorageLayer ["Vector Persistence"]
            direction TB
            SQLMetadata["SQL Metadata DB"]:::database
            MilvusDB["Milvus Vector DB"]:::database
        end
        
        subgraph AILayer ["AI Service Layer"]
            direction TB
            subgraph LiteLLMProxy ["LiteLLM Proxy"]
                CloudLLMs["Cloud LLMs (OpenAI, Claude)"]:::service
                LocalLLMs["Local LLMs (Ollama/Llama3/Phi-4)"]:::service
            end
        end
    end
    
    %% Integration and Clients (more compact)
    subgraph BottomLayers ["Integration & Client Layers"]
        direction LR
        
        subgraph MCPLayer ["MCP Integration"]
            direction TB
            ObeliskRAGAPI["Obelisk RAG API"]:::api
            MCPServer["MCP Server"]:::service
        end
        
        subgraph ClientApps ["Client Applications"]
            direction TB
            WebUI["OpenWebUI"]:::client
            MCPClients["Claude Desktop, ChatGPT Desktop, VSCode"]:::client
        end
    end
    
    %% CONNECTIONS: Simplified for clarity
    DocMetadata --> SQLMetadata
    ChunkVectors --> MilvusDB
    
    %% WebUI direct connections
    SQLMetadata --> WebUI
    MilvusDB --> WebUI
    LiteLLMProxy --> WebUI
    
    %% MCP pathway
    SQLMetadata --> ObeliskRAGAPI
    MilvusDB --> ObeliskRAGAPI
    LiteLLMProxy --> ObeliskRAGAPI
    ObeliskRAGAPI --> MCPServer
    MCPServer --> MCPClients
    
    %% Main flow
    DocumentProcessing --> MiddleLayers
    MiddleLayers --> BottomLayers
    
    %% STYLING: Enhanced visual appearance
    classDef process fill:#f9f,stroke:#333,stroke-width:2px
    classDef data fill:#bbf,stroke:#333,stroke-width:2px
    classDef file fill:#afa,stroke:#333,stroke-width:2px
    classDef database fill:#fda,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    classDef deleted fill:transparent,stroke:#FF6D00,stroke-width:3px
    classDef service fill:#d9f,stroke:#333,stroke-width:2px
    classDef api fill:#faa,stroke:#333,stroke-width:2px
    classDef client fill:#adf,stroke:#333,stroke-width:2px
    classDef decision fill:#ffb,stroke:#333,stroke-width:2px,shape:diamond

    %% Visual grouping emphasis
    style DocumentProcessing fill:#f5f5f5,stroke:#333,stroke-width:2px
    style MiddleLayers fill:#f0f8ff,stroke:#333,stroke-width:2px
    style BottomLayers fill:#fff0f5,stroke:#333,stroke-width:2px
    style Reconciliation fill:#f0f0f0,stroke:#333,stroke-width:1px
    style Encoder fill:#f0f0f0,stroke:#333,stroke-width:1px
    style StorageLayer fill:#e6f2ff,stroke:#333,stroke-width:1px
    style AILayer fill:#f0fff0,stroke:#333,stroke-width:1px 
    style MCPLayer fill:#fff0f5,stroke:#333,stroke-width:1px
    style ClientApps fill:#fffaf0,stroke:#333,stroke-width:1px
```

## Component Descriptions

### Document Processing Pipeline

The foundation of the Obelisk RAG system is the document processing pipeline, which handles:

#### Document Reconciliation
- **Vault Directory**: Source of markdown documents from the Obsidian vault
- **Document Object Reconciler**: Determines which documents need processing based on changes
- **Hash Table**: Stores document hashes to detect changes
- **Change Detection**: Identifies new, modified, and deleted documents

#### Embedding Generation
- **Document Chunker**: Breaks documents into semantic chunks for better retrieval
- **Metadata Generator**: Extracts and creates metadata for each document and chunk
- **Vector Generator**: Creates embeddings using mxbai-embed-large model
- **Chunk Vectors**: The embedded vector representations of document chunks

### Data & AI Layers

The middle layers provide data persistence and AI model access:

#### Vector Persistence
- **SQL Metadata DB**: Stores document metadata and relationships
- **Milvus Vector DB**: High-performance vector database for semantic search

#### AI Service Layer
- **LiteLLM Proxy**: Unified interface to multiple LLM providers
  - **Cloud LLMs**: Access to OpenAI and Anthropic Claude models
  - **Local LLMs**: Integration with Ollama for running Llama 3, Phi-4, etc.

### Integration & Client Layers

The user-facing components of the system:

#### MCP Integration
- **Obelisk RAG API**: REST API for accessing RAG capabilities
- **MCP Server**: Model Control Protocol server for standardized AI interaction

#### Client Applications
- **OpenWebUI**: Web-based chat interface with direct RAG integration
- **MCP Clients**: Desktop and IDE clients that connect via the MCP protocol

## Data Flow

1. **Document Ingestion**: The system monitors the Vault Directory for changes, creating hash values for each document
2. **Document Processing**: Changed documents are chunked, embedded, and stored in the vector database
3. **Storage**: Document metadata is stored in SQL, while vector embeddings are stored in Milvus
4. **Query Processing**: When a user query arrives, relevant documents are retrieved from vector storage
5. **LLM Enhancement**: Retrieved documents are used to enhance prompts sent to LLM models
6. **Client Delivery**: Responses are delivered through either OpenWebUI or MCP-compatible clients

## Integration Points

The architecture supports multiple integration pathways:

1. **Direct OpenWebUI Path**: For web-based chat interface users
2. **MCP Protocol Path**: For desktop applications and IDE integrations
3. **API Access**: For custom integrations with the Obelisk RAG capability

For detailed implementation guidance, see the [RAG Implementation Guide](rag/implementation.md) and [Using RAG](rag/using-rag.md) sections.
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Obelisk is a tool that transforms Obsidian vaults into MkDocs Material Theme sites with AI integration through Ollama and Open WebUI. It preserves Obsidian's rich features while delivering a modern documentation website with AI chat capabilities, including a RAG (Retrieval-Augmented Generation) pipeline for context-aware responses.

## Repository
- GitHub: https://github.com/usrbinkat/obelisk

## Core Features
- Convert Obsidian vaults to MkDocs Material Theme sites (wiki links, callouts, comments)
- Built-in AI chatbot integration via Ollama and Open WebUI
- RAG pipeline for context-aware document retrieval
- Vector database integration (ChromaDB with Milvus planned)
- Custom styling and theming capabilities
- Documentation versioning with mike
- Docker and container-based deployment

## Architecture

The project consists of several integrated components:

1. **Python Package** (`/obelisk/`): Core utilities
   - `cli.py`: Command-line interface
   - `config.py`: Configuration management
   - `convert.py`: Obsidian to MkDocs conversion
   - `/rag/`: RAG system components
     - `service.py`: Main RAG service coordinator
     - `document.py`: Document processing and chunking
     - `embedding.py`: Vector embedding generation
     - `storage.py`: Vector database integration
     - `api.py`: OpenAI-compatible API endpoints

2. **Documentation Content** (`/vault/`): Source content and customizations
   - `stylesheets/extra.css`: Custom CSS styles
   - `javascripts/extra.js`: Custom JavaScript
   - `overrides/main.html`: HTML template overrides

3. **Container Architecture**:
   - `obelisk`: MkDocs documentation server (port 8000)
   - `ollama`: Local LLM serving (port 11434)
   - `open-webui`: Chat interface (port 8080)
   - `obelisk-rag`: RAG API service (port 8001)
   - `milvus`: Vector database (port 19530)
   - `litellm`: LLM API proxy for integration
   - `init-service`: Container initialization

## Project Structure
```
/workspaces/obelisk/
├── obelisk/                # Python package
│   ├── __init__.py         # Version and metadata
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration utilities
│   └── convert.py          # Conversion logic
├── vault/                  # Documentation content
│   ├── assets/             # Static assets
│   ├── stylesheets/        # CSS customizations
│   ├── javascripts/        # JS customizations
│   └── overrides/          # HTML template overrides
├── .github/workflows/      # CI/CD configuration
├── mkdocs.yml              # MkDocs configuration
├── docker-compose.yaml     # Docker services definition
├── Dockerfile              # Container definition
├── pyproject.toml          # Python project definition
└── README.md               # Project documentation
```

## Build Commands
- `poetry install --no-root` - Install dependencies
- `poetry run mkdocs build` - Build static site
- `poetry run mkdocs build --clean --strict` - Run strict build testing
- `poetry run mkdocs serve --livereload --dirty` - Fast development server with livereload
- `poetry run mkdocs serve --livereload --watch-theme --open` - Build and serve with browser opening
- `rm -rf site && find . -type d -name __pycache__ -exec rm -rf {} +` - Remove build artifacts
- `poetry update` - Update all dependencies
- `poetry run mkdocs gh-deploy --force` - Deploy to GitHub Pages
- `poetry run mike deploy --push --update-aliases <VERSION> "<DESCRIPTION>"` - Deploy version
- `poetry run mike set-default --push <VERSION>` - Set default version

## Docker Commands
- `docker build -t obelisk:latest .` - Build Docker container
- `docker run -p 8000:8000 -v ${PWD}/vault:/app/vault -v ${PWD}/mkdocs.yml:/app/mkdocs.yml -v ${PWD}/pyproject.toml:/app/pyproject.toml -v ${PWD}/poetry.lock:/app/poetry.lock obelisk:latest` - Run with local volumes mounted
- `docker-compose up obelisk` - Run Obelisk service only
- `docker-compose up` - Run full stack with Ollama and OpenWebUI

## Creating New Content
To create a new markdown file in the vault:
```bash
mkdir -p vault
cat > vault/page-name.md << EOF
---
title: page-name
date: $(date +%Y-%m-%d)
---

EOF
```

## AI Integration

Obelisk integrates AI capabilities through a multi-service architecture:

1. **Ollama**: Lightweight local model server
   - Port: `11434`
   - Supports models like Llama3, Mistral, Phi, Gemma
   - Used for both text generation and embeddings

2. **Open WebUI**: Web interface for chat
   - Port: `8080`
   - Connected to Ollama for model inference
   - Supports direct RAG integration

3. **Documentation Server**: MkDocs site
   - Port: `8000`
   - Integrated with chat UI via JavaScript

4. **RAG API Service**: OpenAI-compatible API
   - Port: `8001`
   - Processes and indexes markdown documents
   - Handles document retrieval via vector search
   - Augments LLM responses with relevant context

5. **LiteLLM Proxy**: LLM middleware
   - Port: `4000`
   - Provides unified interface for multiple LLM providers
   - Handles authentication and routing

The RAG pipeline flow:
1. Document processing: Markdown files are parsed, chunked, and metadata extracted
2. Embedding generation: Text chunks are converted to vector embeddings via Ollama
3. Vector storage: Embeddings stored in ChromaDB/Milvus with metadata
4. Query processing: User questions embedded and similar documents retrieved
5. Response generation: Context and query sent to LLM for enhanced responses

## Code Style Guidelines
- Python: Follow PEP 8 standards, target Python 3.12
- Use Poetry for dependency management
- YAML files: 2-space indentation
- MkDocs Markdown content: Use Material theme features (admonitions, etc.)
- Prefer absolute imports in Python code
- Use ruff for linting (configured in pyproject.toml)

## Testing and Validation
- Use `poetry run mkdocs build --clean --strict` for strict build testing
- Ensure all links resolve correctly
- Validate HTML templates with proper syntax
- Test site rendering across different viewports
- **CRITICAL**: NEVER commit code without thorough testing first
- Run appropriate tests for any code changes (`poetry run pytest`)
- For container changes, test with `docker-compose up` before committing
- Validate all configuration changes before pushing to a branch

## Git Commit Standards
When managing code changes with git, adhere to the following strict standards:

### Commit Process
1. **Test Before Commit**: ALL code MUST be thoroughly tested before any commit
   - Run appropriate unit/integration tests for the changed components
   - For container changes, validate with docker-compose
   - Verify that the application functions correctly with your changes
2. **Individual File Commits**: Commit each file individually to maintain atomic, focused changes
3. **Comprehensive Review**: For each file in `git status`, evaluate whether to:
   - Stage and commit the file
   - Add to `.gitignore` if it's a generated artifact
   - Remove if it's temporary/unnecessary

### Staging Guidelines
- Use precise path targeting: `git add <specific-file-path>` instead of broad patterns
- Review staged changes with `git diff --staged` before committing
- For new files, verify they belong in the repository and aren't build artifacts

### Commit Message Format
Each commit message must follow this structure:
```
<type>(<scope>): <technical description>

<optional detailed explanation>
```

Where:
- **type**: feat, fix, docs, style, refactor, test, chore
- **scope**: Component affected (e.g., cli, config, rag)
- **description**: Technical, precise explanation of the change (not the work done)

Example commit messages:
```
feat(rag): implement vector similarity search with FAISS backend

fix(config): resolve path normalization issue in Windows environments

test(pipeline): add comprehensive unit tests for document chunking
```

### Commit Message Requirements
- Focus exclusively on technical implementation details
- Describe what was changed and why, not how it was changed
- Use imperative, present tense verbs (e.g., "add" not "added")
- Maximum 72 characters for the first line
- No references to authorship or AI assistance
- No marketing language or non-technical descriptions
- Include relevant technical context (performance impacts, algorithm choices)

### Prohibited Content
- No signatures, attribution, or references to Claude/AI assistance
- No "I" statements or personal language
- No placeholder text or generic descriptions 
- No emojis or decorative elements

## Deployment Workflow
1. Make changes to documentation or code
2. Test locally with `poetry run mkdocs build --clean --strict`
3. Build and review with `poetry run mkdocs build`
4. Deploy new version with `poetry run mike deploy --push --update-aliases <VERSION> "<DESCRIPTION>"`
5. Set as default version if needed with `poetry run mike set-default --push <VERSION>`
6. For GitHub Pages, use `poetry run mkdocs gh-deploy --force`

## Dependencies
- Python 3.12+
- MkDocs and Material theme
- Poetry for package management
- Docker and Docker Compose (for containerization)
- NVIDIA Container Toolkit (for GPU acceleration with Ollama)
- LangChain and LangChain-Ollama for RAG pipelines
- ChromaDB/Milvus for vector storage
- FastAPI and Uvicorn for API services
- Watchdog for file monitoring

## RAG Implementation Status
- Core RAG pipeline is functional using ChromaDB
- OpenAI-compatible API endpoint available at `/v1/chat/completions`
- Document chunking and embedding operational
- Milvus integration planned but not fully implemented
- LiteLLM integration for multiple model providers
- File watching for real-time document updates
- Support for YAML frontmatter metadata extraction
- Hierarchical chunking based on markdown structure

## MCP Server Skills
The following MCP servers are available for use:
- `puppeteer`: Browser automation with Puppeteer
- `playwright`: Browser automation with Playwright
- `pulumi`: Infrastructure as code with Pulumi
- `github`: GitHub API integration
- `sequential-thinking`: Sequential thinking for complex problems
- `gitlab`: GitLab API integration
- `kubernetes`: Kubernetes integration
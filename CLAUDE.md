# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Obelisk is a tool that transforms Obsidian vaults into MkDocs Material Theme sites with AI integration through Ollama and Open WebUI. It focuses on preserving Obsidian's rich features while delivering a modern, responsive documentation website with integrated AI chat capabilities.

## Core Features
- Convert Obsidian vaults to MkDocs Material Theme sites
- Built-in AI chatbot integration via Ollama and Open WebUI
- RAG (Retrieval-Augmented Generation) pipeline (planned)
- Custom styling and theming capabilities
- Documentation versioning with mike
- Docker and container-based deployment

## Architecture

The project consists of several key components:

1. **Python Package** (`/obelisk/`): Core conversion utilities
   - `cli.py`: Command-line interface
   - `config.py`: Configuration management
   - `convert.py`: Obsidian to MkDocs conversion

2. **Documentation Content** (`/vault/`): Source content and customizations
   - `stylesheets/extra.css`: Custom CSS styles
   - `javascripts/extra.js`: Custom JavaScript
   - `overrides/main.html`: HTML template overrides

3. **Configuration Files**:
   - `mkdocs.yml`: MkDocs configuration
   - `pyproject.toml`: Python package configuration
   - `docker-compose.yaml`: Container orchestration

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

Obelisk integrates AI capabilities through:

1. **Ollama**: Lightweight local model server
   - Port: `11434`
   - Supports models like Llama2, Mistral, Phi, Gemma

2. **Open WebUI**: Web interface for chat
   - Port: `8080`
   - Connected to Ollama for model inference

3. **Documentation Server**: MkDocs site
   - Port: `8000`
   - Can be integrated with chat UI

The planned RAG pipeline will allow:
- Document processing and embedding
- Vector database storage
- Query processing and retrieval
- Enhanced AI responses with document context

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
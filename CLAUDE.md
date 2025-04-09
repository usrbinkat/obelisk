# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Obelisk is a tool to publish Obsidian vaults as MkDocs Material Theme sites with AI integration.

## Build Commands
- `task install` - Install dependencies (Poetry)
- `task build` - Build static site
- `task test` - Run strict build testing
- `task run` - Fast development server with livereload
- `task serve` - Build and serve with browser opening
- `task clean` - Remove build artifacts

## Docker Commands
- `task docker-build` - Build Docker container
- `task docker-run` - Run with local volumes mounted
- `task compose-obelisk` - Run Obelisk service only
- `task compose` - Run full stack with Ollama and OpenWebUI

## Code Style Guidelines
- Python: Follow PEP 8 standards
- Use Poetry for dependency management
- YAML files: 2-space indentation
- Markdown content: Use Material theme features (admonitions, etc.)
- Prefer absolute imports in Python code
- Maintain consistent naming convention in Taskfile
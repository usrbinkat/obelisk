# Obelisk

Publish Obsidian vaults as MkDocs Material Theme GitHub Pages with AI integration.

## Overview

Obelisk is a tool designed to transform your Obsidian vault into a beautifully rendered static site using MkDocs with the Material theme. It features built-in AI capabilities through integration with Ollama and Open WebUI.

## Features

- **Obsidian Compatibility**: Works with existing Obsidian vaults
- **MkDocs Material Theme**: Beautiful, responsive, and feature-rich documentation
- **AI Integration**: Connect with Ollama and Open WebUI for AI-enhanced content
- **Docker Support**: Easy deployment with containerization
- **Poetry**: Python dependency management

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Docker (optional, for containerized usage)

### Installation

```bash
# Clone the repository
git clone https://github.com/usrbinkat/obelisk.git
cd obelisk

# Install dependencies
poetry install
```

### Usage

#### Task Commands

Obelisk includes several task commands to simplify common operations:

```bash
# Install dependencies
task install

# Start the development server
task run

# Build the static site
task build

# Test the build with strict mode
task test

# Create a new page
task new -- page-name

# Update dependencies
task update

# Deploy to GitHub Pages
task gh-pages
```

#### Docker Commands

```bash
# Build the Docker image
task docker-build

# Run locally with Docker
task docker-run

# Run only the Obelisk service
task compose-obelisk

# Run the full stack (Obelisk, Ollama, OpenWebUI)
task compose
```

## License

[MIT](LICENSE)
# Development Configuration

This section documents the development environment configuration files and tools used in the Obelisk project.

## Project Structure

The root level of the Obelisk project contains several configuration files and directories that control development, building, and deployment:

```
/workspaces/obelisk/
├── .devcontainer/                # Development container configuration
│   ├── devcontainer.json         # VS Code development container settings
│   └── Dockerfile                # Development container image definition
├── .github/                      # GitHub-specific configurations
│   └── dependabot.yml            # Dependabot configuration
├── obelisk/                      # Python package for Obelisk
│   ├── __init__.py               # Package initialization
│   ├── cli.py                    # Command-line interface
│   ├── config.py                 # Configuration utilities
│   └── convert.py                # Conversion utilities
├── site/                         # Generated static site (output)
├── vault/                        # Documentation content (input)
├── .editorconfig                 # Editor configuration for consistency
├── .envrc                        # direnv configuration for environment setup
├── .gitattributes                # Git attributes configuration
├── .gitignore                    # Files ignored by Git
├── CLAUDE.md                     # Instructions for Claude AI assistant
├── CONTRIBUTING.md               # Contribution guidelines
├── docker-compose.yaml           # Docker Compose configuration
├── Dockerfile                    # Main Docker image definition
├── LICENSE                       # Project license
├── mkdocs.yml                    # MkDocs configuration
├── poetry.lock                   # Poetry locked dependencies
├── pyproject.toml                # Python project configuration
├── README.md                     # Project README
├── Taskfile.yaml                 # Task runner configuration
└── versions.json                 # Documentation version information
```

## Development Environment Files

The following sections document the various configuration files and their purposes:

- [Docker Configuration](docker.md) - Docker and container configuration
- [Task Runner](task-runner.md) - Task runner configuration and usage
- [Python Configuration](python-config.md) - Python project settings and dependencies
- [Git Configuration](git-config.md) - Git workflow and settings
- [Editor Configuration](editor-config.md) - Code editor settings
- [Documentation Files](documentation.md) - Project documentation
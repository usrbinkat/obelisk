# Python Configuration

Obelisk uses modern Python tooling for dependency management, packaging, and development.

## pyproject.toml

The `pyproject.toml` file defines the project's metadata, dependencies, and build system:

```toml
# View the pyproject.toml contents
cat /workspaces/obelisk/pyproject.toml
```

Key sections include:

### Project Metadata

```toml
[project]
name = "obelisk"
version = "0.1.0"
description = "Obsidian vault to MkDocs Material Theme site generator"
authors = [
    {name = "Obelisk Team"}
]
readme = "README.md"
requires-python = "^3.12"
license = "MIT"
```

### Dependencies

```toml
dependencies = [
    "mkdocs>=1.6.0,<2.0.0",
    "mkdocs-material>=9.6.11,<10.0.0",
    "mkdocs-material-extensions>=1.3.1,<2.0.0",
    "mkdocs-git-revision-date-localized-plugin>=1.4.5,<2.0.0",
    # Other dependencies...
]
```

### Script Entrypoints

```toml
[project.scripts]
obelisk = "obelisk.cli:main"
```

### Development Tools Configuration

```toml
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.ruff]
line-length = 88
target-version = "py312"
select = ["E", "F", "I", "W"]
ignore = []
```

## poetry.lock

The `poetry.lock` file contains the exact versions of all dependencies:

```
# View lock file summary
cat /workspaces/obelisk/poetry.lock | head -n 20
```

This file ensures reproducible builds by pinning exact versions of:
- Direct dependencies
- Transitive dependencies
- Platform-specific dependencies

## Poetry Usage

[Poetry](https://python-poetry.org/) is used for dependency management and packaging:

```bash
# Install dependencies
poetry install

# Add a dependency
poetry add package-name

# Update dependencies
poetry update

# Run a command in the virtual environment
poetry run command

# Activate the virtual environment
poetry shell
```

## direnv Integration

The `.envrc` file integrates with [direnv](https://direnv.net/) for automatic environment activation:

```
# View .envrc contents
cat /workspaces/obelisk/.envrc
```

When entering the project directory, direnv:
1. Activates the Python virtual environment
2. Sets necessary environment variables
3. Adds development tools to the PATH
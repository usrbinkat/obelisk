# Python Integration

Obelisk uses Python for extending MkDocs functionality and providing utilities for managing the documentation. This section details the Python components related to MkDocs customization.

## Project Structure

The Python code for Obelisk is organized in the `/workspaces/obelisk/obelisk` directory:

```
/workspaces/obelisk/obelisk/
├── __init__.py          # Package initialization with version info
├── cli.py               # Command-line interface 
├── config.py            # Configuration utilities
└── convert.py           # Conversion utilities for Obsidian to MkDocs
```

## Package Initialization

The `__init__.py` file defines basic package information:

```python
"""
Obelisk - Obsidian vault to MkDocs Material Theme site generator.
"""

__version__ = "0.1.0"
__author__ = "Obelisk Team"
```

## Command-Line Interface

The `cli.py` module provides a command-line interface for using Obelisk:

```python
"""
Obelisk CLI tool to convert Obsidian vaults to MkDocs sites.
"""

import argparse
import sys
import subprocess
from pathlib import Path

from . import __version__

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Obsidian vault to MkDocs Material Theme site."
    )
    parser.add_argument(
        "--version", action="version", version=f"Obelisk {__version__}"
    )
    parser.add_argument(
        "--vault", 
        type=str, 
        help="Path to Obsidian vault directory",
        default="vault"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output directory for the generated site",
        default="site"
    )
    parser.add_argument(
        "--serve", 
        action="store_true", 
        help="Start a development server after building"
    )
    
    # Command processing logic...
```

## Configuration Utilities

The `config.py` module contains utilities for handling MkDocs configuration:

```python
"""
Configuration utilities for Obelisk.
"""

import yaml

def get_default_config():
    """Return the default Obelisk configuration."""
    return {
        "site_name": "Obelisk",
        "site_description": "Obsidian vault to MkDocs Material Theme site generator",
        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.tabs",
                # Other features...
            ],
            "palette": [
                {
                    "scheme": "default",
                    "primary": "deep purple",
                    "accent": "deep orange"
                },
                {
                    "scheme": "slate",
                    "primary": "deep purple",
                    "accent": "deep orange"
                }
            ]
        },
        # Other configuration options...
    }
```

## Conversion Utilities

The `convert.py` module handles conversion from Obsidian to MkDocs format:

```python
"""
Conversion utilities for transforming Obsidian files to MkDocs-compatible format.
"""

import re
import shutil
from pathlib import Path

def process_obsidian_vault(vault_path, output_path="vault"):
    """
    Process an Obsidian vault directory and prepare it for MkDocs.
    """
    # Process all markdown files...

def convert_file(input_path, output_path):
    """
    Convert an Obsidian markdown file to MkDocs compatible format.
    """
    # Convert wiki links to markdown links
    # Convert Obsidian callouts to admonitions
    # Convert Obsidian comments to HTML comments
```

## Integration with MkDocs

The Python code integrates with MkDocs through:

1. **Command execution** - Running MkDocs commands via `subprocess`
2. **Configuration generation** - Creating and modifying `mkdocs.yml`
3. **Content processing** - Transforming Obsidian syntax to MkDocs/Material compatible format

## Using the Python CLI

The CLI is registered as an entry point in `pyproject.toml`:

```toml
[project.scripts]
obelisk = "obelisk.cli:main"
```

This allows running Obelisk as a command:

```bash
obelisk --vault /path/to/obsidian/vault --serve
```

## Extending with MkDocs Plugins

For more complex customizations, Python can be used to create custom MkDocs plugins. These would be placed in a `plugins` subdirectory and registered in `mkdocs.yml`.
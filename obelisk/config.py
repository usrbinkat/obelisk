"""
Configuration utilities for Obelisk.
"""

import os
import yaml
from pathlib import Path


def get_default_config():
    """Return the default Obelisk configuration."""
    return {
        "site_name": "Obelisk",
        "site_description": "Obsidian vault to MkDocs Material Theme site generator",
        "site_author": "Obelisk Team",
        "repo_name": "usrbinkat/obelisk",
        "repo_url": "https://github.com/usrbinkat/obelisk",
        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.tabs",
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "search.suggest",
                "search.highlight",
                "content.tabs.link",
                "content.code.copy"
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
        "markdown_extensions": [
            "admonition",
            "attr_list",
            "def_list",
            "footnotes",
            "md_in_html",
            "toc",
            "pymdownx.arithmatex",
            "pymdownx.betterem",
            "pymdownx.caret",
            "pymdownx.details",
            "pymdownx.emoji",
            "pymdownx.highlight",
            "pymdownx.inlinehilite",
            "pymdownx.keys",
            "pymdownx.mark",
            "pymdownx.smartsymbols",
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.tasklist",
            "pymdownx.tilde"
        ],
        "plugins": [
            "search",
            "git-revision-date-localized",
            "minify",
            "glightbox"
        ]
    }


def load_config(config_path=None):
    """Load configuration from a YAML file."""
    if config_path is None:
        config_path = os.path.join(os.getcwd(), "obelisk.yaml")
    
    config = get_default_config()
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f)
            if user_config:
                # Deep merge user config with default config
                config = deep_merge(config, user_config)
    
    return config


def deep_merge(base, override):
    """
    Deep merge two dictionaries.
    Values in override will overwrite values in base.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def generate_mkdocs_config(config, output_path="mkdocs.yml"):
    """Generate mkdocs.yml from Obelisk configuration."""
    with open(output_path, "w") as f:
        yaml.dump(config, f, sort_keys=False)
    
    return output_path
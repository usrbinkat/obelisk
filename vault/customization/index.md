# MkDocs Customization Guide

This section documents all customizations applied to the MkDocs Material theme in the Obelisk project.

## Overview

Obelisk uses [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/) to generate a static site from Markdown files. Several customizations have been applied to enhance the appearance and functionality.

## Customization Categories

- [CSS Styling](css/index.md) - Custom CSS styles applied to the Material theme
- [HTML Templates](html/index.md) - Customized HTML template overrides
- [JavaScript Enhancements](javascript/index.md) - Custom JavaScript functionality
- [Python Integration](python/index.md) - Python scripts and utilities for MkDocs
- [Versioning](versioning/index.md) - Documentation versioning with Mike

## Configuration

The primary configuration for MkDocs is in the `mkdocs.yml` file in the project root. This file controls theme settings, plugins, navigation, and more.

See the [detailed MkDocs configuration guide](mkdocs-configuration.md) for a complete reference.

## Directory Structure

Key directories related to MkDocs customization:

```
/workspaces/obelisk/
├── mkdocs.yml           # Main configuration file
├── vault/               # Content source (similar to "docs" in standard MkDocs)
│   ├── index.md         # Homepage
│   ├── stylesheets/     # Custom CSS
│   │   └── extra.css    # Primary custom styles
│   ├── javascripts/     # Custom JavaScript
│   │   └── extra.js     # Custom scripts
│   └── overrides/       # HTML template overrides
│       └── main.html    # Main template override
└── site/                # Output directory (generated)
    └── versions.json    # Versioning information
```
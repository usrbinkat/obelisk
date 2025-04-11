# MkDocs Configuration

The `mkdocs.yml` file is the central configuration file for the Obelisk documentation site. This file controls theme settings, plugins, navigation structure, and more.

## Basic Configuration

```yaml
site_name: Obelisk
site_description: Obsidian vault to MkDocs Material Theme site generator with AI integration
site_author: Obelisk Team
site_url: https://usrbinkat.github.io/obelisk

repo_name: usrbinkat/obelisk
repo_url: https://github.com/usrbinkat/obelisk
edit_uri: edit/main/vault/
```

These settings define:
- **site_name**: The name displayed in the header and browser title
- **site_description**: Used for SEO and metadata
- **site_author**: The author metadata
- **site_url**: The base URL where the site is hosted
- **repo_name**: The name of the GitHub repository 
- **repo_url**: Link to the GitHub repository
- **edit_uri**: Path for the "edit this page" functionality

## Theme Configuration

```yaml
theme:
  name: material
  custom_dir: vault/overrides
  features:
    # Navigation
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - navigation.top
    - navigation.footer
    - navigation.path
    
    # Table of contents
    - toc.follow
    - toc.integrate
    
    # Search
    - search.suggest
    - search.highlight
    - search.share
    
    # Content
    - content.tabs.link
    - content.code.annotation
    - content.code.copy
    - content.action.edit
    - content.action.view
    
    # Header anchors and tooltips
    - header.autohide
    
  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
      primary: deep purple
      accent: deep orange
    # Dark mode  
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
      primary: deep purple
      accent: deep orange
  font:
    text: Roboto
    code: Roboto Mono
  favicon: assets/favicon.png
  icon:
    logo: material/book-open-page-variant
    repo: fontawesome/brands/github
  language: en
```

Key theme settings:
- **name**: Specifies the Material theme
- **custom_dir**: Directory for template overrides
- **features**: Enables specific theme features
- **palette**: Defines color schemes for light and dark mode
- **font**: Specifies the fonts for text and code
- **favicon**: Path to the favicon
- **icon**: Icons for logo and repository
- **language**: Default language

## Markdown Extensions

```yaml
markdown_extensions:
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink:
      repo_url_shorthand: true
      user: usrbinkat
      repo: obelisk
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde
```

This section enables various Markdown extensions that enhance the standard Markdown syntax:
- **admonition**: Adds note, warning, tip blocks
- **attr_list**: Allows adding HTML attributes to elements
- **toc**: Table of contents with permalinks
- **pymdownx.emoji**: Adds emoji support
- **pymdownx.highlight**: Code syntax highlighting
- **pymdownx.superfences**: Fenced code blocks with support for Mermaid diagrams
- **pymdownx.tabbed**: Tabbed content
- **pymdownx.tasklist**: Task lists with custom checkboxes

## Plugins

```yaml
plugins:
  - search
  - git-revision-date-localized:
      enable_creation_date: true
      fallback_to_build_date: true
      type: date
  - minify:
      minify_html: true
      minify_js: true
      minify_css: true
  - awesome-pages
  - glightbox:
      touchNavigation: true
      loop: false
      effect: zoom
      width: 100%
      height: auto
      zoomable: true
      draggable: true
```

Plugins add additional functionality:
- **search**: Adds search functionality
- **git-revision-date-localized**: Shows last update date based on git
- **minify**: Reduces file sizes
- **awesome-pages**: Simplifies navigation configuration
- **glightbox**: Enhanced image viewing

## Extra Configuration

```yaml
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/usrbinkat
      name: GitHub
  version:
    provider: mike
    default: 0.1.0
  consent:
    title: Cookie consent
    description: >- 
      We use cookies to recognize your repeated visits and preferences, as well
      as to analyze traffic and understand where our visitors are coming from.
  generator: false

extra_css:
  - stylesheets/extra.css
extra_javascript:
  - javascripts/extra.js
```

Additional configuration options:
- **social**: Social media links for the footer
- **version**: Documentation versioning configuration
- **consent**: Cookie consent configuration
- **generator**: Hides the "Made with Material for MkDocs" notice
- **extra_css/extra_javascript**: Paths to custom CSS and JavaScript files

## Navigation

```yaml
docs_dir: vault

nav:
  - Home: index.md
  - Cloud: 
    - Overview: cloud/Cloud Native Tooling.md
```

- **docs_dir**: Specifies the directory containing documentation files
- **nav**: Defines the navigation structure
  - Can contain nested sections
  - Each entry has a title and a path to a markdown file
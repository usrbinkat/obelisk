# Sprint Notes: MkDocs Material Documentation Enhancement

**Sprint**: Documentation Enhancement with MkDocs Material
**Date**: January 2025
**Status**: Research Complete, Implementation Pending

## Research Findings

### MkDocs Core Features
- **Plugin System**: Extensible via Python modules with event hooks
- **No Built-in Code Generation**: Relies on plugin ecosystem
- **mkdocstrings**: Primary plugin for API documentation from docstrings
- **Hooks**: Lightweight automation via Python scripts in mkdocs.yml

### MkDocs Material Advanced Features
- **Code Annotations**: Interactive markers (`content.code.annotate`)
- **Content Tabs**: Switchable content groups
- **Social Cards**: Auto-generated preview images
- **Blog Plugin**: Built-in blogging support
- **Tags Plugin**: Content categorization
- **Version Selectors**: Via mike integration

## Implementation Approach

### 1. Template-Based Generators
Instead of print-heavy scripts, use Jinja2 templates:

```python
# scripts/gen-config-docs.py
from jinja2 import Template

CONFIG_TEMPLATE = Template("""
## Configuration Reference
{{ content }}
""")
```

### 2. Data-Driven Documentation
Store documentation structure in YAML/JSON:
```yaml
# docs/schema/config.yaml
providers:
  - name: LiteLLM
    default: true
    env_vars:
      - LITELLM_API_BASE
      - LITELLM_API_KEY
```

### 3. mkdocstrings Integration
Add to pyproject.toml:
```toml
[tool.poetry.group.docs.dependencies]
mkdocstrings = "^0.24.0"
mkdocstrings-python = "^1.8.0"
```

Configure in mkdocs.yml (see TASK.docs.md for full config).

## Benefits Analysis

### Automation Benefits
1. **Reduced Manual Sync**: API docs auto-generate from docstrings
2. **Type Safety**: Type annotations automatically documented
3. **Source Links**: Direct links to implementation
4. **Version Tracking**: Git revision dates on all pages

### User Experience Benefits
1. **Interactive Code**: Copy buttons, syntax highlighting
2. **Smart Navigation**: Instant loading, search suggestions
3. **Responsive Design**: Works on all devices
4. **Content Tabs**: Multiple examples in one place

### Maintenance Benefits
1. **Single Source**: Docstrings are the documentation
2. **Automatic Updates**: Changes reflect immediately
3. **Validation**: Build fails on broken references
4. **Minimal Custom CSS**: Leverages Material theme

## Migration from Print Strings

### Current Issues
- Hundreds of `print()` statements in generators
- Hard to maintain and modify
- No syntax validation
- Difficult to test

### Solution: Template + Data Architecture
```
docs/
├── templates/         # Jinja2 templates
│   ├── config.j2
│   ├── api.j2
│   └── service.j2
├── schemas/          # Data definitions
│   ├── config.yaml
│   └── api.yaml
└── generated/        # Output directory
```

## Action Items
1. ✅ Research MkDocs/Material capabilities
2. ✅ Create template-based generator example
3. ✅ Document patterns in LEAN_DOCUMENTATION.md
4. ⏳ Refactor all generators to use templates
5. ⏳ Add mkdocstrings to project
6. ⏳ Update documentation files with Material features

## Key Decisions
- Use Jinja2 for all documentation generation
- Store templates separately from logic
- Leverage mkdocstrings for API documentation
- Minimize custom HTML/CSS
- Use Material's built-in components

---

**Next Steps**: Implement template-based generators and add mkdocstrings to the project.
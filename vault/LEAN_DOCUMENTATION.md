# Lean Documentation Standard

> **Purpose**: Centralized specification for creating, maintaining, and evaluating documentation
> **Principle**: Just-in-time documentation that stays accurate through rapid iteration
> **Target**: Internal developers and early access technical insiders

## Core Principles

### 1. Just-In-Time Documentation
- Document only what's stable enough to survive multiple sprints
- Defer comprehensive guides until APIs stabilize
- Focus on what developers need TODAY

### 2. Code-as-Documentation
- Leverage type hints, docstrings, and tests as primary docs
- Generate documentation from code where possible
- Keep examples executable and testable

### 3. Single Source of Truth
- One canonical location per concept
- Aggressive cross-linking over duplication
- Reference implementation code directly

### 4. Automation First
- Generate what we can (configs, APIs, schemas)
- Manually write only what we must
- Validate documentation in CI/CD

## Documentation Categories

### 🚨 Critical (Must Have)
- **Architecture Overview**: Design decisions and component interactions
- **Developer Setup**: Environment configuration and quick start
- **API Reference**: Essential endpoints with working examples
- **Troubleshooting**: Common issues and solutions

### 📝 Important (Should Have)
- **Configuration Guide**: Environment variables and defaults
- **Integration Patterns**: How components work together
- **Performance Notes**: Key metrics and optimization tips

### 💡 Nice to Have (Could Have)
- **Extended Examples**: Complex use cases
- **Migration Guides**: For future major changes
- **Video Tutorials**: Visual walkthroughs

## Document Templates

### Architecture Decision Record (ADR)
```markdown
# ADR-XXX: [Decision Title]

> **Status**: Proposed/Accepted/Deprecated
> **Date**: YYYY-MM-DD
> **Deciders**: [Team/Person]

## Context
[What issue motivates this decision?]

## Decision
[What change are we implementing?]

## Consequences
- **Positive**: [Benefits]
- **Negative**: [Trade-offs]
- **Neutral**: [Side effects]

## Alternatives Considered
1. **[Option A]**: [Why not chosen]
2. **[Option B]**: [Why not chosen]
```

### API Endpoint Documentation
```markdown
## POST /endpoint/path

[One sentence description]

### Request
```json
{
  "required_field": "string",
  "optional_field": 123  // Optional: defaults to X
}
```

### Response
```json
{
  "status": "success",
  "data": {...}
}
```

### Errors
- `400`: Invalid input - [common cause]
- `500`: Server error - [troubleshooting link]

### Example
```bash
curl -X POST http://localhost:8001/endpoint/path \
  -H "Content-Type: application/json" \
  -d '{"required_field": "test"}'
```

### Source
[`src/path/to/implementation.py#L123`](link)
```

### Troubleshooting Entry
```markdown
## [Problem Description]

### Symptoms
- Error: `exact error text`
- When: During [operation]

### Quick Fix
```bash
# Immediate resolution
```

### Root Cause
[1-2 sentences explaining why]

### Prevention
[How to avoid this issue]
```

### Configuration Documentation
```markdown
## [Component] Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `ENV_VAR` | `value` | Purpose | Yes/No |

### Example
```bash
export ENV_VAR=custom_value
```

### Source
[`src/obelisk/common/config.py`](link)
```

## Documentation Standards

### File Naming
- Architecture: `docs/ARCHITECTURE.md`
- Setup: `docs/DEV-SETUP.md`
- API: `docs/API-QUICKSTART.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- ADRs: `docs/adr/XXX-title.md`

### Version Markers
```markdown
> **Version**: 0.1.0-alpha
> **Last Updated**: [git commit hash]
> **Stability**: 🟡 Experimental - API may change
```

### Stability Indicators
- 🟢 **Stable**: Unlikely to change
- 🟡 **Experimental**: May change in minor versions
- 🔴 **Unstable**: Will change, use at own risk

### Cross-References
- Use relative links: `../src/module/file.py`
- Include line numbers: `file.py#L42`
- Link to tests: `See tests/unit/test_feature.py`

## Automation Tools

### 1. Config Documentation Generator
```python
# scripts/gen-config-docs.py
"""Extract configuration from code and generate markdown tables."""
# Uses Jinja2 templates instead of print statements
# Example created during TASK.docs.md restructuring
```

### 2. API Documentation Generator
```python
# scripts/gen-api-docs.py
"""Generate OpenAPI spec and markdown from FastAPI routes."""
```

### 3. Service Dependency Visualizer
```python
# scripts/compose-to-mermaid.py
"""Create Mermaid diagrams from docker-compose.yaml."""
```

### 4. Documentation Validator
```python
# scripts/validate-docs.py
"""Ensure code examples are valid and links work."""
# Validates markdown code blocks
# Checks for outdated references
# Example created during TASK.docs.md restructuring
```

### 5. Progress Tracker
```bash
# scripts/track-progress.sh
# Tracks documentation update progress
# Counts completed vs pending tasks
# Validates no ChromaDB references remain
```

## Documentation Lifecycle

### Creation
1. Start with minimal viable documentation
2. Use templates for consistency
3. Link to implementation code
4. Add stability markers

### Maintenance
1. Update docs in same PR as code changes
2. Run validation scripts in CI
3. Review quarterly for accuracy
4. Deprecate outdated sections

### Evaluation Criteria
- **Accuracy**: Do examples work?
- **Completeness**: Are critical paths documented?
- **Freshness**: Last updated within sprint?
- **Accessibility**: Can developers find what they need?

## Current Documentation Index

### Core Documentation
- [Architecture Overview](../docs/ARCHITECTURE.md) - 🔴 Not Created
- [Developer Setup](../docs/DEV-SETUP.md) - 🔴 Not Created
- [API Quickstart](../docs/API-QUICKSTART.md) - 🔴 Not Created
- [Troubleshooting](../docs/TROUBLESHOOTING.md) - 🔴 Not Created

### Component Documentation
- [RAG Getting Started](./chatbot/rag/getting-started.md) - 🟡 Needs Update
- [RAG Implementation](./chatbot/rag/implementation.md) - 🟡 Needs Update
- [Vector Database](./chatbot/rag/vector-database.md) - 🟡 Needs Update
- [Deployment Architecture](./deployment/deployment-architecture.md) - 🟡 Needs Update

### Integration Guides
- [LiteLLM Integration](./chatbot/litellm-integration.md) - 🟡 Needs Update
- [Ollama Integration](./chatbot/rag/ollama-integration.md) - 🟡 Needs Update
- [OpenAI Integration](./chatbot/rag/openai/integration.md) - 🟢 Minor Updates
- [Milvus Integration](./chatbot/rag/milvus/integration.md) - 🟢 Minor Updates

## Review Checklist

### Before Publishing
- [ ] Code examples execute without errors
- [ ] Environment variables match implementation
- [ ] Links to source code are valid
- [ ] No references to deprecated features
- [ ] Version and stability markers present

### Quarterly Review
- [ ] Remove deprecated sections
- [ ] Update stability markers
- [ ] Consolidate duplicate content
- [ ] Generate fresh API docs
- [ ] Validate all examples

## MkDocs Material Integration

### Native Features We Use
MkDocs Material provides powerful features that enhance our documentation:

#### 1. Content Organization
- **Content Tabs**: Group related content (providers, languages, environments)
- **Admonitions**: Warnings, info boxes, tips for important information
- **Collapsible Sections**: `<details>` tags for advanced/optional content
- **Code Annotations**: Inline explanations with `(1)!` markers

#### 2. Code Examples
```markdown
=== "Python"
    ```python
    client = OpenAI(base_url="http://localhost:8001/v1")
    response = client.chat.completions.create(
        model="gpt-4o",  # (1)!
        messages=[{"role": "user", "content": "Hello"}]
    )
    ```
    
    1. Uses LiteLLM proxy by default

=== "cURL"
    ```bash
    curl -X POST http://localhost:8001/v1/chat/completions \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"model": "gpt-4o", "messages": [...]}'
    ```
```

#### 3. Navigation & Search
- Instant loading with `navigation.instant`
- Search suggestions and highlighting
- Sticky navigation tabs
- Table of contents integration

### Documentation Generators

Instead of print-heavy scripts, use template-based generators:

#### 1. Jinja2 Templates
```python
from jinja2 import Template

TEMPLATE = Template("""
## {{ title }}

{% for section in sections %}
### {{ section.name }}
{{ section.content }}
{% endfor %}
""")
```

#### 2. YAML/JSON Schemas
Define documentation structure in data files:
```yaml
# docs/schema/config.yaml
configuration:
  milvus:
    vars:
      - name: MILVUS_HOST
        default: milvus
        description: Milvus server hostname
```

#### 3. mkdocstrings Plugin
Auto-generate API docs from docstrings:
```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: google
```

Then reference in markdown:
```markdown
::: src.obelisk.rag.service.coordinator.RAGService
```

### Best Practices

1. **Prefer Templates Over Print Strings**
   - Use Jinja2 for complex output
   - Store templates as separate files
   - Pass data dictionaries to templates

2. **Leverage MkDocs Plugins**
   - mkdocstrings for API docs
   - git-revision-date for freshness
   - awesome-pages for auto-navigation

3. **Minimize Manual HTML**
   - Use Material's built-in components
   - Prefer markdown extensions
   - CSS customization only when necessary

## Contributing

### Adding New Documentation
1. Check this standard first
2. Use appropriate template
3. Add to documentation index
4. Include in TASK.docs.md if needed

### Updating Existing Documentation
1. Maintain version history in git
2. Update stability markers
3. Validate examples still work
4. Update cross-references

### Deprecating Documentation
1. Mark as deprecated with date
2. Point to replacement (if any)
3. Remove after one sprint
4. Update all references

---

> **Note**: This document is the source of truth for documentation standards. All documentation should follow these patterns for consistency and maintainability.
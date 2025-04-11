# Editor Configuration

Obelisk includes configuration files for consistent code formatting and editor behavior across development environments.

## .editorconfig

The `.editorconfig` file defines coding style preferences that many editors and IDEs support:

```
# View .editorconfig contents
cat /workspaces/obelisk/.editorconfig
```

Key settings include:
- **indent_style**: Spaces vs tabs
- **indent_size**: Number of spaces per indentation level
- **end_of_line**: Line ending style (LF, CRLF)
- **charset**: Character encoding
- **trim_trailing_whitespace**: Remove trailing spaces
- **insert_final_newline**: Ensure files end with a newline

Different rules can be specified for different file types:

```ini
# Python files
[*.py]
indent_style = space
indent_size = 4

# YAML files
[*.{yml,yaml}]
indent_style = space
indent_size = 2
```

## VS Code Integration

The `.devcontainer/devcontainer.json` file includes VS Code-specific settings:

```json
"settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "terminal.integrated.defaultProfile.linux": "bash"
}
```

These settings configure:
- Python interpreter path
- Linting tools and settings
- Code formatting (Black)
- Format on save behavior
- Visual rulers for line length
- Terminal configuration

## Recommended Extensions

The development container configuration includes recommended VS Code extensions:

```json
"extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "batisteo.vscode-django",
    "yzhang.markdown-all-in-one"
]
```

Popular extensions for Obelisk development include:
- **Python**: Python language support
- **Pylance**: Python language server
- **Django**: Django framework support
- **Markdown All in One**: Markdown editing features

## Code Style Enforcement

Obelisk uses several tools to enforce code style:

1. **Black**: Code formatter with minimal configuration
2. **Ruff**: Fast Python linter
3. **mypy**: Optional static type checking

Configuration for these tools is in `pyproject.toml`:

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
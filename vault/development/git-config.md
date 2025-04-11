# Git Configuration

Obelisk uses Git for version control with several additional configuration files for managing repository behavior.

## .gitignore

The `.gitignore` file specifies which files and directories should be excluded from Git:

```
# View .gitignore contents
cat /workspaces/obelisk/.gitignore
```

Key exclusions include:
- Built documentation (`/site/`)
- Python cache files (`__pycache__/`, `*.py[cod]`)
- Virtual environments (`.venv/`, `venv/`)
- Environment files (`.env`)
- System and editor files (`.DS_Store`, `.idea/`)

## .gitattributes

The `.gitattributes` file defines attributes for paths in the repository:

```
# View .gitattributes contents
cat /workspaces/obelisk/.gitattributes
```

This file controls:
- Line ending normalization
- Diff behavior for specific file types
- Merge strategies
- Export settings

## GitHub Configuration

### .github/dependabot.yml

Dependabot configuration for automated dependency updates:

```yaml
# View dependabot.yml contents
cat /workspaces/obelisk/.github/dependabot.yml
```

This configuration specifies:
- Package ecosystems to monitor (e.g., pip, docker)
- Update frequency
- Target branches
- Reviewers and assignees
- Version update strategy

## Git Workflow

### Branching Strategy

The project follows a feature branch workflow:

1. The `main` branch contains stable releases
2. Feature branches are created for new features or fixes
3. Pull requests are used to merge changes back to main
4. The `v4` branch is used for publishing docs with versioning

### Commit Conventions

Commit messages follow the conventional commits format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types include:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Version Tags

Git tags are used to mark version releases:

```bash
# Create a version tag
git tag -a v0.1.0 -m "Initial release"

# Push tags to remote
git push --tags
```
# Task Runner

Obelisk uses [Task](https://taskfile.dev/) (via Taskfile.yaml) as a task runner for development and deployment workflows.

## Taskfile.yaml

The `Taskfile.yaml` file defines all project tasks and their dependencies:

```yaml
# View the Taskfile.yaml contents
cat /workspaces/obelisk/Taskfile.yaml
```

## Available Tasks

### Development Tasks

```bash
# Install dependencies (Poetry)
task install

# Build static site
task build

# Run strict build testing
task test

# Fast development server with livereload
task run

# Build and serve with browser opening
task serve

# Remove build artifacts
task clean
```

### Versioning Tasks

```bash
# Deploy version (requires version number and description)
task version-deploy -- X.Y.Z "Description"

# Set default version (requires version number)
task version-set-default -- X.Y.Z
```

### Docker Tasks

```bash
# Build Docker container
task docker-build

# Run with local volumes mounted
task docker-run

# Run Obelisk service only
task compose-obelisk

# Run full stack with Ollama and OpenWebUI
task compose
```

## Task Implementation Details

Each task in the Taskfile defines:

- **desc**: Description of what the task does
- **deps**: Tasks that must run before this one
- **cmds**: Commands to execute
- **vars**: Variables used by the task
- **sources/generates**: Files to watch for incremental builds

## Task Variables

The Taskfile also defines variables for configuration:

```yaml
vars:
  # Project settings
  PACKAGE: obelisk
  PYTHON_VERSION: "3.12"
  
  # Docker settings
  DOCKER_IMAGE: {{.PACKAGE}}
  DOCKER_TAG: latest
  DOCKER_RUN_PORT: 8000
```

## Example Usage

```bash
# Install dependencies
task install

# Start development server
task run

# Deploy a new version
task version-deploy -- 0.1.0 "Initial release"
```
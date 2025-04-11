# Docker Configuration

Obelisk uses Docker for containerization of both the development environment and the production deployment.

## Dockerfile

The main `Dockerfile` defines the container image for running Obelisk:

```dockerfile
# View the Dockerfile contents
cat /workspaces/obelisk/Dockerfile
```

This file defines:
- Base image selection
- System dependencies installation
- Python environment setup
- Obelisk installation
- Default command execution

## Docker Compose Configuration

The `docker-compose.yaml` file orchestrates the complete Obelisk stack, including optional AI components:

```yaml
# View the docker-compose.yaml contents
cat /workspaces/obelisk/docker-compose.yaml
```

Key services include:
- **obelisk**: The main Obelisk documentation server
- **ollama**: (Optional) AI model server for local embedding and inference
- **openwebui**: (Optional) Web interface for interacting with AI models

## Development Container

The `.devcontainer` directory contains configuration for VS Code's Development Containers feature:

### devcontainer.json

```json
# View the devcontainer.json contents
cat /workspaces/obelisk/.devcontainer/devcontainer.json
```

This file configures:
- Development container settings
- VS Code extensions to install
- Port forwarding
- Environment variables
- Startup commands

### Dockerfile (Dev)

```dockerfile
# View the development container Dockerfile
cat /workspaces/obelisk/.devcontainer/Dockerfile
```

The development container Dockerfile includes:
- Development-specific tools and dependencies
- Debugging utilities
- Additional build tools

## Running with Docker

To run Obelisk using Docker:

1. **Build the image**:
   ```bash
   docker build -t obelisk .
   ```

2. **Run with Docker**:
   ```bash
   docker run -p 8000:8000 obelisk
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up obelisk
   ```

4. **Run the full stack with AI**:
   ```bash
   docker-compose up
   ```

## Task Runner Integration

Docker commands are also available through the Task runner:

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
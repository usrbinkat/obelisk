FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create directories for mounting volumes
RUN mkdir -p /app/init-scripts /app/tokens /app/config

# Copy initialization scripts directly
COPY ./deployments/docker/images/init/scripts/* /app/init-scripts/

# Set proper permissions
RUN chmod +x /app/init-scripts/*.sh

# Default command runs the initialization sequence
ENTRYPOINT ["/bin/bash"]
CMD ["/app/init-scripts/init-sequence.sh"]
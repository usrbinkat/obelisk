FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtualenv
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files (including vault directory and mkdocs.yml)
COPY . .

# Environment variables to silence git plugin errors
ENV GIT_PYTHON_REFRESH=quiet
ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

# Expose MkDocs default port
EXPOSE 8000

# Run MkDocs
CMD ["poetry", "run", "mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
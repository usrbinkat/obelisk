FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtualenv
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project
COPY . .

# Expose MkDocs default port
EXPOSE 8000

# Run MkDocs
CMD ["poetry", "run", "mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
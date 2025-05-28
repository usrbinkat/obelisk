# Documentation Update Runbook

> **Purpose**: Step-by-step commands and procedures for updating Obelisk documentation
> **Last Updated**: January 2025

## Pre-Update Verification

### 1. Verify Current State
```bash
# Check for outdated references
echo "=== Documentation Audit ==="
echo -n "ChromaDB references: "
grep -r "ChromaDB\|chroma" vault/ --include="*.md" | grep -v "TASK\|historical" | wc -l

echo -n "Milvus references: "
grep -r "Milvus\|milvus" vault/ --include="*.md" | wc -l

echo -n "Outdated embedding refs: "
grep -r "mxbai-embed-large\|1024.*dim" vault/ --include="*.md" | wc -l

echo -n "Outdated API endpoints: "
grep -r "/v1/litellm\|/api/generate" vault/ --include="*.md" | wc -l
```

### 2. Implementation Verification
```bash
# Verify source code state
echo "=== Code Verification ==="

# Check Milvus implementation
echo -n "ChromaDB in code: "
grep -r "ChromaDB\|Chroma" src/ --include="*.py" | wc -l

echo -n "Milvus in code: "
grep -r "Milvus\|pymilvus" src/ --include="*.py" | wc -l

# Verify key files exist
test -f src/obelisk/rag/common/providers.py && echo "✅ Provider factory exists" || echo "❌ Provider factory missing"
test -f src/obelisk/rag/storage/store.py && echo "✅ Vector storage exists" || echo "❌ Vector storage missing"
```

## Documentation Generation

### 1. Generate Configuration Documentation
```bash
# Run configuration generator
poetry run python scripts/gen-config-docs.py > vault/chatbot/rag/configuration-reference.md

# Verify output
head -20 vault/chatbot/rag/configuration-reference.md
```

### 2. Generate API Documentation
```bash
# Using mkdocstrings (add to vault file)
cat > vault/chatbot/rag/api-reference.md << 'EOF'
# API Reference

## RAG Service

::: src.obelisk.rag.service.coordinator.RAGService
    options:
      show_source: true
      heading_level: 3

## Vector Storage

::: src.obelisk.rag.storage.store.VectorStorage
    options:
      show_source: true
      heading_level: 3

## Model Providers

### LiteLLM Provider
::: src.obelisk.rag.common.providers.LiteLLMProvider

### Ollama Provider  
::: src.obelisk.rag.common.providers.OllamaProvider
EOF
```

### 3. Generate Service Dependency Diagram
```bash
# Generate Mermaid diagram
poetry run python scripts/compose-to-mermaid.py > vault/deployment/service-architecture.md

# Or manually verify services
docker-compose -f deployments/docker/compose/dev.yaml config --services | sort
```

## File Update Procedures

### Critical Files (Priority 10)

#### Update getting-started.md
```bash
# Backup original
cp vault/chatbot/rag/getting-started.md vault/chatbot/rag/getting-started.md.bak

# Find and replace
sed -i 's/mxbai-embed-large/text-embedding-3-large/g' vault/chatbot/rag/getting-started.md
sed -i 's/1024/3072/g' vault/chatbot/rag/getting-started.md
sed -i 's/ChromaDB/Milvus/g' vault/chatbot/rag/getting-started.md

# Verify changes
diff vault/chatbot/rag/getting-started.md.bak vault/chatbot/rag/getting-started.md
```

#### Update implementation.md
```bash
# This requires manual rewrite - use the template
cat > vault/chatbot/rag/implementation.md << 'EOF'
# RAG Implementation

## Vector Storage

We use Milvus for vector storage with the following configuration:

```python
from src.obelisk.rag.storage.store import VectorStorage

# Initialize with 3072-dimensional embeddings
storage = VectorStorage(config)
```

## Provider Architecture

```python
from src.obelisk.rag.common.providers import ProviderFactory, ProviderType

# Default: LiteLLM
provider = ProviderFactory.create(ProviderType.LITELLM, config)

# Hardware tuning: Ollama
provider = ProviderFactory.create(ProviderType.OLLAMA, config)
```
EOF
```

### High Priority Files (Priority 8-9)

#### Update vector-database.md
```bash
# Complete replacement needed
cat > vault/chatbot/rag/vector-database.md << 'EOF'
# Vector Database: Milvus

> **Version**: Milvus 2.5.10
> **Stability**: 🟢 Production-ready

## Overview
Milvus is our production vector database, providing high-performance similarity search for RAG.

## Configuration
```bash
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION=obelisk_rag
```

## Features
- 3072-dimensional embeddings (text-embedding-3-large)
- HNSW indexing for fast search
- Distributed architecture
- JSON metadata support
EOF
```

## Environment Variable Updates

### Update All .env References
```bash
# Find all .env example files
find . -name "*.env*" -o -name ".env" | while read file; do
    echo "Updating $file"
    
    # Remove ChromaDB vars
    sed -i '/CHROMA_/d' "$file"
    
    # Add Milvus vars if not present
    grep -q "MILVUS_HOST" "$file" || cat >> "$file" << 'EOF'

# Milvus Configuration
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION=obelisk_rag
EOF
done
```

### Docker Compose Environment
```bash
# Verify environment in docker-compose
docker-compose -f deployments/docker/compose/dev.yaml config | grep -A5 "environment:"
```

## Testing Updated Documentation

### 1. Build Documentation Site
```bash
# Test build with strict mode
poetry run mkdocs build --strict

# Check for warnings
poetry run mkdocs build 2>&1 | grep -i "warning"
```

### 2. Test Code Examples
```bash
# Extract and test Python examples
grep -A10 "```python" vault/chatbot/rag/*.md | grep -v "```" > /tmp/code_examples.py

# Syntax check
poetry run python -m py_compile /tmp/code_examples.py
```

### 3. Test Commands
```bash
# Extract bash commands
grep -A5 "```bash" vault/chatbot/rag/*.md | grep -v "```" | grep -E "^(curl|docker|task)" > /tmp/commands.sh

# Test each command (dry run)
while read cmd; do
    echo "Would run: $cmd"
done < /tmp/commands.sh
```

## Progress Tracking

### Track Updates
```bash
# Mark completed in TASK.docs.md
update_task() {
    local file="$1"
    sed -i "s|- \[ \] \`$file\`|- [x] \`$file\`|" TASK.docs.md
    echo "✅ Marked $file as complete"
}

# Usage
update_task "/chatbot/rag/getting-started.md"
```

### Generate Progress Report
```bash
# Simple progress counter
total=$(grep -c "^- \[ \]" TASK.docs.md)
completed=$(grep -c "^- \[x\]" TASK.docs.md)
percent=$((completed * 100 / total))

echo "Documentation Update Progress"
echo "============================"
echo "Completed: $completed / $total ($percent%)"
echo ""
echo "Remaining files:"
grep "^- \[ \]" TASK.docs.md | head -10
```

## Final Validation

### 1. No ChromaDB References
```bash
# Final check - should return 0
grep -r "ChromaDB\|chroma" vault/ --include="*.md" | grep -v "TASK\|migration\|historical" | wc -l
```

### 2. Correct Configuration
```bash
# Verify all config examples use new variables
grep -r "MILVUS_\|LITELLM_" vault/ --include="*.md" | wc -l
```

### 3. API Endpoint Consistency  
```bash
# Should only find /v1/chat/completions
grep -r "POST.*\/v1\/" vault/ --include="*.md" | grep -v "chat/completions" | wc -l
```

### 4. Link Validation
```bash
# Check internal links
poetry run linkchecker vault/
```

## Rollback Procedure

```bash
# If issues found, restore from backup
for file in vault/**/*.md.bak; do
    original="${file%.bak}"
    echo "Restoring $original"
    mv "$file" "$original"
done
```

## Quick Reference Commands

```bash
# Most used commands during doc updates
alias check-chroma='grep -r "ChromaDB" vault/ --include="*.md" | wc -l'
alias check-milvus='grep -r "Milvus" vault/ --include="*.md" | wc -l'
alias doc-build='poetry run mkdocs build --strict'
alias doc-serve='poetry run mkdocs serve'
alias update-progress='grep -c "^- \[x\]" TASK.docs.md'
```
#!/bin/bash

echo "Checking latest versions of container images..."
echo "----------------------------------------------"

# PostgreSQL
pg_version=$(docker run --rm postgres:latest postgres --version | grep -o '[0-9]\+\.[0-9]\+\(.[0-9]\+\)\?' | head -1)
echo "PostgreSQL: $pg_version (postgres:$pg_version)"

# Minio
minio_version=$(curl -s "https://api.github.com/repos/minio/minio/releases/latest" | jq -r '.tag_name')
echo "MinIO: $minio_version (minio/minio:$minio_version)"

# Ollama
ollama_version=$(curl -s "https://api.github.com/repos/ollama/ollama/releases/latest" | jq -r '.tag_name')
echo "Ollama: $ollama_version (ollama/ollama:${ollama_version#v})"

# Milvus
milvus_version=$(curl -s "https://api.github.com/repos/milvus-io/milvus/releases" | jq -r '[.[] | select(.tag_name | test("^v[0-9]+\\.[0-9]+\\.[0-9]+$"))] | first | .tag_name')
echo "Milvus: $milvus_version (milvusdb/milvus:$milvus_version)"

# Apache Tika
tika_version=$(curl -s "https://registry.hub.docker.com/v2/repositories/apache/tika/tags?page_size=100" | grep -o '"name":"[^"]*' | grep -o "[0-9].*full" | sort -V | tail -1)
echo "Apache Tika: ${tika_version%-full} (apache/tika:$tika_version)"

# LiteLLM - GitHub Container Registry uses main-latest tag 
# We track the latest stable git tag for reference but use main-latest for the container
litellm_git_version=$(curl -s "https://api.github.com/repos/BerriAI/litellm/tags" | jq -r '[.[] | select(.name | contains("stable"))] | first | .name')
echo "LiteLLM: $litellm_git_version (ghcr.io/berriai/litellm:main-latest)"

# etcd
etcd_version=$(curl -s "https://api.github.com/repos/etcd-io/etcd/releases/latest" | jq -r '.tag_name')
echo "etcd: $etcd_version (quay.io/coreos/etcd:$etcd_version)"

# Open WebUI
openwebui_version=$(curl -s "https://api.github.com/repos/open-webui/open-webui/tags" | jq -r 'first | .name')
echo "Open WebUI: $openwebui_version (ghcr.io/open-webui/open-webui:${openwebui_version#v})"

echo "----------------------------------------------"
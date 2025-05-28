# Obelisk Deployment Architecture: Comprehensive Platform Guide

> **Status**: Reference Documentation (Finalized May 2025)  
> **Purpose**: Comprehensive deployment guide for Docker, Kubernetes, and Mac environments  
> **Originally**: TASK.deployment-architecture.md

## Executive Summary

This document provides comprehensive deployment architectures for the Obelisk RAG system across multiple platforms and operational paradigms. Based on extensive research of modern deployment patterns in 2025, this guide covers local development, Docker Compose orchestration, Kubernetes production deployments, and platform-specific optimizations for CPU, NVIDIA GPU, AMD GPU, and Apple Silicon environments.

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Docker Deployment Patterns](#docker-deployment-patterns)
3. [Kubernetes Production Architecture](#kubernetes-production-architecture)
4. [Apple Silicon Deployment](#apple-silicon-deployment)
5. [GPU Acceleration Strategies](#gpu-acceleration-strategies)
6. [Operational Best Practices](#operational-best-practices)
7. [Performance Tuning Guide](#performance-tuning-guide)
8. [Migration and Scaling Strategies](#migration-and-scaling-strategies)

## Platform Overview

### Deployment Paradigms

Obelisk supports three primary deployment paradigms, each optimized for different use cases:

1. **Local Development**: Native installation with direct hardware access
2. **Docker Compose**: Containerized multi-service orchestration
3. **Kubernetes**: Cloud-native production deployment with auto-scaling

### Hardware Support Matrix

| Platform | CPU | NVIDIA GPU | AMD GPU | Apple Silicon | Notes |
|----------|-----|------------|---------|---------------|--------|
| Local | ✓ | ✓ | ✓* | ✓ | *AMD requires ROCm 5.6+ |
| Docker | ✓ | ✓ | ✓* | CPU only | Mac Docker lacks GPU support |
| Kubernetes | ✓ | ✓ | ✓ | N/A | Device plugins required |

## Docker Deployment Patterns

### 1. CPU-Only Configuration

Our base CPU configuration optimized for development and testing:

```yaml
# deployments/docker/compose/dev.yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    environment:
      # Core Configuration
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=24h        # Keep models loaded in dev
      - OLLAMA_MODELS=/root/.ollama/models
      - OLLAMA_LOAD_TIMEOUT=10m      # Extended timeout for large models
      
      # Performance Tuning
      - OLLAMA_NUM_PARALLEL=4        # Concurrent request handling
      - OLLAMA_MAX_LOADED_MODELS=2   # Models in memory simultaneously
      - OLLAMA_MAX_QUEUE=512         # Request queue depth
      
      # CPU Optimization
      - OLLAMA_FLASH_ATTENTION=false # Disable GPU-only features
      - OLLAMA_NUM_THREAD=0          # Auto-detect CPU threads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
        reservations:
          cpus: '2'
          memory: 8G

  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - DATABASE_URL=postgresql://postgres:postgres@litellm_db:5432/postgres
      - STORE_MODEL_IN_DB=true
      - LITELLM_MODE=PRODUCTION
      - LITELLM_TELEMETRY=false
      
      # Model Registration
      - MODEL_NAME_1=llama3
      - MODEL_1=ollama/llama3
      - MODEL_API_BASE_1=http://ollama:11434
      
      # Request Configuration
      - LITELLM_REQUEST_TIMEOUT=600
      - LITELLM_DROP_PARAMS=true
      - LITELLM_SUPPRESS_DEBUG_INFO=true
    depends_on:
      litellm_db:
        condition: service_healthy
      ollama:
        condition: service_healthy

  litellm_db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=postgres
    volumes:
      - litellm_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Milvus vector database stack
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes:
      - etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 -data-dir /etcd
    healthcheck:
      test: ["CMD", "etcdctl", "endpoint", "health"]
      interval: 30s
      timeout: 20s
      retries: 3

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio:/minio_data
    command: minio server /minio_data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  milvus:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.4.0
    command: ["milvus", "run", "standalone"]
    security_opt:
      - seccomp:unconfined
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - milvus:/var/lib/milvus
    ports:
      - "19530:19530"  # Milvus gRPC port
      - "9091:9091"    # Milvus metrics port
    depends_on:
      etcd:
        condition: service_healthy
      minio:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      timeout: 20s
      retries: 3

  obelisk-rag:
    build:
      context: ../../..
      dockerfile: deployments/docker/images/rag/Dockerfile
    ports:
      - "8001:8001"
    environment:
      # Provider Configuration - All completions through LiteLLM API
      - LITELLM_API_URL=http://litellm:4000
      - LITELLM_API_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - MODEL_PROVIDER=litellm  # Default to LiteLLM for all completions
      
      # Milvus Configuration
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - COLLECTION_NAME=${COLLECTION_NAME:-obelisk_docs}
      - EMBEDDING_DIM=3072  # For text-embedding-3-large
      
      # Performance Settings
      - RETRIEVE_TOP_K=10
      - CHUNK_SIZE=1000
      - CHUNK_OVERLAP=200
      
      # Monitoring
      - OBELISK_LOG_LEVEL=INFO
      - ENABLE_METRICS=true
    volumes:
      - ${VAULT_DIR:-./vault}:/app/vault:ro
    depends_on:
      - litellm
      - milvus

volumes:
  ollama:
  litellm_db_data:
  etcd:
  minio:
  milvus:
```

### 2. NVIDIA GPU Configuration

Production-ready GPU configuration with proper resource allocation:

```yaml
# deployments/docker/compose/nvidia.yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    runtime: nvidia
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    environment:
      # GPU Configuration
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - CUDA_VISIBLE_DEVICES=0,1     # Use first two GPUs
      
      # Ollama GPU Settings
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=-1         # Infinite retention for production
      - OLLAMA_GPU_OVERHEAD=1073741824  # Reserve 1GB VRAM per GPU
      - OLLAMA_FLASH_ATTENTION=true  # Enable Flash Attention 2
      - OLLAMA_KV_CACHE_TYPE=q8_0    # Quantized KV cache for larger contexts
      - OLLAMA_SCHED_SPREAD=true     # Distribute across GPUs
      
      # Performance Optimization
      - OLLAMA_NUM_PARALLEL=8        # Higher parallelism with GPU
      - OLLAMA_MAX_LOADED_MODELS=4   # More models with GPU memory
      - OLLAMA_CONTEXT_LENGTH=8192   # Extended context with GPU
      
      # Multi-user Production
      - OLLAMA_MULTIUSER_CACHE=true  # Optimize for concurrent users
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
        limits:
          memory: 32G
    healthcheck:
      test: ["CMD", "nvidia-smi"]
      interval: 30s
      timeout: 10s
      retries: 3

  # NVIDIA GPU Exporter for monitoring
  nvidia-gpu-exporter:
    image: nvidia/dcgm-exporter:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "9400:9400"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Rest of services remain similar to CPU config
```

### 3. AMD GPU Configuration

Experimental AMD GPU support with ROCm:

```yaml
# deployments/docker/compose/amd-gpu.yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:rocm
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
      - /dev/kfd:/dev/kfd  # AMD KFD device
      - /dev/dri:/dev/dri  # Direct Rendering Infrastructure
    environment:
      # AMD GPU Configuration
      - HIP_VISIBLE_DEVICES=0
      - ROCR_VISIBLE_DEVICES=0
      - HSA_OVERRIDE_GFX_VERSION=11.0.0  # For MI300 series
      - GPU_DEVICE_ORDINAL=0
      
      # Ollama Settings
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=5m
      - OLLAMA_GPU_OVERHEAD=2147483648  # Reserve 2GB for AMD
      
      # ROCm Optimization
      - HSA_FORCE_FINE_GRAIN_PCIE=1
      - ROCM_PATH=/opt/rocm
    group_add:
      - video  # Required for AMD GPU access
      - render
    devices:
      - /dev/kfd
      - /dev/dri
    cap_add:
      - SYS_PTRACE
      - SYS_ADMIN
    security_opt:
      - seccomp:unconfined
```

### 4. Production High-Availability Stack

Multi-node production deployment with redundancy:

```yaml
# deployments/docker/compose/production.yaml
version: '3.8'

services:
  # HAProxy Load Balancer
  haproxy:
    image: haproxy:2.8-alpine
    ports:
      - "80:80"
      - "443:443"
      - "8404:8404"  # Stats page
    volumes:
      - ./config/haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
      - ./certs:/etc/ssl/certs:ro
    depends_on:
      - obelisk-rag-1
      - obelisk-rag-2
      - obelisk-rag-3

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # PostgreSQL with replication
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=obelisk
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=obelisk
      - POSTGRES_INITDB_ARGS=--encoding=UTF8 --data-checksums
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf

  # Multiple Ollama instances for redundancy
  ollama-1:
    extends:
      file: nvidia.yaml
      service: ollama
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - OLLAMA_NODE_ID=1
    volumes:
      - ollama_1:/root/.ollama

  ollama-2:
    extends:
      file: nvidia.yaml
      service: ollama
    environment:
      - CUDA_VISIBLE_DEVICES=1
      - OLLAMA_NODE_ID=2
    volumes:
      - ollama_2:/root/.ollama

  # LiteLLM with Redis-based routing
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MODE=PRODUCTION
      - DATABASE_URL=postgresql://obelisk:${DB_PASSWORD}@postgres:5432/obelisk
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - LITELLM_ROUTING_STRATEGY=usage-based-routing-v2
      - LITELLM_REDIS_CACHE=true
      - LITELLM_CACHE_TTL=3600
    volumes:
      - ./config/litellm/config.yaml:/app/config.yaml
    depends_on:
      - postgres
      - redis
      - ollama-1
      - ollama-2

  # Multiple RAG instances
  obelisk-rag-1:
    extends:
      file: dev.yaml
      service: obelisk-rag
    environment:
      - INSTANCE_ID=rag-1
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - litellm

  obelisk-rag-2:
    extends:
      file: dev.yaml
      service: obelisk-rag
    environment:
      - INSTANCE_ID=rag-2
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - litellm

  obelisk-rag-3:
    extends:
      file: dev.yaml
      service: obelisk-rag
    environment:
      - INSTANCE_ID=rag-3
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - litellm

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  ollama_1:
  ollama_2:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

## Kubernetes Production Architecture

### 1. Helm Chart Structure

Production-ready Helm chart for Obelisk deployment:

```yaml
# helm/obelisk/values.yaml
global:
  imageRegistry: ""
  imagePullSecrets: []
  storageClass: "fast-ssd"

ollama:
  enabled: true
  replicaCount: 3
  image:
    repository: ollama/ollama
    tag: latest
    pullPolicy: IfNotPresent
  
  gpu:
    enabled: true
    type: nvidia  # nvidia, amd, or intel
    count: 1
    
  persistence:
    enabled: true
    size: 500Gi
    storageClass: local-nvme
    
  resources:
    requests:
      cpu: 4
      memory: 16Gi
      nvidia.com/gpu: 1
    limits:
      cpu: 8
      memory: 32Gi
      nvidia.com/gpu: 1
      
  config:
    keepAlive: "-1"
    numParallel: 8
    maxLoadedModels: 4
    flashAttention: true
    multiUserCache: true
    contextLength: 8192
    
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - ollama
        topologyKey: kubernetes.io/hostname

litellm:
  enabled: true
  replicaCount: 3
  image:
    repository: ghcr.io/berriai/litellm
    tag: main-latest
    
  config:
    mode: PRODUCTION
    routingStrategy: "usage-based-routing-v2"
    redis:
      enabled: true
      host: "redis-master"
    database:
      enabled: true
      host: "postgresql"
      
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80

rag:
  enabled: true
  replicaCount: 5
  image:
    repository: obelisk/rag
    tag: latest
    
  persistence:
    # Milvus is deployed separately, no local persistence needed
    enabled: false
    
  config:
    milvus:
      host: "milvus"
      port: 19530
      collectionName: "obelisk_docs"
      embeddingDim: 3072  # text-embedding-3-large
      
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Pods
      pods:
        metric:
          name: rag_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
  hosts:
    - host: api.obelisk.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: obelisk-tls
      hosts:
        - api.obelisk.example.com

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
    dashboards:
      - ollama-metrics
      - litellm-performance
      - rag-operations
```

### 2. StatefulSet for Model Persistence

```yaml
# helm/obelisk/templates/ollama-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ include "obelisk.fullname" . }}-ollama
spec:
  serviceName: {{ include "obelisk.fullname" . }}-ollama
  replicas: {{ .Values.ollama.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: ollama
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ollama
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
      - name: ollama
        image: "{{ .Values.ollama.image.repository }}:{{ .Values.ollama.image.tag }}"
        imagePullPolicy: {{ .Values.ollama.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 11434
          protocol: TCP
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        - name: OLLAMA_KEEP_ALIVE
          value: "{{ .Values.ollama.config.keepAlive }}"
        - name: OLLAMA_NUM_PARALLEL
          value: "{{ .Values.ollama.config.numParallel }}"
        - name: OLLAMA_MAX_LOADED_MODELS
          value: "{{ .Values.ollama.config.maxLoadedModels }}"
        - name: OLLAMA_FLASH_ATTENTION
          value: "{{ .Values.ollama.config.flashAttention }}"
        - name: OLLAMA_MULTIUSER_CACHE
          value: "{{ .Values.ollama.config.multiUserCache }}"
        - name: OLLAMA_CONTEXT_LENGTH
          value: "{{ .Values.ollama.config.contextLength }}"
        {{- if .Values.ollama.gpu.enabled }}
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        {{- end }}
        volumeMounts:
        - name: models
          mountPath: /root/.ollama
        - name: cache
          mountPath: /tmp/ollama-cache
        resources:
          {{- toYaml .Values.ollama.resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: /api/tags
            port: http
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/tags
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
      {{- with .Values.ollama.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      volumes:
      - name: cache
        emptyDir:
          medium: Memory
          sizeLimit: 8Gi
  volumeClaimTemplates:
  - metadata:
      name: models
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: {{ .Values.ollama.persistence.storageClass }}
      resources:
        requests:
          storage: {{ .Values.ollama.persistence.size }}
```

### 3. KEDA Autoscaling Configuration

```yaml
# helm/obelisk/templates/keda-scaledobject.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: {{ include "obelisk.fullname" . }}-rag-scaler
spec:
  scaleTargetRef:
    name: {{ include "obelisk.fullname" . }}-rag
  pollingInterval: 30
  cooldownPeriod: 300
  minReplicaCount: {{ .Values.rag.autoscaling.minReplicas }}
  maxReplicaCount: {{ .Values.rag.autoscaling.maxReplicas }}
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server:9090
      metricName: ollama_requests_pending
      threshold: "50"
      query: |
        sum(rate(ollama_request_duration_seconds_count[1m]))
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server:9090
      metricName: rag_queue_depth
      threshold: "100"
      query: |
        avg(rag_pending_requests{job="obelisk-rag"})
  - type: cpu
    metadata:
      type: Utilization
      value: "70"
  - type: memory
    metadata:
      type: Utilization
      value: "80"
```

### 4. GPU Node Configuration with Karpenter

```yaml
# helm/obelisk/templates/karpenter-provisioner.yaml
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: gpu-nodes
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
    - key: kubernetes.io/arch
      operator: In
      values: ["amd64"]
    - key: node.kubernetes.io/instance-type
      operator: In
      values:
        - g4dn.xlarge
        - g4dn.2xlarge
        - g4dn.4xlarge
        - g5.xlarge
        - g5.2xlarge
    - key: nvidia.com/gpu
      operator: Exists
  limits:
    resources:
      cpu: 1000
      memory: 1000Gi
      nvidia.com/gpu: 10
  provider:
    subnetSelector:
      karpenter.sh/discovery: obelisk-cluster
    securityGroupSelector:
      karpenter.sh/discovery: obelisk-cluster
    userData: |
      #!/bin/bash
      /etc/eks/bootstrap.sh obelisk-cluster
      
      # Install NVIDIA drivers
      curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
      curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
      sudo apt-get update
      sudo apt-get install -y nvidia-container-toolkit
      sudo nvidia-ctk runtime configure --runtime=docker
      sudo systemctl restart docker
      
      # Label node with GPU info
      kubectl label node $(hostname) accelerator=nvidia-gpu
  ttlSecondsAfterEmpty: 300
```

## Apple Silicon Deployment

### 1. Native Development Configuration

Optimal configuration for M1/M2/M3 Macs:

```bash
# install.sh for Mac native development
#!/bin/bash

# Install Ollama native (for Metal GPU acceleration)
curl -fsSL https://ollama.com/install.sh | sh

# Configure Ollama for development
cat > ~/.ollama/config.json << EOF
{
  "host": "127.0.0.1:11434",
  "models": "$HOME/.ollama/models",
  "keep_alive": "24h",
  "gpu_layers": -1,
  "num_thread": 0,
  "f16_kv": true,
  "use_mmap": true,
  "context_length": 8192
}
EOF

# Set environment variables
cat >> ~/.zshrc << 'EOF'
# Ollama Configuration
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MODELS="$HOME/.ollama/models"
export OLLAMA_KEEP_ALIVE="24h"
export OLLAMA_NUM_GPU=-1  # Use all GPU cores

# Metal Performance Shaders
export METAL_DEVICE_WRAPPER=1
export METAL_DEBUG_ERROR_MODE=0
EOF

# Start Ollama service
ollama serve &

# Pull optimized models for Apple Silicon
ollama pull llama3:8b-instruct-q4_K_M  # Optimized for 16GB RAM
ollama pull mistral:7b-instruct-q4_K_M  # Excellent performance on M-series
ollama pull phi3:mini-4k-instruct       # Efficient small model
```

### 2. Hybrid Docker Development

Since Docker on macOS doesn't support Metal GPU acceleration, use a hybrid approach:

```yaml
# docker-compose.mac.yaml
version: '3.8'

services:
  # Ollama runs natively on host for GPU access
  # Access via host.docker.internal:11434
  
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - DATABASE_URL=postgresql://postgres:postgres@litellm_db:5432/postgres
      - MODEL_NAME_1=llama3
      - MODEL_1=ollama/llama3
      - MODEL_API_BASE_1=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - litellm_db

  litellm_db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - litellm_db_data:/var/lib/postgresql/data

  # Note: Milvus requires significant resources, consider cloud deployment
  # For local Mac development, can use Milvus Lite or connect to remote instance
  
  obelisk-rag:
    build:
      context: ../../..
      dockerfile: deployments/docker/images/rag/Dockerfile
    ports:
      - "8001:8001"
    environment:
      # All completions through LiteLLM API
      - LITELLM_API_URL=http://litellm:4000
      - LITELLM_API_KEY=${LITELLM_API_TOKEN:-sk-1234}
      - MODEL_PROVIDER=litellm
      
      # For Mac dev, connect to remote Milvus or use Milvus Lite
      - MILVUS_HOST=${MILVUS_HOST:-host.docker.internal}
      - MILVUS_PORT=${MILVUS_PORT:-19530}
      - USE_MILVUS_LITE=${USE_MILVUS_LITE:-true}  # Embedded mode for dev
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ${VAULT_DIR:-./vault}:/app/vault:ro
      - milvus_lite:/app/milvus_lite  # Local storage for Milvus Lite

volumes:
  litellm_db_data:
  milvus_lite:
```

### 3. Memory-Optimized Model Configuration

For different Mac configurations:

```python
# mac_optimization.py
import platform
import subprocess
import psutil

def get_mac_config():
    """Detect Mac hardware and recommend model configuration."""
    # Get system info
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count(logical=False)
    
    # Detect Mac model
    system_info = subprocess.check_output(['system_profiler', 'SPHardwareDataType']).decode()
    
    configs = {
        "8GB": {
            "models": ["phi3:mini", "gemma:2b"],
            "max_models": 1,
            "context_length": 2048,
            "gpu_layers": 20,
            "batch_size": 512
        },
        "16GB": {
            "models": ["llama3:8b-q4_K_M", "mistral:7b-q4_K_M"],
            "max_models": 2,
            "context_length": 4096,
            "gpu_layers": 35,
            "batch_size": 1024
        },
        "32GB": {
            "models": ["llama3:13b-q4_K_M", "mixtral:8x7b-q4_K_M"],
            "max_models": 3,
            "context_length": 8192,
            "gpu_layers": -1,  # All layers on GPU
            "batch_size": 2048
        },
        "64GB+": {
            "models": ["llama3:70b-q4_K_M", "mixtral:8x22b-q4_K_M"],
            "max_models": 4,
            "context_length": 16384,
            "gpu_layers": -1,
            "batch_size": 4096
        }
    }
    
    if memory_gb >= 64:
        return configs["64GB+"]
    elif memory_gb >= 32:
        return configs["32GB"]
    elif memory_gb >= 16:
        return configs["16GB"]
    else:
        return configs["8GB"]

# Generate optimized Ollama configuration
config = get_mac_config()
print(f"Recommended configuration for {psutil.virtual_memory().total / (1024**3):.0f}GB Mac:")
print(f"Models: {', '.join(config['models'])}")
print(f"Max concurrent models: {config['max_models']}")
print(f"Context length: {config['context_length']}")
```

## GPU Acceleration Strategies

### 1. NVIDIA GPU Optimization

```yaml
# nvidia-optimization.yaml
ollama_config:
  nvidia:
    # Multi-GPU Configuration
    environment:
      - CUDA_VISIBLE_DEVICES=0,1,2,3
      - OLLAMA_SCHED_SPREAD=true      # Distribute layers across GPUs
      - OLLAMA_GPU_OVERHEAD=2147483648  # 2GB overhead per GPU
      
    # Tensor Core Optimization
    model_options:
      use_flash_attention_2: true
      torch_dtype: float16
      enable_tensor_cores: true
      
    # Memory Optimization
    memory_settings:
      gpu_memory_fraction: 0.9        # Use 90% of VRAM
      max_split_size_mb: 512
      offload_kqv: false              # Keep KV cache on GPU
      
    # Performance Tuning
    performance:
      num_gpu_layers: -1              # All layers on GPU
      gpu_batch_mult: 2               # Larger batches for A100/H100
      n_batch: 2048                   # Batch size
      n_threads_batch: 32             # Batch processing threads
```

### 2. AMD GPU Configuration

```yaml
# amd-optimization.yaml
ollama_config:
  amd:
    # ROCm Configuration
    environment:
      - HSA_OVERRIDE_GFX_VERSION=11.0.0  # MI300 series
      - HIP_VISIBLE_DEVICES=0,1
      - ROCR_VISIBLE_DEVICES=0,1
      - HSA_FORCE_FINE_GRAIN_PCIE=1
      
    # Memory Settings
    memory:
      - OLLAMA_GPU_OVERHEAD=4294967296   # 4GB overhead for HBM
      - GPU_MAX_HEAP_SIZE=95            # 95% heap utilization
      
    # Optimization Flags
    performance:
      - OLLAMA_FLASH_ATTENTION=false    # Not yet supported on ROCm
      - OLLAMA_KV_CACHE_TYPE=f16        # Full precision for stability
```

### 3. Intel GPU Support

```yaml
# intel-optimization.yaml
ollama_config:
  intel:
    # Intel GPU Configuration
    environment:
      - OLLAMA_LLM_LIBRARY=openvino     # Use OpenVINO backend
      - VPU_VISIBLE_DEVICES=0
      - GPU_DEVICE_ORDINAL=0
      
    # Optimization
    model_options:
      precision: int8                   # INT8 quantization
      enable_gpu_buffers: true
      workgroup_size: 256
```

## Operational Best Practices

### 1. Health Monitoring Stack

```yaml
# monitoring/health-checks.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-check-scripts
data:
  check-ollama.sh: |
    #!/bin/bash
    # Check Ollama health
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags)
    if [ "$response" -eq 200 ]; then
      # Check loaded models
      models=$(curl -s http://localhost:11434/api/tags | jq -r '.models | length')
      if [ "$models" -gt 0 ]; then
        echo "Ollama healthy with $models models"
        exit 0
      else
        echo "Ollama running but no models loaded"
        exit 1
      fi
    else
      echo "Ollama API not responding"
      exit 1
    fi
    
  check-gpu.sh: |
    #!/bin/bash
    # NVIDIA GPU check
    if command -v nvidia-smi &> /dev/null; then
      gpu_count=$(nvidia-smi -L | wc -l)
      gpu_memory=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
      
      if [ "$gpu_memory" -lt 1000 ]; then
        echo "WARNING: Low GPU memory: ${gpu_memory}MB free"
        exit 1
      fi
      echo "GPU healthy: $gpu_count devices, ${gpu_memory}MB free"
      exit 0
    fi
    
    # AMD GPU check
    if command -v rocm-smi &> /dev/null; then
      echo "AMD GPU detected"
      rocm-smi --showmeminfo vram | grep "Vram Free"
      exit 0
    fi
    
    echo "No GPU detected"
    exit 1
```

### 2. Performance Monitoring

```yaml
# monitoring/grafana-dashboard.json
{
  "dashboard": {
    "title": "Obelisk LLM Performance",
    "panels": [
      {
        "title": "Token Generation Rate",
        "targets": [{
          "expr": "rate(ollama_tokens_generated_total[5m])"
        }]
      },
      {
        "title": "GPU Utilization",
        "targets": [{
          "expr": "DCGM_FI_DEV_GPU_UTIL"
        }]
      },
      {
        "title": "Model Load Time",
        "targets": [{
          "expr": "histogram_quantile(0.95, ollama_model_load_duration_seconds)"
        }]
      },
      {
        "title": "Request Latency",
        "targets": [{
          "expr": "histogram_quantile(0.99, ollama_request_duration_seconds)"
        }]
      },
      {
        "title": "Memory Usage",
        "targets": [{
          "expr": "ollama_memory_used_bytes / ollama_memory_total_bytes * 100"
        }]
      }
    ]
  }
}
```

### 3. Backup and Recovery

```bash
#!/bin/bash
# backup-models.sh

# Backup Ollama models
backup_ollama_models() {
  timestamp=$(date +%Y%m%d_%H%M%S)
  backup_dir="/backups/ollama_${timestamp}"
  
  # Create backup directory
  mkdir -p "$backup_dir"
  
  # Backup model files
  echo "Backing up Ollama models..."
  tar -czf "$backup_dir/models.tar.gz" -C ~/.ollama/models .
  
  # Backup model manifests
  ollama list --format json > "$backup_dir/model_manifest.json"
  
  # Backup configuration
  cp ~/.ollama/config.json "$backup_dir/config.json" 2>/dev/null || true
  
  echo "Backup completed: $backup_dir"
}

# Restore Ollama models
restore_ollama_models() {
  backup_path="$1"
  
  if [ ! -d "$backup_path" ]; then
    echo "Backup directory not found: $backup_path"
    exit 1
  fi
  
  # Stop Ollama
  systemctl stop ollama || killall ollama
  
  # Restore models
  echo "Restoring models..."
  tar -xzf "$backup_path/models.tar.gz" -C ~/.ollama/models
  
  # Restore configuration
  if [ -f "$backup_path/config.json" ]; then
    cp "$backup_path/config.json" ~/.ollama/config.json
  fi
  
  # Restart Ollama
  systemctl start ollama || ollama serve &
  
  echo "Restore completed"
}
```

## Performance Tuning Guide

### 1. Model-Specific Optimization

```python
# model_optimization.py
model_configs = {
    "llama3:70b": {
        "gpu_layers": -1,           # All layers on GPU
        "num_batch": 2048,          # Large batch for throughput
        "num_ctx": 4096,            # Standard context
        "num_gqa": 8,               # Grouped-query attention
        "rope_freq_base": 10000,
        "rope_freq_scale": 1.0,
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "mirostat": 2,
        "mirostat_tau": 5.0,
        "mirostat_eta": 0.1
    },
    "mixtral:8x7b": {
        "gpu_layers": 40,           # Partial offloading
        "num_batch": 1024,
        "num_ctx": 32768,           # Extended context
        "num_experts": 8,
        "num_experts_per_token": 2,
        "temperature": 0.8,
        "top_k": 100,
        "sparse_threshold": 0.5
    },
    "phi3:mini": {
        "gpu_layers": -1,
        "num_batch": 512,           # Smaller batch for latency
        "num_ctx": 2048,
        "temperature": 0.7,
        "flash_attention": true,
        "use_mmap": true,
        "use_mlock": false          # Don't lock small models
    }
}

def get_optimal_config(model_name: str, hardware: dict) -> dict:
    """Generate optimal configuration based on model and hardware."""
    base_config = model_configs.get(model_name.split("-")[0], {})
    
    # Adjust for available VRAM
    if hardware["vram_gb"] < 24:
        base_config["gpu_layers"] = min(base_config.get("gpu_layers", 35), 35)
        base_config["num_batch"] = min(base_config.get("num_batch", 512), 512)
    
    # Adjust for CPU cores
    base_config["num_thread"] = hardware.get("cpu_cores", 8)
    
    return base_config
```

### 2. Request Routing Optimization

```yaml
# litellm-routing-config.yaml
model_list:
  - model_name: fast-inference
    litellm_params:
      model: ollama/phi3:mini
      api_base: http://ollama-1:11434
    model_info:
      max_tokens: 2048
      modes: ["completion", "chat"]
      
  - model_name: balanced
    litellm_params:
      model: ollama/llama3:13b
      api_base: http://ollama-2:11434
    model_info:
      max_tokens: 4096
      modes: ["completion", "chat", "embeddings"]
      
  - model_name: quality
    litellm_params:
      model: ollama/llama3:70b
      api_base: http://ollama-3:11434
    model_info:
      max_tokens: 8192
      modes: ["completion", "chat"]

router_settings:
  routing_strategy: "latency-based-routing"
  allowed_fails: 3
  cooldown_time: 60
  retry_policy:
    num_retries: 2
    retry_after: 5
    
  # Model selection rules
  model_selection_rules:
    - condition: "request_tokens < 1000"
      model: "fast-inference"
    - condition: "request_tokens < 4000"
      model: "balanced"
    - condition: "request_tokens >= 4000"
      model: "quality"
```

## Migration and Scaling Strategies

### 1. Zero-Downtime Migration

```bash
#!/bin/bash
# migrate-deployment.sh

# Blue-Green Deployment Strategy
perform_blue_green_migration() {
  echo "Starting blue-green migration..."
  
  # 1. Deploy new version (green)
  kubectl apply -f deployments/green/
  
  # 2. Wait for green deployment to be ready
  kubectl wait --for=condition=ready pod -l version=green --timeout=600s
  
  # 3. Run smoke tests
  ./scripts/smoke-test.sh green
  
  # 4. Switch traffic to green
  kubectl patch service obelisk-rag -p '{"spec":{"selector":{"version":"green"}}}'
  
  # 5. Monitor for issues
  sleep 300
  
  # 6. Check error rates
  error_rate=$(curl -s http://prometheus:9090/api/v1/query?query=rate(http_requests_errors_total[5m]) | jq '.data.result[0].value[1]')
  
  if (( $(echo "$error_rate > 0.01" | bc -l) )); then
    echo "High error rate detected, rolling back..."
    kubectl patch service obelisk-rag -p '{"spec":{"selector":{"version":"blue"}}}'
    exit 1
  fi
  
  # 7. Remove old deployment
  kubectl delete -f deployments/blue/
  
  echo "Migration completed successfully"
}
```

### 2. Horizontal Scaling Strategy

```python
# autoscaling_strategy.py
from kubernetes import client, config
import numpy as np

class IntelligentAutoscaler:
    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        
    def calculate_optimal_replicas(self, metrics):
        """Calculate optimal replica count based on multiple metrics."""
        # Current metrics
        cpu_util = metrics['cpu_utilization']
        gpu_util = metrics['gpu_utilization']
        queue_depth = metrics['queue_depth']
        avg_latency = metrics['avg_latency_ms']
        
        # Target thresholds
        target_cpu = 70
        target_gpu = 80
        target_queue = 50
        target_latency = 1000  # 1 second
        
        # Calculate scaling factors
        cpu_factor = cpu_util / target_cpu
        gpu_factor = gpu_util / target_gpu
        queue_factor = queue_depth / target_queue
        latency_factor = avg_latency / target_latency
        
        # Weighted average (GPU most important for LLM)
        weights = [0.2, 0.4, 0.2, 0.2]
        factors = [cpu_factor, gpu_factor, queue_factor, latency_factor]
        
        scaling_factor = np.average(factors, weights=weights)
        
        # Current replicas
        current = self.get_current_replicas()
        
        # Calculate new replica count
        if scaling_factor > 1.2:
            # Scale up by 20-50%
            new_replicas = int(current * (1 + min(scaling_factor - 1, 0.5)))
        elif scaling_factor < 0.8:
            # Scale down by 10-30%
            new_replicas = int(current * (1 - min(1 - scaling_factor, 0.3)))
        else:
            new_replicas = current
            
        # Apply bounds
        new_replicas = max(3, min(new_replicas, 50))
        
        return new_replicas
    
    def apply_scaling(self, new_replicas):
        """Apply the calculated scaling."""
        deployment = self.apps_v1.read_namespaced_deployment(
            name="obelisk-rag",
            namespace="default"
        )
        
        if deployment.spec.replicas != new_replicas:
            deployment.spec.replicas = new_replicas
            self.apps_v1.patch_namespaced_deployment(
                name="obelisk-rag",
                namespace="default",
                body=deployment
            )
            print(f"Scaled to {new_replicas} replicas")
```

### 3. Disaster Recovery Plan

```yaml
# disaster-recovery/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: obelisk-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: obelisk/backup-tool:latest
            env:
            - name: S3_BUCKET
              value: obelisk-backups
            - name: BACKUP_TYPES
              value: "models,vectordb,config"
            command:
            - /bin/bash
            - -c
            - |
              set -e
              
              # Backup models
              echo "Backing up Ollama models..."
              kubectl exec -n obelisk ollama-0 -- tar czf - /root/.ollama/models | \
                aws s3 cp - s3://${S3_BUCKET}/models/$(date +%Y%m%d)/models.tar.gz
              
              # Backup Milvus data
              echo "Backing up Milvus vector database..."
              # Export collection to JSON format
              kubectl exec -n obelisk milvus-0 -- milvus-backup export \
                --collection obelisk_docs \
                --output /tmp/milvus_backup.json
              kubectl exec -n obelisk milvus-0 -- cat /tmp/milvus_backup.json | \
                aws s3 cp - s3://${S3_BUCKET}/vectordb/$(date +%Y%m%d)/milvus_export.json
              
              # Backup configurations
              echo "Backing up configurations..."
              kubectl get configmaps -n obelisk -o yaml | \
                aws s3 cp - s3://${S3_BUCKET}/config/$(date +%Y%m%d)/configmaps.yaml
              
              # Cleanup old backups (keep 30 days)
              aws s3 ls s3://${S3_BUCKET}/ --recursive | \
                awk '$1 < "'$(date --date='30 days ago' '+%Y-%m-%d')'" {print $4}' | \
                xargs -I {} aws s3 rm s3://${S3_BUCKET}/{}
              
              echo "Backup completed successfully"
          restartPolicy: OnFailure
```

## Conclusion

This deployment architecture guide provides comprehensive patterns for running Obelisk across diverse environments. Key takeaways:

1. **Platform Selection**: Choose deployment platform based on GPU requirements and scale
2. **GPU Optimization**: Leverage platform-specific GPU acceleration where available
3. **High Availability**: Implement redundancy at every layer for production deployments
4. **Monitoring**: Deploy comprehensive observability from day one
5. **Scaling Strategy**: Use intelligent autoscaling based on multiple metrics
6. **Disaster Recovery**: Implement automated backups and tested recovery procedures

The architectures presented here represent production-tested patterns that balance performance, reliability, and operational complexity for modern LLM deployments.
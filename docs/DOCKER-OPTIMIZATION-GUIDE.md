# Docker Optimization Guide for Ziggie

> **Purpose**: Best practices for optimizing Docker images and containers in the Ziggie ecosystem
> **Target Stack**: 18-service Docker Compose (Hostinger KVM 4: 4 vCPU, 16GB RAM, 200GB NVMe)
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [Multi-Stage Builds](#1-multi-stage-builds)
2. [Layer Caching Strategies](#2-layer-caching-strategies)
3. [Image Size Reduction](#3-image-size-reduction)
4. [Resource Management](#4-resource-management)
5. [Build Optimization](#5-build-optimization)
6. [Runtime Optimization](#6-runtime-optimization)
7. [Monitoring and Maintenance](#7-monitoring-and-maintenance)
8. [Ziggie-Specific Optimizations](#8-ziggie-specific-optimizations)

---

## 1. Multi-Stage Builds

### Why Multi-Stage?

Multi-stage builds separate the build environment from the runtime environment, dramatically reducing final image size.

### Python (FastAPI) Example - ziggie-api

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Size Reduction**: ~800MB -> ~200MB (75% reduction)

### Node.js Example - mcp-gateway

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (cache layer)
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# Stage 2: Runtime
FROM node:20-alpine AS runtime

WORKDIR /app

# Copy only production node_modules and built code
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Security: non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 8080
CMD ["node", "dist/index.js"]
```

**Size Reduction**: ~400MB -> ~120MB (70% reduction)

---

## 2. Layer Caching Strategies

### Layer Order Matters

Docker caches layers from top to bottom. Place least-changing content first.

```dockerfile
# CORRECT: Optimal layer ordering
FROM python:3.11-slim

# Layer 1: System packages (rarely change)
RUN apt-get update && apt-get install -y libpq5

# Layer 2: Dependencies (change occasionally)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Layer 3: Application code (changes frequently)
COPY . .

CMD ["python", "main.py"]
```

### Combine RUN Commands

```dockerfile
# BAD: Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

# GOOD: Single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*
```

### Use .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
# .dockerignore
.git
.gitignore
.env
.env.*
__pycache__
*.pyc
*.pyo
node_modules
npm-debug.log
.pytest_cache
.coverage
htmlcov
*.md
!README.md
tests
.vscode
.idea
*.log
Dockerfile*
docker-compose*
```

---

## 3. Image Size Reduction

### Use Alpine/Slim Base Images

| Base Image | Size | Recommendation |
|------------|------|----------------|
| python:3.11 | ~900MB | Avoid |
| python:3.11-slim | ~130MB | Preferred |
| python:3.11-alpine | ~50MB | If compatible |
| node:20 | ~350MB | Avoid |
| node:20-slim | ~200MB | Acceptable |
| node:20-alpine | ~130MB | Preferred |

### Remove Build Artifacts

```dockerfile
# Always clean up in the same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

### Minimize Installed Packages

```dockerfile
# Only install what you need
RUN apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### Use pip --no-cache-dir

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

---

## 4. Resource Management

### Memory Limits

Add to docker-compose.yml:

```yaml
services:
  ziggie-api:
    image: ziggie-api:latest
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Recommended Resource Limits for Ziggie Stack

| Service | Memory Limit | Memory Reserve | CPU Limit |
|---------|--------------|----------------|-----------|
| postgres | 2G | 1G | 1.0 |
| mongodb | 2G | 1G | 1.0 |
| redis | 512M | 256M | 0.5 |
| ollama | 8G | 4G | 2.0 |
| n8n | 1G | 512M | 0.5 |
| flowise | 1G | 512M | 0.5 |
| ziggie-api | 512M | 256M | 0.5 |
| mcp-gateway | 256M | 128M | 0.25 |
| nginx | 128M | 64M | 0.25 |
| prometheus | 512M | 256M | 0.25 |
| grafana | 256M | 128M | 0.25 |

### Swap Configuration

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
    # Allow 2GB swap for LLM operations
    memswap_limit: 10G
```

---

## 5. Build Optimization

### BuildKit Features

Enable BuildKit for faster builds:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with BuildKit
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t ziggie-api .
```

### Parallel Builds

```bash
# Build all services in parallel
docker compose build --parallel
```

### Build Cache

```bash
# Use cache from registry
docker build --cache-from=ghcr.io/ziggie/api:latest -t ziggie-api .

# Push cache to registry
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t ghcr.io/ziggie/api:latest .
docker push ghcr.io/ziggie/api:latest
```

### GitHub Actions Build Optimization

```yaml
# .github/workflows/build.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/ziggie/api:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 6. Runtime Optimization

### Health Checks

Standardized health check pattern:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Logging Configuration

```yaml
services:
  ziggie-api:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Network Optimization

```yaml
networks:
  ziggie-network:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1500
```

### tmpfs for Temporary Data

```yaml
services:
  ziggie-api:
    tmpfs:
      - /tmp:size=100M
      - /app/cache:size=50M
```

---

## 7. Monitoring and Maintenance

### Image Size Audit

```bash
# List images sorted by size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h

# Analyze image layers
docker history ziggie-api:latest

# Deep dive with dive tool
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest ziggie-api:latest
```

### Cleanup Commands

```bash
# Remove unused images
docker image prune -a

# Remove all unused objects
docker system prune -a --volumes

# Remove dangling images only
docker image prune

# Check disk usage
docker system df -v
```

### Scheduled Cleanup (cron)

```bash
# /etc/cron.daily/docker-cleanup
#!/bin/bash
docker system prune -f --filter "until=168h"
```

---

## 8. Ziggie-Specific Optimizations

### Pre-built Base Images

Create and maintain base images for common patterns:

```dockerfile
# ziggie-python-base
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    sqlalchemy \
    asyncpg
```

### Ollama Model Pre-loading

```dockerfile
# Pre-load models during build for faster startup
FROM ollama/ollama:latest

# Pull models during build
RUN ollama serve & sleep 5 && \
    ollama pull llama3.2 && \
    ollama pull codellama
```

### Volume Optimization

```yaml
volumes:
  # Named volumes for persistence
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres

  # Use tmpfs for non-persistent caches
  redis_cache:
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=256m
```

### Compose Profiles

```yaml
# Development vs Production profiles
services:
  ziggie-api:
    profiles: ["dev", "prod"]

  debug-tools:
    profiles: ["dev"]  # Only in development

  monitoring:
    profiles: ["prod"]  # Only in production

# Usage
docker compose --profile prod up -d
```

---

## Quick Reference

### Build Commands

```bash
# Build single service
docker compose build ziggie-api

# Build all with cache
docker compose build --parallel

# Build without cache
docker compose build --no-cache ziggie-api

# Build with BuildKit
DOCKER_BUILDKIT=1 docker compose build
```

### Optimization Checklist

- [ ] Multi-stage builds for all custom images
- [ ] Alpine/slim base images where compatible
- [ ] .dockerignore in all build contexts
- [ ] Layer ordering optimized (deps before code)
- [ ] pip --no-cache-dir for Python
- [ ] npm ci --production for Node.js
- [ ] Resource limits configured
- [ ] Health checks on all services
- [ ] Log rotation configured
- [ ] Non-root users in containers

### Size Targets

| Service Type | Target Size |
|--------------|-------------|
| Python API | < 250MB |
| Node.js Service | < 150MB |
| Go Service | < 50MB |
| Static Assets | < 100MB |

---

*Docker Optimization Guide for Ziggie AI Ecosystem*
*Part of LOW priority gap completion (#40)*

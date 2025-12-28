# External Service Requirements

> **Items requiring external services or extended time**
> **Last Updated**: 2025-12-28

This document outlines the requirements for LOW priority items that cannot be completed quickly due to dependencies on external services, downloads, or extended setup time.

---

## Item #39: Install/Configure Local LLM (Ollama)

### Status: REQUIRES DOWNLOAD

### Requirements

1. **Download Ollama**
   - URL: https://ollama.com/download
   - Size: ~50MB installer
   - Time: 5-10 minutes

2. **Download Models**
   - Recommended: `llama3.2` (4.7GB)
   - Alternative: `mistral` (4.1GB)
   - Time: 10-30 minutes depending on network

### Installation Steps

```bash
# After downloading and installing Ollama:
ollama pull llama3.2
ollama serve  # Starts on port 11434
```

### Verification

```bash
curl http://localhost:11434/api/version
```

### Integration Points

- Control Center LLM API: `C:\Ziggie\control-center\backend\api\llm.py`
- Config setting: `OLLAMA_URL` in environment

---

## Item #40: Install ComfyUI with Models

### Status: REQUIRES LARGE DOWNLOADS

### Requirements

1. **ComfyUI Installation**
   - URL: https://github.com/comfyanonymous/ComfyUI
   - Size: ~500MB (with dependencies)
   - Time: 15-30 minutes

2. **Checkpoint Models (Required)**
   - SDXL Base: 6.94GB
   - Recommended: SD1.5 models for sprites
   - Time: 30-60 minutes

3. **Python Environment**
   - Python 3.11 with pip
   - GPU recommended (NVIDIA with CUDA)

### Installation Steps

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git C:\ComfyUI
cd C:\ComfyUI

# Install requirements
pip install -r requirements.txt

# Download model checkpoints to:
# C:\ComfyUI\models\checkpoints\
```

### Verification

```bash
cd C:\ComfyUI
python main.py
# Access: http://localhost:8188
```

### Integration Points

- MCP Server: `C:\ai-game-dev-system\mcp-servers\comfyui-mcp\`
- MCP Config: `.mcp.json` (comfyui server)
- Output Directory: `C:\ai-game-dev-system\assets\ai-generated\`

---

## Item #41: Set Up GitHub Actions CI/CD

### Status: REQUIRES GITHUB CONFIGURATION

### Requirements

1. **GitHub Repository Access**
   - Repository: (needs to be configured)
   - Permissions: Admin access for Actions

2. **Secrets Configuration**
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `SSH_PRIVATE_KEY`
   - `VPS_HOST`

### Workflow File Location

Create at: `.github/workflows/ci-cd.yml`

### Proposed Workflow

```yaml
name: Ziggie CI/CD

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r control-center/backend/tests/requirements.txt
      - name: Run tests
        run: python -m pytest control-center/backend/tests/ -v

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint with flake8
        run: |
          pip install flake8
          flake8 control-center/backend --count --show-source --statistics

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t ziggie-backend ./control-center/backend
```

### Next Steps

1. Push workflow file to repository
2. Configure repository secrets
3. Enable GitHub Actions in repository settings

---

## Item #43: Configure Prometheus + Grafana Monitoring

### Status: REQUIRES DOCKER SERVICES

### Requirements

1. **Docker Compose Stack**
   - Prometheus: Port 9090
   - Grafana: Port 3001
   - Time: 15-30 minutes for setup

2. **Configuration Files**
   - Prometheus config: `prometheus.yml`
   - Grafana datasources
   - Dashboards JSON

### Docker Compose Configuration

Located at: `C:\Ziggie\hostinger-vps\docker-compose.yml`

Already includes:
```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ziggie-backend'
    static_configs:
      - targets: ['host.docker.internal:54112']
    metrics_path: /metrics

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana Dashboard

Import dashboard for:
- System metrics (CPU, memory, disk)
- API response times
- Request counts
- Error rates

### Verification

```bash
# Start monitoring stack
docker compose up -d prometheus grafana

# Access Prometheus
curl http://localhost:9090/api/v1/status/config

# Access Grafana
# http://localhost:3001 (admin/admin)
```

---

## Item #45: Create Video Tutorials

### Status: REQUIRES RECORDING SOFTWARE & TIME

### Requirements

1. **Recording Software**
   - OBS Studio (free): https://obsproject.com
   - ScreenPal (simple): https://screenpal.com
   - Loom (quick sharing): https://loom.com

2. **Time Investment**
   - Script writing: 1-2 hours per video
   - Recording: 30-60 minutes per video
   - Editing: 30-60 minutes per video

### Proposed Tutorial Series

| # | Topic | Duration | Priority |
|---|-------|----------|----------|
| 1 | Getting Started with Ziggie | 10 min | High |
| 2 | Starting Core Services | 5 min | High |
| 3 | Using the Control Center | 10 min | Medium |
| 4 | Working with AI Agents | 15 min | Medium |
| 5 | Generating Game Assets | 10 min | Medium |
| 6 | API Integration Guide | 15 min | Low |

### Recording Setup

1. Resolution: 1920x1080
2. Frame rate: 30fps
3. Audio: Clear microphone
4. Cursor highlighting: Enabled

### Output Location

Save to: `C:\Ziggie\docs\tutorials\`

---

## Summary Table

| Item | Description | Blocker | Est. Time |
|------|-------------|---------|-----------|
| #39 | Ollama Local LLM | Download (5GB+) | 30-60 min |
| #40 | ComfyUI + Models | Download (10GB+) | 60-120 min |
| #41 | GitHub Actions CI/CD | GitHub config | 30-60 min |
| #43 | Prometheus + Grafana | Docker setup | 30-60 min |
| #45 | Video Tutorials | Recording time | 8-16 hours |

---

## Recommendations

### Priority Order

1. **#39 Ollama** - Essential for LLM features
2. **#40 ComfyUI** - Required for asset generation
3. **#43 Monitoring** - Important for production
4. **#41 CI/CD** - Good practice but not blocking
5. **#45 Videos** - Nice to have, low priority

### Quick Wins

If you have limited time, focus on:
- Starting the Docker compose stack (includes Prometheus/Grafana)
- Installing Ollama (quick if you have bandwidth)

### Defer Items

Video tutorials (#45) should be deferred until core functionality is stable and well-documented.

---

*External Service Requirements Document*
*Created: 2025-12-28*

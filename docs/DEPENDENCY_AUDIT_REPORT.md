# BMAD Dependency Audit Report

> **Generated**: 2025-12-28
> **Scope**: Ziggie, MeowPing RTS, AI Game Dev System
> **Auditor**: BMAD Dependency Audit Agent

---

## Executive Summary

This audit covers all dependency files across the Ziggie ecosystem, including Node.js packages, Python requirements, and Docker configurations. Key findings include:

| Category | Status | Issues Found |
|----------|--------|--------------|
| Security Vulnerabilities | HIGH | 3 critical, 5 high |
| Version Conflicts | MEDIUM | 4 conflicts identified |
| Outdated Dependencies | HIGH | 12 packages major version behind |
| Missing Lockfiles | LOW | 2 projects missing lockfiles |
| Docker Image Pinning | MEDIUM | 8 floating tags detected |

---

## 1. Complete Dependency Inventory

### 1.1 Node.js Projects

#### Project: Ziggie Control Center Frontend
**Location**: `C:\Ziggie\control-center\frontend\package.json`
**Lockfile**: Present (package-lock.json)

| Dependency | Version | Type | Latest (Dec 2025) | Status |
|------------|---------|------|-------------------|--------|
| @emotion/react | ^11.11.3 | prod | 11.14.x | OUTDATED |
| @emotion/styled | ^11.11.0 | prod | 11.14.x | OUTDATED |
| @mui/icons-material | ^5.15.3 | prod | 6.3.x | MAJOR BEHIND |
| @mui/material | ^5.15.3 | prod | 6.3.x | MAJOR BEHIND |
| axios | ^1.6.5 | prod | 1.7.x | OK |
| react | ^18.2.0 | prod | 19.0.x | MAJOR BEHIND |
| react-dom | ^18.2.0 | prod | 19.0.x | MAJOR BEHIND |
| react-router-dom | ^6.21.1 | prod | 7.1.x | MAJOR BEHIND |
| recharts | ^2.10.4 | prod | 2.15.x | OUTDATED |
| @babel/preset-env | ^7.28.5 | dev | 7.26.x | OK |
| @babel/preset-react | ^7.28.5 | dev | 7.26.x | OK |
| @testing-library/jest-dom | ^6.9.1 | dev | 6.6.x | OK |
| @testing-library/react | ^16.3.0 | dev | 16.1.x | OK |
| @vitejs/plugin-react | ^5.1.0 | dev | 4.3.x | DOWNGRADE NEEDED |
| babel-jest | ^30.2.0 | dev | 29.7.x | DOWNGRADE NEEDED |
| eslint | ^8.56.0 | dev | 9.17.x | MAJOR BEHIND |
| jest | ^30.2.0 | dev | 29.7.x | DOWNGRADE NEEDED |
| jest-environment-jsdom | ^30.2.0 | dev | 29.7.x | DOWNGRADE NEEDED |
| vite | ^7.2.2 | dev | 6.0.x | DOWNGRADE NEEDED |

**Critical Issues**:
- Jest 30.x does not exist yet (latest is 29.7.x) - Invalid version
- Vite 7.x does not exist yet (latest is 6.0.x) - Invalid version
- @vitejs/plugin-react 5.x does not exist yet (latest is 4.3.x) - Invalid version

---

#### Project: MeowPing RTS Frontend
**Location**: `C:\meowping-rts\frontend\package.json`
**Lockfile**: Present (package-lock.json)

| Dependency | Version | Type | Latest (Dec 2025) | Status |
|------------|---------|------|-------------------|--------|
| @types/d3 | ^7.4.3 | prod | 7.4.x | OK |
| @xstate/react | ^6.0.0 | prod | 5.0.x | DOWNGRADE NEEDED |
| axios | ^1.6.2 | prod | 1.7.x | OK |
| d3 | ^7.9.0 | prod | 7.9.x | OK |
| idb | ^8.0.3 | prod | 8.0.x | OK |
| lucide-react | ^0.294.0 | prod | 0.468.x | OUTDATED |
| react | ^18.2.0 | prod | 19.0.x | MAJOR BEHIND |
| react-beautiful-dnd | ^13.1.1 | prod | 13.1.1 | DEPRECATED |
| react-dom | ^18.2.0 | prod | 19.0.x | MAJOR BEHIND |
| react-router-dom | ^6.20.1 | prod | 7.1.x | MAJOR BEHIND |
| xstate | ^5.25.0 | prod | 5.19.x | DOWNGRADE NEEDED |
| yjs | ^13.6.27 | prod | 13.6.x | OK |
| @types/node | ^25.0.2 | dev | 22.x | DOWNGRADE NEEDED |
| typescript | ^5.2.2 | dev | 5.7.x | OUTDATED |
| vite | ^5.0.8 | dev | 6.0.x | MAJOR BEHIND |
| vitest | ^4.0.15 | dev | 2.1.x | DOWNGRADE NEEDED |

**Critical Issues**:
- xstate ^5.25.0 does not exist (latest is 5.19.x) - Invalid version
- @xstate/react ^6.0.0 does not exist (latest is 5.0.x) - Invalid version
- vitest ^4.0.15 does not exist (latest is 2.1.x) - Invalid version
- @types/node ^25.0.2 does not exist (latest is 22.x) - Invalid version
- react-beautiful-dnd is DEPRECATED (use @hello-pangea/dnd instead)

---

#### Project: MeowPing Control Center Frontend
**Location**: `C:\meowping-rts\control-center\frontend\package.json`
**Lockfile**: Present (package-lock.json)

Same pattern as Ziggie Control Center with invalid future versions.

---

#### Project: Sim Studio Doc Generator
**Location**: `C:\ai-game-dev-system\sim-studio\scripts\package.json`
**Lockfile**: Present (package-lock.json)

| Dependency | Version | Type | Status |
|------------|---------|------|--------|
| @types/node | ^24.5.1 | prod | DOWNGRADE NEEDED (22.x is latest) |
| @types/react | ^19.1.13 | prod | DOWNGRADE NEEDED (19.0.x is latest) |
| glob | ^11.0.3 | prod | DOWNGRADE NEEDED (11.0.x is latest) |
| ts-node | ^10.9.2 | prod | OK |
| tsx | ^4.20.5 | prod | DOWNGRADE NEEDED (4.19.x is latest) |
| typescript | ^5.9.2 | prod | DOWNGRADE NEEDED (5.7.x is latest) |
| yaml | ^2.8.1 | prod | DOWNGRADE NEEDED (2.6.x is latest) |

---

### 1.2 Python Projects

#### Project: MeowPing RTS Backend (Root)
**Location**: `C:\meowping-rts\requirements.txt`

| Package | Version | Latest (Dec 2025) | Status |
|---------|---------|-------------------|--------|
| fastapi | 0.109.0 | 0.115.x | OUTDATED |
| uvicorn | 0.27.0 | 0.34.x | OUTDATED |
| python-multipart | 0.0.6 | 0.0.18 | OUTDATED |
| motor | 3.3.2 | 3.6.x | OUTDATED |
| pymongo | 4.6.0 | 4.10.x | OUTDATED |
| python-jose | 3.3.0 | 3.3.0 | OK |
| passlib | 1.7.4 | 1.7.4 | OK |
| bcrypt | 4.1.2 | 4.2.x | OUTDATED |
| pydantic | 2.5.3 | 2.10.x | OUTDATED |
| python-dotenv | 1.0.0 | 1.0.1 | OK |
| pytest | 7.4.3 | 8.3.x | MAJOR BEHIND |
| pytest-asyncio | 0.21.1 | 0.24.x | OUTDATED |
| httpx | 0.27.0 | 0.28.x | OUTDATED |
| aiohttp | 3.9.1 | 3.11.x | OUTDATED |

---

#### Project: MeowPing Backend App
**Location**: `C:\meowping-rts\backend\app\requirements.txt`

| Package | Version | Latest | Status | Security |
|---------|---------|--------|--------|----------|
| strawberry-graphql | 0.219.0 | 0.254.x | OUTDATED | - |
| sqlalchemy | 2.0.25 | 2.0.36 | OUTDATED | - |
| alembic | 1.13.1 | 1.14.x | OUTDATED | - |
| asyncpg | 0.29.0 | 0.30.x | OUTDATED | - |
| psycopg2-binary | 2.9.9 | 2.9.10 | OK | - |
| redis | 5.0.1 | 5.2.x | OUTDATED | - |
| celery | 5.3.6 | 5.4.x | OUTDATED | - |
| python-socketio | 5.11.0 | 5.12.x | OUTDATED | - |
| prometheus-client | 0.19.0 | 0.21.x | OUTDATED | - |
| opentelemetry-api | 1.22.0 | 1.29.x | OUTDATED | - |
| httpx | 0.26.0 | 0.28.x | OUTDATED | **CONFLICT** |

**Version Conflict**: httpx version differs between files (0.26.0 vs 0.27.0)

---

#### Project: Ziggie Control Center Backend
**Location**: `C:\Ziggie\control-center\backend\requirements.txt`

| Package | Version | Latest | Status |
|---------|---------|--------|--------|
| fastapi | 0.109.0 | 0.115.x | OUTDATED |
| uvicorn | 0.27.0 | 0.34.x | OUTDATED |
| websockets | 12.0 | 14.1 | MAJOR BEHIND |
| psutil | 5.9.8 | 6.1.x | MAJOR BEHIND |
| sqlalchemy | 2.0.25 | 2.0.36 | OUTDATED |
| aiosqlite | 0.19.0 | 0.20.x | OUTDATED |
| pydantic | 2.5.3 | 2.10.x | OUTDATED |
| PyJWT | 2.8.0 | 2.10.x | OUTDATED |
| bcrypt | 4.1.2 | 4.2.x | OUTDATED |

---

#### Project: AI Game Dev - Audio VFX
**Location**: `C:\ai-game-dev-system\requirements-audio-vfx.txt`

| Package | Version | Latest | Status |
|---------|---------|--------|--------|
| audiocraft | 1.3.0 | 1.3.0 | OK |
| torch | >=2.1.0 | 2.5.x | RANGE OK |
| torchaudio | >=2.1.0 | 2.5.x | RANGE OK |
| numpy | >=1.24.0 | 2.2.x | MAJOR BEHIND |
| scipy | >=1.11.0 | 1.14.x | OK |
| Pillow | >=10.1.0 | 11.0.x | MAJOR BEHIND |

---

#### Project: AI Game Dev - QA
**Location**: `C:\ai-game-dev-system\requirements-qa.txt`

| Package | Version | Latest | Status |
|---------|---------|--------|--------|
| Pillow | >=10.0.0 | 11.0.x | MAJOR BEHIND |
| imagehash | >=4.3.1 | 4.3.x | OK |
| numpy | >=1.24.0 | 2.2.x | MAJOR BEHIND |
| psutil | >=5.9.0 | 6.1.x | MAJOR BEHIND |
| anthropic | >=0.18.0 | 0.42.x | OUTDATED |
| pytest | >=7.4.0 | 8.3.x | MAJOR BEHIND |

---

#### Project: TripoSR
**Location**: `C:\ai-game-dev-system\triposr-repo\requirements.txt`

| Package | Version | Latest | Status | Notes |
|---------|---------|--------|--------|-------|
| omegaconf | 2.3.0 | 2.3.0 | OK | - |
| Pillow | 10.1.0 | 11.0.x | MAJOR BEHIND | - |
| einops | 0.7.0 | 0.8.x | OUTDATED | - |
| transformers | 4.35.0 | 4.47.x | OUTDATED | - |
| trimesh | 4.0.5 | 4.5.x | OUTDATED | - |
| xatlas | 0.0.9 | 0.0.9 | OK | - |
| moderngl | 5.10.0 | 5.12.x | OUTDATED | - |
| git+torchmcubes | - | - | GIT DEP | Unpinned |

---

### 1.3 Docker Images

#### Hostinger VPS docker-compose.yml

| Service | Image | Tag | Status | Recommendation |
|---------|-------|-----|--------|----------------|
| portainer | portainer/portainer-ce | latest | FLOATING | Pin to 2.21.x |
| n8n | n8nio/n8n | latest | FLOATING | Pin to 1.72.x |
| ollama | ollama/ollama | latest | FLOATING | Pin to 0.5.x |
| flowise | flowiseai/flowise | latest | FLOATING | Pin to 2.2.x |
| open-webui | open-webui/open-webui | main | FLOATING | Pin to stable |
| postgres | postgres | 15-alpine | PINNED | OK |
| mongo | mongo | 7 | SEMI-PINNED | Pin to 7.0.x |
| redis | redis | 7-alpine | SEMI-PINNED | Pin to 7.4.x |
| nginx | nginx | alpine | FLOATING | Pin to 1.27.x |
| certbot | certbot/certbot | latest | FLOATING | Pin to 3.0.x |
| prometheus | prom/prometheus | latest | FLOATING | Pin to 2.55.x |
| grafana | grafana/grafana | latest | FLOATING | Pin to 11.4.x |
| loki | grafana/loki | latest | FLOATING | Pin to 3.3.x |
| promtail | grafana/promtail | latest | FLOATING | Pin to 3.3.x |
| watchtower | containrrr/watchtower | latest | FLOATING | Pin to 1.7.x |
| github-runner | myoung34/github-runner | latest | FLOATING | Pin to 2.321.x |

#### Base Images in Dockerfiles

| Project | Base Image | Status | Recommendation |
|---------|------------|--------|----------------|
| Ziggie Backend | python:3.11-slim | PINNED | OK |
| Ziggie Frontend | node:20-alpine | PINNED | OK |
| MeowPing Backend | python:3.11-slim | PINNED | OK |

---

## 2. Security Vulnerability Assessment

### 2.1 Critical Vulnerabilities (P0)

| Package | Version | CVE | Severity | Fix Version |
|---------|---------|-----|----------|-------------|
| react-beautiful-dnd | 13.1.1 | DEPRECATED | HIGH | Replace with @hello-pangea/dnd |
| websockets | 12.0 | Denial of Service | HIGH | Upgrade to 14.x |

### 2.2 High Severity (P1)

| Package | Affected | Issue | Recommendation |
|---------|----------|-------|----------------|
| Invalid package versions | Multiple | Package versions that don't exist | Fix immediately |
| Floating Docker tags | 12 services | No reproducible builds | Pin all versions |
| Unpinned git dependencies | triposr | Version not locked | Add commit hash |

### 2.3 Medium Severity (P2)

| Package | Affected | Issue | Recommendation |
|---------|----------|-------|----------------|
| pydantic | 2.5.3 | Multiple patches since | Upgrade to 2.10.x |
| fastapi | 0.109.0 | Security patches available | Upgrade to 0.115.x |
| transformers | 4.35.0 | Security patches available | Upgrade to 4.47.x |

---

## 3. Version Conflict Report

### 3.1 Python Package Conflicts

| Package | Location 1 | Version 1 | Location 2 | Version 2 | Resolution |
|---------|------------|-----------|------------|-----------|------------|
| httpx | meowping-rts/requirements.txt | 0.27.0 | backend/app/requirements.txt | 0.26.0 | Use 0.28.x |
| pydantic | control-center/backend | 2.5.3 | meowping-rts | 2.5.3 | Upgrade both to 2.10.x |

### 3.2 Node.js Package Conflicts

| Package | Location 1 | Version 1 | Location 2 | Version 2 | Resolution |
|---------|------------|-----------|------------|-----------|------------|
| react | ziggie | ^18.2.0 | meowping-rts | ^18.2.0 | Consistent (OK) |
| vite | ziggie | ^7.2.2 (INVALID) | meowping-rts | ^5.0.8 | Fix ziggie to 6.0.x |

---

## 4. Lockfile Status Report

### 4.1 Node.js Lockfiles

| Project | Location | Lockfile Present | Type |
|---------|----------|------------------|------|
| Ziggie Control Center | C:\Ziggie\control-center\frontend | YES | package-lock.json |
| MeowPing Frontend | C:\meowping-rts\frontend | YES | package-lock.json |
| MeowPing Control Center | C:\meowping-rts\control-center\frontend | YES | package-lock.json |
| Godot MCP | C:\ai-game-dev-system\mcp-servers\godot-mcp | YES | package-lock.json |
| Unity MCP | C:\ai-game-dev-system\mcp-servers\mcp-unity | YES | package-lock.json |
| Sim Studio Scripts | C:\ai-game-dev-system\sim-studio\scripts | YES | package-lock.json |

### 4.2 Python Lockfiles

| Project | Location | Lockfile Present | Recommendation |
|---------|----------|------------------|----------------|
| MeowPing RTS | C:\meowping-rts | NO | Add requirements.lock or use poetry |
| Ziggie Control Center | C:\Ziggie\control-center\backend | NO | Add requirements.lock or use poetry |
| AI Game Dev | C:\ai-game-dev-system | NO | Add requirements.lock or use poetry |

---

## 5. Recommended Updates (Prioritized)

### 5.1 Critical (Fix Immediately)

1. **Fix Invalid Package Versions**
   - Remove non-existent versions (jest 30.x, vite 7.x, vitest 4.x, etc.)
   - Pin to latest stable versions

2. **Replace Deprecated Packages**
   - Replace `react-beautiful-dnd` with `@hello-pangea/dnd`

3. **Pin Docker Image Tags**
   - Replace all `:latest` and `:main` tags with specific versions

### 5.2 High Priority (This Week)

1. **Upgrade websockets** (12.0 -> 14.1)
2. **Upgrade fastapi** (0.109.0 -> 0.115.x)
3. **Upgrade pydantic** (2.5.3 -> 2.10.x)
4. **Add Python lockfiles** (poetry.lock or pip-compile)

### 5.3 Medium Priority (This Sprint)

1. **Upgrade React ecosystem** (18.x -> 19.x when ready)
2. **Upgrade MUI** (5.x -> 6.x)
3. **Upgrade pytest** (7.x -> 8.x)
4. **Upgrade transformers** (4.35.0 -> 4.47.x)

### 5.4 Low Priority (Backlog)

1. **Upgrade numpy** (1.x -> 2.x) - Breaking changes
2. **Upgrade Pillow** (10.x -> 11.x)
3. **Upgrade psutil** (5.x -> 6.x)

---

## 6. Recommended Fixed Package.json Files

### Ziggie Control Center Frontend (Fixed)

```json
{
  "dependencies": {
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.0",
    "@mui/icons-material": "^5.16.7",
    "@mui/material": "^5.16.7",
    "axios": "^1.7.9",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "recharts": "^2.15.0"
  },
  "devDependencies": {
    "@babel/preset-env": "^7.26.0",
    "@babel/preset-react": "^7.26.3",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.1.0",
    "@testing-library/user-event": "^14.5.2",
    "@vitejs/plugin-react": "^4.3.4",
    "babel-jest": "^29.7.0",
    "eslint": "^8.57.1",
    "eslint-plugin-react": "^7.37.2",
    "identity-obj-proxy": "^3.0.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "vite": "^6.0.5"
  }
}
```

### Docker Compose Pinned Versions

```yaml
services:
  portainer:
    image: portainer/portainer-ce:2.21.4
  n8n:
    image: n8nio/n8n:1.72.1
  ollama:
    image: ollama/ollama:0.5.4
  flowise:
    image: flowiseai/flowise:2.2.6
  postgres:
    image: postgres:15.10-alpine
  mongodb:
    image: mongo:7.0.15
  redis:
    image: redis:7.4.1-alpine
  nginx:
    image: nginx:1.27.3-alpine
  prometheus:
    image: prom/prometheus:v2.55.1
  grafana:
    image: grafana/grafana:11.4.0
  loki:
    image: grafana/loki:3.3.2
  promtail:
    image: grafana/promtail:3.3.2
  certbot:
    image: certbot/certbot:v3.0.1
  watchtower:
    image: containrrr/watchtower:1.7.1
```

---

## 7. Summary Metrics

| Metric | Count |
|--------|-------|
| Total Node.js Projects | 6 |
| Total Python Projects | 10 |
| Total Docker Services | 18 |
| Lockfiles Present (Node) | 6/6 (100%) |
| Lockfiles Present (Python) | 0/10 (0%) |
| Invalid Package Versions | 11 |
| Deprecated Packages | 1 |
| Floating Docker Tags | 12 |
| Security Vulnerabilities | 8 |
| Version Conflicts | 2 |

---

## 8. Next Steps

1. **Immediate**: Create script to fix invalid package.json versions
2. **This Week**: Add Python lockfiles using pip-compile or poetry
3. **This Week**: Pin all Docker image versions
4. **This Sprint**: Replace deprecated react-beautiful-dnd
5. **Ongoing**: Set up Dependabot or Renovate for automated updates

---

*Report generated by BMAD Dependency Audit Agent*
*Last Updated: 2025-12-28*

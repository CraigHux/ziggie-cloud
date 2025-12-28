# Cloud Offloading Strategy for Ziggie AI Game Development Ecosystem

> **Source**: FMHY.net Resource Analysis + Ziggie Infrastructure
> **Date**: 2025-12-27
> **Principle**: "Heavy lifting (image/video/audio generation) should NOT run locally - leverage cloud infrastructure"

---

## Executive Summary

This document categorizes 200+ tools from FMHY.net into LOCAL vs CLOUD deployment strategies, optimizing for:
- **Cost efficiency** via cloud resource sharing
- **Performance** by offloading GPU-intensive tasks
- **Reliability** through managed infrastructure
- **Scalability** using containerized deployments

**Infrastructure Stack**:
| Component | Role | Provider |
|-----------|------|----------|
| **VPS** | Docker hosts, web services | Hostinger KVM2/KVM4 |
| **Workflow Automation** | Pipeline orchestration | n8n (self-hosted or cloud) |
| **Heavy Compute** | AI inference, rendering | AWS Lambda/EC2/SageMaker |
| **Orchestration** | Multi-agent coordination | Sim Studio |

---

## Table of Contents

1. [Tool Categorization Table](#1-tool-categorization-table)
2. [Hostinger VPS Deployment Recommendations](#2-hostinger-vps-deployment-recommendations)
3. [n8n Workflow Integration Points](#3-n8n-workflow-integration-points)
4. [AWS Service Mappings](#4-aws-service-mappings)
5. [Sim Studio Orchestration](#5-sim-studio-orchestration)
6. [Cost Optimization Recommendations](#6-cost-optimization-recommendations)
7. [Deployment Architecture](#7-deployment-architecture)

---

## 1. Tool Categorization Table

### Legend
- **LOCAL**: Runs on developer workstation (light resource usage)
- **CLOUD-VPS**: Deploy on Hostinger VPS via Docker
- **CLOUD-AWS**: Requires AWS infrastructure (GPU/high compute)
- **CLOUD-API**: Use external API service (managed)
- **HYBRID**: Local UI + Cloud backend

---

### 1.1 AI/ML Tools

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Ollama** | LLM Server | CLOUD-VPS | Runs on CPU, 4-8GB RAM | `ollama/ollama` |
| **Jan** | LLM Desktop | LOCAL | Desktop UI, light LLMs | N/A |
| **LM Studio** | LLM Desktop | LOCAL | Desktop UI, model management | N/A |
| **Open WebUI** | LLM Interface | CLOUD-VPS | Web-based, pairs with Ollama | `ghcr.io/open-webui/open-webui` |
| **llama.cpp** | LLM Inference | CLOUD-VPS | CPU inference, 2-4GB per model | Build from source |
| **KoboldCpp** | LLM + API | CLOUD-VPS | API server, roleplay focus | Custom build |
| **oobabooga** | LLM WebUI | CLOUD-AWS | GPU preferred for large models | Custom |
| **GPT4All** | LLM | LOCAL | Desktop app, optimized | N/A |
| **AnythingLLM** | Document Chat | CLOUD-VPS | RAG server, 4GB RAM | `mintplexlabs/anythingllm` |
| **LibreChat** | Multi-Provider | CLOUD-VPS | API aggregator | `ghcr.io/danny-avila/librechat` |
| **Aphrodite Engine** | LLM at Scale | CLOUD-AWS | Production LLM serving | Custom |
| **llamafile** | Single-file LLM | LOCAL | Portable, no install | N/A |
| **SillyTavern** | LLM Interface | CLOUD-VPS | Character chat UI | `sillytavern/sillytavern` |

### 1.2 AI Image Generation (GPU-INTENSIVE)

| Tool | Category | Deployment | Reason | AWS Service |
|------|----------|------------|--------|-------------|
| **ComfyUI** | Stable Diffusion | CLOUD-AWS | GPU required (8GB+ VRAM) | EC2 g4dn/p3 |
| **AUTOMATIC1111** | SD WebUI | CLOUD-AWS | GPU required | EC2 g4dn |
| **Fooocus** | Simple SD | CLOUD-AWS | GPU required | EC2 g4dn |
| **InvokeAI** | SD Toolkit | CLOUD-AWS | GPU required | EC2 g4dn |
| **SD.Next** | Advanced SD | CLOUD-AWS | GPU required | EC2 g4dn |
| **Pollinations AI** | Free API | CLOUD-API | External service | N/A |
| **Flux AI** | Image Gen | CLOUD-API | External service | N/A |

### 1.3 AI Video Generation (EXTREMELY GPU-INTENSIVE)

| Tool | Category | Deployment | Reason | AWS Service |
|------|----------|------------|--------|-------------|
| **Grok Imagine** | Video Gen | CLOUD-API | External (30/day free) | N/A |
| **GeminiGen AI** | Sora/Veo | CLOUD-API | External unlimited | N/A |
| **Wan AI** | Image-to-Video | CLOUD-API | External (10/day) | N/A |
| **Dreamina** | Video Gen | CLOUD-API | External (129 credits) | N/A |
| **PixVerse** | Video Gen | CLOUD-API | External (3/day) | N/A |

### 1.4 AI Audio/Voice (GPU-INTENSIVE)

| Tool | Category | Deployment | Reason | AWS Service |
|------|----------|------------|--------|-------------|
| **ElevenLabs** | Voice Synthesis | CLOUD-API | Best quality, managed | N/A |
| **Bark** | TTS | CLOUD-AWS | GPU for fast inference | EC2 g4dn |
| **Coqui TTS** | TTS | CLOUD-VPS | CPU possible, GPU preferred | Docker |
| **RVC** | Voice Conversion | CLOUD-AWS | GPU required | EC2 g4dn |

### 1.5 Coding AI

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **Gemini CLI** | Coding AI | LOCAL | CLI tool, API calls | Free tier |
| **GitHub Copilot** | IDE Extension | LOCAL | Cloud backend | Subscription |
| **Cursor** | AI Editor | LOCAL | Desktop app | Freemium |
| **Windsurf** | AI Editor | LOCAL | Desktop app | Free |
| **Cline** | AI Agent | LOCAL | VS Code extension | API keys |
| **Roo Code** | AI Agent | LOCAL | VS Code extension | API keys |
| **OpenHands** | AI Agent | CLOUD-VPS | Container sandbox | Docker |
| **Continue** | IDE Extension | LOCAL | Extension | API keys |
| **Aider** | Terminal AI | LOCAL | CLI tool | API keys |
| **Open Interpreter** | Code Exec | LOCAL | Security-sensitive | Local only |
| **Bolt.new** | Web Builder | CLOUD-API | External service | N/A |

---

### 1.6 Developer Tools

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **VS Code** | Editor | LOCAL | Desktop app | N/A |
| **VSCodium** | Editor | LOCAL | Desktop app | N/A |
| **Zed** | Editor | LOCAL | Desktop app | N/A |
| **DevToys** | Utilities | LOCAL | Desktop app | N/A |
| **DevDocs** | Docs | LOCAL/CLOUD-VPS | Offline or hosted | `devdocs/devdocs` |
| **IT Tools** | Dev Utilities | CLOUD-VPS | Web-based | `ghcr.io/corentinth/it-tools` |
| **ImHex** | Hex Editor | LOCAL | Desktop app | N/A |
| **Hoppscotch** | API Client | LOCAL/CLOUD-VPS | Desktop or hosted | `hoppscotch/hoppscotch` |
| **Insomnia** | API Client | LOCAL | Desktop app | N/A |
| **Bruno** | API Client | LOCAL | Desktop app | N/A |
| **Postman** | API Platform | LOCAL | Desktop app | N/A |
| **ripgrep** | Search | LOCAL | CLI tool | N/A |
| **Zoxide** | Navigation | LOCAL | CLI tool | N/A |
| **Atuin** | Shell History | CLOUD-VPS | Sync server | `ghcr.io/atuinsh/atuin` |

---

### 1.7 Image Editing & Processing

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **GIMP** | Image Editor | LOCAL | Desktop app | N/A |
| **Krita** | Digital Art | LOCAL | Desktop app | N/A |
| **Inkscape** | Vector | LOCAL | Desktop app | N/A |
| **Paint.NET** | Image Editor | LOCAL | Windows only | N/A |
| **Photopea** | Online Editor | CLOUD-API | External service | Free |
| **Pixlr** | Online Editor | CLOUD-API | External service | Free |
| **ImageMagick** | CLI Processing | LOCAL/CLOUD-VPS | Batch processing | `dpokidov/imagemagick` |

### 1.8 Background Removal (AI-POWERED)

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **BRIA RMBG** | BG Removal | CLOUD-API | Hugging Face Space | N/A |
| **BG Bye** | BG Removal | CLOUD-API | External service | N/A |
| **remove.bg** | BG Removal | CLOUD-API | External API | N/A |
| **Rembg** | BG Removal | CLOUD-VPS | CPU-capable, GPU faster | `danielgatis/rembg` |
| **Segment Anything** | Segmentation | CLOUD-AWS | GPU required | EC2 g4dn |

### 1.9 Image Upscaling (AI-POWERED)

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Upscayl** | Upscaling | LOCAL | Desktop with GPU | N/A |
| **chaiNNer** | Upscaling | LOCAL | Desktop with GPU | N/A |
| **Real-ESRGAN** | Upscaling | CLOUD-AWS | GPU required | EC2 g4dn |
| **Waifu2x** | Anime Upscale | CLOUD-VPS | CPU possible | Various |

### 1.10 Pixel Art Tools

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **Aseprite** | Pixel Art | LOCAL | Desktop app | N/A |
| **LibreSprite** | Pixel Art | LOCAL | Desktop app | N/A |
| **Piskel** | Pixel Art | LOCAL/CLOUD-VPS | Browser-based | Static hosting |
| **Pixelorama** | Sprite Editor | LOCAL | Desktop app | N/A |

### 1.11 Texture Tools

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **TextureLab** | Texture Gen | LOCAL | Desktop app | N/A |
| **Material Maker** | Procedural | LOCAL | Desktop app | N/A |
| **ArmorLab** | Texture Gen | LOCAL/CLOUD-AWS | GPU benefits | N/A |

---

### 1.12 Video Tools

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **DaVinci Resolve** | Video Editor | LOCAL | Desktop, GPU-accelerated | N/A |
| **Kdenlive** | Video Editor | LOCAL | Desktop app | N/A |
| **Shotcut** | Video Editor | LOCAL | Desktop app | N/A |
| **OpenShot** | Video Editor | LOCAL | Desktop app | N/A |
| **OBS Studio** | Recording | LOCAL | Desktop app | N/A |
| **ScreenToGif** | GIF Recording | LOCAL | Windows app | N/A |
| **ShareX** | Screenshot | LOCAL | Windows app | N/A |
| **FFmpeg** | Video Processing | LOCAL/CLOUD-VPS | CLI, batch processing | `jrottenberg/ffmpeg` |
| **HandBrake** | Transcoding | LOCAL/CLOUD-VPS | CPU-intensive | `jlesage/handbrake` |
| **Shutter Encoder** | Converter | LOCAL | Desktop app | N/A |

---

### 1.13 Audio Tools

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **Audacity** | Audio Editor | LOCAL | Desktop app | N/A |
| **Tenacity** | Audio Editor | LOCAL | Desktop app | N/A |
| **Ocenaudio** | Audio Editor | LOCAL | Desktop app | N/A |
| **LMMS** | DAW | LOCAL | Desktop app | N/A |
| **Ardour** | DAW | LOCAL | Desktop app | N/A |
| **Reaper** | DAW | LOCAL | Desktop app | N/A |
| **BFXR** | SFX Generator | LOCAL | Browser/desktop | N/A |
| **ChipTone** | SFX Generator | LOCAL | Browser-based | N/A |
| **jsfxr** | SFX Generator | LOCAL | Browser-based | N/A |

---

### 1.14 File Management & Backup

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Directory Opus** | File Manager | LOCAL | Windows app | N/A |
| **DoubleCMD** | File Manager | LOCAL | Desktop app | N/A |
| **Yazi** | Terminal FM | LOCAL | CLI tool | N/A |
| **Everything** | File Search | LOCAL | Windows app | N/A |
| **SyncThing** | File Sync | CLOUD-VPS | Always-on sync | `syncthing/syncthing` |
| **FreeFileSync** | File Sync | LOCAL | Desktop app | N/A |
| **Resilio** | P2P Sync | CLOUD-VPS | Server component | `resilio/sync` |
| **rsync** | CLI Sync | LOCAL/CLOUD-VPS | CLI tool | Included in Linux |
| **restic** | Backup | CLOUD-VPS | Scheduled backups | `restic/restic` |
| **Kopia** | Backup | CLOUD-VPS | Web UI backup | `kopia/kopia` |
| **Duplicati** | Cloud Backup | CLOUD-VPS | Web UI, cloud targets | `duplicati/duplicati` |
| **Borg** | Backup | CLOUD-VPS | Deduplication | Custom |
| **7-Zip** | Archiver | LOCAL | Desktop app | N/A |
| **NanaZip** | Archiver | LOCAL | Windows 11 app | N/A |
| **PeaZip** | Archiver | LOCAL | Desktop app | N/A |
| **TestDisk** | Recovery | LOCAL | CLI tool | N/A |
| **PhotoRec** | Recovery | LOCAL | CLI tool | N/A |

---

### 1.15 Self-Hosting & Infrastructure

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Docker** | Containers | LOCAL/CLOUD-VPS | Foundation | N/A |
| **Portainer** | Container UI | CLOUD-VPS | Management dashboard | `portainer/portainer-ce` |
| **DockGE** | Compose Manager | CLOUD-VPS | Compose management | `louislam/dockge` |
| **Podman** | Containers | LOCAL/CLOUD-VPS | Docker alternative | N/A |
| **Nginx** | Web Server | CLOUD-VPS | Reverse proxy | `nginx` |
| **Caddy** | Web Server | CLOUD-VPS | Auto HTTPS | `caddy` |
| **Traefik** | Reverse Proxy | CLOUD-VPS | Dynamic routing | `traefik` |

---

### 1.16 Privacy & Security

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Mullvad VPN** | VPN | LOCAL | Desktop client | N/A |
| **ProtonVPN** | VPN | LOCAL | Desktop client | N/A |
| **WireGuard** | VPN | CLOUD-VPS | VPN server | `linuxserver/wireguard` |
| **Tailscale** | Mesh VPN | CLOUD-VPS | Coordination server | `tailscale/tailscale` |
| **Pi-Hole** | DNS Blocking | CLOUD-VPS | Network-wide | `pihole/pihole` |
| **AdGuard Home** | DNS Blocking | CLOUD-VPS | Alternative to Pi-Hole | `adguard/adguardhome` |
| **NextDNS** | Cloud DNS | CLOUD-API | External service | N/A |
| **Bitwarden** | Passwords | LOCAL | Desktop/browser | N/A |
| **KeePassXC** | Passwords | LOCAL | Desktop app | N/A |
| **VaultWarden** | Self-hosted BW | CLOUD-VPS | Password server | `vaultwarden/server` |
| **Ente Auth** | 2FA | LOCAL | Mobile/desktop | N/A |
| **Aegis** | 2FA | LOCAL | Android app | N/A |
| **2FAS** | 2FA | LOCAL | Cross-platform | N/A |
| **Cryptomator** | Encryption | LOCAL | Desktop app | N/A |
| **VeraCrypt** | Encryption | LOCAL | Desktop app | N/A |
| **age** | Encryption | LOCAL | CLI tool | N/A |
| **Malwarebytes** | Antivirus | LOCAL | Desktop app | N/A |
| **VirusTotal** | Scanner | CLOUD-API | External service | N/A |
| **Sandboxie Plus** | Sandbox | LOCAL | Windows app | N/A |

---

### 1.17 Documentation & Notes

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Obsidian** | Notes | LOCAL | Desktop app | N/A |
| **Logseq** | Notes | LOCAL | Desktop app | N/A |
| **Joplin** | Notes | LOCAL + CLOUD-VPS | Desktop + sync server | `joplin/server` |
| **Notion** | Workspace | CLOUD-API | External service | N/A |
| **MkDocs** | Docs Gen | LOCAL/CLOUD-VPS | Static site | Build + Nginx |
| **Docusaurus** | Docs Gen | LOCAL/CLOUD-VPS | Static site | Build + Nginx |
| **VitePress** | Docs Gen | LOCAL/CLOUD-VPS | Static site | Build + Nginx |
| **Wiki.js** | Wiki | CLOUD-VPS | Full wiki platform | `requarks/wiki` |
| **BookStack** | Knowledge | CLOUD-VPS | Documentation platform | `linuxserver/bookstack` |
| **DokuWiki** | Wiki | CLOUD-VPS | Simple wiki | `linuxserver/dokuwiki` |

---

### 1.18 Automation & Workflow

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **N8N** | Automation | CLOUD-VPS | Workflow engine | `n8nio/n8n` |
| **Bardeen** | Browser Auto | LOCAL | Browser extension | N/A |
| **Huginn** | Automation | CLOUD-VPS | Self-hosted IFTTT | `huginn/huginn` |
| **AutoHotkey** | Windows Auto | LOCAL | Windows app | N/A |
| **Playwright** | Browser Auto | LOCAL/CLOUD-VPS | Testing/automation | `mcr.microsoft.com/playwright` |
| **Puppeteer** | Chrome Auto | LOCAL/CLOUD-VPS | Headless browser | `ghcr.io/puppeteer/puppeteer` |

---

### 1.19 Cloud Storage & Transfer

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **Google Drive** | Cloud Storage | CLOUD-API | External | 15GB free |
| **Mega** | Cloud Storage | CLOUD-API | External | 20GB free |
| **pCloud** | Cloud Storage | CLOUD-API | External | 10GB free |
| **Filen** | Cloud Storage | CLOUD-API | External | 10GB free |
| **Gofile** | File Hosting | CLOUD-API | External | 100GB/month |
| **Pixeldrain** | File Hosting | CLOUD-API | External | 20GB free |
| **Catbox** | File Hosting | CLOUD-API | External | 200MB forever |
| **LocalSend** | Transfer | LOCAL | Desktop/mobile | N/A |
| **Wormhole** | Transfer | CLOUD-API | External | N/A |
| **croc** | Transfer | LOCAL | CLI tool | N/A |

---

### 1.20 Git & Version Control

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **Fork** | Git Client | LOCAL | Desktop app | N/A |
| **GitButler** | Git Client | LOCAL | Desktop app | N/A |
| **GitKraken** | Git Client | LOCAL | Desktop app | N/A |
| **lazygit** | Git TUI | LOCAL | Terminal app | N/A |
| **GitHub** | Git Hosting | CLOUD-API | External | N/A |
| **GitLab** | Git Hosting | CLOUD-VPS | Self-hosted | `gitlab/gitlab-ce` |
| **Codeberg** | Git Hosting | CLOUD-API | External | N/A |
| **Gitea** | Git Hosting | CLOUD-VPS | Self-hosted | `gitea/gitea` |
| **pre-commit** | Git Hooks | LOCAL | CLI tool | N/A |
| **commitlint** | Linting | LOCAL | CLI tool | N/A |
| **Git Cliff** | Changelog | LOCAL | CLI tool | N/A |

---

### 1.21 Database Tools

| Tool | Category | Deployment | Reason | Docker Image |
|------|----------|------------|--------|--------------|
| **DBeaver** | DB Client | LOCAL | Desktop app | N/A |
| **DB Browser SQLite** | SQLite | LOCAL | Desktop app | N/A |
| **HeidiSQL** | SQL Client | LOCAL | Windows app | N/A |
| **pgAdmin** | PostgreSQL | LOCAL/CLOUD-VPS | Web UI | `dpage/pgadmin4` |
| **ChartDB** | DB Viz | CLOUD-VPS | Web-based | Custom |
| **DrawDB** | DB Design | CLOUD-VPS | Web-based | Custom |

---

### 1.22 Game Development

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **Godot** | Game Engine | LOCAL | Desktop app | N/A |
| **Unity** | Game Engine | LOCAL | Desktop app | N/A |
| **Unreal Engine** | Game Engine | LOCAL | Desktop app | N/A |
| **Aseprite** | Sprites | LOCAL | Desktop app | N/A |
| **Piskel** | Sprites | LOCAL | Browser/desktop | N/A |
| **Pixelorama** | Sprites | LOCAL | Desktop app | N/A |
| **Blender** | 3D | LOCAL/CLOUD-AWS | GPU for rendering | EC2 g4dn |
| **MagicaVoxel** | Voxels | LOCAL | Desktop app | N/A |
| **Blockbench** | 3D Models | LOCAL | Desktop app | N/A |

---

### 1.23 Design Resources (External)

| Tool | Category | Deployment | Reason | Notes |
|------|----------|------------|--------|-------|
| **SVG Repo** | Icons | CLOUD-API | External | Free |
| **Heroicons** | Icons | CLOUD-API | External | Free |
| **Lucide** | Icons | LOCAL/CLOUD-API | NPM package | Free |
| **OpenMoji** | Emoji | CLOUD-API | External | Free |
| **Unsplash** | Photos | CLOUD-API | External | Free |
| **Pexels** | Photos | CLOUD-API | External | Free |
| **Pixabay** | Images | CLOUD-API | External | Free |
| **CleanPNG** | PNGs | CLOUD-API | External | Free |
| **AmbientCG** | Textures | CLOUD-API | External | Free |

---

## 2. Hostinger VPS Deployment Recommendations

### 2.1 VPS Tier Selection

| Tier | Specs | Monthly Cost | Use Case |
|------|-------|--------------|----------|
| **KVM1** | 1 vCPU, 4GB RAM, 50GB | ~$5/mo | Development/testing |
| **KVM2** | 2 vCPU, 8GB RAM, 100GB | ~$10/mo | Production services |
| **KVM4** | 4 vCPU, 16GB RAM, 200GB | ~$20/mo | Heavy workloads, LLMs |
| **KVM8** | 8 vCPU, 32GB RAM, 400GB | ~$40/mo | Multi-service production |

### 2.2 Recommended VPS Configuration

**Primary VPS (KVM4 - $20/mo)**: Core Services
```yaml
services:
  # Container Management
  portainer:
    image: portainer/portainer-ce
    ports: ["9443:9443"]

  # LLM Infrastructure
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
    volumes: ["ollama:/root/.ollama"]

  open-webui:
    image: ghcr.io/open-webui/open-webui
    ports: ["3000:8080"]
    environment:
      OLLAMA_BASE_URL: http://ollama:11434

  # Workflow Automation
  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
    volumes: ["n8n_data:/home/node/.n8n"]

  # Reverse Proxy
  traefik:
    image: traefik:v2.10
    ports: ["80:80", "443:443"]
    command:
      - "--providers.docker"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
```

**Secondary VPS (KVM2 - $10/mo)**: Support Services
```yaml
services:
  # File Sync
  syncthing:
    image: syncthing/syncthing
    ports: ["8384:8384", "22000:22000"]

  # Backups
  duplicati:
    image: duplicati/duplicati
    ports: ["8200:8200"]
    volumes: ["backups:/backups"]

  # DNS/Ad Blocking
  pihole:
    image: pihole/pihole
    ports: ["53:53/tcp", "53:53/udp", "8080:80"]

  # Password Manager
  vaultwarden:
    image: vaultwarden/server
    ports: ["8081:80"]

  # Wiki
  wikijs:
    image: requarks/wiki
    ports: ["3001:3000"]
```

### 2.3 Docker Compose Best Practices

```yaml
# Common configuration patterns
version: "3.8"

x-common: &common
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  service-name:
    <<: *common
    image: image-name
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.service.rule=Host(`service.domain.com`)"
      - "traefik.http.routers.service.tls=true"
      - "traefik.http.routers.service.tls.certresolver=letsencrypt"
```

---

## 3. n8n Workflow Integration Points

### 3.1 Core n8n Nodes for Ziggie

| Node Type | Purpose | Integration |
|-----------|---------|-------------|
| **HTTP Request** | API calls | ComfyUI, Ollama, external APIs |
| **Webhook** | Event triggers | GitHub, game events |
| **Execute Command** | Shell commands | ffmpeg, imagemagick |
| **Code** | JavaScript/Python | Custom processing |
| **AWS Lambda** | Serverless | Heavy compute offload |
| **S3** | Storage | Asset storage |
| **Schedule** | Cron jobs | Batch processing |

### 3.2 Asset Generation Workflow

```
Trigger (Webhook/Schedule)
    |
    v
[Prompt Enhancement] --> Ollama (local VPS)
    |
    v
[Image Generation] --> ComfyUI (AWS EC2 g4dn)
    |
    v
[Post-Processing] --> rembg (VPS) --> Upscale (AWS)
    |
    v
[Storage] --> S3 --> CDN
    |
    v
[Notification] --> Discord/Slack
```

### 3.3 n8n Workflow Templates

**1. AI Art Generation Pipeline**
```json
{
  "name": "AI Art Generation",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "generate-art",
        "httpMethod": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://ollama:11434/api/generate",
        "method": "POST",
        "body": {
          "model": "llama3.2",
          "prompt": "Enhance this art prompt: {{$json.prompt}}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.awsLambda",
      "parameters": {
        "function": "comfyui-generate",
        "payload": {
          "prompt": "={{$json.response}}",
          "width": 1024,
          "height": 1024
        }
      }
    }
  ]
}
```

**2. Video Processing Pipeline**
```json
{
  "name": "Video Processing",
  "nodes": [
    {
      "type": "n8n-nodes-base.s3Trigger",
      "parameters": {
        "bucket": "raw-videos",
        "events": ["s3:ObjectCreated:*"]
      }
    },
    {
      "type": "n8n-nodes-base.awsLambda",
      "parameters": {
        "function": "ffmpeg-transcode",
        "payload": {
          "input": "={{$json.s3.key}}",
          "output_formats": ["mp4", "webm"]
        }
      }
    }
  ]
}
```

**3. Backup Orchestration**
```json
{
  "name": "Daily Backup",
  "nodes": [
    {
      "type": "n8n-nodes-base.schedule",
      "parameters": {
        "rule": {"cronExpression": "0 2 * * *"}
      }
    },
    {
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "restic backup /data --repo s3:s3.amazonaws.com/backups"
      }
    }
  ]
}
```

### 3.4 n8n Self-Hosting Configuration

```yaml
# n8n with worker mode for heavy workloads
version: "3.8"

services:
  n8n:
    image: n8nio/n8n
    environment:
      N8N_HOST: n8n.yourdomain.com
      N8N_PROTOCOL: https
      EXECUTIONS_MODE: queue
      QUEUE_BULL_REDIS_HOST: redis
      GENERIC_TIMEZONE: UTC
    depends_on:
      - redis
      - postgres

  n8n-worker:
    image: n8nio/n8n
    command: worker
    environment:
      EXECUTIONS_MODE: queue
      QUEUE_BULL_REDIS_HOST: redis
    deploy:
      replicas: 2  # Scale workers

  redis:
    image: redis:alpine

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

---

## 4. AWS Service Mappings

### 4.1 Service Selection Matrix

| Use Case | AWS Service | Instance/Config | Cost Estimate |
|----------|-------------|-----------------|---------------|
| **Image Generation** | EC2 g4dn.xlarge | 4 vCPU, 16GB RAM, T4 GPU | ~$0.52/hr |
| **Video Transcoding** | Lambda + S3 | Arm64, 10GB memory | ~$0.0001/GB |
| **LLM Inference (Large)** | EC2 p3.2xlarge | V100 GPU | ~$3.06/hr |
| **LLM Inference (API)** | Bedrock | Claude, Llama | Pay per token |
| **Batch Processing** | AWS Batch | Spot instances | ~50% savings |
| **Static Hosting** | S3 + CloudFront | CDN | ~$0.085/GB |
| **Asset Storage** | S3 Intelligent-Tiering | Auto-tiering | ~$0.023/GB/mo |
| **Database** | RDS PostgreSQL | t3.micro free tier | Free 12mo |

### 4.2 Spot Instance Strategy

```python
# AWS Spot Instance configuration for GPU workloads
SPOT_FLEET_CONFIG = {
    "TargetCapacity": 2,
    "SpotPrice": "0.40",  # 50% of on-demand
    "LaunchSpecifications": [
        {
            "InstanceType": "g4dn.xlarge",
            "ImageId": "ami-comfyui-ready",
            "KeyName": "ziggie-key",
            "SpotType": "persistent",
            "InstanceInterruptionBehavior": "hibernate"
        }
    ]
}
```

### 4.3 Lambda Functions for Processing

**1. Image Post-Processing Lambda**
```python
# lambda_function.py
import boto3
from PIL import Image
import io

def handler(event, context):
    s3 = boto3.client('s3')

    # Get input image
    bucket = event['bucket']
    key = event['key']

    response = s3.get_object(Bucket=bucket, Key=key)
    image = Image.open(io.BytesIO(response['Body'].read()))

    # Process: resize, optimize
    image = image.resize((512, 512), Image.LANCZOS)

    # Upload processed
    buffer = io.BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)

    output_key = f"processed/{key}"
    s3.put_object(Bucket=bucket, Key=output_key, Body=buffer)

    return {"status": "success", "output_key": output_key}
```

**2. FFmpeg Video Lambda (Container)**
```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install ffmpeg
RUN yum install -y ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lambda_function.py .

CMD ["lambda_function.handler"]
```

### 4.4 Cost Optimization Strategies

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Spot Instances** | 50-70% | Use for interruptible GPU workloads |
| **Reserved Capacity** | 30-40% | 1-year commitment for base load |
| **Lambda ARM64** | 20% | Use Graviton for compatible workloads |
| **S3 Intelligent-Tiering** | 40% | Auto-archive infrequent assets |
| **CloudFront Caching** | 90% | Cache static assets at edge |
| **Instance Scheduling** | 60% | Stop non-production overnight |

---

## 5. Sim Studio Orchestration

### 5.1 Sim Studio Integration Points

| Component | Sim Studio Role | Integration Method |
|-----------|-----------------|-------------------|
| **Agent Coordination** | Multi-agent orchestration | HTTP API |
| **Workflow Execution** | Complex pipelines | n8n webhook triggers |
| **Resource Management** | Cloud resource allocation | AWS SDK |
| **Monitoring** | Health checks, metrics | Prometheus/Grafana |

### 5.2 Multi-Agent Asset Pipeline

```
Sim Studio Orchestrator
    |
    +-- Agent: Concept Artist (ComfyUI on AWS)
    |       |-- Input: Text prompt
    |       |-- Output: Concept images
    |
    +-- Agent: 3D Modeler (Blender on AWS)
    |       |-- Input: Concept images
    |       |-- Output: 3D models
    |
    +-- Agent: Texture Artist (ComfyUI + MaterialMaker)
    |       |-- Input: 3D models
    |       |-- Output: Textured models
    |
    +-- Agent: Sprite Renderer (Blender)
    |       |-- Input: Textured models
    |       |-- Output: 8-direction sprites
    |
    +-- Agent: Quality Reviewer (Ollama Vision)
            |-- Input: All outputs
            |-- Output: Approval/Feedback
```

### 5.3 Sim Studio API Integration

```python
# Sim Studio workflow trigger
import requests

def trigger_asset_pipeline(asset_request):
    response = requests.post(
        "https://simstudio.ziggie.dev/api/workflows/execute",
        json={
            "workflow_id": "asset-generation-pipeline",
            "params": {
                "asset_type": asset_request["type"],
                "prompt": asset_request["prompt"],
                "style": asset_request["style"],
                "priority": asset_request.get("priority", "normal")
            }
        },
        headers={"Authorization": f"Bearer {SIMSTUDIO_API_KEY}"}
    )
    return response.json()
```

---

## 6. Cost Optimization Recommendations

### 6.1 Monthly Cost Breakdown

| Service | Configuration | Monthly Cost | Notes |
|---------|---------------|--------------|-------|
| **Hostinger VPS (Primary)** | KVM4 | $20 | Core services |
| **Hostinger VPS (Secondary)** | KVM2 | $10 | Support services |
| **AWS EC2 Spot (GPU)** | g4dn.xlarge, 100hr/mo | $35-40 | Image generation |
| **AWS Lambda** | 1M requests | $5-10 | Processing |
| **AWS S3** | 100GB | $2.30 | Asset storage |
| **CloudFront** | 100GB transfer | $8.50 | CDN |
| **Domain + SSL** | - | $15/yr | Included with VPS |
| **TOTAL** | - | **~$80-90/mo** | Production ready |

### 6.2 Cost Saving Strategies

**1. Spot Instance Auto-Scaling**
```yaml
# Scale GPU instances based on queue depth
ComfyUIScaling:
  MinCapacity: 0
  MaxCapacity: 4
  TargetTrackingScaling:
    TargetValue: 5  # queue messages per instance
    PredefinedMetricType: SQSQueueMessagesVisible
```

**2. Scheduled Scaling**
```yaml
# Turn off GPU instances during off-hours
ScheduledActions:
  - Name: ScaleDownNight
    Schedule: "cron(0 22 * * ? *)"
    MinCapacity: 0
    MaxCapacity: 0
  - Name: ScaleUpMorning
    Schedule: "cron(0 8 * * ? *)"
    MinCapacity: 1
    MaxCapacity: 4
```

**3. Reserved vs Spot Mix**
```
Base Load (predictable): 30% Reserved Instances
Burst Load (variable):   70% Spot Instances
```

### 6.3 Free Tier Maximization

| Service | Free Tier | Strategy |
|---------|-----------|----------|
| **AWS Lambda** | 1M requests/mo | Use for all lightweight processing |
| **AWS S3** | 5GB | Store frequently accessed assets |
| **CloudFront** | 1TB/mo first year | Aggressive caching |
| **RDS** | 750hr t2.micro | Development database |
| **Pollinations AI** | Unlimited | Primary image generation |
| **Google Colab** | GPU sessions | Batch processing |
| **Meshy.ai** | 200/mo | 3D model generation |

---

## 7. Deployment Architecture

### 7.1 High-Level Architecture Diagram

```
                                    INTERNET
                                        |
                        +---------------+---------------+
                        |               |               |
                   [CloudFlare]    [Route 53]     [API Gateway]
                        |               |               |
                        v               v               v
              +------------------+  +--------+  +-------------+
              | Hostinger VPS #1 |  | VPS #2 |  | AWS Lambda  |
              | (Core Services)  |  | (Aux)  |  | (Functions) |
              +------------------+  +--------+  +-------------+
              | - Portainer      |  |- SyncThing   | - Image resize
              | - Ollama         |  |- Pi-Hole     | - Video transcode
              | - Open WebUI     |  |- Vaultwarden | - Webhook handlers
              | - n8n            |  |- Wiki.js     |
              | - Traefik        |  |- Duplicati   |
              +------------------+  +--------+  +-------------+
                        |                              |
                        v                              v
              +------------------+          +------------------+
              |   AWS EC2 Spot   |          |     AWS S3       |
              | (GPU Workloads)  |          | (Asset Storage)  |
              +------------------+          +------------------+
              | - ComfyUI        |          | - Raw assets     |
              | - Stable Diff    |          | - Processed      |
              | - Blender render |          | - Backups        |
              +------------------+          +------------------+
                                                    |
                                                    v
                                          +------------------+
                                          |   CloudFront     |
                                          |     (CDN)        |
                                          +------------------+
                                          | - Cached assets  |
                                          | - Global edge    |
                                          +------------------+
```

### 7.2 Network Security

```yaml
# Security Groups
ComfyUISecurityGroup:
  Ingress:
    - Port: 8188
      Source: n8n-sg  # Only n8n can access
  Egress:
    - All  # Needs to download models

n8nSecurityGroup:
  Ingress:
    - Port: 5678
      Source: 0.0.0.0/0  # Public webhook access
  Egress:
    - All

VPSSecurityGroup:
  Ingress:
    - Port: 443
      Source: 0.0.0.0/0  # HTTPS only
    - Port: 22
      Source: YOUR_IP/32  # SSH restricted
```

### 7.3 Monitoring Stack

```yaml
# Prometheus + Grafana on VPS
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}

  # Node exporter for VPS metrics
  node-exporter:
    image: prom/node-exporter

  # cAdvisor for container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor
```

---

## Summary: LOCAL vs CLOUD Quick Reference

### LOCAL Tools (Run on Developer Machine)
- Code editors (VS Code, Cursor, Zed)
- Git clients (Fork, lazygit)
- Image editors (GIMP, Krita, Inkscape)
- Audio editors (Audacity, LMMS)
- Video editors (DaVinci Resolve, Kdenlive)
- Pixel art (Aseprite, Pixelorama)
- Game engines (Godot, Unity, Unreal)
- Password managers (KeePassXC, Bitwarden desktop)
- File managers (Everything, DoubleCMD)
- Browser automation (Playwright local runs)
- CLI tools (ripgrep, ffmpeg local)

### CLOUD-VPS Tools (Deploy on Hostinger)
- Container management (Portainer, Dockge)
- LLM servers (Ollama, Open WebUI)
- Workflow automation (n8n, Huginn)
- File sync (SyncThing)
- Backups (Duplicati, restic)
- DNS blocking (Pi-Hole, AdGuard)
- Password server (VaultWarden)
- Wiki/Docs (Wiki.js, BookStack)
- Reverse proxy (Traefik, Caddy)
- Git hosting (Gitea)
- Background removal (Rembg)

### CLOUD-AWS Tools (Heavy GPU/Compute)
- Image generation (ComfyUI, AUTOMATIC1111)
- Video generation (via API calls)
- Voice synthesis (Bark, RVC)
- Image upscaling (Real-ESRGAN)
- Blender rendering
- Large LLM inference
- Video transcoding (FFmpeg at scale)
- Segmentation (Segment Anything)

### CLOUD-API Tools (External Services)
- AI chatbots (Claude, GPT, Gemini)
- Image generation (Pollinations, Flux)
- Video generation (Grok, GeminiGen)
- Voice (ElevenLabs)
- Cloud storage (Google Drive, Mega)
- Stock resources (Unsplash, Pexels)

---

*Document created for Ziggie AI Game Development Ecosystem*
*Last Updated: 2025-12-27*

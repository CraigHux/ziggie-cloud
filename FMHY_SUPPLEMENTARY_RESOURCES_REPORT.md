# FMHY.net Supplementary Resources Report

> **Source**: https://fmhy.net/
> **Date**: 2025-12-27
> **Purpose**: Supplementary report covering Backups, Glossary, Changelogs, and new sections not in previous report
> **Companion To**: FMHY_RESOURCES_COMPREHENSIVE_REPORT.md

---

## Executive Summary

This supplementary report focuses on three specific FMHY sections requested by the user:
1. **Backups** - FMHY backup strategies and mirror sites
2. **Glossary** - Technical terms and definitions (Piracy Glossary)
3. **Changelogs** - Version tracking and change monitoring tools

Additionally, this report identifies **NEW ecosystem tools and resources** not captured in the original report.

---

## Table of Contents

1. [FMHY Backup Resources](#1-fmhy-backup-resources)
2. [The Piracy Glossary](#2-the-piracy-glossary)
3. [Changelog & Version Tracking](#3-changelog--version-tracking)
4. [FMHY Ecosystem Tools (NEW)](#4-fmhy-ecosystem-tools-new)
5. [Self-Hosting FMHY (NEW)](#5-self-hosting-fmhy-new)
6. [Integration Recommendations](#6-integration-recommendations)

---

## 1. FMHY Backup Resources

### Official Backup Sites

| Site | URL | Description | Relevance |
|------|-----|-------------|-----------|
| **FMHY.net** | https://fmhy.net/ | Official main site | **PRIMARY** |
| **fmhyclone** | https://fmhyclone.pages.dev/ | Official Cloudflare Pages mirror | **HIGH** |
| **fmhy.pages.dev** | https://fmhy.pages.dev/ | Official Pages mirror | **HIGH** |

### Community Backup Sites (Unofficial)

| Site | URL | Notes |
|------|-----|-------|
| **fmhy.bid** | https://fmhy.bid/ | Community mirror |
| **fmhy.artistgrid.cx** | https://fmhy.artistgrid.cx/ | Community instance |
| **fmhy.blooketbot.me** | https://fmhy.blooketbot.me/ | Community instance |
| **fmhy.joyconlab.net** | https://fmhy.joyconlab.net/ | Community instance |
| **fmhy.monochrome.tf** | https://fmhy.monochrome.tf/ | Community instance |
| **a-fmhy** | https://a-fmhy.pages.dev/ | AMOLED theme variant |
| **fmhy.xyz** | https://fmhy.xyz/ | Safe-for-work version |
| **fmhy.vercel.app** | https://fmhy.vercel.app/ | Vercel deployment |

### Platform Backups

| Platform | URL | Description |
|----------|-----|-------------|
| **Reddit** | https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index | Original Reddit wiki |
| **Saidit** | https://saidit.net/s/freemediaheckyeah/wiki/index | Alternative platform backup |
| **GitHub Wiki** | https://github.com/fmhy/FMHY/wiki | GitHub wiki backup |
| **Rentry** | https://rentry.co/FMHY | Rentry paste backup |
| **SFW Rentry** | https://rentry.co/piracy | Safe-for-work version |

### Markdown Source Access

| Resource | URL | Description |
|----------|-----|-------------|
| **Markdown Files** | https://github.com/fmhy/FMHYedit/archive/refs/heads/main.zip | Download all markdown |
| **Single-Page MD** | https://api.fmhy.net/single-page | Full wiki as single page |
| **GitHub Source** | https://github.com/fmhy/edit | Source code repository |

### Backup Strategy for Ziggie

**Recommended Approach**:
1. **Primary**: Bookmark https://fmhy.net/
2. **Secondary**: Keep https://fmhyclone.pages.dev/ as fallback
3. **Local**: Clone GitHub repo for offline access: `git clone https://github.com/fmhy/edit.git`
4. **Automated**: Use wget or httrack to mirror the site periodically

```bash
# Clone FMHY for local offline access
git clone https://github.com/fmhy/edit.git fmhy-backup
cd fmhy-backup && pnpm install && pnpm docs:build
```

---

## 2. The Piracy Glossary

**Source**: https://rentry.org/The-Piracy-Glossary

The Piracy Glossary is maintained by the FMHY community and contains essential technical terms for understanding piracy, torrenting, and digital media distribution.

### General Terms

| Term | Definition | Ziggie Relevance |
|------|------------|------------------|
| **2FA** | Two-factor authentication - security layer requiring two verification methods | HIGH - VPS/AWS security |
| **Adblocker** | Browser extension for blocking advertisements | Medium |
| **Archive** | Single file containing multiple files (ZIP, RAR, 7z) | HIGH - Asset distribution |
| **DDL** | Direct Download Link - HTTPS download from server | HIGH - Asset downloads |
| **DNS** | Domain Name System - converts domain names to IPs | HIGH - VPS configuration |
| **Encoding** | Converting data from one format to another | HIGH - Game assets |
| **False Positive** | Antivirus incorrectly flagging benign content | HIGH - Game dev tools |
| **Firewall** | Network security device for traffic control | HIGH - VPS security |
| **FTP** | File Transfer Protocol - client-server file transfers | HIGH - Asset pipeline |
| **IP Address** | Unique numerical label for network devices | HIGH - Networking |
| **VPN** | Virtual Private Network - encrypted connection | HIGH - Remote work |
| **Virtual Machine** | Virtualized computer OS | HIGH - Testing environments |

### Software / Video-game Terms

| Term | Definition | Ziggie Relevance |
|------|------------|------------------|
| **CFW** | Custom Firmware - altered system software | Medium - Console dev |
| **Clean Steam Files (CSF)** | Unmodified game files from Steam | HIGH - Game testing |
| **Crack** | File bypassing DRM protection | Reference only |
| **Denuvo** | Difficult-to-crack DRM type | Reference only |
| **DLC** | Downloadable Content - additional game content | HIGH - Game design |
| **Emulator** | Software running games from different platforms | HIGH - Testing |
| **Homebrew** | Modding/jailbreaking gaming consoles | Medium |
| **Keygen** | Key generator for product licensing | Reference only |
| **Patch** | Small program modifying another program | HIGH - Updates |
| **Repack** | Compressed game with crack included | Reference only |
| **ROM** | Game data file for emulators | HIGH - Emulation testing |
| **Trainer** | Cheat application for game modification | HIGH - Game testing |

### Torrenting Terms

| Term | Definition | Ziggie Relevance |
|------|------------|------------------|
| **BitTorrent** | Decentralized P2P filesharing protocol | Medium |
| **Magnet** | Hyperlink form of torrent file | Medium |
| **Peer** | BitTorrent client instance | Medium |
| **Port Forwarding** | Opening router ports for connectivity | HIGH - VPS config |
| **Seed/Seeding** | Uploading downloaded content | Medium |
| **Seedbox** | Server for torrent download/upload | Medium |
| **Swarm** | All peers sharing same content | Medium |
| **Tracker** | Server coordinating P2P connections | Medium |

### Media Terms

| Term | Definition | Ziggie Relevance |
|------|------------|------------------|
| **Bitrate** | Data processed per unit time | HIGH - Audio/Video quality |
| **Codec** | Specification for converting raw data to images | HIGH - Video encoding |
| **Fansub** | Unofficial fan-made subtitles | Medium |
| **Muxing** | Combining audio/video/subtitle tracks | HIGH - Media processing |
| **Remux** | Container format transfer without quality loss | HIGH - Media workflow |
| **Resolution** | Video detail in pixels (1080p, 4K) | HIGH - Asset quality |
| **Lossless** | Audio preserving all original data | HIGH - Audio quality |
| **Lossy** | Compressed audio with size reduction | HIGH - Audio optimization |

---

## 3. Changelog & Version Tracking

### FMHY Changelog Sites

| Site | URL | Description | Relevance |
|------|-----|-------------|-----------|
| **FMHY Changes** | https://changes.fmhy.bid/ | Tracks Discord #Recently-Added and #Monthly-Update | **HIGH** |
| **FMHY Tracker** | https://fmhy-tracker.pages.dev/ | Tracks GitHub commits (adds, updates, removes) | **HIGH** |
| **GitHub Commits** | https://github.com/fmhy/edit/commits/main/ | Raw commit history | Medium |

### Version Tracking Tools (From Developer Tools)

| Tool | Description | URL | Relevance |
|------|-------------|-----|-----------|
| **Git Cliff** | Changelog generator from commits | https://git-cliff.org | **HIGH** |
| **commitlint** | Lint commit messages for consistency | https://commitlint.js.org/ | **HIGH** |
| **pre-commit** | Git hooks manager | https://pre-commit.com/ | **HIGH** |
| **Semantic Release** | Automated version management | https://semantic-release.gitbook.io/ | **HIGH** |

### Recommended Changelog Strategy for Ziggie

1. **Adopt Conventional Commits**: Use standard commit message format
2. **Use Git Cliff**: Auto-generate changelogs from commits
3. **Integrate pre-commit hooks**: Enforce commit message standards
4. **Track Dependencies**: Monitor upstream changes (Unity, Godot, ComfyUI)

```bash
# Install Git Cliff for changelog generation
cargo install git-cliff

# Generate changelog
git cliff -o CHANGELOG.md

# Or use npm equivalent
npm install -g conventional-changelog-cli
conventional-changelog -p angular -i CHANGELOG.md -s
```

---

## 4. FMHY Ecosystem Tools (NEW)

These are FMHY ecosystem tools NOT covered in the original report.

### FMHY-Specific Tools

| Tool | URL | Description | Relevance |
|------|-----|-------------|-----------|
| **FMHY SafeGuard** | https://github.com/fmhy/FMHY-SafeGuard | Browser extension for unsafe site warnings | **HIGH** - Security |
| **FMHY Bookmarks** | https://github.com/fmhy/bookmarks | Importable browser bookmarks | Medium |
| **FMHY Startpage** | https://fmhy.net/startpage | Custom homepage with quick links | Medium |
| **snowbin (Pastes)** | https://pastes.fmhy.net | FMHY paste service | Medium |
| **SearXNG Instance** | https://searx.fmhy.net/ | Privacy-focused meta search | **HIGH** - Research |

### Search & Discovery

| Tool | URL | Description | Relevance |
|------|-----|-------------|-----------|
| **FMHY Search** | https://fmhy.net/posts/search | Full-text search across FMHY | **HIGH** |
| **Site Hunting Guide** | https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/find-new-sites/ | Guide for finding new resources | Medium |

### Community Resources

| Resource | URL | Description |
|----------|-----|-------------|
| **Discord** | Via FMHY wiki | Community chat and updates |
| **Reddit** | https://reddit.com/r/FREEMEDIAHECKYEAH | Community discussion |
| **Monthly Posts** | https://fmhy.net/posts | Monthly update summaries |
| **FAQ** | https://fmhy.net/other/FAQ | Frequently asked questions |
| **Contributing Guide** | https://fmhy.net/other/contributing | How to contribute to FMHY |

---

## 5. Self-Hosting FMHY (NEW)

FMHY can be self-hosted for offline access or custom instances.

### Docker Deployment

```bash
# Clone and run FMHY with Docker
git clone https://github.com/fmhy/edit.git
cd edit
sudo docker compose up --build
# Runs on port 4173
```

### Manual Deployment

**Requirements**:
- Git
- Node.js 21.7.3+
- pnpm 9.12.2+

```bash
# Clone repository
git clone https://github.com/fmhy/edit.git
cd edit

# Install dependencies
pnpm install

# Development mode (http://localhost:5173)
pnpm docs:dev

# Production build
pnpm docs:build
pnpm docs:preview
```

### Nix Flake (for NixOS users)

```bash
git clone https://github.com/fmhy/edit.git
cd edit
nix flake update
nix develop
# Make changes, then exit
```

### API Deployment (Cloudflare Workers)

For full feedback functionality:

```bash
# Create KV namespace
npx wrangler kv:namespace create STORAGE

# Build and deploy API
pnpm api:build
pnpm api:deploy
```

**Environment Variables**:
- `FMHY_BUILD_NSFW` - Enable NSFW sidebar
- `FMHY_BUILD_API` - Enable API component
- `WEBHOOK_URL` - Discord webhook for feedback

### Ziggie Self-Hosting Strategy

**Recommended**: Run local FMHY instance on Hostinger VPS for offline reference:

```bash
# On Hostinger VPS
docker run -d -p 4173:4173 --name fmhy-local fmhy-custom
```

---

## 6. Integration Recommendations

### Immediate Actions (Week 1)

| Action | Tool/Resource | Purpose |
|--------|---------------|---------|
| **Clone FMHY** | `git clone https://github.com/fmhy/edit.git` | Local offline backup |
| **Install SafeGuard** | https://github.com/fmhy/FMHY-SafeGuard | Browser security |
| **Bookmark Changes** | https://changes.fmhy.bid/ | Track new resources |
| **Bookmark Tracker** | https://fmhy-tracker.pages.dev/ | Track link changes |

### Short-Term (Month 1)

| Action | Tool/Resource | Purpose |
|--------|---------------|---------|
| **Setup Git Cliff** | `cargo install git-cliff` | Automated changelogs |
| **Configure pre-commit** | https://pre-commit.com/ | Commit standards |
| **SearXNG Bookmark** | https://searx.fmhy.net/ | Privacy search |

### Medium-Term (Quarter 1)

| Action | Tool/Resource | Purpose |
|--------|---------------|---------|
| **Self-host FMHY** | Docker on Hostinger | Offline access |
| **RSS Feed Setup** | GitHub commits RSS | Auto-notifications |
| **Backup Automation** | wget/httrack script | Regular mirrors |

---

## Glossary Quick Reference Card

### Most Relevant Terms for Ziggie

| Term | Quick Definition |
|------|------------------|
| **Archive** | ZIP/RAR/7z compressed file bundle |
| **Bitrate** | Data quality (higher = better) |
| **Codec** | Video encoding format (H.264, H.265) |
| **DDL** | Direct download via HTTPS |
| **Encoding** | Format conversion |
| **Lossless** | Full quality audio (FLAC) |
| **Lossy** | Compressed audio (MP3, AAC) |
| **Muxing** | Combining tracks into container |
| **Port Forwarding** | Opening router/firewall ports |
| **Remux** | Lossless container conversion |
| **Resolution** | Pixel dimensions (1080p, 4K) |
| **Seed** | Upload completed content |
| **Transcode** | Convert between formats |
| **VPN** | Encrypted network tunnel |

---

## Sources & References

- **FMHY Backups**: https://fmhy.net/other/backups
- **Piracy Glossary**: https://rentry.org/The-Piracy-Glossary
- **Changelog Sites Post**: https://fmhy.net/posts/changelog-sites
- **Self-Hosting Guide**: https://fmhy.net/other/selfhosting
- **FMHY GitHub**: https://github.com/fmhy/edit

---

## Appendix: FMHY Site Structure

```
FMHY Categories (Sidebar Navigation):
├── Beginners Guide
├── Posts (Monthly updates)
├── Contribute
│
├── Wiki
│   ├── Adblocking / Privacy
│   ├── Artificial Intelligence
│   ├── Movies / TV / Anime
│   ├── Music / Podcasts / Radio
│   ├── Gaming / Emulation
│   ├── Books / Comics / Manga
│   ├── Downloading
│   ├── Torrenting
│   ├── Educational
│   ├── Android / iOS
│   ├── Linux / macOS
│   ├── Non-English
│   └── Miscellaneous
│
├── Tools
│   ├── System Tools
│   ├── File Tools
│   ├── Internet Tools
│   ├── Social Media Tools
│   ├── Text Tools
│   ├── Gaming Tools
│   ├── Image Tools
│   ├── Video Tools
│   ├── Audio Tools
│   ├── Educational Tools
│   └── Developer Tools
│
└── More
    ├── NSFW (external)
    ├── Unsafe Sites
    └── Storage
```

---

*Supplementary Report for Ziggie AI Game Development Ecosystem*
*Complements: FMHY_RESOURCES_COMPREHENSIVE_REPORT.md*
*Last Updated: 2025-12-27*

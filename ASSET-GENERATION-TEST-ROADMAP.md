# Asset Generation Test Roadmap
## Meow Ping RTS - AWS Foundation Validation

> **Created**: 2025-12-24
> **Purpose**: Validate AWS infrastructure through practical asset generation workflow
> **Status**: Phase 1 - Initial Testing

---

## Executive Summary

This roadmap tests the AWS foundation (Phase 7.5 complete) by generating game assets for Meow Ping RTS. The workflow validates:
- S3 storage for generated assets
- Bedrock LLM for prompt enhancement
- Lambda monitoring for GPU instances (when launched)
- CloudWatch events for automation

---

## Test Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ASSET GENERATION PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [1] PROMPT CREATION                                             │
│      │                                                           │
│      ├─> Manual (ImagineArt UI)                                 │
│      │   └─> Nano Banana model (selected)                       │
│      │                                                           │
│      └─> AI-Enhanced (Bedrock Nova)                             │
│          └─> bedrock-game-content.ps1                           │
│                                                                  │
│  [2] IMAGE GENERATION                                            │
│      │                                                           │
│      ├─> ImagineArt (Free, Unlimited)                           │
│      │   └─> Manual download to local                           │
│      │                                                           │
│      └─> ComfyUI on AWS GPU (Future)                            │
│          └─> Auto-save to S3                                    │
│                                                                  │
│  [3] ASSET STORAGE                                               │
│      │                                                           │
│      └─> S3: ziggie-assets-prod                                 │
│          ├─> game-assets/concepts/                              │
│          ├─> game-assets/sprites/                               │
│          └─> generated/raw/                                     │
│                                                                  │
│  [4] PROCESSING PIPELINE                                         │
│      │                                                           │
│      ├─> Background Removal                                     │
│      ├─> 8-Direction Sprite Rendering                           │
│      └─> Sprite Sheet Assembly                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Manual Generation Test (Current)

### Objective
Generate first character asset using ImagineArt to establish visual reference.

### Steps

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 1.1 | Create T-Stand prompt | This document | Prompt text |
| 1.2 | Generate in ImagineArt | Nano Banana | PNG image |
| 1.3 | Download to local | Browser | C:\Ziggie\assets\concepts\ |
| 1.4 | Upload to S3 | AWS CLI | s3://ziggie-assets-prod/game-assets/concepts/ |
| 1.5 | Verify S3 storage | AWS CLI | Confirmation |

### Test Character: Salvage Warrior (Desert Wastes)

**Rationale**:
- COMMON rarity = foundational unit for gameplay
- Desert Wastes = Phase 1 priority faction
- Simple design = good baseline for style validation

---

## Phase 2: Bedrock Prompt Enhancement

### Objective
Use Bedrock Nova to enhance and vary prompts programmatically.

### Steps

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 2.1 | Base prompt input | Manual | Prompt text |
| 2.2 | Enhance with Bedrock | bedrock-chat.ps1 | Enhanced prompt |
| 2.3 | Generate variants | bedrock-game-content.ps1 | 5 prompt variations |
| 2.4 | Batch generate | ImagineArt | 5 character variants |

### Example Command
```powershell
cd C:\Ziggie\aws-config
.\bedrock-chat.ps1 -Prompt "Enhance this game art prompt for a dark fantasy cat warrior: [base prompt]" -Model nova-pro
```

---

## Phase 3: S3 Integration Test

### Objective
Validate S3 bucket for asset storage and retrieval.

### Steps

| Step | Action | Command |
|------|--------|---------|
| 3.1 | Upload concept | `aws s3 cp concept.png s3://ziggie-assets-prod/game-assets/concepts/` |
| 3.2 | List assets | `aws s3 ls s3://ziggie-assets-prod/game-assets/ --recursive` |
| 3.3 | Download test | `aws s3 cp s3://ziggie-assets-prod/game-assets/concepts/concept.png ./test/` |
| 3.4 | Verify versioning | `aws s3api list-object-versions --bucket ziggie-assets-prod --prefix game-assets/` |

---

## Phase 4: GPU Spot Instance Test (Optional)

### Objective
Launch ComfyUI on AWS GPU for automated generation.

### Prerequisites
- Generated concept art approved
- S3 storage validated
- SSH key ready (ziggie-gpu-key.pem)

### Steps

| Step | Action | Command |
|------|--------|---------|
| 4.1 | Launch GPU | `.\launch-gpu.ps1` |
| 4.2 | Wait for bootstrap | ~5 minutes |
| 4.3 | Access ComfyUI | `http://<public-ip>:8188` |
| 4.4 | Generate asset | ComfyUI workflow |
| 4.5 | Verify auto-shutdown | Check Lambda logs |
| 4.6 | Terminate instance | `.\stop-gpu.ps1` |

**Cost Estimate**: ~$0.18/hour for g4dn.xlarge

---

## Success Criteria

| Test | Criteria | Status |
|------|----------|--------|
| ImagineArt generation | Image matches style guide | Pending |
| S3 upload | File accessible via CLI | Pending |
| S3 versioning | Multiple versions tracked | Pending |
| Bedrock enhancement | Coherent prompt output | Pending |
| GPU launch (optional) | Instance running with public IP | Pending |
| ComfyUI access (optional) | UI accessible in browser | Pending |

---

## Asset Specifications Reference

### Character Requirements
- **Pose**: T-Stand (arms extended horizontally at shoulder height)
- **View**: Front-facing, full body visible
- **Features**: Cat ears visible, glowing cat eyes (vertical pupils), tail visible
- **Style**: Dark fantasy, battle-worn aesthetic (NOT cartoon)
- **Lighting**: 45-degree from top-right
- **Background**: Solid color (non-clashing with faction colors)

### Background Color Selection
To avoid conflicts with faction colors:

| Faction | Primary Color | Avoid in BG |
|---------|---------------|-------------|
| Desert Wastes | Tan #D4A574 | Orange, Yellow, Brown |
| Volcanic Lands | Charcoal #3D3D3D | Black, Dark Gray |
| Frozen Ruins | Ice Blue #A8D8EA | Light Blue, White |
| Jungle Overgrowth | Forest Green #2A5A2A | Green shades |
| Neon Megacity | Dark Gray #2A2A3A | Gray, Cyan |

**Recommended Background**: Solid Blue #0066FF or Magenta #FF00FF
- High contrast with all faction colors
- Easy chroma-key removal
- Standard game art practice

---

## Prompt Template Structure

```
[SUBJECT] + [POSE] + [VIEW] + [STYLE] + [DETAILS] + [BACKGROUND] + [TECHNICAL]
```

### Components

| Component | Purpose | Example |
|-----------|---------|---------|
| SUBJECT | Character identity | "Cat warrior salvage soldier" |
| POSE | Body position | "T-pose, arms extended horizontally" |
| VIEW | Camera angle | "front view, full body" |
| STYLE | Art direction | "dark fantasy, battle-worn" |
| DETAILS | Specific features | "glowing eyes, visible tail" |
| BACKGROUND | Isolation | "solid blue background #0066FF" |
| TECHNICAL | Generation hints | "game asset, character concept" |

---

## Next Steps After Phase 1

1. **Evaluate generated asset** against style guide
2. **Iterate prompt** if needed based on results
3. **Generate faction variants** (5 color schemes)
4. **Process for game** (background removal, sprite sheets)
5. **Upload to S3** for permanent storage
6. **Document successful prompts** in prompt library

---

*Roadmap created for Meow Ping RTS asset generation testing*
*AWS Foundation Phase 7.5 - Validation Stage*

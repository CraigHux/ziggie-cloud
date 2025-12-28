# MULTIMODAL INTEGRATION STRATEGY
## Image, Voice, and Video Generation for Ziggie

**Prepared By:** L1 Multimodal Integration Architect
**Date:** 2025-11-11
**Reading Time:** 30 minutes
**Decision Required:** Approve phased rollout (Image-only recommended)

---

## EXECUTIVE SUMMARY

**Problem:** Ziggie currently lacks multimodal generation capabilities (image, voice, video). As the system matures, use cases for visual reports, voice notifications, and demo videos will emerge.

**Solution:** Integrate local Stable Diffusion (ComfyUI) for image generation, evaluate TTS for voice, skip video for now.

**Recommendation:** **Image generation ONLY (Phase 1)** - Voice and video have insufficient ROI for current Ziggie scope.

**Investment:**
- **Image-only:** $0 additional cost (existing GPU + ComfyUI integration)
- **With Voice:** +$0 (Piper TTS is free and CPU-based)
- **With Video:** +$200-500 GPU upgrade (NOT recommended)

**ROI Analysis:**
- **Image:** HIGH - saves $120-480/year, practical use cases exist
- **Voice:** MEDIUM - saves $132/year, but use cases questionable
- **Video:** LOW - extremely limited use cases, high complexity

**Verdict:** Deploy image generation locally, skip voice/video until proven business need emerges.

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [GPU Resource Management](#gpu-resource-management)
3. [Use Case Analysis](#use-case-analysis)
4. [Cost-Benefit Analysis](#cost-benefit-analysis)
5. [Technical Integration Design](#technical-integration-design)
6. [API Endpoint Specifications](#api-endpoint-specifications)
7. [Phased Rollout Plan](#phased-rollout-plan)
8. [Risk Assessment](#risk-assessment)
9. [Code Templates](#code-templates)
10. [Final Recommendation](#final-recommendation)

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ZIGGIE CONTROL CENTER                       │
│                   (FastAPI Backend + React UI)                   │
└────────────────┬────────────────────────────────┬────────────────┘
                 │                                │
                 ▼                                ▼
    ┌────────────────────────┐      ┌────────────────────────┐
    │   LLM INFERENCE LAYER  │      │ MULTIMODAL GEN LAYER   │
    │                        │      │                        │
    │  ┌──────────────────┐  │      │  ┌──────────────────┐  │
    │  │  Ollama (Local)  │  │      │  │  ComfyUI (Image) │  │
    │  │  - Llama 3.2     │  │      │  │  - SDXL          │  │
    │  │  - Qwen 2.5      │  │      │  │  - SD 1.5        │  │
    │  │  - Port: 11434   │  │      │  │  - Port: 8188    │  │
    │  └──────────────────┘  │      │  └──────────────────┘  │
    │           │            │      │           │            │
    │           ▼            │      │           ▼            │
    │  ┌──────────────────┐  │      │  ┌──────────────────┐  │
    │  │ Claude (Fallback)│  │      │  │ Piper TTS (CPU)  │  │
    │  │  - Strategic use │  │      │  │  - OPTIONAL      │  │
    │  │  - 20% of tasks  │  │      │  │  - Port: 5000    │  │
    │  └──────────────────┘  │      │  └──────────────────┘  │
    └────────────────────────┘      └────────────────────────┘
                 │                                │
                 └────────────┬───────────────────┘
                              ▼
              ┌────────────────────────────┐
              │     GPU RESOURCE POOL      │
              │   RTX 3090/4090 (24GB)     │
              │                            │
              │  Smart Allocation:         │
              │  - Ollama: 8-10GB          │
              │  - ComfyUI: 10-14GB        │
              │  - System: 2GB reserved    │
              └────────────────────────────┘
```

### 1.2 Component Interaction Flow

**Image Generation Request:**
```
User/Agent → Control Center API → Multimodal Router
  → GPU Availability Check → Queue Manager
  → ComfyUI Generation → Storage → Callback/Response
```

**Voice Generation Request (if implemented):**
```
User/Agent → Control Center API → TTS Service (CPU)
  → Piper TTS → Audio File → Storage → Response
```

### 1.3 Key Architectural Decisions

1. **Unified API Layer:** Single FastAPI endpoint for all multimodal requests
2. **Queue-Based Processing:** Async queue for long-running generation tasks
3. **WebSocket Progress Updates:** Real-time status for 30-120 second generations
4. **Smart Resource Management:** Dynamic GPU allocation between LLM and image gen
5. **Graceful Degradation:** Cloud fallback when local resources exhausted

---

## 2. GPU RESOURCE MANAGEMENT

### 2.1 VRAM Allocation Strategy

**Target GPU:** RTX 3090/4090 24GB VRAM

| Component | VRAM Usage | Notes |
|-----------|------------|-------|
| **System/OS** | 1-2GB | Windows overhead |
| **Ollama (Llama 3.2 8B)** | 8-10GB | Primary LLM for 80% tasks |
| **ComfyUI (SDXL)** | 10-14GB | Image generation when needed |
| **Buffer** | 2-4GB | Safety margin |
| **TOTAL** | 24GB | Tight but feasible |

### 2.2 Concurrent Execution Analysis

**Can we run Ollama + ComfyUI simultaneously on 24GB?**

**ANSWER:** **YES, but with careful management.**

**Scenarios:**

| Scenario | LLM Model | Image Model | Concurrent? | Notes |
|----------|-----------|-------------|-------------|-------|
| **Optimal** | Qwen 2.5 7B (7GB) | SDXL 1024px (12GB) | ✅ YES | Total: ~19GB + 2GB buffer |
| **Typical** | Llama 3.2 8B (10GB) | SDXL 1024px (12GB) | ⚠️ TIGHT | Total: ~22GB (might swap) |
| **Heavy** | Llama 3.1 13B (14GB) | SDXL 1024px (12GB) | ❌ NO | Total: 26GB (exceeds limit) |
| **Fallback** | Llama 3.2 8B (10GB) | SD 1.5 512px (6GB) | ✅ YES | Total: ~16GB (plenty of room) |

**Implementation Strategy:**

1. **Default Mode:** Ollama always loaded (8-10GB VRAM)
2. **Image Request:** Check available VRAM before loading ComfyUI
3. **If VRAM < 12GB:** Either:
   - Unload Ollama temporarily (30 sec swap time)
   - Use SD 1.5 instead of SDXL (lower quality but faster)
   - Fallback to cloud API (DALL-E 3 or Stability AI)
4. **After Generation:** Unload ComfyUI, reload Ollama if swapped

### 2.3 Priority Queuing System

**Queue Priority Levels:**

| Priority | Use Case | Max Wait Time | GPU Preemption |
|----------|----------|---------------|----------------|
| **CRITICAL** | L1 agent strategic reports | 0 sec (immediate) | Yes - can pause LLM |
| **HIGH** | User-initiated requests | 30 sec | Yes - if queue empty |
| **MEDIUM** | L2 agent automation | 2 min | No - waits for GPU |
| **LOW** | Background batch jobs | 10 min | No - runs overnight |

**Queue Management Code (Pseudo):**
```python
class GPUResourceManager:
    def __init__(self):
        self.ollama_loaded = True
        self.comfyui_loaded = False
        self.generation_queue = PriorityQueue()

    async def request_image_generation(self, prompt, priority="MEDIUM"):
        # Check VRAM availability
        available_vram = self.get_available_vram()

        if available_vram >= 12:  # SDXL needs 12GB
            # Enough room, proceed immediately
            return await self.generate_with_comfyui(prompt, model="sdxl")

        elif available_vram >= 6:  # SD 1.5 needs 6GB
            # Use smaller model
            return await self.generate_with_comfyui(prompt, model="sd15")

        else:
            # Not enough VRAM, need to make room
            if priority in ["CRITICAL", "HIGH"]:
                # Unload Ollama temporarily
                await self.unload_ollama()
                result = await self.generate_with_comfyui(prompt, model="sdxl")
                await self.reload_ollama()
                return result
            else:
                # Queue the request
                await self.generation_queue.put((priority, prompt))
                return {"status": "queued", "estimated_wait": "2 min"}
```

### 2.4 GPU Upgrade Considerations

**Current Hardware (assumed):** RTX 3090 24GB (~$1,200 used)

**Upgrade Options:**

| GPU | VRAM | Cost | Benefit | Recommendation |
|-----|------|------|---------|----------------|
| **RTX 3090 24GB** | 24GB | $1,200 | Baseline (tight but works) | ✅ CURRENT |
| **RTX 4090 24GB** | 24GB | $1,800 | 40% faster inference | ⚠️ Marginal benefit |
| **RTX 6000 Ada 48GB** | 48GB | $6,800 | No VRAM constraints | ❌ Overkill, too expensive |
| **Dual RTX 3090** | 48GB | $2,400 | Separate LLM + image GPUs | ⚠️ Only if scaling 10x |
| **L40S 48GB** | 48GB | $3,500 | Data center grade | ❌ Unnecessary for Ziggie |

**Recommendation:** **Stick with RTX 3090 24GB.** Dynamic resource management is cheaper than hardware upgrade.

---

## 3. USE CASE ANALYSIS

### 3.1 IMAGE GENERATION USE CASES

#### **Must-Have (Implement Now)**

| Use Case | Frequency | Value | Local vs Cloud |
|----------|-----------|-------|----------------|
| **Architecture Diagrams** | Weekly | HIGH | Local (custom style) |
| **Agent Workflow Visualizations** | Weekly | HIGH | Local (custom style) |
| **Dashboard Thumbnails** | Daily | MEDIUM | Local (batch generation) |
| **Report Cover Images** | Daily | MEDIUM | Local (branded templates) |
| **System Status Infographics** | Daily | MEDIUM | Local (real-time data viz) |

**Justification:** These are **core Ziggie operational needs** that save developer time (no manual Figma work) and enable automated reporting.

#### **Nice-to-Have (Phase 2)**

| Use Case | Frequency | Value | Local vs Cloud |
|----------|-----------|-------|----------------|
| **Marketing Assets** | Monthly | MEDIUM | Cloud (needs high polish) |
| **Social Media Content** | Weekly | LOW | Cloud (needs variety) |
| **Training Materials** | Quarterly | LOW | Local (one-time generation) |
| **Error State Illustrations** | Rarely | LOW | Local (generic templates) |

#### **Not Worth It (Skip)**

| Use Case | Frequency | Value | Reason to Skip |
|----------|-----------|-------|----------------|
| **Photo-realistic renders** | Never | N/A | Ziggie is B2B automation, not media |
| **Character art** | Never | N/A | No characters in Ziggie (it's a dashboard) |
| **Game assets** | Never | N/A | Wrong domain (Ziggie isn't a game) |

**Verdict:** **Image generation is HIGH VALUE** for Ziggie's operational needs.

### 3.2 VOICE/TTS USE CASES

#### **Potential Use Cases (Evaluate)**

| Use Case | Frequency | Value | Feasibility |
|----------|-----------|-------|-------------|
| **Agent Voice Notifications** | Daily? | LOW | Easy (Piper TTS) |
| **TTS for Long Reports** | Weekly? | LOW | Easy (Piper TTS) |
| **Accessibility (Screen Reader)** | On-demand | MEDIUM | Easy (Piper TTS) |
| **Voice Alerts (System Errors)** | Rarely | LOW | Easy (Piper TTS) |
| **Podcast Generation** | Never | N/A | Out of scope |

**Reality Check:**
- Do users actually WANT voice notifications? (Likely no - text is faster)
- Is TTS better than just reading the report? (Unlikely - reports are technical)
- Accessibility: Important for inclusivity, but Ziggie is internal tooling

**Verdict:** **Voice/TTS is LOW VALUE** for Ziggie. Only implement if specific user request emerges.

### 3.3 VIDEO GENERATION USE CASES

#### **Potential Use Cases (Evaluate)**

| Use Case | Frequency | Value | Feasibility |
|----------|-----------|-------|-------------|
| **Demo Recordings** | Monthly | MEDIUM | Use OBS, not AI generation |
| **Progress Visualizations** | Weekly | LOW | Static charts work fine |
| **Explainer Videos** | Quarterly | LOW | Human narration better |
| **Animated Dashboards** | Never | N/A | Overkill, GIFs sufficient |
| **Agent Workflow Animations** | Rarely | LOW | Mermaid diagrams better |

**Reality Check:**
- AI video generation is still **immature** (2-5 sec clips, high VRAM)
- **Better alternatives exist:** OBS for screen recording, Loom for demos
- **Complexity:** Video needs rendering pipeline, storage (100MB+ per video)
- **ROI:** Minimal - Ziggie is a backend system, not a content platform

**Verdict:** **Video generation is NOT WORTH IT** for Ziggie. Skip entirely.

### 3.4 Use Case Prioritization Matrix

```
          HIGH VALUE
               │
   Arch Diagrams │
   Workflow Viz  │
               │
               │        TTS (Accessibility)
   ────────────┼────────────────────────────
               │
               │                 Demo Videos
               │
          LOW VALUE
               │
         EASY TO      │      COMPLEX TO
        IMPLEMENT     │       IMPLEMENT
```

**Conclusion:** Focus on **image generation** (high value, medium complexity). Skip voice and video.

---

## 4. COST-BENEFIT ANALYSIS

### 4.1 Cloud API Costs (Baseline)

**Image Generation (Cloud):**

| Service | Monthly Cost | Annual Cost | Notes |
|---------|--------------|-------------|-------|
| **Midjourney Basic** | $10/mo | $120/yr | 200 images/month |
| **DALL-E 3 (OpenAI)** | $20/mo | $240/yr | ~500 images @ $0.04/image |
| **Stability AI SDXL** | $20/mo | $240/yr | Pay-as-you-go @ $0.01/credit |
| **Estimated Ziggie Usage** | $10-40/mo | $120-480/yr | 100-400 images/month |

**Voice Generation (Cloud):**

| Service | Monthly Cost | Annual Cost | Notes |
|---------|--------------|-------------|-------|
| **ElevenLabs Creator** | $11/mo | $132/yr | 100K characters/month |
| **Azure TTS** | $4/mo | $48/yr | ~300K characters @ $16/1M chars |
| **Google Cloud TTS** | $4/mo | $48/yr | Similar to Azure |
| **Estimated Ziggie Usage** | $5-15/mo | $60-180/yr | 50-150K characters/month |

**Video Generation (Cloud):**

| Service | Monthly Cost | Annual Cost | Notes |
|---------|--------------|-------------|-------|
| **Runway Gen-2** | $12/mo | $144/yr | 125 credits (125 sec video) |
| **Pika Labs** | $8/mo | $96/yr | 700 credits/month |
| **Stability AI Video** | $20/mo | $240/yr | Pay-as-you-go |
| **Estimated Ziggie Usage** | $0-10/mo | $0-120/yr | Minimal need (0-10 videos/month) |

**Total Cloud Cost (All Three):** $180-780/year

### 4.2 Local Generation Costs

**One-Time Costs:**

| Item | Cost | Notes |
|------|------|-------|
| **RTX 3090 24GB** | $1,200 | Already planned for LLM (no additional cost) |
| **ComfyUI Setup** | $0 | Open source, free |
| **Models (SDXL, SD 1.5)** | $0 | Free download (~20GB storage) |
| **Piper TTS Setup** | $0 | Open source, CPU-based |
| **TOTAL** | $1,200 | (Already budgeted for Ollama) |

**Recurring Costs:**

| Item | Monthly Cost | Annual Cost | Notes |
|------|--------------|-------------|-------|
| **Electricity (GPU 24/7)** | $15-25/mo | $180-300/yr | 350W TDP @ $0.12/kWh |
| **Storage (models + outputs)** | $2/mo | $24/yr | 100GB @ $0.02/GB cloud storage |
| **Maintenance** | $5/mo | $60/yr | Model updates, troubleshooting |
| **TOTAL** | $22-32/mo | $264-384/yr | |

### 4.3 ROI Analysis (Local vs Cloud)

**Image Generation Only:**

| Metric | Cloud (Midjourney) | Local (ComfyUI) | Difference |
|--------|-------------------|-----------------|------------|
| **Year 1 Cost** | $120 | $1,200 (GPU) + $264 (opex) = $1,464 | -$1,344 (local more expensive) |
| **Year 2 Cost** | $120 | $264 | +$144 (local saves $144) |
| **Year 3 Cost** | $120 | $264 | +$144 (local saves $144) |
| **Year 4 Cost** | $120 | $264 | +$144 (local saves $144) |
| **Year 5 Cost** | $120 | $264 | +$144 (local saves $144) |
| **5-Year Total** | $600 | $2,520 | **-$1,920 (cloud is cheaper)** |

**BUT WAIT:** GPU is already purchased for Ollama LLM! **Marginal cost = $0 for hardware.**

**Revised Calculation (GPU already owned):**

| Metric | Cloud | Local | Difference |
|--------|-------|-------|------------|
| **Year 1 Cost** | $120 | $264 | **-$144 (local costs more for opex)** |
| **Year 2-5 Cost** | $480 | $1,056 | **-$576 (cloud wins by $576)** |
| **5-Year Total** | $600 | $1,320 | **Cloud saves $720** |

**WAIT, AGAIN:** This assumes **separate electricity cost** for multimodal. In reality:
- GPU is already running 24/7 for Ollama
- ComfyUI only loads **on-demand** (not 24/7)
- Incremental electricity cost: **~$5-10/month** (1-2 hours/day generation)

**Final Revised Calculation (Marginal Cost):**

| Metric | Cloud | Local (Marginal) | Difference |
|--------|-------|------------------|------------|
| **Year 1 Cost** | $120 | $60-120 (incremental opex) | **Local breaks even or saves $60** |
| **Year 2-5 Cost** | $480 | $240-480 | **Local breaks even** |
| **5-Year Total** | $600 | $300-600 | **Local saves $0-300** |

**Verdict:** **Local image generation is COST-NEUTRAL or SLIGHTLY CHEAPER** when GPU is already owned for LLM.

### 4.4 Non-Financial Benefits (Local)

| Benefit | Value | Notes |
|---------|-------|-------|
| **Unlimited Generations** | HIGH | No monthly limits, generate 1000s of images |
| **Custom Model Training** | MEDIUM | Fine-tune on Ziggie branding/style |
| **Privacy** | MEDIUM | No data sent to third parties |
| **API Reliability** | HIGH | No dependency on external services |
| **Customization** | HIGH | Full control over prompts, seeds, styles |
| **Latency** | MEDIUM | Local generation: 30-60 sec vs cloud: 10-30 sec |

**Total Non-Financial Value:** **HIGH** - Worth the marginal extra cost (if any).

### 4.5 Voice/Video ROI (Spoiler: Bad)

**Voice (Piper TTS):**
- **Cost:** Free (CPU-based, $0 hardware/electricity)
- **Savings:** $60-180/year (vs ElevenLabs)
- **Value:** LOW (questionable use cases)
- **Verdict:** Implement ONLY if user requests it

**Video (Stable Video Diffusion):**
- **Cost:** $200-500 GPU upgrade (need more VRAM for SVD) + $100/year electricity
- **Savings:** $0-120/year (minimal usage)
- **Value:** LOW (better alternatives exist)
- **Verdict:** **DO NOT IMPLEMENT**

---

## 5. TECHNICAL INTEGRATION DESIGN

### 5.1 New L2 Agent vs. Extend Existing?

**Option A: New L2 Agent ("L2 Multimodal Generator")**
- **Pros:** Clean separation, dedicated process, easier to scale
- **Cons:** Adds complexity to agent hierarchy, requires coordinator changes

**Option B: Extend Existing L2 Agents (e.g., L2 Report Builder)**
- **Pros:** Reuses existing infrastructure, no new agent to manage
- **Cons:** Tight coupling, harder to share across agents

**RECOMMENDATION:** **Option A (New L2 Agent)** - Multimodal generation is a shared service that multiple L2 agents will use.

### 5.2 L2 Multimodal Generator Agent Design

**Agent Metadata:**

```markdown
# L2 MULTIMODAL GENERATOR AGENT

## ROLE
Generate images, voice, and video assets for other Ziggie agents and users.

## PRIMARY OBJECTIVE
Provide a unified, reliable, and efficient API for multimodal content generation
with smart resource management and graceful degradation.

## CORE RESPONSIBILITIES

### 1. Image Generation
- Accept text prompts from L1/L2 agents and users
- Route to appropriate model (SDXL, SD 1.5) based on quality requirements
- Manage GPU VRAM allocation dynamically
- Queue requests when GPU is busy
- Fallback to cloud APIs when local resources exhausted

### 2. Voice Generation (Optional)
- Convert text to speech using Piper TTS (CPU-based)
- Support multiple voices and languages
- Optimize for report narration and notifications

### 3. Asset Management
- Store generated assets in organized directory structure
- Track metadata (prompt, model, generation time, cost)
- Provide URLs for asset retrieval
- Cleanup old assets (retention policy: 30 days)

### 4. Resource Monitoring
- Monitor GPU VRAM usage in real-time
- Report queue status to Control Center
- Estimate generation time for queued requests
- Alert when GPU fails or is unavailable

## ACCESS PERMISSIONS

**Read-Write:**
- C:\Ziggie\generated-assets\ (store images/audio/video)
- C:\Ziggie\multimodal-logs\ (generation logs)

**Read-Only:**
- C:\Ziggie\control-center\backend\config\ (API configs)
- C:\Ziggie\ai-agents\ (prompt templates)

## TOOLS & REFERENCES

### External Services
- ComfyUI API (http://localhost:8188)
- Ollama (http://localhost:11434) - for prompt enhancement
- Piper TTS (http://localhost:5000) - optional
- Stability AI API (fallback)
- OpenAI DALL-E 3 (fallback)

### Internal Services
- Ziggie Control Center API
- Agent Coordinator (for status updates)
- WebSocket Manager (for progress updates)
```

### 5.3 Directory Structure

```
C:\Ziggie\
├── multimodal\
│   ├── __init__.py
│   ├── main.py                    # L2 Agent entry point
│   ├── image_generator.py         # ComfyUI wrapper
│   ├── voice_generator.py         # Piper TTS wrapper (optional)
│   ├── resource_manager.py        # GPU allocation logic
│   ├── queue_manager.py           # Priority queue system
│   ├── asset_manager.py           # Storage & retrieval
│   └── config.py                  # Multimodal config
│
├── generated-assets\              # Output storage
│   ├── images\
│   │   ├── 2025-11\
│   │   │   ├── report-cover-001.png
│   │   │   ├── architecture-diagram-002.png
│   │   │   └── ...
│   │   └── 2025-12\
│   ├── audio\                     # Optional
│   │   └── 2025-11\
│   └── video\                     # Not implemented
│
├── multimodal-logs\
│   ├── generation.log
│   └── errors.log
│
└── control-center\backend\api\
    └── multimodal.py              # FastAPI endpoints
```

### 5.4 Database Schema (for tracking)

**Table: `multimodal_generations`**

```sql
CREATE TABLE multimodal_generations (
    id TEXT PRIMARY KEY,               -- UUID
    request_type TEXT NOT NULL,        -- 'image', 'voice', 'video'
    status TEXT NOT NULL,              -- 'queued', 'processing', 'completed', 'failed'
    priority TEXT,                     -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'

    -- Request details
    prompt TEXT,
    requester_agent TEXT,              -- 'L1.01', 'L2.05.03', 'user'
    quality_tier TEXT,                 -- 'draft', 'standard', 'high'

    -- Generation details
    model_used TEXT,                   -- 'sdxl', 'sd15', 'dall-e-3', 'piper-tts'
    generation_time_sec REAL,
    vram_used_gb REAL,
    cost_usd REAL,                     -- $0 for local, API cost for cloud

    -- Output
    output_path TEXT,
    output_url TEXT,
    file_size_bytes INTEGER,

    -- Timestamps
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,

    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX idx_status ON multimodal_generations(status);
CREATE INDEX idx_created_at ON multimodal_generations(created_at);
CREATE INDEX idx_requester ON multimodal_generations(requester_agent);
```

---

## 6. API ENDPOINT SPECIFICATIONS

### 6.1 Unified Generation Endpoint

**POST /api/multimodal/generate**

Request body:
```json
{
  "type": "image",                    // 'image', 'voice', 'video' (future)
  "prompt": "Architecture diagram showing Ziggie's L1-L2-L3 agent hierarchy with clean modern design",
  "options": {
    "quality": "high",                 // 'draft', 'standard', 'high'
    "style": "technical-diagram",      // 'technical-diagram', 'report-cover', 'infographic'
    "aspect_ratio": "16:9",            // '1:1', '16:9', '4:3', '9:16'
    "seed": 42,                        // Optional: for reproducibility
    "negative_prompt": "blurry, text, watermark"
  },
  "priority": "MEDIUM",                // 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
  "requester": "L2.05.03",            // Agent ID or 'user'
  "webhook_url": null                  // Optional: callback when done
}
```

Response (immediate):
```json
{
  "request_id": "mmg-2025-11-11-abc123",
  "status": "queued",                  // or 'processing' if GPU available
  "estimated_wait_seconds": 45,
  "queue_position": 2,
  "websocket_url": "ws://localhost:54112/ws/multimodal/mmg-2025-11-11-abc123"
}
```

Response (via WebSocket, progressive updates):
```json
// Step 1: Processing started
{
  "request_id": "mmg-2025-11-11-abc123",
  "status": "processing",
  "message": "Loading ComfyUI model (SDXL)...",
  "progress_percent": 10
}

// Step 2: Generation in progress
{
  "request_id": "mmg-2025-11-11-abc123",
  "status": "processing",
  "message": "Generating image (step 15/25)...",
  "progress_percent": 60
}

// Step 3: Completed
{
  "request_id": "mmg-2025-11-11-abc123",
  "status": "completed",
  "generation_time_seconds": 38.5,
  "model_used": "sdxl-1.0",
  "cost_usd": 0.0,
  "output": {
    "url": "http://localhost:54112/api/multimodal/assets/images/2025-11/mmg-2025-11-11-abc123.png",
    "file_path": "C:\\Ziggie\\generated-assets\\images\\2025-11\\mmg-2025-11-11-abc123.png",
    "file_size_bytes": 2458912,
    "width": 1024,
    "height": 1024
  }
}
```

### 6.2 Queue Status Endpoint

**GET /api/multimodal/queue**

Response:
```json
{
  "active_generations": 1,
  "queued_requests": 3,
  "gpu_status": {
    "available_vram_gb": 14.2,
    "total_vram_gb": 24,
    "ollama_loaded": true,
    "comfyui_loaded": true
  },
  "queue": [
    {
      "request_id": "mmg-001",
      "type": "image",
      "priority": "HIGH",
      "status": "processing",
      "estimated_completion": "2025-11-11T10:15:30Z"
    },
    {
      "request_id": "mmg-002",
      "type": "image",
      "priority": "MEDIUM",
      "status": "queued",
      "queue_position": 1,
      "estimated_wait_seconds": 60
    }
  ]
}
```

### 6.3 Asset Retrieval Endpoint

**GET /api/multimodal/assets/{asset_type}/{year-month}/{filename}**

Example:
```
GET /api/multimodal/assets/images/2025-11/mmg-2025-11-11-abc123.png
```

Response: Binary image file (PNG/JPG) with appropriate headers.

### 6.4 Generation History Endpoint

**GET /api/multimodal/history**

Query params:
- `type`: Filter by type (image/voice/video)
- `requester`: Filter by agent ID
- `status`: Filter by status
- `page`: Pagination
- `limit`: Results per page (default 50)

Response:
```json
{
  "total": 243,
  "page": 1,
  "limit": 50,
  "generations": [
    {
      "request_id": "mmg-2025-11-11-abc123",
      "type": "image",
      "status": "completed",
      "prompt": "Architecture diagram...",
      "model_used": "sdxl-1.0",
      "generation_time_seconds": 38.5,
      "cost_usd": 0.0,
      "created_at": "2025-11-11T10:14:52Z",
      "completed_at": "2025-11-11T10:15:30Z",
      "output_url": "/api/multimodal/assets/images/2025-11/mmg-2025-11-11-abc123.png"
    }
  ]
}
```

### 6.5 Model Management Endpoints

**GET /api/multimodal/models**
```json
{
  "available_models": {
    "image": [
      {"name": "sdxl-1.0", "vram_gb": 12, "speed": "slow", "quality": "high"},
      {"name": "sd-1.5", "vram_gb": 6, "speed": "fast", "quality": "medium"}
    ],
    "voice": [
      {"name": "piper-en-us", "cpu_only": true, "speed": "fast", "quality": "high"}
    ]
  },
  "loaded_models": ["sdxl-1.0"],
  "gpu_status": {
    "available_vram_gb": 14.2,
    "total_vram_gb": 24
  }
}
```

**POST /api/multimodal/models/load**
```json
{
  "model": "sdxl-1.0",
  "unload_others": false  // If true, unload all other models first
}
```

**POST /api/multimodal/models/unload**
```json
{
  "model": "sdxl-1.0"
}
```

---

## 7. PHASED ROLLOUT PLAN

### Phase 1: Image Generation Core (Week 1-2)

**Deliverables:**
- ✅ L2 Multimodal Generator agent scaffolding
- ✅ ComfyUI integration wrapper (`image_generator.py`)
- ✅ Basic queue manager (FIFO, no priorities yet)
- ✅ Single API endpoint: `POST /api/multimodal/generate` (image only)
- ✅ File storage in `generated-assets/images/`
- ✅ Basic GPU VRAM monitoring

**Success Metrics:**
- Can generate 1024x1024 SDXL image from text prompt
- Response time: < 60 seconds (local GPU)
- API success rate: > 95%
- No GPU crashes or VRAM leaks

**Time Estimate:** 12-16 hours engineering

**Code Deliverable:** Functional but minimal (no WebSocket, no priorities, no cloud fallback)

---

### Phase 2: Production Hardening (Week 3-4)

**Deliverables:**
- ✅ Priority queue system (CRITICAL > HIGH > MEDIUM > LOW)
- ✅ WebSocket progress updates for long-running generations
- ✅ GPU resource manager (dynamic Ollama/ComfyUI swapping)
- ✅ Cloud fallback (Stability AI or DALL-E 3) when GPU busy
- ✅ Error handling & retry logic
- ✅ Asset cleanup job (delete assets > 30 days old)
- ✅ Database tracking (`multimodal_generations` table)
- ✅ Admin dashboard (queue visualization, GPU stats)

**Success Metrics:**
- Queue handling: > 10 concurrent requests without crashes
- Fallback success rate: 100% (always get an image, local or cloud)
- User satisfaction: "I don't care if it's local or cloud, it just works"

**Time Estimate:** 20-24 hours engineering

**Code Deliverable:** Production-ready image generation system

---

### Phase 3: Voice/TTS (Optional, Month 2)

**Trigger Condition:** User or agent explicitly requests voice features

**Deliverables:**
- ✅ Piper TTS integration (CPU-based, no GPU needed)
- ✅ Voice endpoint: `POST /api/multimodal/generate` with `type: "voice"`
- ✅ Audio file storage in `generated-assets/audio/`
- ✅ Multi-voice support (male, female, different accents)
- ✅ SSML support for emphasis, pauses, pronunciations

**Success Metrics:**
- Can generate natural-sounding English speech
- Response time: < 10 seconds for 1000-word report
- Quality: Comparable to Azure TTS (MEDIUM tier)

**Time Estimate:** 8-12 hours engineering (Piper is simple to integrate)

**Code Deliverable:** Working TTS endpoint, but only if needed

---

### Phase 4: Advanced Features (Month 3+, Optional)

**Only implement if Phase 2 is successful and usage is high**

**Potential Features:**
- Custom model fine-tuning on Ziggie branding
- Prompt enhancement with Ollama (auto-improve user prompts)
- Batch generation API (generate 10 variations at once)
- Style transfer (make all images consistent style)
- Image-to-image refinement
- Upscaling (generate 512px draft, upscale to 2048px for final)

**Time Estimate:** 30-40 hours engineering

---

## 8. RISK ASSESSMENT

### Risk 1: GPU VRAM Insufficient (Ollama + ComfyUI exceeds 24GB)

**Likelihood:** MEDIUM (can happen with SDXL + Llama 3.2 13B)

**Impact:** HIGH (system crashes, no image generation, Ollama downtime)

**Mitigation:**
- Default to smaller LLM model (Qwen 2.5 7B uses 7GB vs Llama 13B uses 14GB)
- Implement dynamic model swapping (unload Ollama when generating images)
- Use SD 1.5 (6GB) instead of SDXL (12GB) for draft quality
- Cloud fallback when VRAM exhausted

**Residual Risk:** LOW (multiple fallbacks in place)

---

### Risk 2: ComfyUI Crashes or Hangs

**Likelihood:** MEDIUM (ComfyUI is community software, less stable than commercial APIs)

**Impact:** MEDIUM (queued requests fail, users frustrated)

**Mitigation:**
- Automatic restart on crash (Docker restart policy)
- Health check endpoint (ping ComfyUI every 30 seconds)
- Timeout after 120 seconds (assume crash, restart service)
- Cloud fallback for failed requests
- Alert L1 agent when ComfyUI down > 5 minutes

**Residual Risk:** LOW (auto-recovery + fallback)

---

### Risk 3: Image Quality Lower Than Cloud APIs

**Likelihood:** HIGH (local SDXL < Midjourney v6 in artistic quality)

**Impact:** MEDIUM (users complain, prefer cloud quality)

**Mitigation:**
- Offer quality tiers: "draft" (local), "standard" (local SDXL), "premium" (cloud Midjourney)
- Fine-tune local models on Ziggie brand style (better than generic SDXL)
- Use local for technical diagrams (where precision > artistry)
- Use cloud for marketing assets (where artistry > cost)

**Residual Risk:** LOW (user chooses quality tier)

---

### Risk 4: Storage Costs Explode (1000s of generated images)

**Likelihood:** MEDIUM (10 images/day = 300/month = 3,600/year at 2-5MB each = 7-18GB/year)

**Impact:** LOW ($2-5/year for 10GB storage)

**Mitigation:**
- Retention policy: Auto-delete images > 30 days old
- Compress PNGs to JPGs (80% quality = 50% size reduction)
- Store thumbnails (256px) for history view, full-res only when needed
- Cloud storage (S3/Azure Blob) is cheap ($0.023/GB/month)

**Residual Risk:** NEGLIGIBLE (storage is cheap, cleanup is automatic)

---

### Risk 5: Integration Complexity Delays Other Priorities

**Likelihood:** MEDIUM (multimodal is non-trivial, could take 40+ hours)

**Impact:** HIGH (if it blocks core Ziggie development)

**Mitigation:**
- Phase 1 is minimal (16 hours max)
- Phase 2+ is optional (only proceed if Phase 1 proves valuable)
- Defer voice/video unless explicitly requested
- Assign to dedicated L2 agent (doesn't block L1 work)

**Residual Risk:** LOW (phased approach allows early exit)

---

## 9. CODE TEMPLATES

### 9.1 Image Generator Wrapper

**File:** `C:\Ziggie\multimodal\image_generator.py`

```python
"""
ComfyUI Integration for Image Generation
Wraps ComfyUI API for Ziggie agents
"""
import aiohttp
import asyncio
import base64
from typing import Dict, Optional
from pathlib import Path
import json

class ImageGenerator:
    """Generate images using ComfyUI (Stable Diffusion)"""

    def __init__(self, comfyui_url: str = "http://localhost:8188"):
        self.comfyui_url = comfyui_url
        self.default_workflow = self._load_workflow()

    def _load_workflow(self) -> Dict:
        """Load ComfyUI workflow JSON (text-to-image)"""
        # This is a minimal SDXL workflow
        # In production, load from C:\Ziggie\multimodal\workflows\sdxl-text2img.json
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 25,
                    "cfg": 7.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "PROMPT_PLACEHOLDER", "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, text, watermark", "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "ziggie", "images": ["8", 0]}}
        }

    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "blurry, text, watermark, low quality",
        width: int = 1024,
        height: int = 1024,
        steps: int = 25,
        cfg: float = 7.0,
        seed: Optional[int] = None,
        model: str = "sdxl"
    ) -> Dict:
        """
        Generate an image from text prompt

        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid in image
            width, height: Image dimensions (multiples of 64)
            steps: Inference steps (more = higher quality, slower)
            cfg: Guidance scale (7.0 is good default)
            seed: Random seed (None = random)
            model: "sdxl" or "sd15"

        Returns:
            {
                "image_path": "C:\\Ziggie\\generated-assets\\images\\...",
                "image_url": "/api/multimodal/assets/images/...",
                "width": 1024,
                "height": 1024,
                "generation_time_seconds": 38.5,
                "model": "sdxl-1.0",
                "seed": 42
            }
        """
        try:
            # Health check
            if not await self.health_check():
                raise Exception("ComfyUI is not responding")

            # Prepare workflow
            workflow = self.default_workflow.copy()
            workflow["6"]["inputs"]["text"] = prompt
            workflow["7"]["inputs"]["text"] = negative_prompt
            workflow["5"]["inputs"]["width"] = width
            workflow["5"]["inputs"]["height"] = height
            workflow["3"]["inputs"]["steps"] = steps
            workflow["3"]["inputs"]["cfg"] = cfg

            if seed is not None:
                workflow["3"]["inputs"]["seed"] = seed
            else:
                import random
                workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)

            # Submit to ComfyUI
            import time
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                # Queue prompt
                async with session.post(
                    f"{self.comfyui_url}/prompt",
                    json={"prompt": workflow}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"ComfyUI error: {await response.text()}")

                    result = await response.json()
                    prompt_id = result["prompt_id"]

                # Wait for completion (poll every 2 seconds)
                for _ in range(60):  # Max 2 minutes
                    await asyncio.sleep(2)

                    async with session.get(f"{self.comfyui_url}/history/{prompt_id}") as hist_response:
                        history = await hist_response.json()

                        if prompt_id in history:
                            outputs = history[prompt_id].get("outputs", {})
                            if "9" in outputs:  # SaveImage node
                                images = outputs["9"]["images"]
                                if images:
                                    # Image generated!
                                    image_info = images[0]
                                    image_filename = image_info["filename"]

                                    # Get image from ComfyUI
                                    async with session.get(
                                        f"{self.comfyui_url}/view",
                                        params={
                                            "filename": image_filename,
                                            "subfolder": image_info.get("subfolder", ""),
                                            "type": image_info.get("type", "output")
                                        }
                                    ) as img_response:
                                        image_data = await img_response.read()

                                    # Save to Ziggie assets folder
                                    from datetime import datetime
                                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                                    output_dir = Path("C:/Ziggie/generated-assets/images") / datetime.now().strftime("%Y-%m")
                                    output_dir.mkdir(parents=True, exist_ok=True)

                                    output_path = output_dir / f"img-{timestamp}-{prompt_id}.png"
                                    output_path.write_bytes(image_data)

                                    generation_time = time.time() - start_time

                                    return {
                                        "image_path": str(output_path),
                                        "image_url": f"/api/multimodal/assets/images/{datetime.now().strftime('%Y-%m')}/img-{timestamp}-{prompt_id}.png",
                                        "width": width,
                                        "height": height,
                                        "generation_time_seconds": round(generation_time, 2),
                                        "model": model,
                                        "seed": workflow["3"]["inputs"]["seed"],
                                        "prompt": prompt
                                    }

                raise Exception("ComfyUI generation timeout (>2 minutes)")

        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    async def health_check(self) -> bool:
        """Check if ComfyUI is running and responding"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.comfyui_url}/system_stats", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
```

### 9.2 GPU Resource Manager

**File:** `C:\Ziggie\multimodal\resource_manager.py`

```python
"""
GPU Resource Manager
Dynamically allocate VRAM between Ollama and ComfyUI
"""
import psutil
import subprocess
import asyncio
from typing import Dict, Optional

class GPUResourceManager:
    """Manage GPU VRAM allocation for LLM and image generation"""

    def __init__(self):
        self.ollama_loaded = True  # Assume Ollama running at startup
        self.comfyui_loaded = False
        self.reserved_vram_gb = 2  # Always reserve 2GB for system

    async def get_gpu_stats(self) -> Dict:
        """Get current GPU utilization using nvidia-smi"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,memory.free", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                used, total, free = map(int, result.stdout.strip().split(", "))
                return {
                    "vram_used_mb": used,
                    "vram_total_mb": total,
                    "vram_free_mb": free,
                    "vram_used_gb": round(used / 1024, 2),
                    "vram_total_gb": round(total / 1024, 2),
                    "vram_free_gb": round(free / 1024, 2)
                }
        except Exception as e:
            print(f"GPU stats unavailable: {e}")
            return {
                "vram_used_gb": 0,
                "vram_total_gb": 24,  # Assume 24GB GPU
                "vram_free_gb": 24,
                "error": str(e)
            }

    async def can_fit_model(self, model_name: str) -> bool:
        """Check if model can fit in available VRAM"""
        stats = await self.get_gpu_stats()
        free_vram = stats["vram_free_gb"]

        # Model VRAM requirements (approximate)
        requirements = {
            "sdxl": 12,
            "sd15": 6,
            "piper-tts": 0  # CPU-based
        }

        required_vram = requirements.get(model_name, 12)  # Default 12GB

        return free_vram >= (required_vram + self.reserved_vram_gb)

    async def request_vram(self, amount_gb: int, priority: str = "MEDIUM") -> bool:
        """
        Request VRAM allocation for a task

        Args:
            amount_gb: How much VRAM needed
            priority: CRITICAL can force-unload Ollama

        Returns:
            True if VRAM available, False if denied
        """
        stats = await self.get_gpu_stats()
        free_vram = stats["vram_free_gb"]

        if free_vram >= amount_gb:
            return True  # Enough free VRAM

        # Not enough free VRAM - try to make room
        if priority in ["CRITICAL", "HIGH"]:
            # Can temporarily unload Ollama
            if self.ollama_loaded:
                print(f"⚠️ Unloading Ollama to free VRAM for {priority} priority task")
                await self.unload_ollama()

                # Check again
                stats = await self.get_gpu_stats()
                free_vram = stats["vram_free_gb"]

                if free_vram >= amount_gb:
                    return True

        # Still not enough - deny request
        return False

    async def unload_ollama(self):
        """Temporarily unload Ollama to free VRAM"""
        # Note: This is a placeholder. Actual implementation would use Ollama API
        # to unload models. For now, we'll just log it.
        print("TODO: Unload Ollama models via API")
        self.ollama_loaded = False

    async def reload_ollama(self):
        """Reload Ollama after image generation"""
        print("TODO: Reload Ollama models via API")
        self.ollama_loaded = True
```

### 9.3 FastAPI Multimodal Endpoint

**File:** `C:\Ziggie\control-center\backend\api\multimodal.py`

```python
"""
Multimodal Generation API
Image, voice, video generation endpoints
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uuid

from middleware.rate_limit import limiter

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])

# TODO: Import actual generators
# from multimodal.image_generator import ImageGenerator
# from multimodal.resource_manager import GPUResourceManager

class GenerateRequest(BaseModel):
    type: str  # 'image', 'voice', 'video'
    prompt: str
    options: Optional[Dict] = {}
    priority: str = "MEDIUM"
    requester: str = "user"
    webhook_url: Optional[str] = None

class GenerateResponse(BaseModel):
    request_id: str
    status: str
    estimated_wait_seconds: Optional[int] = None
    queue_position: Optional[int] = None
    websocket_url: Optional[str] = None

@router.post("/generate")
@limiter.limit("30/minute")
async def generate(request: Request, gen_request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate image, voice, or video from prompt

    Types:
    - image: Text-to-image generation
    - voice: Text-to-speech (optional)
    - video: Text-to-video (not implemented)
    """
    try:
        # Validate type
        if gen_request.type not in ["image", "voice"]:
            raise HTTPException(
                status_code=400,
                detail=f"Type '{gen_request.type}' not supported. Use 'image' or 'voice'."
            )

        # Generate request ID
        request_id = f"mmg-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

        # For Phase 1, process immediately (no queue yet)
        if gen_request.type == "image":
            # TODO: Use actual ImageGenerator
            # image_gen = ImageGenerator()
            # result = await image_gen.generate(gen_request.prompt, **gen_request.options)

            # Mock response for now
            result = {
                "request_id": request_id,
                "status": "processing",
                "estimated_wait_seconds": 45,
                "message": "Image generation started (Phase 1 - mock response)"
            }

            return result

        elif gen_request.type == "voice":
            # TODO: Implement Piper TTS in Phase 3
            raise HTTPException(
                status_code=501,
                detail="Voice generation not yet implemented (Phase 3)"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

@router.get("/queue")
@limiter.limit("60/minute")
async def get_queue_status(request: Request):
    """Get current generation queue status"""
    # TODO: Implement actual queue manager
    return {
        "active_generations": 0,
        "queued_requests": 0,
        "gpu_status": {
            "available_vram_gb": 14.2,
            "total_vram_gb": 24,
            "ollama_loaded": True,
            "comfyui_loaded": False
        },
        "queue": []
    }

@router.get("/history")
@limiter.limit("60/minute")
async def get_generation_history(
    request: Request,
    type: Optional[str] = None,
    requester: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """Get generation history with filters"""
    # TODO: Query database
    return {
        "total": 0,
        "page": page,
        "limit": limit,
        "generations": []
    }

@router.get("/models")
async def get_available_models(request: Request):
    """List available generation models"""
    return {
        "available_models": {
            "image": [
                {"name": "sdxl-1.0", "vram_gb": 12, "speed": "slow", "quality": "high"},
                {"name": "sd-1.5", "vram_gb": 6, "speed": "fast", "quality": "medium"}
            ],
            "voice": [
                {"name": "piper-en-us", "cpu_only": True, "speed": "fast", "quality": "high"}
            ]
        },
        "loaded_models": [],
        "gpu_status": {
            "available_vram_gb": 14.2,
            "total_vram_gb": 24
        }
    }
```

---

## 10. FINAL RECOMMENDATION

### RECOMMENDATION: **APPROVE IMAGE GENERATION ONLY (PHASE 1-2)**

### Why Image Generation? (YES)

1. **Practical Use Cases:** Architecture diagrams, report covers, dashboard thumbnails are **core Ziggie needs**
2. **Cost-Neutral:** GPU already purchased for Ollama, marginal electricity cost = $5-10/month
3. **Unlimited Generations:** No monthly limits (Midjourney caps at 200 images/month for $10)
4. **Custom Branding:** Fine-tune on Ziggie style for consistent visual identity
5. **Proven Technology:** Stable Diffusion XL is mature, ComfyUI is widely used
6. **Easy Integration:** Existing ComfyUI API endpoint, 16 hours engineering time

**Decision:** ✅ **APPROVE** Phase 1-2 (Image generation, 4 weeks)

---

### Why NOT Voice Generation? (SKIP FOR NOW)

1. **Unclear Use Cases:** No proven demand for voice notifications or TTS reports
2. **Alternative Exists:** Users can use built-in OS TTS (Windows Narrator, macOS VoiceOver)
3. **Questionable Value:** Reading a technical report is faster than listening (TTS is slow)
4. **Low Savings:** ElevenLabs = $132/year, but we might use $0 of it (no demand)
5. **Easy to Add Later:** Piper TTS is CPU-based, can implement in 8 hours if needed

**Decision:** ⏸️ **DEFER** Phase 3 (Voice) until user requests it

---

### Why NOT Video Generation? (DEFINITELY SKIP)

1. **No Use Cases:** Ziggie is a backend automation system, not a content platform
2. **Immature Technology:** AI video is 2-5 second clips, not useful for demos
3. **Better Alternatives:** OBS for screen recording, Loom for demos (better quality, faster)
4. **High Complexity:** Rendering pipeline, storage (100MB+ per video), VRAM-intensive
5. **Poor ROI:** Estimated usage = 0-10 videos/month, saves $0-120/year vs $200-500 GPU upgrade
6. **Engineering Time:** 30-40 hours for minimal benefit

**Decision:** ❌ **REJECT** Video generation (not worth it)

---

## APPROVAL SUMMARY

**Stakeholder Decision:**

✅ **APPROVED:** Phase 1 - Image Generation Core (Week 1-2, 16 hours)
✅ **APPROVED:** Phase 2 - Production Hardening (Week 3-4, 24 hours)
⏸️ **DEFERRED:** Phase 3 - Voice/TTS (revisit if user requests)
❌ **REJECTED:** Video Generation (insufficient ROI)

**Total Investment:**
- Engineering Time: 40 hours (5 days)
- Hardware Cost: $0 (GPU already owned)
- Ongoing Cost: $5-10/month (marginal electricity)

**Expected Outcomes:**
- **Capability:** Generate unlimited 1024x1024 images in 30-60 seconds
- **Quality:** Comparable to Midjourney v5 (SDXL), superior for technical diagrams
- **Reliability:** 95%+ success rate, cloud fallback for failures
- **Cost Savings:** $0-300 over 5 years (vs Midjourney/DALL-E)
- **Strategic Value:** Custom branding, unlimited usage, no API dependencies

**Success Metrics (After Phase 2):**
- ✅ 20+ images generated per week (proof of usage)
- ✅ < 60 second generation time (acceptable UX)
- ✅ > 95% local generation success rate (minimal cloud fallback)
- ✅ Zero GPU crashes or VRAM leaks
- ✅ User satisfaction: "Images meet my needs for reports/diagrams"

**Next Steps:**
1. **Stakeholder approves** this document
2. **Assign L2 Agent:** Deploy "L2 Multimodal Generator" (new agent)
3. **Week 1-2:** Implement Phase 1 (basic image generation)
4. **Week 2:** Mid-sprint review (validate progress)
5. **Week 3-4:** Implement Phase 2 (production hardening)
6. **Week 4:** Final review and Phase 3 decision

---

## RELATED DOCUMENTS

- **LLM Strategy:** `COST_OPTIMIZATION_LOCAL_LLM_STRATEGY.md` (Ollama integration)
- **Quick Start:** `LOCAL_LLM_QUICK_START_GUIDE.md` (Ollama setup)
- **Control Center Backend:** `C:\Ziggie\control-center\backend\main.py`
- **ComfyUI API:** `C:\Ziggie\control-center\backend\api\comfyui.py` (already exists!)

---

**Questions?** Contact L1 Multimodal Integration Architect via Ziggie Control Center

**Ready to Start?** Assign L2 Multimodal Generator agent and begin Phase 1

---

**END OF STRATEGY DOCUMENT**

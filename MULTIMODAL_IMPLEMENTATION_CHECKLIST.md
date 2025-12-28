# MULTIMODAL IMPLEMENTATION CHECKLIST
## Phase-by-Phase Implementation Guide

**Project:** Ziggie Multimodal Integration (Image Generation)
**Duration:** 4 weeks (Phase 1-2 only)
**Assignee:** L2 Multimodal Generator Agent

---

## PRE-FLIGHT CHECKS

Before starting, verify:

- [ ] RTX 3090/4090 24GB GPU installed and working
- [ ] Ollama running and tested (see `LOCAL_LLM_QUICK_START_GUIDE.md`)
- [ ] ComfyUI installed at `C:\ComfyUI` (see existing `control-center\backend\api\comfyui.py`)
- [ ] SDXL model downloaded (`sd_xl_base_1.0.safetensors` in `C:\ComfyUI\models\checkpoints\`)
- [ ] nvidia-smi command works (GPU monitoring)
- [ ] Docker available (if using containerized approach)
- [ ] Python 3.10+ installed
- [ ] FastAPI backend running (`control-center\backend\main.py`)

**Estimated Setup Time:** 1-2 hours (if ComfyUI already installed)

---

## PHASE 1: IMAGE GENERATION CORE (Week 1-2)

**Goal:** Basic image generation working (minimal features)

### Week 1: Days 1-3 (8 hours)

#### Day 1: Directory Setup & Agent Scaffolding (2 hours)

- [ ] Create directory structure:
  ```bash
  mkdir C:\Ziggie\multimodal
  mkdir C:\Ziggie\multimodal\workflows
  mkdir C:\Ziggie\generated-assets
  mkdir C:\Ziggie\generated-assets\images
  mkdir C:\Ziggie\multimodal-logs
  ```

- [ ] Create Python files:
  - [ ] `C:\Ziggie\multimodal\__init__.py`
  - [ ] `C:\Ziggie\multimodal\main.py` (L2 Agent entry point)
  - [ ] `C:\Ziggie\multimodal\image_generator.py` (ComfyUI wrapper)
  - [ ] `C:\Ziggie\multimodal\config.py` (Configuration)

- [ ] Update `requirements.txt`:
  ```
  aiohttp==3.9.1
  pillow==10.1.0
  pydantic==2.5.0
  ```

- [ ] Install dependencies:
  ```bash
  cd C:\Ziggie\multimodal
  pip install -r requirements.txt
  ```

**Checkpoint:** Directory structure exists, Python packages installed

---

#### Day 2: ComfyUI Integration (3 hours)

- [ ] Copy `image_generator.py` template from strategy document (Section 9.1)

- [ ] Test ComfyUI connection:
  ```python
  # Test script
  import asyncio
  from image_generator import ImageGenerator

  async def test():
      gen = ImageGenerator()
      healthy = await gen.health_check()
      print(f"ComfyUI healthy: {healthy}")

  asyncio.run(test())
  ```

- [ ] Create basic SDXL workflow JSON:
  - [ ] Export workflow from ComfyUI UI (Save API Format)
  - [ ] Save to `C:\Ziggie\multimodal\workflows\sdxl-text2img.json`
  - [ ] Update `image_generator.py` to load this workflow

- [ ] Test image generation:
  ```python
  async def test_generation():
      gen = ImageGenerator()
      result = await gen.generate("A technical architecture diagram showing a neural network")
      print(f"Image saved to: {result['image_path']}")

  asyncio.run(test_generation())
  ```

**Checkpoint:** Can generate 1024x1024 image from Python script

---

#### Day 3: FastAPI Endpoint (3 hours)

- [ ] Create `C:\Ziggie\control-center\backend\api\multimodal.py`
- [ ] Copy endpoint template from strategy document (Section 9.3)

- [ ] Update `main.py` to include multimodal router:
  ```python
  from api import multimodal
  app.include_router(multimodal.router)
  ```

- [ ] Test endpoint with cURL:
  ```bash
  curl -X POST http://localhost:54112/api/multimodal/generate \
    -H "Content-Type: application/json" \
    -d '{
      "type": "image",
      "prompt": "Technical diagram of a multi-agent system",
      "options": {"quality": "high"},
      "priority": "MEDIUM",
      "requester": "user"
    }'
  ```

- [ ] Verify response:
  - [ ] Returns `request_id`
  - [ ] Returns `status: "processing"` or `"completed"`
  - [ ] Image file created in `generated-assets/images/`

**Checkpoint:** API endpoint works, returns generated image

---

### Week 2: Days 4-5 (8 hours)

#### Day 4: GPU Resource Monitoring (4 hours)

- [ ] Create `C:\Ziggie\multimodal\resource_manager.py`
- [ ] Copy template from strategy document (Section 9.2)

- [ ] Test GPU stats:
  ```python
  from resource_manager import GPUResourceManager

  async def test():
      mgr = GPUResourceManager()
      stats = await mgr.get_gpu_stats()
      print(f"VRAM: {stats['vram_used_gb']}GB / {stats['vram_total_gb']}GB")

  asyncio.run(test())
  ```

- [ ] Add VRAM check before generation:
  ```python
  # In image_generator.py generate() method
  mgr = GPUResourceManager()
  if not await mgr.can_fit_model("sdxl"):
      raise Exception("Insufficient VRAM for SDXL (need 12GB)")
  ```

- [ ] Add new endpoint `GET /api/multimodal/models`:
  ```python
  @router.get("/models")
  async def get_models():
      mgr = GPUResourceManager()
      stats = await mgr.get_gpu_stats()
      return {
          "available_models": [...],
          "gpu_status": stats
      }
  ```

**Checkpoint:** GPU monitoring works, API reports VRAM usage

---

#### Day 5: File Storage & Asset Retrieval (4 hours)

- [ ] Create `C:\Ziggie\multimodal\asset_manager.py`:
  ```python
  class AssetManager:
      def save_image(self, image_data, metadata):
          # Save to generated-assets/images/YYYY-MM/
          # Return URL
          pass

      def get_image_url(self, filename):
          # Return /api/multimodal/assets/images/...
          pass
  ```

- [ ] Add asset retrieval endpoint:
  ```python
  from fastapi.responses import FileResponse

  @router.get("/assets/{asset_type}/{year_month}/{filename}")
  async def get_asset(asset_type: str, year_month: str, filename: str):
      file_path = Path(f"C:/Ziggie/generated-assets/{asset_type}/{year_month}/{filename}")
      if not file_path.exists():
          raise HTTPException(404, "Asset not found")
      return FileResponse(file_path)
  ```

- [ ] Test asset retrieval:
  ```bash
  # After generating an image, retrieve it
  curl http://localhost:54112/api/multimodal/assets/images/2025-11/img-20251111-123456-abc.png -o test.png
  ```

- [ ] Update generation response to include URL:
  ```json
  {
    "request_id": "...",
    "status": "completed",
    "output": {
      "url": "/api/multimodal/assets/images/2025-11/img-20251111-123456-abc.png",
      "file_path": "C:\\Ziggie\\generated-assets\\images\\2025-11\\img-20251111-123456-abc.png"
    }
  }
  ```

**Checkpoint:** Images are stored with metadata, retrievable via URL

---

### Phase 1 Review (End of Week 2)

**Success Criteria:**
- [ ] Can generate 1024x1024 images from text prompts
- [ ] API endpoint works (`POST /api/multimodal/generate`)
- [ ] Images stored in organized folder structure
- [ ] Assets retrievable via URL
- [ ] GPU VRAM monitored and reported
- [ ] Response time < 60 seconds (with GPU)
- [ ] No crashes or VRAM leaks

**Deliverables:**
- [ ] Working Python modules (`image_generator.py`, `resource_manager.py`, `asset_manager.py`)
- [ ] FastAPI endpoint (`api/multimodal.py`)
- [ ] 5+ test images generated successfully
- [ ] Documentation updated (README, API docs)

**Go/No-Go Decision:** Proceed to Phase 2?
- [ ] YES - All criteria met, proceed to Phase 2
- [ ] NO - Address issues, extend Phase 1 by 1 week
- [ ] ABORT - Insufficient value, revert changes

---

## PHASE 2: PRODUCTION HARDENING (Week 3-4)

**Goal:** Production-ready system with queue, WebSockets, fallback

### Week 3: Days 6-8 (12 hours)

#### Day 6: Priority Queue System (4 hours)

- [ ] Create `C:\Ziggie\multimodal\queue_manager.py`:
  ```python
  import asyncio
  from queue import PriorityQueue

  class GenerationQueue:
      def __init__(self):
          self.queue = PriorityQueue()
          self.processing = {}

      async def enqueue(self, request, priority):
          # Add to queue with priority
          pass

      async def dequeue(self):
          # Get next request based on priority
          pass

      def get_status(self):
          # Return queue stats
          pass
  ```

- [ ] Define priority levels:
  ```python
  PRIORITY_MAP = {
      "CRITICAL": 0,  # Highest priority
      "HIGH": 1,
      "MEDIUM": 2,
      "LOW": 3        # Lowest priority
  }
  ```

- [ ] Update generate endpoint to use queue:
  ```python
  queue = GenerationQueue()

  @router.post("/generate")
  async def generate(gen_request: GenerateRequest, background_tasks: BackgroundTasks):
      request_id = generate_request_id()

      # Enqueue request
      await queue.enqueue(gen_request, priority=gen_request.priority)

      # Start background processing
      background_tasks.add_task(process_queue)

      return {
          "request_id": request_id,
          "status": "queued",
          "queue_position": queue.get_position(request_id)
      }
  ```

- [ ] Test queue with multiple requests:
  ```bash
  # Submit 5 requests with different priorities
  for i in {1..5}; do
    curl -X POST http://localhost:54112/api/multimodal/generate \
      -H "Content-Type: application/json" \
      -d "{\"type\": \"image\", \"prompt\": \"Test $i\", \"priority\": \"MEDIUM\"}"
  done
  ```

**Checkpoint:** Queue system works, processes requests by priority

---

#### Day 7: WebSocket Progress Updates (4 hours)

- [ ] Add WebSocket endpoint in `main.py`:
  ```python
  from fastapi import WebSocket

  @app.websocket("/ws/multimodal/{request_id}")
  async def websocket_generation_progress(websocket: WebSocket, request_id: str):
      await websocket.accept()
      try:
          while True:
              # Send progress updates
              progress = get_generation_progress(request_id)
              await websocket.send_json(progress)
              await asyncio.sleep(1)
      except WebSocketDisconnect:
          pass
  ```

- [ ] Update `image_generator.py` to emit progress events:
  ```python
  async def generate(self, prompt, progress_callback=None):
      if progress_callback:
          await progress_callback({"status": "loading_model", "progress_percent": 10})

      # ... generation code ...

      if progress_callback:
          await progress_callback({"status": "generating", "progress_percent": 50})
  ```

- [ ] Test WebSocket connection:
  ```javascript
  // JavaScript client test
  const ws = new WebSocket('ws://localhost:54112/ws/multimodal/mmg-123');
  ws.onmessage = (event) => {
      const progress = JSON.parse(event.data);
      console.log(`Progress: ${progress.progress_percent}%`);
  };
  ```

**Checkpoint:** WebSocket sends real-time progress updates during generation

---

#### Day 8: Cloud Fallback (4 hours)

- [ ] Add Stability AI API integration:
  ```python
  # In image_generator.py
  async def generate_with_fallback(self, prompt):
      try:
          # Try local first
          return await self.generate_local(prompt)
      except Exception as e:
          print(f"Local generation failed: {e}, trying cloud...")
          return await self.generate_cloud_fallback(prompt)

  async def generate_cloud_fallback(self, prompt):
      # Call Stability AI API
      import os
      api_key = os.getenv("STABILITY_API_KEY")
      async with aiohttp.ClientSession() as session:
          async with session.post(
              "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
              headers={"Authorization": f"Bearer {api_key}"},
              json={"text_prompts": [{"text": prompt}]}
          ) as response:
              # ... handle response ...
              pass
  ```

- [ ] Add fallback configuration to `.env`:
  ```
  STABILITY_API_KEY=your-api-key-here
  ENABLE_CLOUD_FALLBACK=true
  ```

- [ ] Test fallback by stopping ComfyUI:
  ```bash
  # Stop ComfyUI
  docker stop comfyui

  # Generate image (should fallback to cloud)
  curl -X POST http://localhost:54112/api/multimodal/generate \
    -d '{"type": "image", "prompt": "Test fallback"}'

  # Restart ComfyUI
  docker start comfyui
  ```

**Checkpoint:** Cloud fallback works when local GPU unavailable

---

### Week 4: Days 9-10 (12 hours)

#### Day 9: Error Handling & Retry Logic (4 hours)

- [ ] Add retry logic to generation:
  ```python
  async def generate_with_retry(self, prompt, max_retries=3):
      for attempt in range(max_retries):
          try:
              return await self.generate(prompt)
          except Exception as e:
              if attempt == max_retries - 1:
                  raise
              print(f"Attempt {attempt+1} failed, retrying...")
              await asyncio.sleep(5)
  ```

- [ ] Add error logging:
  ```python
  import logging

  logging.basicConfig(
      filename='C:/Ziggie/multimodal-logs/errors.log',
      level=logging.ERROR,
      format='%(asctime)s - %(levelname)s - %(message)s'
  )

  try:
      result = await generate(prompt)
  except Exception as e:
      logging.error(f"Generation failed: {str(e)}", exc_info=True)
  ```

- [ ] Add database tracking (create table):
  ```sql
  -- In control-center/backend/database/
  CREATE TABLE multimodal_generations (
      id TEXT PRIMARY KEY,
      request_type TEXT NOT NULL,
      status TEXT NOT NULL,
      prompt TEXT,
      requester_agent TEXT,
      model_used TEXT,
      generation_time_sec REAL,
      cost_usd REAL,
      output_path TEXT,
      output_url TEXT,
      error_message TEXT,
      created_at TEXT,
      completed_at TEXT
  );
  ```

- [ ] Log all generations to database:
  ```python
  async def log_generation(request_id, status, **kwargs):
      # Insert into multimodal_generations table
      pass
  ```

**Checkpoint:** Errors logged, retries work, database tracking enabled

---

#### Day 10: Asset Cleanup & Monitoring (4 hours)

- [ ] Create cleanup job:
  ```python
  # In asset_manager.py
  async def cleanup_old_assets(retention_days=30):
      import shutil
      from datetime import datetime, timedelta

      cutoff = datetime.now() - timedelta(days=retention_days)
      assets_dir = Path("C:/Ziggie/generated-assets")

      for file_path in assets_dir.rglob("*.png"):
          if file_path.stat().st_mtime < cutoff.timestamp():
              file_path.unlink()  # Delete file
              print(f"Deleted old asset: {file_path}")
  ```

- [ ] Schedule cleanup job (daily):
  ```python
  # In main.py lifespan
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Startup
      print("Starting multimodal cleanup job...")
      cleanup_task = asyncio.create_task(schedule_daily_cleanup())

      yield

      # Shutdown
      cleanup_task.cancel()

  async def schedule_daily_cleanup():
      while True:
          await asyncio.sleep(86400)  # 24 hours
          await cleanup_old_assets()
  ```

- [ ] Add monitoring endpoint:
  ```python
  @router.get("/stats")
  async def get_multimodal_stats():
      return {
          "total_generations": count_generations(),
          "success_rate": calculate_success_rate(),
          "avg_generation_time": calculate_avg_time(),
          "disk_usage_gb": get_disk_usage(),
          "queue_length": queue.size(),
          "gpu_status": await mgr.get_gpu_stats()
      }
  ```

**Checkpoint:** Cleanup job runs daily, monitoring endpoint works

---

#### Day 10 (continued): Admin Dashboard (4 hours)

- [ ] Add dashboard route in `control-center/frontend/src/pages/`:
  ```jsx
  // MultimodalDashboard.jsx
  import React, { useEffect, useState } from 'react';

  export default function MultimodalDashboard() {
      const [stats, setStats] = useState(null);
      const [queue, setQueue] = useState([]);

      useEffect(() => {
          fetch('/api/multimodal/stats')
              .then(r => r.json())
              .then(setStats);

          fetch('/api/multimodal/queue')
              .then(r => r.json())
              .then(data => setQueue(data.queue));
      }, []);

      return (
          <div>
              <h1>Multimodal Generation Dashboard</h1>
              <div>
                  <h2>Statistics</h2>
                  <p>Total Generations: {stats?.total_generations}</p>
                  <p>Success Rate: {stats?.success_rate}%</p>
                  <p>Avg Time: {stats?.avg_generation_time}s</p>
              </div>
              <div>
                  <h2>Current Queue</h2>
                  <ul>
                      {queue.map(item => (
                          <li key={item.request_id}>
                              {item.request_id} - {item.status} ({item.priority})
                          </li>
                      ))}
                  </ul>
              </div>
          </div>
      );
  }
  ```

- [ ] Add route to navigation:
  ```jsx
  // In App.jsx or routes.jsx
  <Route path="/multimodal" element={<MultimodalDashboard />} />
  ```

- [ ] Test dashboard:
  - [ ] Navigate to http://localhost:3000/multimodal
  - [ ] Verify stats display correctly
  - [ ] Verify queue updates in real-time

**Checkpoint:** Admin dashboard functional

---

### Phase 2 Review (End of Week 4)

**Success Criteria:**
- [ ] Priority queue handles 10+ concurrent requests
- [ ] WebSocket progress updates work
- [ ] GPU VRAM dynamically managed (Ollama/ComfyUI swapping)
- [ ] Cloud fallback works (100% success rate)
- [ ] Error handling & retry logic functional
- [ ] Asset cleanup job runs daily
- [ ] Database tracking all generations
- [ ] Admin dashboard displays stats and queue

**Deliverables:**
- [ ] Production-ready multimodal system
- [ ] Full API documentation
- [ ] Admin dashboard
- [ ] Monitoring & logging
- [ ] Database schema
- [ ] Cleanup automation

**Go/No-Go Decision:** Launch to production?
- [ ] YES - All criteria met, launch to production
- [ ] NO - Address issues, extend Phase 2 by 1 week
- [ ] ABORT - Insufficient value, revert to Phase 1 (minimal version)

---

## PHASE 3: VOICE/TTS (OPTIONAL, DEFERRED)

**Trigger:** User or agent explicitly requests voice features

**Estimated Time:** 8-12 hours

**Checklist (if approved):**
- [ ] Install Piper TTS
- [ ] Test voice generation
- [ ] Add voice endpoint to API
- [ ] Update multimodal.py to handle `type: "voice"`
- [ ] Add audio storage directory
- [ ] Test voice retrieval

**Not implemented unless requested.**

---

## TESTING CHECKLIST

### Unit Tests

- [ ] `test_image_generator.py` (generation, health check, workflows)
- [ ] `test_resource_manager.py` (VRAM stats, model fitting)
- [ ] `test_queue_manager.py` (priority queue, dequeue logic)
- [ ] `test_asset_manager.py` (save, retrieve, cleanup)

### Integration Tests

- [ ] `test_api_endpoints.py` (all API endpoints)
- [ ] `test_websocket.py` (progress updates)
- [ ] `test_fallback.py` (cloud fallback when local fails)
- [ ] `test_end_to_end.py` (full generation flow)

### Performance Tests

- [ ] Generate 10 images sequentially (measure time, VRAM usage)
- [ ] Generate 10 images concurrently (test queue, no crashes)
- [ ] Stress test: 50 requests (ensure queue doesn't crash)

### User Acceptance Tests

- [ ] L1 agent requests image for report (works seamlessly)
- [ ] User generates image from dashboard (UI integration)
- [ ] System handles GPU crash gracefully (fallback works)
- [ ] Old assets cleaned up after 30 days (retention policy)

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All tests passing (unit, integration, performance)
- [ ] Code reviewed by L1 agent
- [ ] Documentation complete (API docs, README)
- [ ] Configuration verified (`.env` file, secrets)
- [ ] Database migration run (`multimodal_generations` table)
- [ ] GPU drivers up to date
- [ ] ComfyUI running and healthy
- [ ] Ollama running and healthy

### Deployment Steps

1. [ ] Backup current system (database, configs)
2. [ ] Deploy code to production (`git pull` or `rsync`)
3. [ ] Install dependencies (`pip install -r requirements.txt`)
4. [ ] Run database migrations
5. [ ] Restart FastAPI backend (`systemctl restart ziggie-backend`)
6. [ ] Verify health endpoints (`/api/multimodal/models`, `/api/multimodal/queue`)
7. [ ] Generate test image (smoke test)
8. [ ] Monitor logs for 1 hour (no errors)

### Post-Deployment

- [ ] Alert team in Ziggie Control Center
- [ ] Monitor GPU usage for 24 hours
- [ ] Track generation success rate (target >95%)
- [ ] Collect user feedback (L1/L2 agents)
- [ ] Schedule Phase 3 decision meeting (1 week)

---

## ROLLBACK PLAN

If Phase 2 fails or causes issues:

1. [ ] Revert code to Phase 1 version (git checkout)
2. [ ] Restart FastAPI backend
3. [ ] Disable multimodal routes (comment out in main.py)
4. [ ] Alert team
5. [ ] Investigate root cause
6. [ ] Fix issues
7. [ ] Re-test
8. [ ] Re-deploy

**Rollback Time:** 15 minutes

---

## SUCCESS METRICS (After 1 Month)

Track these metrics after Phase 2 launch:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Total Generations** | 80+ | ___ | ___ |
| **Success Rate** | >95% | ___ | ___ |
| **Avg Generation Time** | <60s | ___ | ___ |
| **Local vs Cloud** | >80% local | ___ | ___ |
| **GPU Crashes** | 0 | ___ | ___ |
| **User Satisfaction** | "Works well" | ___ | ___ |

**If 4+ metrics meet targets:** Phase 2 is a SUCCESS, consider Phase 3

**If 2-3 metrics meet targets:** Phase 2 is OK, continue monitoring

**If <2 metrics meet targets:** Phase 2 is a FAILURE, investigate or revert

---

## TROUBLESHOOTING GUIDE

### Issue: ComfyUI not responding

**Symptoms:** Health check fails, timeout errors

**Solutions:**
1. Check ComfyUI is running: `docker ps | grep comfyui`
2. Restart ComfyUI: `docker restart comfyui`
3. Check logs: `docker logs comfyui`
4. Verify port 8188 is open: `netstat -an | grep 8188`

---

### Issue: VRAM full (out of memory)

**Symptoms:** CUDA out of memory errors, GPU crashes

**Solutions:**
1. Unload Ollama: `curl -X POST http://localhost:11434/api/unload`
2. Use smaller model: Switch to SD 1.5 (6GB instead of SDXL 12GB)
3. Reduce image resolution: Generate 512x512 instead of 1024x1024
4. Clear GPU memory: `nvidia-smi --gpu-reset`
5. Fallback to cloud: Stability AI or DALL-E 3

---

### Issue: Slow generation (>2 minutes)

**Symptoms:** Images taking forever, users complaining

**Solutions:**
1. Check GPU utilization: `nvidia-smi`
2. Verify GPU mode (not CPU): Check ComfyUI startup flags
3. Reduce inference steps: 25 steps → 15 steps (faster, slight quality loss)
4. Use smaller model: SD 1.5 is 2x faster than SDXL
5. Check for other GPU-intensive processes

---

### Issue: Queue not processing

**Symptoms:** Requests stuck in queue, nothing happening

**Solutions:**
1. Check background task is running: Verify `process_queue()` is executing
2. Check for exceptions: Look in logs (`multimodal-logs/errors.log`)
3. Restart backend: `systemctl restart ziggie-backend`
4. Clear queue: `curl -X POST http://localhost:54112/api/multimodal/queue/clear`

---

## CONTACTS

**L1 Multimodal Integration Architect:** Design and strategy
**L2 Multimodal Generator Agent:** Implementation and maintenance
**L1 Resource Manager:** GPU allocation, cost optimization
**Control Center Team:** API integration, dashboard development

---

**Full Strategy:** `MULTIMODAL_INTEGRATION_STRATEGY.md`
**Quick Reference:** `MULTIMODAL_DECISION_MATRIX.md`
**This Checklist:** `MULTIMODAL_IMPLEMENTATION_CHECKLIST.md`

---

**END OF IMPLEMENTATION CHECKLIST**

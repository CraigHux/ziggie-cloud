# End-to-End Game Asset Creation Pipeline

> **Created**: 2025-12-29 (Session M)
> **Updated**: 2025-12-30 (Stage 4.5 Addition)
> **Purpose**: Comprehensive 8-stage asset pipeline with AI+Human approval gates
> **Target**: MeowPing RTS game assets (units, buildings, terrain, VFX)

---

## Executive Summary

This pipeline leverages **cloud GPU services** (RunPod, Meshy, Tripo, Colab, AWS) combined with **55+ FMHY tools** to create a production-ready asset workflow with quality gates at each stage.

**Pipeline Stages**:
1. 2D Image Generation (AI)
2. Cleanup/Background Removal (AI)
3. Upscaling/Enhancement (AI)
4. 2D to 3D Conversion (AI)
4.5. **Auto-Rigging & Animation (AI) - OPTIONAL**
5. 8-Direction Sprite Rendering (Blender)
6. Sprite Sheet Assembly (Automated)
7. Game Engine Integration (Automated)

**Total Tools Integrated**: 55+
**Estimated Time per Asset**: 15-45 minutes (depending on complexity)
**Approval Gates**: 8 (AI pre-filter + Human final approval)

---

## Pipeline Architecture Diagram

```
+------------------+     +------------------+     +------------------+
|  STAGE 1: 2D     |     |  STAGE 2: CLEANUP|     |  STAGE 3: UPSCALE|
|  Generation      | --> |  BG Removal      | --> |  Enhancement     |
|                  |     |                  |     |                  |
| - RunPod ComfyUI |     | - BRIA RMBG      |     | - Upscayl        |
| - Flux AI        |     | - Rembg          |     | - Real-ESRGAN    |
| - Pollinations   |     | - Segment Anything|    | - chaiNNer       |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
    [GATE 1]                 [GATE 2]                 [GATE 3]
    AI Pre-filter            AI Quality              AI Quality
    Human Approve            Human Approve           Human Approve
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|  STAGE 4: 2D->3D |     | STAGE 4.5: RIG   |     |  STAGE 5: RENDER |
|  Conversion      | --> |  (OPTIONAL)      | --> |  8-Direction     |
|                  |     |                  |     |                  |
| - Meshy.ai API   |     | - Tripo AI API   |     | - Blender CLI    |
| - TripoSR (Colab)|     | - Mixamo (manual)|     | - 8 Angles       |
| - Tripo3D        |     | - Cascadeur      |     | - Orthographic   |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
    [GATE 4]                 [GATE 4.5]              [GATE 5]
    AI Validation            Animation QA            Sprite QA
    Human Approve            Human Approve           Human Approve
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
+------------------+     +------------------+
|  STAGE 6: SPRITE |     |  STAGE 7: EXPORT |
|  Sheet Assembly  | --> |  Integration     |
|                  |     |                  |
| - PIL/Python     |     | - S3 Upload      |
| - 4x2 Grid       |     | - Engine Import  |
| - Power-of-2     |     | - Asset Database |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
    [GATE 6]                 [GATE 7]
    Format QA                Final QA
    Size Check               Game Ready
```

### Stage 3→4 Decision Tree (3D Service Selection)

```text
                    +------------------+
                    | Stage 3 Complete |
                    | (Upscaled 2D)    |
                    +--------+---------+
                             |
                 Discord Bot Prompt:
                 "Choose 3D Generation Service"
                             |
        +--------+-----------+-----------+--------+
        |        |           |           |        |
     MESHY    TRIPO     TRIPOSR      SKIP 3D
        |        |        (COLAB)        |
        v        v           |           v
   +--------+ +--------+     |     +----------+
   | Fast   | | Full   |     |     | 2D Only  |
   | Good   | | Pipeline|    |     | Sprites  |
   | Quality| | Support|     |     | No 3D    |
   +--------+ +--------+     |     +----------+
        |        |           |
        |        |           v
        |        |     +----------+
        |        |     | Free     |
        |        |     | Manual   |
        |        |     | Upload   |
        |        |     +----------+
        |        |           |
        v        v           v
   +---------------------------------+
   | Stage 4: 2D→3D Conversion      |
   +---------------------------------+
        |
   Animation available?
        |
   +----+----+
   |         |
 MESHY     TRIPO
   |         |
   v         v
 MANUAL    API
 ONLY    RIGGING

NOTE: Service choice at Gate 3 determines animation
options at Gate 4. Choosing Tripo AI enables full
auto-rig pipeline; other services require manual tools.
```

### Stage 4.5 Decision Tree (Animation Selection)

```text
                    +------------------+
                    |  GLB from Stage 4|
                    +--------+---------+
                             |
                 Discord Bot Prompt:
                 "Does this asset need animation?"
                             |
              +--------------+-------------+
              |                            |
             YES                          NO
              |                            |
    +--------------------+      +--------------------+
    | Source of 3D Model?|      | Stage 4.5: SKIP    |
    +---------+----------+      | (Pass-through)     |
              |                 +--------------------+
    +---------+----------+
    |                    |
  MESHY.AI            TRIPO.AI
    |                    |
    v                    v
+------------------+  +------------------+
| Option A:        |  | Option B:        |
| Manual Rigging   |  | Tripo Full       |
|                  |  | Pipeline         |
| - Mixamo.com     |  |                  |
| - Cascadeur      |  | - image_to_3d()  |
| - Blender Manual |  | - rig_model()    |
+------------------+  | - retarget()     |
                      +------------------+

NOTE: Tripo AI SDK requires models generated through their
pipeline for auto-rigging. External GLB files (Meshy.ai)
cannot be rigged via Tripo API - use manual tools instead.
```

---

## Stage 1: 2D Image Generation

### Primary Tools

| Tool | Cost | Best For | API |
|------|------|----------|-----|
| **RunPod ComfyUI** | $0.34-0.69/hr | Production batches | Yes |
| **Pollinations AI** | Free | Quick tests | Yes |
| **Flux AI** | Free tier | High quality | Yes |
| **ImagineArt** | Free (browser) | Unlimited free | Playwright |

### Workflow

```python
# n8n Workflow: 2D Generation
{
    "nodes": [
        {
            "name": "Prompt Input",
            "type": "Manual Trigger",
            "parameters": {
                "prompt": "{{ $json.prompt }}",
                "style": "{{ $json.style }}",  # dark_fantasy, stylized, cartoon
                "asset_type": "{{ $json.type }}"  # unit, building, terrain
            }
        },
        {
            "name": "RunPod ComfyUI",
            "type": "HTTP Request",
            "method": "POST",
            "url": "https://api.runpod.ai/v2/{{ $env.RUNPOD_ENDPOINT }}/runsync",
            "headers": {
                "Authorization": "Bearer {{ $env.RUNPOD_API_KEY }}"
            },
            "body": {
                "input": {
                    "workflow": "txt2img_sdxl",
                    "prompt": "{{ $json.prompt }}, isometric view, game asset, blue screen background",
                    "negative_prompt": "blurry, low quality, watermark",
                    "width": 1024,
                    "height": 1024,
                    "steps": 30,
                    "cfg_scale": 7.5
                }
            }
        },
        {
            "name": "Save to S3",
            "type": "AWS S3",
            "operation": "upload",
            "bucket": "ziggie-assets-prod",
            "key": "stage1-raw/{{ $json.asset_id }}.png"
        }
    ]
}
```

### Prompt Templates

```python
PROMPTS = {
    "unit_melee": """
        Cat warrior knight in medieval plate armor,
        holding sword and shield, fierce expression,
        isometric 45-degree view, game unit sprite,
        dark fantasy art style, highly detailed,
        solid blue background (#0000FF) for chroma key
    """,
    "unit_ranged": """
        Cat archer in leather armor,
        drawing bow with arrow, focused expression,
        isometric 45-degree view, game unit sprite,
        dark fantasy art style, highly detailed,
        solid blue background (#0000FF) for chroma key
    """,
    "building_barracks": """
        Medieval fantasy barracks building,
        stone walls with wooden beams, cat banners,
        isometric 45-degree view, RTS game building,
        dark fantasy architecture, highly detailed,
        solid blue background (#0000FF) for chroma key
    """,
    "terrain_grass": """
        Seamless tileable grass texture,
        top-down view for isometric game,
        fantasy meadow with small flowers,
        game terrain tile, 2D art style
    """
}
```

### Gate 1: AI Pre-Filter + Human Approval

```python
# AI Pre-Filter (Automated)
def gate_1_ai_filter(image_path: str) -> dict:
    """AI quality pre-filter before human review"""
    checks = {
        "resolution": check_resolution(image_path, min_size=1024),
        "has_subject": detect_subject(image_path),  # YOLO/SAM
        "blue_screen": detect_blue_background(image_path),
        "artifact_score": calculate_artifact_score(image_path),
        "style_match": check_style_consistency(image_path, reference_set)
    }

    passed = all([
        checks["resolution"],
        checks["has_subject"],
        checks["artifact_score"] < 0.3,
        checks["style_match"] > 0.7
    ])

    return {
        "passed": passed,
        "checks": checks,
        "recommendation": "APPROVE" if passed else "REJECT",
        "human_review_required": True  # Always require human final
    }

# Human Approval (via n8n + Discord/Slack)
def gate_1_human_approval(image_url: str, ai_report: dict) -> bool:
    """Send to human for approval via Discord/Slack"""
    # Post to approval channel with AI report
    # Wait for reaction (thumbs up/down)
    # Return approval status
    pass
```

---

## Stage 2: Cleanup & Background Removal

### Primary Tools

| Tool | Cost | Quality | API |
|------|------|---------|-----|
| **BRIA RMBG 2.0** | Free | Excellent | Hugging Face |
| **Rembg** | Free (self-host) | Excellent | Python |
| **remove.bg** | Freemium | Excellent | Yes |
| **Segment Anything** | Free | Excellent | Python |

### Workflow

```python
# Background Removal Pipeline
import rembg
from PIL import Image
import io

class BackgroundRemover:
    def __init__(self):
        self.model = rembg.new_session("u2net")

    def remove_background(self, input_path: str, output_path: str) -> dict:
        """Remove background using Rembg (self-hosted)"""
        with open(input_path, "rb") as f:
            input_data = f.read()

        # Remove background
        output_data = rembg.remove(
            input_data,
            session=self.model,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10
        )

        # Save result
        with open(output_path, "wb") as f:
            f.write(output_data)

        # Calculate quality metrics
        return {
            "input_size": len(input_data),
            "output_size": len(output_data),
            "alpha_coverage": self._calculate_alpha_coverage(output_data)
        }

    def _calculate_alpha_coverage(self, image_data: bytes) -> float:
        """Calculate percentage of transparent pixels"""
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        alpha = img.getchannel("A")
        transparent = sum(1 for p in alpha.getdata() if p < 128)
        return transparent / (img.width * img.height)
```

### Additional Cleanup Tools

| Tool | Purpose | Source |
|------|---------|--------|
| **GIMP** | Manual edge cleanup | FMHY |
| **Photopea** | Online cleanup | FMHY |
| **ImageMagick** | Batch processing | FMHY |

### Gate 2: Cleanup Quality

```python
def gate_2_cleanup_quality(image_path: str) -> dict:
    """Verify background removal quality"""
    img = Image.open(image_path).convert("RGBA")

    checks = {
        "has_alpha": img.mode == "RGBA",
        "edge_quality": analyze_edge_quality(img),
        "halo_detection": detect_color_halo(img),
        "subject_intact": verify_subject_integrity(img)
    }

    passed = all([
        checks["has_alpha"],
        checks["edge_quality"] > 0.8,
        not checks["halo_detection"],
        checks["subject_intact"]
    ])

    return {
        "passed": passed,
        "checks": checks,
        "issues": identify_cleanup_issues(checks)
    }
```

---

## Stage 3: Upscaling & Enhancement

### Primary Tools

| Tool | Scale | Quality | GPU Required |
|------|-------|---------|--------------|
| **Upscayl** | 2x-4x | Excellent | Optional |
| **Real-ESRGAN** | 2x-4x | Excellent | Recommended |
| **chaiNNer** | Custom | Excellent | Optional |
| **OpenModelDB** | Various | Models | N/A |

### Best Models for Game Assets

```python
UPSCALE_MODELS = {
    "units": {
        "model": "realesrgan-x4plus-anime",
        "scale": 4,
        "notes": "Best for stylized game characters"
    },
    "buildings": {
        "model": "realesrgan-x4plus",
        "scale": 4,
        "notes": "Best for architectural details"
    },
    "terrain": {
        "model": "realesrgan-x4plus",
        "scale": 2,
        "notes": "Keep tileable, lower scale"
    },
    "vfx": {
        "model": "realesrgan-x4plus-anime",
        "scale": 2,
        "notes": "Preserve particle details"
    }
}
```

### Workflow

```python
# Upscaling with Real-ESRGAN (via Google Colab - FREE)
COLAB_NOTEBOOK = """
# Real-ESRGAN Upscaling Notebook
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install Real-ESRGAN
!git clone https://github.com/xinntao/Real-ESRGAN.git
%cd Real-ESRGAN
!pip install basicsr facexlib gfpgan

# Download models
!wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights
!wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth -P weights

# Batch upscale
import os
input_dir = '/content/drive/MyDrive/MeowPing_Assets/stage2_cleanup'
output_dir = '/content/drive/MyDrive/MeowPing_Assets/stage3_upscaled'

for img in os.listdir(input_dir):
    if img.endswith('.png'):
        !python inference_realesrgan.py -n RealESRGAN_x4plus_anime_6B -i "{input_dir}/{img}" -o "{output_dir}" --face_enhance
        print(f"Upscaled: {img}")
"""
```

### Gate 3: Enhancement Quality

```python
def gate_3_enhancement_quality(original_path: str, upscaled_path: str) -> dict:
    """Verify upscaling quality"""
    original = Image.open(original_path)
    upscaled = Image.open(upscaled_path)

    expected_scale = 4  # or 2 depending on model

    checks = {
        "scale_correct": upscaled.width == original.width * expected_scale,
        "sharpness": calculate_sharpness(upscaled) > 0.7,
        "no_artifacts": detect_upscale_artifacts(upscaled) < 0.1,
        "color_preserved": color_similarity(original, upscaled) > 0.95,
        "alpha_preserved": alpha_channel_intact(original, upscaled)
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "original_size": f"{original.width}x{original.height}",
        "upscaled_size": f"{upscaled.width}x{upscaled.height}"
    }
```

---

## Stage 4: 2D to 3D Conversion

### Primary Tools

| Tool | Cost | Quality | API |
|------|------|---------|-----|
| **Meshy.ai** | $20/mo (1000 credits) | Excellent | Yes |
| **TripoSR** | Free (Colab) | Good | Python |
| **Tripo3D** | Freemium | Excellent | Yes |
| **OpenAI Point-E** | Free | Fair | Python |

### Meshy.ai Integration (Primary)

```python
import requests
import time

class MeshyAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.meshy.ai/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def image_to_3d(self, image_path: str, output_path: str) -> dict:
        """Convert 2D image to 3D model"""

        # 1. Upload image and start task
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/image-to-3d",
                headers=self.headers,
                files={"file": f}
            )

        task_id = response.json()["result"]
        print(f"Task started: {task_id}")

        # 2. Poll for completion
        while True:
            status = requests.get(
                f"{self.base_url}/image-to-3d/{task_id}",
                headers=self.headers
            ).json()

            if status["status"] == "SUCCEEDED":
                model_url = status["model_urls"]["glb"]

                # 3. Download GLB
                glb_data = requests.get(model_url).content
                with open(output_path, "wb") as f:
                    f.write(glb_data)

                return {
                    "success": True,
                    "task_id": task_id,
                    "output": output_path,
                    "model_urls": status["model_urls"]
                }

            elif status["status"] in ["FAILED", "EXPIRED"]:
                return {"success": False, "error": status.get("error")}

            time.sleep(5)  # Poll every 5 seconds
```

### TripoSR (Free Colab Alternative)

```python
TRIPOSR_COLAB = """
# TripoSR - Free 2D to 3D
# Works on Google Colab T4 GPU

!pip install torch torchvision
!pip install trimesh pymeshlab rembg
!git clone https://github.com/VAST-AI-Research/TripoSR.git
%cd TripoSR
!pip install -r requirements.txt

# Run inference
from PIL import Image
import trimesh

# Load model
model = load_triposr_model()

# Process images from Drive
input_dir = '/content/drive/MyDrive/MeowPing_Assets/stage3_upscaled'
output_dir = '/content/drive/MyDrive/MeowPing_Assets/stage4_3d'

for img_file in os.listdir(input_dir):
    if img_file.endswith('.png'):
        image = Image.open(f"{input_dir}/{img_file}")
        mesh = model.predict(image)
        mesh.export(f"{output_dir}/{img_file.replace('.png', '.glb')}")
        print(f"Converted: {img_file}")
"""
```

### Gate 4: 3D Conversion Quality

```python
import trimesh

def gate_4_3d_quality(model_path: str) -> dict:
    """Verify 3D model quality"""
    mesh = trimesh.load(model_path)

    checks = {
        "is_watertight": mesh.is_watertight,
        "vertex_count": mesh.vertices.shape[0],
        "face_count": mesh.faces.shape[0],
        "has_normals": mesh.vertex_normals is not None,
        "has_uvs": hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None,
        "bounding_box": mesh.bounding_box.extents.tolist(),
        "volume": mesh.volume if mesh.is_watertight else None
    }

    quality_score = calculate_mesh_quality(mesh)

    return {
        "passed": quality_score > 0.7,
        "quality_score": quality_score,
        "checks": checks,
        "recommendations": get_mesh_recommendations(checks)
    }

def calculate_mesh_quality(mesh) -> float:
    """Calculate overall mesh quality score (0-1)"""
    score = 0

    # Vertex count in good range (1000-50000)
    if 1000 < mesh.vertices.shape[0] < 50000:
        score += 0.25

    # Has proper normals
    if mesh.vertex_normals is not None:
        score += 0.25

    # Has UVs for texturing
    if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None:
        score += 0.25

    # No degenerate faces
    if len(mesh.degenerate_faces) == 0:
        score += 0.25

    return score
```

---

## Stage 4.5: Auto-Rigging & Animation (OPTIONAL)

> **Purpose**: Add skeleton rigging and animation to 3D models before sprite rendering
> **When to Use**: Only for units that need walk/attack/death animations
> **Skip for**: Buildings, terrain, props (static assets)

### Primary Tools

| Tool | Cost | Type | Automation |
|------|------|------|------------|
| **Tripo AI** | 300 free/mo | Cloud API | Full SDK |
| **Mixamo** | Free | Web UI | Manual upload |
| **Cascadeur** | Free tier | Desktop | Manual |
| **Blender** | Free | Desktop | Script-based |

### IMPORTANT: API Limitation

```text
⚠️  CRITICAL LIMITATION DISCOVERED:

Tripo AI's Python SDK (`pip install tripo3d`) can ONLY rig models
that were generated through Tripo's own pipeline.

External GLB files (from Meshy.ai, TripoSR, etc.) CANNOT be rigged
via the Tripo API. The `rig_model()` function requires an
`original_model_task_id` from a previous Tripo generation task.

WORKAROUNDS:
1. Use Tripo AI for BOTH 3D generation AND rigging (replaces Meshy.ai)
2. Use Mixamo.com for manual rigging (free, web-based)
3. Use Cascadeur for AI-assisted animation (desktop app)
4. Skip Stage 4.5 and render static sprites (default)
```

### Option A: Tripo AI Full Pipeline (Replaces Meshy.ai)

Use Tripo AI for the complete 2D→3D→Rig→Animate pipeline:

```python
import asyncio
from tripo3d import Client, RigSpec

async def tripo_full_pipeline(image_path: str, output_path: str, animation: str = None):
    """
    Full Tripo AI pipeline: Image → 3D → Rig → Animate

    Cost: Tripo AI credits (300 free/month on Basic plan)
    Time: ~2-4 minutes for complete pipeline
    """
    client = Client()

    # Step 1: Image to 3D (replaces Meshy.ai)
    print("[Stage 4] Generating 3D model via Tripo AI...")
    model_task = await client.image_to_model(image_path)
    model_result = await model_task.wait()

    if not model_result.model:
        return False, "3D generation failed"

    print(f"[Stage 4] 3D model generated: {model_result.model.task_id}")

    # Step 2: Check if model can be rigged
    print("[Stage 4.5] Checking riggability...")
    riggable = await client.check_riggable(model_result.model.task_id)

    if not riggable.is_riggable:
        # Download static model
        await model_result.model.download_glb(output_path)
        return True, output_path  # Static model, no animation

    # Step 3: Auto-rig with skeleton
    print("[Stage 4.5] Auto-rigging model...")
    rig_task = await client.rig_model(
        original_model_task_id=model_result.model.task_id,
        spec=RigSpec.MIXAMO  # or RigSpec.TRIPO
    )
    rig_result = await rig_task.wait()

    if not rig_result.model:
        return False, "Rigging failed"

    # Step 4: Apply animation (optional)
    if animation:
        print(f"[Stage 4.5] Applying animation: {animation}...")
        anim_task = await client.retarget_animation(
            original_model_task_id=rig_result.model.task_id,
            animation=animation  # "idle", "walk", "run", "jump"
        )
        anim_result = await anim_task.wait()

        if anim_result.model:
            await anim_result.model.download_glb(output_path)
            return True, output_path

    # Download rigged (non-animated) model
    await rig_result.model.download_glb(output_path)
    return True, output_path

# Usage
asyncio.run(tripo_full_pipeline(
    "warrior_upscaled.png",
    "warrior_rigged.glb",
    animation="walk"
))
```

### Option B: Mixamo Manual Rigging (For Meshy.ai GLBs)

```python
# Mixamo is web-based, requires manual upload
MIXAMO_WORKFLOW = """
1. Export GLB from Stage 4 (Meshy.ai output)
2. Go to mixamo.com and sign in (free Adobe account)
3. Upload Character:
   - Click "Upload Character"
   - Select your GLB/FBX file
   - Wait for auto-rigging (~30 seconds)
4. Auto-Rig Setup:
   - Position markers: chin, wrists, elbows, groin, knees
   - Click "Next" for skeleton preview
   - Adjust if needed, then "Finish"
5. Select Animations:
   - idle: "Idle" or "Breathing Idle"
   - walk: "Walking" (8-frame loop)
   - attack: "Sword And Shield Slash"
   - death: "Dying"
6. Download Settings:
   - Format: FBX Binary
   - Skin: With Skin
   - Frames per Second: 30
   - Keyframe Reduction: Uniform
7. Import to Blender for Stage 5 rendering
"""
```

### Option C: Skip (Static Sprites)

```python
def stage4_5_skip(glb_path: str) -> tuple[bool, str]:
    """
    Skip Stage 4.5: Pass through static GLB to Stage 5.

    Use this for:
    - Buildings (no animation needed)
    - Terrain tiles (static)
    - Props/decorations (static)
    - Quick prototyping (animation later)
    """
    print(f"[Stage 4.5] Skipped - passing static GLB to Stage 5")
    return True, glb_path
```

### Gate 4.5: Animation Quality

```python
def gate_4_5_animation_quality(model_path: str) -> dict:
    """Verify rigged/animated model quality"""
    import trimesh

    mesh = trimesh.load(model_path)

    # Check for skeleton/armature
    has_skeleton = hasattr(mesh, 'skeleton') or 'armature' in str(mesh.metadata)

    checks = {
        "has_skeleton": has_skeleton,
        "bone_count": count_bones(model_path) if has_skeleton else 0,
        "animation_clips": count_animations(model_path),
        "vertex_weights": verify_vertex_weights(model_path),
        "deformation_clean": check_deformation_quality(model_path)
    }

    # Static models pass automatically
    if not has_skeleton:
        return {
            "passed": True,
            "type": "static",
            "checks": checks,
            "note": "Static model - no rigging required"
        }

    # Animated models need quality checks
    passed = all([
        checks["bone_count"] >= 15,  # Minimum humanoid skeleton
        checks["vertex_weights"],
        checks["deformation_clean"]
    ])

    return {
        "passed": passed,
        "type": "animated",
        "checks": checks
    }
```

### Tripo AI Pricing

| Plan | Credits/Month | Cost | Notes |
| ---- | ------------- | ---- | ----- |
| Basic | 300 | Free | Good for testing |
| Pro | 3000 | $24/mo | Production use |
| Enterprise | Custom | Contact | High volume |

**Credit Usage**:

- Image to 3D: ~50 credits
- Rigging: ~30 credits
- Animation: ~20 credits
- **Full pipeline**: ~100 credits per asset

---

## Stage 5: 8-Direction Sprite Rendering

### Primary Tools

| Tool | Purpose | Cost |
|------|---------|------|
| **Blender** | Full 3D editing | Free |
| **MagicaVoxel** | Voxel editing | Free |
| **Blockbench** | Simple models | Free |

### Blender Automation Scripts

```python
# Blender Python Script: Auto-fix common issues
import bpy
import bmesh

def auto_fix_mesh():
    """Automatic mesh cleanup and optimization"""
    obj = bpy.context.active_object

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    # 1. Remove doubles (merge close vertices)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    # 2. Recalculate normals (fix inside-out faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # 3. Fill holes
    bmesh.ops.holes_fill(bm, edges=bm.edges)

    # Update mesh
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return {
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "status": "cleaned"
    }

def generate_lod_levels():
    """Generate LOD levels for game optimization"""
    obj = bpy.context.active_object
    lods = []

    ratios = [1.0, 0.5, 0.25, 0.1]  # LOD0, LOD1, LOD2, LOD3

    for i, ratio in enumerate(ratios):
        # Duplicate
        bpy.ops.object.duplicate()
        lod_obj = bpy.context.active_object
        lod_obj.name = f"{obj.name}_LOD{i}"

        # Decimate
        modifier = lod_obj.modifiers.new(name="Decimate", type='DECIMATE')
        modifier.ratio = ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

        lods.append({
            "name": lod_obj.name,
            "ratio": ratio,
            "faces": len(lod_obj.data.polygons)
        })

    return lods
```

### Texture Enhancement

```python
# Material Maker - Procedural PBR textures
TEXTURE_WORKFLOW = """
1. Import base texture from Stage 3
2. Generate PBR maps:
   - Albedo (from original)
   - Normal map (auto-generated)
   - Roughness map (auto-generated)
   - Ambient Occlusion (baked)
3. Apply to 3D model
4. Export texture atlas
"""

# Tools for texture generation
TEXTURE_TOOLS = {
    "Material Maker": "https://rodzilla.itch.io/material-maker",
    "ArmorLab": "https://armory3d.org/lab/",
    "TextureLab": "https://njbrown.itch.io/texturelab",
    "AmbientCG": "https://ambientcg.com/"  # Free PBR textures
}
```

### Gate 5: 3D Perfection Quality

```python
def gate_5_perfection_quality(model_path: str, texture_path: str) -> dict:
    """Human QA gate for 3D model perfection"""

    automated_checks = {
        "lod_levels": verify_lod_levels(model_path),
        "uv_unwrapped": verify_uv_mapping(model_path),
        "texture_resolution": check_texture_resolution(texture_path),
        "pbr_complete": verify_pbr_maps(texture_path),
        "poly_budget": check_poly_budget(model_path, max_tris=10000)
    }

    human_review = {
        "silhouette_readable": None,  # Human checks
        "proportions_correct": None,
        "style_consistent": None,
        "game_ready": None
    }

    return {
        "automated": automated_checks,
        "human_review": human_review,
        "passed": all(automated_checks.values())  # Human overrides possible
    }
```

---

## Stage 6: 3D Animation

### Primary Tools

| Tool | Purpose | Cost |
|------|---------|------|
| **Blender** | Manual animation | Free |
| **Mixamo** | Auto-rigging + animations | Free |
| **Cascadeur** | AI-assisted animation | Free tier |
| **AI Video Gen** | Reference animation | Various |

### Mixamo Auto-Rigging Pipeline

```python
# Mixamo integration for character rigging
MIXAMO_WORKFLOW = """
1. Export character as FBX (T-pose, no rig)
2. Upload to mixamo.com
3. Auto-rig with bone mapping
4. Select animations:
   - Idle (4 frames)
   - Walk cycle (8 frames)
   - Attack (6 frames)
   - Death (4 frames)
5. Download as FBX with animations
6. Import to Blender for cleanup
"""

# Blender animation bake script
import bpy

def bake_animation_to_sprite_frames(obj_name: str, animation_name: str, output_dir: str):
    """Render animation frames from 8 directions"""
    obj = bpy.data.objects[obj_name]
    action = bpy.data.actions[animation_name]

    frame_start = int(action.frame_range[0])
    frame_end = int(action.frame_range[1])

    # 8 camera angles for isometric sprites
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    direction_names = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW']

    for angle, dir_name in zip(angles, direction_names):
        # Set camera rotation
        camera = bpy.data.objects['Camera']
        camera.rotation_euler[2] = math.radians(angle)

        for frame in range(frame_start, frame_end + 1):
            bpy.context.scene.frame_set(frame)

            # Render frame
            output_path = f"{output_dir}/{animation_name}_{dir_name}_{frame:03d}.png"
            bpy.context.scene.render.filepath = output_path
            bpy.ops.render.render(write_still=True)

    return {"frames_rendered": (frame_end - frame_start + 1) * len(angles)}
```

### AI Video Generation for Animation Reference

```python
# Use AI video generation for animation inspiration/reference
AI_VIDEO_TOOLS = {
    "Grok Imagine": {
        "url": "https://grok.com/imagine",
        "free_quota": "30/day",
        "use_case": "Quick animation concepts"
    },
    "Wan AI": {
        "url": "https://wan.video/",
        "free_quota": "10/day",
        "use_case": "Image to video animation"
    },
    "GeminiGen AI": {
        "url": "https://geminigen.ai/",
        "free_quota": "Unlimited (Sora 2 / Veo 3.1)",
        "use_case": "High quality reference"
    },
    "Dreamina": {
        "url": "https://dreamina.capcut.com/",
        "free_quota": "129 credits/day",
        "use_case": "CapCut integration"
    }
}
```

### Gate 6: Animation Quality

```python
def gate_6_animation_quality(sprite_sheet_path: str, animation_data: dict) -> dict:
    """Verify animation quality"""

    automated_checks = {
        "frame_count": verify_frame_count(animation_data),
        "direction_count": verify_8_directions(sprite_sheet_path),
        "consistent_size": verify_frame_sizes(sprite_sheet_path),
        "loop_smooth": analyze_loop_smoothness(sprite_sheet_path),
        "timing_correct": verify_animation_timing(animation_data)
    }

    human_review = {
        "motion_natural": None,  # Human checks
        "impact_readable": None,
        "style_consistent": None,
        "game_feel_good": None
    }

    return {
        "automated": automated_checks,
        "human_review": human_review,
        "animation_data": animation_data
    }
```

---

## Stage 7: Game Engine Integration

### Sprite Sheet Assembly

```python
from PIL import Image
import os

def assemble_sprite_sheet(
    frames_dir: str,
    output_path: str,
    columns: int = 4,
    frame_size: tuple = (128, 128)
) -> dict:
    """Assemble frames into sprite sheet"""

    frames = sorted([
        f for f in os.listdir(frames_dir)
        if f.endswith('.png')
    ])

    rows = (len(frames) + columns - 1) // columns
    sheet_width = columns * frame_size[0]
    sheet_height = rows * frame_size[1]

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    for i, frame_file in enumerate(frames):
        frame = Image.open(os.path.join(frames_dir, frame_file))
        frame = frame.resize(frame_size, Image.LANCZOS)

        x = (i % columns) * frame_size[0]
        y = (i // columns) * frame_size[1]

        sheet.paste(frame, (x, y))

    sheet.save(output_path)

    return {
        "output": output_path,
        "dimensions": f"{sheet_width}x{sheet_height}",
        "frames": len(frames),
        "layout": f"{columns}x{rows}"
    }

# Sprite sheet standard for MeowPing RTS
SPRITE_STANDARDS = {
    "unit": {
        "frame_size": (128, 128),
        "directions": 8,
        "animations": {
            "idle": 4,
            "walk": 8,
            "attack": 6,
            "death": 4
        }
    },
    "building": {
        "frame_size": (256, 256),
        "directions": 1,
        "animations": {
            "idle": 1,
            "construction": 8,
            "destruction": 6
        }
    }
}
```

### Asset Database Registration

```python
import json
from datetime import datetime

def register_asset(asset_data: dict, database_path: str = "asset_database.json"):
    """Register completed asset in database"""

    # Load existing database
    try:
        with open(database_path, 'r') as f:
            database = json.load(f)
    except FileNotFoundError:
        database = {"assets": [], "metadata": {"created": datetime.now().isoformat()}}

    # Create asset entry
    asset_entry = {
        "id": generate_asset_id(),
        "name": asset_data["name"],
        "type": asset_data["type"],  # unit, building, terrain, vfx
        "category": asset_data["category"],  # warrior, archer, barracks, etc.
        "style": asset_data["style"],  # dark_fantasy, stylized, cartoon
        "quality_rating": asset_data["quality_rating"],  # AAA, AA, A, Poor
        "files": {
            "sprite_sheet": asset_data["sprite_sheet_path"],
            "3d_model": asset_data.get("model_path"),
            "source_2d": asset_data["source_path"]
        },
        "metadata": {
            "created": datetime.now().isoformat(),
            "pipeline_version": "1.0",
            "generation_tools": asset_data.get("tools_used", []),
            "approval_gates": asset_data.get("gate_results", {})
        }
    }

    database["assets"].append(asset_entry)
    database["metadata"]["updated"] = datetime.now().isoformat()
    database["metadata"]["total_assets"] = len(database["assets"])

    # Save database
    with open(database_path, 'w') as f:
        json.dump(database, f, indent=2)

    return asset_entry
```

### Gate 7: Final Integration QA

```python
def gate_7_final_qa(asset_entry: dict) -> dict:
    """Final quality assurance before game-ready status"""

    checks = {
        # File integrity
        "sprite_sheet_exists": os.path.exists(asset_entry["files"]["sprite_sheet"]),
        "sprite_sheet_valid": validate_png(asset_entry["files"]["sprite_sheet"]),

        # Technical requirements
        "correct_dimensions": verify_sprite_dimensions(asset_entry),
        "power_of_two": is_power_of_two(asset_entry["files"]["sprite_sheet"]),
        "file_size_ok": check_file_size(asset_entry, max_mb=5),

        # Game engine compatibility
        "unity_compatible": verify_unity_import(asset_entry),
        "godot_compatible": verify_godot_import(asset_entry),

        # Documentation
        "metadata_complete": verify_metadata(asset_entry),
        "naming_convention": verify_naming(asset_entry)
    }

    passed = all(checks.values())

    if passed:
        # Upload to S3 production bucket
        upload_to_production(asset_entry)

        # Update game asset manifest
        update_game_manifest(asset_entry)

    return {
        "passed": passed,
        "checks": checks,
        "status": "GAME_READY" if passed else "NEEDS_FIXES",
        "asset_id": asset_entry["id"]
    }
```

---

## Complete n8n Master Workflow

```json
{
    "name": "MeowPing Asset Pipeline",
    "nodes": [
        {
            "name": "Trigger: New Asset Request",
            "type": "Webhook",
            "parameters": {
                "path": "asset-pipeline",
                "method": "POST"
            }
        },
        {
            "name": "Stage 1: 2D Generation",
            "type": "HTTP Request",
            "url": "https://api.runpod.ai/v2/.../runsync"
        },
        {
            "name": "Gate 1: AI Filter",
            "type": "Function",
            "code": "// AI quality check"
        },
        {
            "name": "Gate 1: Human Approval",
            "type": "Discord",
            "action": "Send message with reactions"
        },
        {
            "name": "Stage 2: BG Removal",
            "type": "HTTP Request",
            "url": "https://briaai-bria-rmbg-2-0.hf.space/api/predict"
        },
        {
            "name": "Gate 2: Cleanup QA",
            "type": "Function"
        },
        {
            "name": "Stage 3: Upscale",
            "type": "Google Colab Trigger",
            "notebook": "real_esrgan_batch"
        },
        {
            "name": "Gate 3: Upscale QA",
            "type": "Function"
        },
        {
            "name": "Stage 4: 2D to 3D",
            "type": "HTTP Request",
            "url": "https://api.meshy.ai/v1/image-to-3d"
        },
        {
            "name": "Gate 4: 3D Validation",
            "type": "Function"
        },
        {
            "name": "Stage 5: 3D Perfection",
            "type": "Blender Script Trigger"
        },
        {
            "name": "Gate 5: Human 3D QA",
            "type": "Discord"
        },
        {
            "name": "Stage 6: Animation",
            "type": "Mixamo + Blender"
        },
        {
            "name": "Gate 6: Animation QA",
            "type": "Discord"
        },
        {
            "name": "Stage 7: Integration",
            "type": "Function",
            "code": "// Sprite sheet + database"
        },
        {
            "name": "Gate 7: Final QA",
            "type": "Function"
        },
        {
            "name": "Output: Game Ready",
            "type": "S3 Upload + Slack Notification"
        }
    ]
}
```

---

## Cost Analysis

### Per-Asset Cost Breakdown

| Stage | Tool | Cost per Asset |
|-------|------|----------------|
| 1. 2D Generation | RunPod ComfyUI | ~$0.05-0.10 |
| 2. BG Removal | BRIA RMBG | Free |
| 3. Upscaling | Colab Real-ESRGAN | Free |
| 4. 2D to 3D | Meshy.ai | ~$0.02 (1000 credits = $20) |
| 5. 3D Perfection | Blender | Free |
| 6. Animation | Mixamo + Blender | Free |
| 7. Integration | n8n + S3 | ~$0.001 |
| **TOTAL** | | **~$0.07-0.13 per asset** |

### Monthly Estimates

| Production Level | Assets/Month | Monthly Cost |
|------------------|--------------|--------------|
| Low (100 assets) | 100 | ~$10-15 |
| Medium (500 assets) | 500 | ~$40-65 |
| High (2000 assets) | 2000 | ~$150-260 |

---

## Additional FMHY Tools by Stage

### Stage 1 Enhancements
- **Pollinations AI**: Free unlimited API for testing
- **Flux AI**: Alternative high-quality generation

### Stage 2 Enhancements
- **Segment Anything**: Visual segmentation for complex subjects
- **Photopea**: Online manual cleanup (free Photoshop)

### Stage 3 Enhancements
- **OpenModelDB**: Download specialized upscale models
- **chaiNNer**: Node-based batch processing

### Stage 5 Enhancements
- **Material Maker**: Procedural PBR texture generation
- **AmbientCG**: Free PBR texture library
- **ArmorLab**: AI-powered texture painting

### Stage 4.5 Enhancements
- **Tripo AI SDK**: `pip install tripo3d` for automated rigging
- **Cascadeur**: AI-assisted animation (physics-based, desktop)
- **Mixamo**: Free web-based auto-rigging (manual upload)

### Stage 6 Enhancements
- **BFXR / ChipTone / jsfxr**: Sound effects for animations

### Audio Pipeline (Bonus Stage)
- **ElevenLabs**: Voice lines for units
- **BFXR**: Attack/impact sounds
- **LMMS / Ardour**: Music composition

---

## Quick Start Commands

```bash
# 1. Setup RunPod API
export RUNPOD_API_KEY="your_key_here"

# 2. Setup Meshy API
export MESHY_API_KEY="your_key_here"

# 3. Install local tools
pip install rembg pillow trimesh

# 4. Clone upscaling models
git clone https://github.com/xinntao/Real-ESRGAN.git

# 5. Test single asset
python scripts/run_pipeline.py --input concept.png --output ./output/

# 6. Batch process
python scripts/batch_pipeline.py --input ./concepts/ --output ./assets/
```

---

---

## Bonus Stage: Audio Pipeline

Game assets need audio! Here's a complete audio pipeline using FMHY tools.

### Sound Effects Generation

| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| **BFXR** | Retro/8-bit SFX | Free | https://www.bfxr.net/ |
| **ChipTone** | Chiptune SFX | Free | https://sfbgames.itch.io/chiptone |
| **jsfxr** | Quick SFX | Free | https://sfxr.me/ |
| **Freesound** | Sound library | Free | https://freesound.org/ |

### Voice Line Generation

| Tool | Purpose | Cost | API |
|------|---------|------|-----|
| **ElevenLabs** | High-quality TTS | Freemium | Yes |
| **Bark** | Expressive TTS | Free | Python |
| **Coqui TTS** | Open-source TTS | Free | Python |
| **RVC** | Voice conversion | Free | Python |

### Music Composition

| Tool | Purpose | Cost |
|------|---------|------|
| **LMMS** | Full DAW | Free |
| **Ardour** | Professional DAW | Free |
| **Suno AI** | AI music generation | Freemium |

### Audio Workflow

```python
# Unit Voice Lines Pipeline
VOICE_WORKFLOW = {
    "1_script": "Write voice lines for each unit type",
    "2_generate": "Use ElevenLabs with custom voice",
    "3_process": "Normalize volume, add effects in Audacity",
    "4_export": "WAV 44.1kHz 16-bit for game engine",
    "5_integrate": "Add to sprite metadata"
}

# SFX for animations
SFX_MAPPING = {
    "attack_sword": "bfxr_slash_01.wav",
    "attack_bow": "bfxr_arrow_01.wav",
    "death": "bfxr_death_01.wav",
    "footsteps": "freesound_footsteps_grass.wav"
}
```

---

## Multi-Machine Pipeline Sync

For teams working across multiple machines, use these FMHY tools:

### SyncThing (Self-Hosted)

```bash
# Install SyncThing
winget install Syncthing.Syncthing

# Configure folders to sync:
# - C:/MeowPing_Assets/concepts/
# - C:/MeowPing_Assets/stage1_raw/
# - C:/MeowPing_Assets/final_sprites/

# Real-time sync between:
# - Local dev machine
# - Hostinger VPS
# - AWS EC2 (when available)
```

### rclone to Google Drive

```bash
# Sync to Google Drive for Colab access
rclone sync ./stage2_cleanup gdrive:MeowPing_Assets/stage2_cleanup -P

# Sync from Drive after Colab processing
rclone sync gdrive:MeowPing_Assets/stage3_upscaled ./stage3_upscaled -P
```

---

## Backup Strategy

### restic for Asset Backups

```bash
# Initialize restic repository
restic init --repo s3:s3.amazonaws.com/ziggie-backups/assets

# Daily backup of processed assets
restic backup ./final_sprites ./3d_models ./audio \
  --repo s3:s3.amazonaws.com/ziggie-backups/assets \
  --tag daily

# Weekly full backup
restic backup ./MeowPing_Assets \
  --repo s3:s3.amazonaws.com/ziggie-backups/assets \
  --tag weekly

# Prune old backups (keep 7 daily, 4 weekly)
restic forget --keep-daily 7 --keep-weekly 4 --prune
```

---

## Pipeline Monitoring Dashboard

### n8n Webhook Endpoints

```javascript
// Pipeline status endpoints
const ENDPOINTS = {
    start: "/webhook/asset-pipeline",
    status: "/webhook/pipeline-status/:id",
    cancel: "/webhook/pipeline-cancel/:id",
    batch: "/webhook/batch-pipeline"
}

// Slack/Discord notifications
const NOTIFICATIONS = {
    started: "#asset-pipeline: New asset ${id} started",
    gate_passed: "#asset-pipeline: Asset ${id} passed Gate ${gate}",
    gate_failed: "#asset-pipeline: Asset ${id} FAILED Gate ${gate}",
    completed: "#asset-pipeline: Asset ${id} COMPLETED - Game Ready!"
}
```

### Grafana Dashboard Metrics

```yaml
# Prometheus metrics for pipeline monitoring
metrics:
  - name: pipeline_assets_total
    help: Total assets processed
    type: counter

  - name: pipeline_stage_duration_seconds
    help: Duration of each stage
    type: histogram

  - name: pipeline_gate_pass_rate
    help: Pass rate per gate
    type: gauge

  - name: pipeline_active_jobs
    help: Currently active pipeline jobs
    type: gauge
```

---

## Tool Alternatives Reference

For each critical tool, here are backup alternatives from FMHY:

### 2D Generation Alternatives
| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| RunPod ComfyUI | Pollinations AI (free) | Flux AI |
| AUTOMATIC1111 | Fooocus (simple) | InvokeAI |

### Background Removal Alternatives
| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| BRIA RMBG | Rembg (local) | remove.bg |
| Segment Anything | BG Bye | Photopea (manual) |

### Upscaling Alternatives
| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| Real-ESRGAN | Upscayl (desktop) | chaiNNer |
| Waifu2x | OpenModelDB | Topaz (paid) |

### 2D to 3D Alternatives
| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| Meshy.ai | TripoSR (Colab) | Tripo3D |
| Point-E | Shap-E | Instant3D |

### 3D Editing Alternatives
| Primary | Alternative 1 | Alternative 2 |
|---------|---------------|---------------|
| Blender | MagicaVoxel | Blockbench |

---

## Complete FMHY Tool Integration Summary

### Total Tools Integrated: 50+

| Category | Count | Key Tools |
|----------|-------|-----------|
| AI Image Gen | 7 | ComfyUI, Flux, Pollinations |
| BG Removal | 5 | BRIA, Rembg, Segment Anything |
| Upscaling | 5 | Real-ESRGAN, Upscayl, chaiNNer |
| 2D to 3D | 4 | Meshy, TripoSR, Tripo3D |
| 3D Editing | 3 | Blender, MagicaVoxel, Blockbench |
| Animation | 4 | Mixamo, Cascadeur, AI Video |
| Textures | 4 | Material Maker, AmbientCG, ArmorLab |
| Audio/SFX | 6 | ElevenLabs, BFXR, ChipTone |
| DAW | 3 | LMMS, Ardour, Reaper |
| Image Edit | 4 | GIMP, Photopea, Krita, Inkscape |
| Automation | 3 | n8n, Playwright, Huginn |
| File Sync | 3 | SyncThing, rclone, LocalSend |
| Backup | 3 | restic, Kopia, Duplicati |
| **TOTAL** | **54** | |

---

## Next Steps

1. **Immediate**: Test Stage 1-3 with RunPod + BRIA + Colab
2. **Week 1**: Integrate Meshy.ai for Stage 4
3. **Week 2**: Set up Blender automation for Stage 5-6
4. **Week 3**: Complete n8n workflow integration
5. **Ongoing**: Refine approval gates based on production experience

---

**Document Status**: Complete
**Pipeline Version**: 1.0
**Last Updated**: 2025-12-29
**Author**: Session M (Ziggie Ecosystem)

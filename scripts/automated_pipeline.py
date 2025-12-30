"""
Automated Asset Pipeline - Stages 1-7 (+ Stage 4.5 Animation)
==============================================================
AI-controlled pipeline with human approval gates only.

Stage 1: 2D Generation (RunPod Serverless API or ComfyUI API)
Stage 2: Background Removal (BRIA RMBG via Gradio Client - FREE)
Stage 3: Upscaling (Replicate API or PIL Lanczos fallback)
Stage 4: 2D to 3D Conversion (Meshy.ai API)
Stage 4.5: Auto-Rigging & Animation (Tripo AI API) - OPTIONAL
Stage 5: 8-Direction Sprite Rendering (Blender CLI - Local or VPS)
Stage 6: Sprite Sheet Assembly (PIL - combines 8 dirs into 4x2 sheet)
Stage 7: Faction Color Variants (PIL HSV shift - red/blue/green/gold)

Human only approves/rejects at gates - AI does all the work.

Cloud vs Local Distribution:
- Stage 1: RunPod (cloud GPU)      - SDXL needs GPU
- Stage 2: HuggingFace (cloud)     - BRIA RMBG model needs GPU
- Stage 3: Local PIL               - CPU-only, instant (<1s)
- Stage 4: Meshy.ai (cloud API)    - 3D inference needs GPU
- Stage 4.5: Tripo AI (cloud API)  - Auto-rigging needs GPU
- Stage 5: Hostinger VPS (cloud)   - Blender headless rendering
- Stage 6: Local PIL               - CPU-only, instant (<1s)
- Stage 7: Local PIL               - CPU-only, instant (<1s)

Tested and Working (Session M - 2025-12-29):
- Stage 1: RunPod SDXL Serverless (994KB image in ~200s)
- Stage 2: BRIA RMBG Gradio API
- Stage 3: PIL Lanczos fallback (Replicate requires API token)
- Stage 4: Meshy.ai API (9.95MB GLB in ~4min)
- Stage 5: Blender 8-direction render - TWO MODES:
    - Local: Blender 5.0 on Windows (for local development)
    - Remote: Blender 4.0 on Hostinger VPS (headless, xvfb-run)
  Both modes tested working: 8 sprites @ 512x512 (~45s on VPS)
- Stage 6: PIL sprite sheet assembly (8 sprites -> 2048x1024 sheet)
- Stage 7: PIL HSV shift faction colors (4 variants in <1s)
"""

import os
import sys
import io
import json
import time
import base64
import shutil
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List

# Import notification system (optional)
try:
    from pipeline_notifications import notify_stage_complete, notify_pipeline_complete, request_approval
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False

# Fix Windows console encoding for Unicode (only if not already wrapped)
if sys.platform == 'win32' and not isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # Already wrapped or not a file-like object

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try VPS path first, then local path
    env_paths = [
        Path("/opt/ziggie/configs/.env"),  # VPS path
        Path("/opt/ziggie/.env"),          # VPS alt path
        Path(__file__).parent.parent / "configs" / ".env",  # Local path
        Path(__file__).parent.parent / ".env",  # Local alt path
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"[Config] Loaded environment from: {env_path}")
            break
except ImportError:
    pass  # python-dotenv not installed, rely on system environment

# Configuration
CONFIG = {
    "input_dir": "C:/Ziggie/assets/concepts",
    "output_dir": "C:/Ziggie/assets/test-results",
    "stage1_output": "C:/Ziggie/assets/test-results/stage1_generated",
    "stage2_output": "C:/Ziggie/assets/test-results/stage2_nobg",
    "stage3_output": "C:/Ziggie/assets/test-results/stage3_upscaled",
    "stage4_output": "C:/Ziggie/assets/test-results/stage4_3d",
    "stage4_5_output": "C:/Ziggie/assets/test-results/stage4_5_rigged",
    "stage5_output": "C:/Ziggie/assets/test-results/stage5_sprites",
    "stage6_output": "C:/Ziggie/assets/test-results/stage6_sheets",
    "stage7_output": "C:/Ziggie/assets/test-results/stage7_factions",

    # Discord Notifications
    "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
    "discord_notifications": True,  # Set to False to disable

    # API Keys (from environment or AWS Secrets Manager)
    "huggingface_token": os.getenv("HUGGINGFACE_TOKEN"),
    "replicate_token": os.getenv("REPLICATE_API_TOKEN"),
    "runpod_api_key": os.getenv("RUNPOD_API_KEY"),
    "meshy_api_key": os.getenv("MESHY_API_KEY"),
    "tripo_api_key": os.getenv("TRIPO_API_KEY"),

    # Local Blender (Windows)
    "blender_path": "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe",
    "blender_script": "C:/Ziggie/scripts/blender_8dir_render.py",

    # Remote VPS (Hostinger) - Blender headless rendering
    "vps_host": "82.25.112.73",
    "vps_user": "root",
    "vps_blender_script": "/opt/ziggie/scripts/blender_8dir_render.py",
    "vps_work_dir": "/opt/ziggie",
}
# VPS Environment Detection - Apply VPS paths if running on Hostinger
import platform
if platform.system() == "Linux" and Path("/opt/ziggie").exists():
    try:
        from vps_config import apply_vps_config
        CONFIG = apply_vps_config(CONFIG)
        print("[VPS] Running on Hostinger VPS - paths configured for /opt/ziggie")
    except ImportError:
        print("[VPS] Warning: vps_config.py not found, using default paths")


# Ensure output directories exist
for dir_path in [CONFIG["output_dir"], CONFIG["stage1_output"],
                 CONFIG["stage2_output"], CONFIG["stage3_output"],
                 CONFIG["stage4_output"], CONFIG["stage4_5_output"],
                 CONFIG["stage5_output"]]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)


class PipelineLogger:
    """Structured logging for pipeline operations."""

    def __init__(self, log_file: str = None):
        self.log_file = log_file or f"{CONFIG['output_dir']}/pipeline_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.logs = []

    def log(self, stage: str, action: str, status: str, details: Dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "action": action,
            "status": status,
            "details": details or {}
        }
        self.logs.append(entry)
        print(f"[{stage}] {action}: {status}")

    def save(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)


logger = PipelineLogger()


def send_notification(stage_name: str, success: bool, output_path: str = None, details: dict = None):
    """Send Discord notification if enabled."""
    if not NOTIFICATIONS_ENABLED or not CONFIG.get("discord_notifications"):
        return

    try:
        notify_stage_complete(
            stage_name=stage_name,
            success=success,
            output_path=output_path,
            details=details,
            webhook_url=CONFIG.get("discord_webhook_url")
        )
    except Exception as e:
        print(f"[Notification] Error sending: {e}")


# =============================================================================
# STAGE 2: Background Removal (BRIA RMBG via Gradio Client - TESTED WORKING)
# =============================================================================

def stage2_remove_background(image_path: str, output_path: str = None) -> Tuple[bool, str]:
    """
    Remove background using BRIA RMBG via Gradio Client API.

    This is FREE and automated - no manual browser interaction needed.
    TESTED WORKING: Session M (2025-12-29)

    Args:
        image_path: Path to input image (JPG/PNG)
        output_path: Path for output PNG (optional, auto-generated if not provided)

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 2", "Starting background removal", "IN_PROGRESS", {"input": image_path})

    # Check if file exists
    if not os.path.exists(image_path):
        logger.log("Stage 2", "File not found", "FAILED", {"path": image_path})
        return False, ""

    try:
        from gradio_client import Client, handle_file

        # Connect to BRIA RMBG Space
        logger.log("Stage 2", "Connecting to BRIA RMBG", "IN_PROGRESS")
        client = Client('briaai/BRIA-RMBG-2.0', verbose=False)

        # Call API - parameter is 'image' not 'images'
        logger.log("Stage 2", "Processing image", "IN_PROGRESS")
        result = client.predict(
            image=handle_file(image_path),
            api_name='/image'
        )

        # Result is tuple: (imageslider_output, png_file_path)
        # The PNG file is the second element
        if isinstance(result, tuple) and len(result) >= 2:
            temp_png = result[1]
        elif isinstance(result, str):
            temp_png = result
        else:
            logger.log("Stage 2", "Unexpected result format", "FAILED", {"result": str(result)[:200]})
            return False, ""

        # Generate output path if not provided
        if not output_path:
            input_name = Path(image_path).stem
            output_path = f"{CONFIG['stage2_output']}/{input_name}_nobg.png"

        # Copy result to output path
        shutil.copy2(temp_png, output_path)
        file_size = os.path.getsize(output_path)

        logger.log("Stage 2", "Background removed", "SUCCESS", {
            "input": image_path,
            "output": output_path,
            "size_bytes": file_size
        })
        return True, output_path

    except ImportError:
        logger.log("Stage 2", "gradio_client not installed", "FAILED",
                   {"fix": "pip install gradio_client"})
        return False, ""
    except Exception as e:
        logger.log("Stage 2", "Exception", "FAILED", {"error": str(e)})
        return False, ""


# =============================================================================
# STAGE 3: Upscaling (Replicate API or PIL Lanczos fallback)
# =============================================================================

def stage3_upscale_pil(image_path: str, output_path: str = None, scale: int = 4) -> Tuple[bool, str]:
    """
    Upscale image using PIL Lanczos resampling (FREE, FAST, RELIABLE).

    This is a high-quality fallback when Replicate API is not available.
    TESTED WORKING: Session M (2025-12-29)

    Args:
        image_path: Path to input image (PNG/JPG)
        output_path: Path for output (optional)
        scale: Upscale factor (2, 4, or 8)

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 3", "Starting PIL Lanczos upscale", "IN_PROGRESS",
               {"input": image_path, "scale": scale})

    try:
        from PIL import Image

        # Load image
        img = Image.open(image_path)
        original_size = img.size

        # Calculate new size
        new_size = (img.size[0] * scale, img.size[1] * scale)

        # Upscale using Lanczos (high quality)
        upscaled = img.resize(new_size, Image.Resampling.LANCZOS)

        # Generate output path if not provided
        if not output_path:
            input_name = Path(image_path).stem
            output_path = f"{CONFIG['stage3_output']}/{input_name}_upscaled_{scale}x_lanczos.png"

        # Save result
        upscaled.save(output_path, 'PNG')
        file_size = os.path.getsize(output_path)

        logger.log("Stage 3", "PIL Lanczos upscale complete", "SUCCESS", {
            "input": image_path,
            "output": output_path,
            "original_size": f"{original_size[0]}x{original_size[1]}",
            "new_size": f"{new_size[0]}x{new_size[1]}",
            "scale": scale,
            "size_bytes": file_size
        })
        return True, output_path

    except ImportError:
        logger.log("Stage 3", "PIL not installed", "FAILED", {"fix": "pip install Pillow"})
        return False, ""
    except Exception as e:
        logger.log("Stage 3", "PIL upscale exception", "FAILED", {"error": str(e)})
        return False, ""


def stage3_upscale(image_path: str, output_path: str = None, scale: int = 4,
                   use_ai: bool = True) -> Tuple[bool, str]:
    """
    Upscale image using Real-ESRGAN via Replicate API, with PIL fallback.

    If Replicate API token is not available, automatically uses PIL Lanczos.

    Cost: ~$0.0023 per image (Replicate) or FREE (PIL fallback)

    Args:
        image_path: Path to input image (PNG preferred)
        output_path: Path for output (optional)
        scale: Upscale factor (2 or 4)
        use_ai: Try AI upscaling first (requires Replicate token)

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 3", "Starting upscale", "IN_PROGRESS", {"input": image_path, "scale": scale})

    # Check for file
    if not os.path.exists(image_path):
        logger.log("Stage 3", "File not found", "FAILED", {"path": image_path})
        return False, ""

    # If no Replicate token or AI not requested, use PIL fallback
    if not CONFIG["replicate_token"] or not use_ai:
        logger.log("Stage 3", "Using PIL Lanczos fallback (no Replicate token)", "INFO")
        return stage3_upscale_pil(image_path, output_path, scale)

    # Replicate API
    API_URL = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {CONFIG['replicate_token']}",
        "Content-Type": "application/json"
    }

    # Read and encode image
    try:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        # Determine mime type
        ext = Path(image_path).suffix.lower()
        mime_type = "image/png" if ext == ".png" else "image/jpeg"
        image_uri = f"data:{mime_type};base64,{image_b64}"

    except FileNotFoundError:
        logger.log("Stage 3", "File not found", "FAILED", {"path": image_path})
        return False, ""

    # Create prediction
    payload = {
        "version": "42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",  # Real-ESRGAN
        "input": {
            "image": image_uri,
            "scale": scale,
            "face_enhance": False
        }
    }

    try:
        # Start prediction
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 201:
            logger.log("Stage 3", "Failed to create prediction", "FAILED", {
                "status": response.status_code,
                "response": response.text[:500]
            })
            return False, ""

        prediction = response.json()
        prediction_id = prediction["id"]
        get_url = prediction["urls"]["get"]

        logger.log("Stage 3", "Prediction created", "PROCESSING", {"id": prediction_id})

        # Poll for completion
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(2)

            status_response = requests.get(get_url, headers=headers, timeout=30)
            status_data = status_response.json()

            status = status_data.get("status")

            if status == "succeeded":
                output_url = status_data.get("output")

                # Download result
                img_response = requests.get(output_url, timeout=60)

                if not output_path:
                    input_name = Path(image_path).stem
                    output_path = f"{CONFIG['stage3_output']}/{input_name}_upscaled_{scale}x.png"

                with open(output_path, "wb") as f:
                    f.write(img_response.content)

                logger.log("Stage 3", "Upscale complete", "SUCCESS", {
                    "input": image_path,
                    "output": output_path,
                    "scale": scale,
                    "size_bytes": len(img_response.content)
                })
                return True, output_path

            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                logger.log("Stage 3", "Prediction failed", "FAILED", {"error": error})
                return False, ""

            elif status in ["starting", "processing"]:
                continue

        logger.log("Stage 3", "Timeout waiting for prediction", "FAILED")
        return False, ""

    except Exception as e:
        logger.log("Stage 3", "Exception", "FAILED", {"error": str(e)})
        return False, ""


# =============================================================================
# STAGE 4: 2D to 3D Conversion (Meshy.ai API)
# =============================================================================

def stage4_2d_to_3d(image_path: str, output_path: str = None) -> Tuple[bool, str]:
    """
    Convert 2D image to 3D model using Meshy.ai API.

    Cost: ~$0.02 per model (1000 credits = $20)
    Time: ~30-60 seconds per model

    Args:
        image_path: Path to input PNG image (with transparent background preferred)
        output_path: Path for output GLB file (optional, auto-generated if not provided)

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 4", "Starting 2D to 3D conversion", "IN_PROGRESS", {"input": image_path})

    if not CONFIG["meshy_api_key"]:
        logger.log("Stage 4", "No Meshy API key", "SKIPPED")
        return False, ""

    if not os.path.exists(image_path):
        logger.log("Stage 4", "File not found", "FAILED", {"path": image_path})
        return False, ""

    # Meshy API uses OpenAPI endpoint with base64 data URI
    API_BASE = "https://api.meshy.ai/openapi/v1"
    headers = {
        "Authorization": f"Bearer {CONFIG['meshy_api_key']}",
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Read image and convert to base64 data URI
        logger.log("Stage 4", "Encoding image for Meshy.ai", "IN_PROGRESS")

        with open(image_path, "rb") as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode("utf-8")

        # Determine MIME type
        ext = Path(image_path).suffix.lower()
        mime_type = "image/png" if ext == ".png" else "image/jpeg"
        image_uri = f"data:{mime_type};base64,{image_b64}"

        # Create task with JSON payload
        payload = {
            "image_url": image_uri,
            "enable_pbr": True,  # Generate PBR textures
            "should_remesh": True,  # Clean up mesh
            "should_texture": True  # Apply textures
        }

        logger.log("Stage 4", "Creating Meshy.ai task", "IN_PROGRESS")
        response = requests.post(
            f"{API_BASE}/image-to-3d",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code not in [200, 201, 202]:
            logger.log("Stage 4", "Task creation failed", "FAILED", {
                "status": response.status_code,
                "response": response.text[:500]
            })
            return False, ""

        result = response.json()
        task_id = result.get("result")

        if not task_id:
            logger.log("Stage 4", "No task ID in response", "FAILED", {"response": str(result)[:500]})
            return False, ""

        logger.log("Stage 4", f"Task created: {task_id}", "IN_PROGRESS")

        # Step 2: Poll for completion
        max_attempts = 120  # 120 * 5s = 10 minutes max
        for attempt in range(max_attempts):
            time.sleep(5)

            status_response = requests.get(
                f"{API_BASE}/image-to-3d/{task_id}",
                headers=headers,
                timeout=30
            )

            if status_response.status_code != 200:
                logger.log("Stage 4", "Status check failed", "FAILED", {
                    "status": status_response.status_code
                })
                continue

            status_data = status_response.json()
            status = status_data.get("status")
            progress = status_data.get("progress", 0)

            if attempt % 6 == 0:  # Log every 30 seconds
                logger.log("Stage 4", f"Poll {attempt+1}: {status} ({progress}%)", "IN_PROGRESS")

            if status == "SUCCEEDED":
                # Get model URL
                model_urls = status_data.get("model_urls", {})
                glb_url = model_urls.get("glb")

                if not glb_url:
                    logger.log("Stage 4", "No GLB URL in response", "FAILED", {
                        "model_urls": list(model_urls.keys())
                    })
                    return False, ""

                # Download GLB file
                logger.log("Stage 4", "Downloading 3D model", "IN_PROGRESS")
                model_response = requests.get(glb_url, timeout=120)

                if model_response.status_code != 200:
                    logger.log("Stage 4", "Model download failed", "FAILED", {
                        "status": model_response.status_code
                    })
                    return False, ""

                # Generate output path if not provided
                if not output_path:
                    input_name = Path(image_path).stem
                    output_path = f"{CONFIG['stage4_output']}/{input_name}.glb"

                # Save model
                with open(output_path, "wb") as f:
                    f.write(model_response.content)

                file_size = os.path.getsize(output_path)
                logger.log("Stage 4", "3D model created", "SUCCESS", {
                    "input": image_path,
                    "output": output_path,
                    "size_bytes": file_size,
                    "task_id": task_id
                })
                return True, output_path

            elif status == "FAILED":
                error = status_data.get("task_error", {}).get("message", "Unknown error")
                logger.log("Stage 4", "Task failed", "FAILED", {"error": error})
                return False, ""

            elif status in ["PENDING", "IN_PROGRESS"]:
                continue

            else:
                logger.log("Stage 4", f"Unknown status: {status}", "WARNING")

        logger.log("Stage 4", "Timeout waiting for 3D model", "FAILED")
        return False, ""

    except Exception as e:
        logger.log("Stage 4", "Exception", "FAILED", {"error": str(e)})
        return False, ""


# =============================================================================
# STAGE 4.5: Auto-Rigging & Animation (Tripo AI API) - OPTIONAL
# =============================================================================

# Check if tripo3d SDK is available
try:
    import asyncio
    from tripo3d import TripoClient
    TRIPO_AVAILABLE = True
except ImportError:
    TRIPO_AVAILABLE = False


def stage4_5_auto_rig(
    glb_path: str,
    output_path: str = None,
    animation: str = None,
    rig_type: str = "mixamo"
) -> Tuple[bool, str]:
    """
    Auto-rig a static GLB model using Tripo AI.

    IMPORTANT LIMITATION:
    Tripo AI's SDK requires models to be generated through their pipeline.
    External GLB files (from Meshy.ai, etc.) CANNOT be rigged directly via API.

    For animation support, use ONE of these approaches:
    1. stage4_tripo_with_rigging() - Replaces Meshy with Tripo (2D->3D->Rig in one)
    2. stage4_5_skip() - Keep static sprites (current default)
    3. Manual: Use Tripo Studio web interface to upload and rig

    This function will attempt rigging but will fail for external GLB files.
    It's provided for future compatibility when/if Tripo adds external GLB support.

    Cost: Tripo AI credits (300 free/month on Basic plan)
    Time: ~30-60 seconds for rigging + animation
    API Docs: https://github.com/VAST-AI-Research/tripo-python-sdk

    Args:
        glb_path: Path to input GLB file (MUST be from Tripo pipeline)
        output_path: Path for output rigged GLB (optional, auto-generated)
        animation: Animation preset to apply (e.g., "idle", "walk", "run")
        rig_type: Rig specification - "mixamo" or "tripo" (default: "mixamo")

    Returns:
        Tuple of (success: bool, output_path: str)

    Prerequisites:
        pip install tripo3d
        Set TRIPO_API_KEY environment variable
    """
    # For external GLB files, log the limitation and suggest alternatives
    logger.log("Stage 4.5", "External GLB rigging not supported via API", "WARNING", {
        "input": glb_path,
        "limitation": "Tripo SDK requires models from their pipeline",
        "alternatives": [
            "Use stage4_tripo_with_rigging() for full Tripo pipeline",
            "Use stage4_5_skip() for static sprites",
            "Manual: Upload to Tripo Studio web interface"
        ]
    })

    # Return skip-through behavior for now
    return stage4_5_skip(glb_path)


async def _async_rig_and_animate(
    api_key: str,
    model_task_id: str,
    output_path: str,
    animation: str = None,
    rig_type: str = "mixamo"
) -> Tuple[bool, str]:
    """
    Async helper for Tripo AI rigging and animation.

    IMPORTANT: This requires a model_task_id from Tripo's own pipeline.
    External GLB files (e.g., from Meshy.ai) cannot be rigged directly.
    Use stage4_tripo_with_rigging() instead for the full Tripo pipeline.

    Args:
        api_key: Tripo API key
        model_task_id: Task ID from a Tripo generation (image_to_model, etc.)
        output_path: Where to save the rigged GLB
        animation: Animation preset name (optional)
        rig_type: "mixamo" or "tripo" skeleton spec

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    try:
        async with TripoClient(api_key=api_key) as client:
            # Step 1: Check if model is riggable
            logger.log("Stage 4.5", "Checking if model is riggable", "IN_PROGRESS")

            try:
                await client.check_riggable(model_task_id)
            except Exception as e:
                logger.log("Stage 4.5", f"Model not riggable: {e}", "FAILED")
                return False, ""

            # Step 2: Create rigging task
            logger.log("Stage 4.5", "Creating rigging task", "IN_PROGRESS")

            # Map rig_type string to RigSpec enum if needed
            from tripo3d import RigSpec
            spec = RigSpec.MIXAMO if rig_type.lower() == "mixamo" else RigSpec.TRIPO

            rig_task_id = await client.rig_model(
                original_model_task_id=model_task_id,
                out_format="glb",
                spec=spec
            )

            # Step 3: Wait for rigging to complete
            logger.log("Stage 4.5", "Waiting for rigging to complete", "IN_PROGRESS")
            rig_task = await client.wait_for_task(rig_task_id, verbose=True)

            if rig_task.status.value != "SUCCESS":
                logger.log("Stage 4.5", f"Rigging failed: {rig_task.status}", "FAILED")
                return False, ""

            # Step 4: Apply animation if requested
            if animation:
                logger.log("Stage 4.5", f"Applying animation: {animation}", "IN_PROGRESS")

                from tripo3d import Animation
                anim_task_id = await client.retarget_animation(
                    original_model_task_id=rig_task_id,
                    animation=Animation[animation.upper()],  # e.g., Animation.IDLE
                    out_format="glb",
                    bake_animation=True,
                    export_with_geometry=True
                )

                anim_task = await client.wait_for_task(anim_task_id, verbose=True)
                if anim_task.status.value != "SUCCESS":
                    logger.log("Stage 4.5", f"Animation failed: {anim_task.status}", "FAILED")
                    return False, ""

                final_task = anim_task
            else:
                final_task = rig_task

            # Step 5: Download the result
            logger.log("Stage 4.5", "Downloading rigged model", "IN_PROGRESS")
            output_dir = str(Path(output_path).parent)
            downloaded = await client.download_task_models(final_task, output_dir)

            # Rename to expected output path
            if downloaded:
                for fmt, path in downloaded.items():
                    if path.endswith('.glb'):
                        shutil.move(path, output_path)
                        return True, output_path

            return False, ""

    except Exception as e:
        logger.log("Stage 4.5", f"Async exception: {e}", "FAILED")
        return False, ""


def stage4_tripo_with_rigging(
    image_path: str,
    output_path: str = None,
    animation: str = None,
    rig_type: str = "mixamo"
) -> Tuple[bool, str]:
    """
    ALTERNATIVE: Use Tripo AI for both 3D generation AND rigging (replaces Meshy.ai).

    This is the recommended approach when animation is needed, as Tripo requires
    models to be generated through their pipeline for rigging.

    Cost: Tripo AI credits (300 free/month on Basic plan)
    Time: ~2-4 minutes for 3D + rigging + animation

    Args:
        image_path: Path to 2D concept image (from Stage 2 or 3)
        output_path: Path for output rigged GLB
        animation: Animation preset (e.g., "idle", "walk", "run")
        rig_type: "mixamo" or "tripo" skeleton spec

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    if not TRIPO_AVAILABLE:
        logger.log("Stage 4+4.5", "tripo3d SDK not installed", "FAILED",
                   {"fix": "pip install tripo3d"})
        return False, ""

    api_key = CONFIG.get("tripo_api_key")
    if not api_key:
        logger.log("Stage 4+4.5", "TRIPO_API_KEY not set", "FAILED")
        return False, ""

    if not os.path.exists(image_path):
        logger.log("Stage 4+4.5", "Input image not found", "FAILED", {"path": image_path})
        return False, ""

    # Generate output path if not provided
    if not output_path:
        base_name = Path(image_path).stem.replace("_nobg", "").replace("_upscaled", "")
        suffix = "_rigged" if not animation else f"_rigged_{animation}"
        output_path = f"{CONFIG['stage4_5_output']}/{base_name}{suffix}.glb"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    logger.log("Stage 4+4.5", "Starting Tripo 3D + rigging pipeline", "IN_PROGRESS", {
        "input": image_path,
        "animation": animation or "none",
        "rig_type": rig_type
    })

    try:
        success, result_path = asyncio.run(_async_tripo_full_pipeline(
            api_key=api_key,
            image_path=image_path,
            output_path=output_path,
            animation=animation,
            rig_type=rig_type
        ))

        if success:
            logger.log("Stage 4+4.5", "Tripo pipeline complete", "SUCCESS", {
                "output": result_path,
                "size": os.path.getsize(result_path) if os.path.exists(result_path) else 0
            })
            return True, result_path
        else:
            logger.log("Stage 4+4.5", "Tripo pipeline failed", "FAILED")
            return False, ""

    except Exception as e:
        logger.log("Stage 4+4.5", "Exception", "FAILED", {"error": str(e)})
        return False, ""


async def _async_tripo_full_pipeline(
    api_key: str,
    image_path: str,
    output_path: str,
    animation: str = None,
    rig_type: str = "mixamo"
) -> Tuple[bool, str]:
    """
    Async helper for full Tripo pipeline: Image -> 3D -> Rig -> Animate.
    """
    try:
        async with TripoClient(api_key=api_key) as client:
            # Step 1: Upload image and generate 3D model
            logger.log("Stage 4+4.5", "Generating 3D model from image", "IN_PROGRESS")

            model_task_id = await client.image_to_model(
                image=image_path,
                texture=True,
                pbr=True,
                texture_quality="standard"
            )

            model_task = await client.wait_for_task(model_task_id, verbose=True, timeout=300)

            if model_task.status.value != "SUCCESS":
                logger.log("Stage 4+4.5", f"3D generation failed: {model_task.status}", "FAILED")
                return False, ""

            logger.log("Stage 4+4.5", "3D model generated, proceeding to rigging", "SUCCESS")

            # Step 2: Rig and animate
            return await _async_rig_and_animate(
                api_key=api_key,
                model_task_id=model_task_id,
                output_path=output_path,
                animation=animation,
                rig_type=rig_type
            )

    except Exception as e:
        logger.log("Stage 4+4.5", f"Pipeline exception: {e}", "FAILED")
        return False, ""


def stage4_5_skip(glb_path: str) -> Tuple[bool, str]:
    """
    Skip Stage 4.5 (pass through static GLB to Stage 5).

    Use this when:
    - Static sprites are acceptable
    - Tripo AI credits are exhausted
    - Animation not needed for this asset

    Returns:
        Tuple of (True, original_glb_path) - always succeeds
    """
    logger.log("Stage 4.5", "Skipped (static model pass-through)", "SKIPPED", {
        "input": glb_path
    })
    return True, glb_path


# =============================================================================
# STAGE 5: 8-Direction Sprite Rendering (Blender CLI)
# =============================================================================

def stage5_render_sprites(glb_path: str, output_dir: str = None,
                          resolution: int = 512) -> Tuple[bool, List[str]]:
    """
    Render 3D GLB model from 8 isometric directions using Blender.

    Cost: FREE (local Blender)
    Time: ~30-60 seconds for 8 renders

    Args:
        glb_path: Path to input GLB file (from Stage 4)
        output_dir: Directory for output sprites (optional)
        resolution: Output image resolution (default: 512x512)

    Returns:
        Tuple of (success: bool, list of output file paths)
    """
    logger.log("Stage 5", "Starting 8-direction sprite rendering", "IN_PROGRESS", {
        "input": glb_path,
        "resolution": resolution
    })

    # Validate Blender installation
    blender_path = CONFIG.get("blender_path")
    if not blender_path or not os.path.exists(blender_path):
        logger.log("Stage 5", "Blender not found", "FAILED", {"path": blender_path})
        return False, []

    # Validate Blender script
    blender_script = CONFIG.get("blender_script")
    if not blender_script or not os.path.exists(blender_script):
        logger.log("Stage 5", "Blender script not found", "FAILED", {"path": blender_script})
        return False, []

    # Validate input file
    if not os.path.exists(glb_path):
        logger.log("Stage 5", "GLB file not found", "FAILED", {"path": glb_path})
        return False, []

    # Set output directory
    if not output_dir:
        output_dir = CONFIG["stage5_output"]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Build Blender command
    # blender --background --python script.py -- --input model.glb --output ./sprites/
    cmd = [
        blender_path,
        "--background",
        "--python", blender_script,
        "--",
        "--input", glb_path,
        "--output", output_dir,
        "--resolution", str(resolution)
    ]

    logger.log("Stage 5", "Running Blender renderer", "IN_PROGRESS")

    try:
        # Run Blender in background mode
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.log("Stage 5", "Blender render failed", "FAILED", {
                "returncode": result.returncode,
                "stderr": result.stderr[:1000] if result.stderr else "No stderr"
            })
            return False, []

        # Find rendered files
        basename = Path(glb_path).stem
        rendered_files = []
        directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']

        for i, direction in enumerate(directions):
            sprite_file = f"{output_dir}/{basename}_dir{i}_{direction}.png"
            if os.path.exists(sprite_file):
                rendered_files.append(sprite_file)

        if not rendered_files:
            logger.log("Stage 5", "No sprite files generated", "FAILED", {
                "output_dir": output_dir,
                "expected_pattern": f"{basename}_dir*_*.png"
            })
            return False, []

        total_size = sum(os.path.getsize(f) for f in rendered_files)
        logger.log("Stage 5", f"Rendered {len(rendered_files)} sprites", "SUCCESS", {
            "files": rendered_files,
            "total_size_bytes": total_size
        })

        return True, rendered_files

    except subprocess.TimeoutExpired:
        logger.log("Stage 5", "Blender render timed out (5 min)", "FAILED")
        return False, []

    except Exception as e:
        logger.log("Stage 5", "Exception", "FAILED", {"error": str(e)})
        return False, []


def stage5_render_sprites_remote(glb_path: str, output_dir: str = None,
                                  resolution: int = 512) -> Tuple[bool, List[str]]:
    """
    Render 3D GLB model from 8 isometric directions using Blender on remote VPS.

    This uses SSH/SCP to:
    1. Upload GLB to VPS
    2. Run Blender headless via xvfb-run
    3. Download rendered sprites back to local

    Cost: FREE (VPS already paid)
    Time: ~45-60 seconds for 8 renders

    Args:
        glb_path: Path to input GLB file (from Stage 4)
        output_dir: Directory for output sprites (optional)
        resolution: Output image resolution (default: 512x512)

    Returns:
        Tuple of (success: bool, list of output file paths)
    """
    logger.log("Stage 5 Remote", "Starting VPS sprite rendering", "IN_PROGRESS", {
        "input": glb_path,
        "resolution": resolution,
        "vps": CONFIG["vps_host"]
    })

    # Validate input file
    if not os.path.exists(glb_path):
        logger.log("Stage 5 Remote", "GLB file not found", "FAILED", {"path": glb_path})
        return False, []

    # Set output directory
    if not output_dir:
        output_dir = CONFIG["stage5_output"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # VPS config
    vps_host = CONFIG["vps_host"]
    vps_user = CONFIG["vps_user"]
    vps_work_dir = CONFIG["vps_work_dir"]
    vps_script = CONFIG["vps_blender_script"]

    # File names
    basename = Path(glb_path).stem
    remote_glb = f"{vps_work_dir}/{basename}.glb"
    remote_output = f"{vps_work_dir}/output"

    try:
        # Step 1: Upload GLB to VPS via SCP
        logger.log("Stage 5 Remote", "Uploading GLB to VPS", "IN_PROGRESS")
        scp_upload_cmd = [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-o", "BatchMode=yes",
            glb_path,
            f"{vps_user}@{vps_host}:{remote_glb}"
        ]

        result = subprocess.run(scp_upload_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.log("Stage 5 Remote", "SCP upload failed", "FAILED", {
                "returncode": result.returncode,
                "stderr": result.stderr[:500] if result.stderr else "No stderr"
            })
            return False, []

        logger.log("Stage 5 Remote", "GLB uploaded to VPS", "SUCCESS")

        # Step 2: Run Blender via SSH with xvfb-run
        logger.log("Stage 5 Remote", "Running Blender on VPS", "IN_PROGRESS")
        blender_cmd = (
            f"mkdir -p {remote_output} && "
            f"xvfb-run blender --background --python {vps_script} -- "
            f"--input {remote_glb} --output {remote_output} --resolution {resolution}"
        )

        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "BatchMode=yes",
            f"{vps_user}@{vps_host}",
            blender_cmd
        ]

        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.log("Stage 5 Remote", "Blender render failed", "FAILED", {
                "returncode": result.returncode,
                "stderr": result.stderr[:1000] if result.stderr else "No stderr"
            })
            return False, []

        logger.log("Stage 5 Remote", "Blender render complete", "SUCCESS")

        # Step 3: Download rendered sprites via SCP
        logger.log("Stage 5 Remote", "Downloading sprites from VPS", "IN_PROGRESS")

        # Download all PNG files matching the pattern
        directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
        rendered_files = []

        for i, direction in enumerate(directions):
            remote_sprite = f"{remote_output}/{basename}_dir{i}_{direction}.png"
            local_sprite = f"{output_dir}/{basename}_dir{i}_{direction}.png"

            scp_download_cmd = [
                "scp",
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",
                f"{vps_user}@{vps_host}:{remote_sprite}",
                local_sprite
            ]

            result = subprocess.run(scp_download_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(local_sprite):
                rendered_files.append(local_sprite)
            else:
                logger.log("Stage 5 Remote", f"Failed to download sprite {direction}", "WARNING")

        if not rendered_files:
            logger.log("Stage 5 Remote", "No sprites downloaded", "FAILED")
            return False, []

        # Step 4: Cleanup remote files (optional, keep for debugging)
        # ssh_cleanup = f"rm -f {remote_glb} {remote_output}/{basename}_*.png"
        # subprocess.run(["ssh", f"{vps_user}@{vps_host}", ssh_cleanup], capture_output=True)

        total_size = sum(os.path.getsize(f) for f in rendered_files)
        logger.log("Stage 5 Remote", f"Downloaded {len(rendered_files)} sprites", "SUCCESS", {
            "files": rendered_files,
            "total_size_bytes": total_size
        })

        return True, rendered_files

    except subprocess.TimeoutExpired:
        logger.log("Stage 5 Remote", "Operation timed out", "FAILED")
        return False, []

    except Exception as e:
        logger.log("Stage 5 Remote", "Exception", "FAILED", {"error": str(e)})
        return False, []


# =============================================================================
# STAGE 6: Sprite Sheet Assembly (PIL)
# =============================================================================

def stage6_assemble_sprite_sheet(sprite_files: List[str], output_path: str = None,
                                  columns: int = 4, padding: int = 0) -> Tuple[bool, str]:
    """
    Assemble 8 direction sprites into a single sprite sheet.

    Layout: 4 columns x 2 rows (default)
    Order: S, SW, W, NW (row 1) | N, NE, E, SE (row 2)

    Cost: FREE (PIL)
    Time: <1 second

    Args:
        sprite_files: List of 8 sprite PNG paths (ordered by direction)
        output_path: Path for output sprite sheet (optional)
        columns: Number of columns in sheet (default: 4)
        padding: Padding between sprites in pixels (default: 0)

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 6", "Assembling sprite sheet", "IN_PROGRESS", {
        "sprites": len(sprite_files),
        "columns": columns
    })

    if not sprite_files:
        logger.log("Stage 6", "No sprite files provided", "FAILED")
        return False, ""

    try:
        from PIL import Image

        # Load all sprites
        sprites = []
        for sprite_path in sprite_files:
            if os.path.exists(sprite_path):
                img = Image.open(sprite_path)
                sprites.append(img)
            else:
                logger.log("Stage 6", f"Sprite not found: {sprite_path}", "WARNING")

        if not sprites:
            logger.log("Stage 6", "No valid sprites loaded", "FAILED")
            return False, ""

        # Get sprite dimensions (assume all same size)
        sprite_width, sprite_height = sprites[0].size

        # Calculate sheet dimensions
        rows = (len(sprites) + columns - 1) // columns  # Ceiling division
        sheet_width = columns * sprite_width + (columns - 1) * padding
        sheet_height = rows * sprite_height + (rows - 1) * padding

        # Create sheet with transparency
        sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

        # Paste sprites into sheet
        for i, sprite in enumerate(sprites):
            row = i // columns
            col = i % columns
            x = col * (sprite_width + padding)
            y = row * (sprite_height + padding)
            sheet.paste(sprite, (x, y))

        # Generate output path if not provided
        if not output_path:
            # Use first sprite's basename
            first_sprite = Path(sprite_files[0])
            # Remove direction suffix to get base name
            basename = first_sprite.stem
            # Remove _dir#_DIRECTION suffix
            for suffix in ['_dir0_S', '_dir1_SW', '_dir2_W', '_dir3_NW',
                          '_dir4_N', '_dir5_NE', '_dir6_E', '_dir7_SE']:
                if basename.endswith(suffix):
                    basename = basename[:-len(suffix)]
                    break
            output_path = f"{CONFIG['stage5_output']}/{basename}_spritesheet.png"

        # Save sprite sheet
        sheet.save(output_path, 'PNG')
        file_size = os.path.getsize(output_path)

        logger.log("Stage 6", "Sprite sheet assembled", "SUCCESS", {
            "output": output_path,
            "size_bytes": file_size,
            "dimensions": f"{sheet_width}x{sheet_height}",
            "sprites": len(sprites),
            "layout": f"{columns}x{rows}"
        })

        return True, output_path

    except ImportError:
        logger.log("Stage 6", "PIL not installed", "FAILED", {"fix": "pip install Pillow"})
        return False, ""

    except Exception as e:
        logger.log("Stage 6", "Exception", "FAILED", {"error": str(e)})
        return False, ""


def stage6_from_directory(sprite_dir: str, basename: str = None,
                          output_path: str = None) -> Tuple[bool, str]:
    """
    Assemble sprite sheet from a directory of rendered sprites.

    Automatically finds sprites matching the 8-direction naming pattern.

    Args:
        sprite_dir: Directory containing sprite files
        basename: Base name of sprites (auto-detected if not provided)
        output_path: Path for output sprite sheet

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 6", f"Scanning directory: {sprite_dir}", "IN_PROGRESS")

    if not os.path.exists(sprite_dir):
        logger.log("Stage 6", "Directory not found", "FAILED", {"path": sprite_dir})
        return False, ""

    # Find all PNG files
    all_pngs = [f for f in os.listdir(sprite_dir) if f.endswith('.png')]

    # If basename not provided, try to detect it
    if not basename:
        # Look for files with _dir0_S pattern
        for png in all_pngs:
            if '_dir0_S.png' in png:
                basename = png.replace('_dir0_S.png', '')
                break

    if not basename:
        logger.log("Stage 6", "Could not detect sprite basename", "FAILED")
        return False, ""

    # Build ordered list of sprite files
    directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    sprite_files = []

    for i, direction in enumerate(directions):
        sprite_name = f"{basename}_dir{i}_{direction}.png"
        sprite_path = os.path.join(sprite_dir, sprite_name)
        if os.path.exists(sprite_path):
            sprite_files.append(sprite_path)
        else:
            logger.log("Stage 6", f"Missing sprite: {sprite_name}", "WARNING")

    if len(sprite_files) < 8:
        logger.log("Stage 6", f"Only found {len(sprite_files)}/8 sprites", "WARNING")

    return stage6_assemble_sprite_sheet(sprite_files, output_path)


# =============================================================================
# STAGE 7: Faction Color Variants (HSV Shift)
# =============================================================================

# Faction hue shifts (in degrees, 0-360 scale converted to 0-1)
FACTION_COLORS = {
    "red": 0.0,       # No shift (original)
    "blue": 0.55,     # Blue hue
    "green": 0.33,    # Green hue
    "gold": 0.12,     # Gold/yellow hue
}


def stage7_create_faction_variants(input_path: str, output_dir: str = None,
                                    factions: List[str] = None) -> Tuple[bool, Dict[str, str]]:
    """
    Create faction color variants of a sprite sheet using HSV hue shifting.

    This preserves the original luminance and saturation while shifting
    the hue to create distinct faction colors (red, blue, green, gold).

    Cost: FREE (PIL)
    Time: <1 second per variant

    Args:
        input_path: Path to input sprite sheet (from Stage 6)
        output_dir: Directory for output variants (optional)
        factions: List of factions to generate (default: all 4)

    Returns:
        Tuple of (success: bool, dict of faction->output_path)
    """
    logger.log("Stage 7", "Creating faction color variants", "IN_PROGRESS", {
        "input": input_path,
        "factions": factions or list(FACTION_COLORS.keys())
    })

    if not os.path.exists(input_path):
        logger.log("Stage 7", "Input file not found", "FAILED", {"path": input_path})
        return False, {}

    if factions is None:
        factions = list(FACTION_COLORS.keys())

    try:
        from PIL import Image
        import colorsys

        # Load source image
        source = Image.open(input_path).convert('RGBA')
        pixels = source.load()
        width, height = source.size

        # Set output directory
        if not output_dir:
            output_dir = CONFIG.get("stage7_output", "C:/Ziggie/assets/test-results/stage7_factions")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Get base filename
        basename = Path(input_path).stem

        results = {}

        for faction in factions:
            if faction not in FACTION_COLORS:
                logger.log("Stage 7", f"Unknown faction: {faction}", "WARNING")
                continue

            hue_shift = FACTION_COLORS[faction]

            # Create variant image
            variant = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            variant_pixels = variant.load()

            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]

                    # Skip fully transparent pixels
                    if a == 0:
                        variant_pixels[x, y] = (0, 0, 0, 0)
                        continue

                    # Convert to HSV
                    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

                    # Shift hue (faction "red" at 0.0 means no shift for original)
                    if faction == "red":
                        new_h = h  # Keep original colors for red faction
                    else:
                        new_h = (hue_shift) % 1.0  # Set to faction hue

                    # Convert back to RGB
                    new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
                    variant_pixels[x, y] = (
                        int(new_r * 255),
                        int(new_g * 255),
                        int(new_b * 255),
                        a
                    )

            # Save variant
            output_path = f"{output_dir}/{basename}_{faction}.png"
            variant.save(output_path, 'PNG')
            results[faction] = output_path

            file_size = os.path.getsize(output_path)
            logger.log("Stage 7", f"Created {faction} variant", "SUCCESS", {
                "output": output_path,
                "size_bytes": file_size
            })

        logger.log("Stage 7", f"Created {len(results)} faction variants", "SUCCESS", {
            "variants": list(results.keys())
        })

        # Send notification with first variant as preview
        first_output = list(results.values())[0] if results else None
        send_notification(
            "Stage 7: Faction Colors",
            success=True,
            output_path=first_output,
            details={"Variants": ", ".join(results.keys()), "Count": len(results)}
        )

        return True, results

    except ImportError:
        logger.log("Stage 7", "PIL not installed", "FAILED", {"fix": "pip install Pillow"})
        send_notification("Stage 7: Faction Colors", success=False, details={"Error": "PIL not installed"})
        return False, {}

    except Exception as e:
        logger.log("Stage 7", "Exception", "FAILED", {"error": str(e)})
        send_notification("Stage 7: Faction Colors", success=False, details={"Error": str(e)})
        return False, {}


def stage7_batch_variants(sprite_dir: str, output_dir: str = None,
                          factions: List[str] = None) -> Tuple[bool, List[Dict[str, str]]]:
    """
    Create faction variants for all sprite sheets in a directory.

    Args:
        sprite_dir: Directory containing sprite sheets
        output_dir: Directory for output variants
        factions: List of factions to generate

    Returns:
        Tuple of (success: bool, list of result dicts)
    """
    logger.log("Stage 7", f"Batch processing directory: {sprite_dir}", "IN_PROGRESS")

    if not os.path.exists(sprite_dir):
        logger.log("Stage 7", "Directory not found", "FAILED", {"path": sprite_dir})
        return False, []

    # Find all sprite sheets (files ending with _spritesheet.png)
    sprite_sheets = [f for f in os.listdir(sprite_dir)
                     if f.endswith('_spritesheet.png') or f.endswith('.png')]

    if not sprite_sheets:
        logger.log("Stage 7", "No sprite sheets found", "FAILED")
        return False, []

    all_results = []
    for sheet in sprite_sheets:
        sheet_path = os.path.join(sprite_dir, sheet)
        success, results = stage7_create_faction_variants(sheet_path, output_dir, factions)
        if success:
            all_results.append(results)

    logger.log("Stage 7", f"Batch complete: {len(all_results)} sheets processed", "SUCCESS")
    return len(all_results) > 0, all_results


# =============================================================================
# STAGE 1: 2D Generation (RunPod Serverless or ComfyUI API)
# =============================================================================

def stage1_generate_2d(prompt: str, output_path: str = None,
                       negative_prompt: str = None) -> Tuple[bool, str]:
    """
    Generate 2D concept art using RunPod Serverless API.

    NOTE: This requires a RunPod Serverless endpoint to be set up.
    Alternative: Use local ComfyUI MCP when available.

    Args:
        prompt: Generation prompt
        output_path: Path for output image
        negative_prompt: What to avoid

    Returns:
        Tuple of (success: bool, output_path: str)
    """
    logger.log("Stage 1", "Starting 2D generation", "IN_PROGRESS", {"prompt": prompt[:100]})

    if not CONFIG["runpod_api_key"]:
        logger.log("Stage 1", "No RunPod API key - use local ComfyUI or Pods instead", "SKIPPED")
        return False, ""

    # Default negative prompt for game assets
    if not negative_prompt:
        negative_prompt = "blurry, low quality, text, watermark, realistic, photorealistic, multiple characters, cropped"

    # RunPod Serverless endpoint
    # Created: 2025-12-29 - ziggie-sdxl-simple (1-Click SDXL)
    # TESTED WORKING: Generated 994KB image in ~200s
    ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "jh2wlpn04ewwjw")
    RUN_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"

    headers = {
        "Authorization": f"Bearer {CONFIG['runpod_api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 25,
            "guidance_scale": 7.5
        }
    }

    try:
        # Submit job (async)
        response = requests.post(RUN_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            logger.log("Stage 1", "Job submission failed", "FAILED", {
                "status": response.status_code,
                "response": response.text[:500]
            })
            return False, ""

        result = response.json()
        job_id = result.get("id")

        if not job_id:
            logger.log("Stage 1", "No job ID in response", "FAILED", {"response": str(result)[:500]})
            return False, ""

        logger.log("Stage 1", f"Job submitted: {job_id}", "IN_PROGRESS")

        # Poll for result (max 10 minutes for cold start + generation)
        STATUS_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"

        for i in range(60):  # 60 * 10s = 10 minutes max
            time.sleep(10)
            status_resp = requests.get(STATUS_URL, headers=headers, timeout=30)
            status_result = status_resp.json()
            status = status_result.get("status")

            logger.log("Stage 1", f"Poll {i+1}: {status}", "IN_PROGRESS")

            if status == "COMPLETED":
                output = status_result.get("output", {})

                # Handle different output formats
                image_b64 = None
                if isinstance(output, dict):
                    if "images" in output and output["images"]:
                        image_b64 = output["images"][0]
                    elif "image" in output:
                        image_b64 = output["image"]

                if image_b64:
                    # Remove data:image/... prefix if present
                    if "," in str(image_b64):
                        image_b64 = image_b64.split(",")[1]

                    if not output_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = f"{CONFIG['stage1_output']}/generated_{timestamp}.png"

                    # Decode and save
                    image_data = base64.b64decode(image_b64)
                    with open(output_path, "wb") as f:
                        f.write(image_data)

                    logger.log("Stage 1", "Generation complete", "SUCCESS", {
                        "output": output_path,
                        "size_bytes": len(image_data)
                    })
                    return True, output_path

                logger.log("Stage 1", "No image in output", "FAILED", {"output_keys": list(output.keys()) if isinstance(output, dict) else str(type(output))})
                return False, ""

            elif status == "FAILED":
                logger.log("Stage 1", "Generation failed", "FAILED", {
                    "error": status_result.get("error", "Unknown")
                })
                return False, ""

            elif status not in ["IN_QUEUE", "IN_PROGRESS"]:
                logger.log("Stage 1", f"Unknown status: {status}", "FAILED")
                return False, ""

        logger.log("Stage 1", "Timeout waiting for generation", "FAILED")
        return False, ""

    except Exception as e:
        logger.log("Stage 1", "Exception", "FAILED", {"error": str(e)})
        return False, ""


# =============================================================================
# GLB Thumbnail Generation
# =============================================================================

def generate_glb_thumbnail(glb_path: str, output_path: str = None, resolution: int = 512) -> Optional[str]:
    """
    Generate a PNG thumbnail preview of a GLB 3D model using Blender.

    Args:
        glb_path: Path to the GLB file
        output_path: Where to save the thumbnail (auto-generated if None)
        resolution: Thumbnail size in pixels (default 512x512)

    Returns:
        Path to the generated thumbnail, or None if failed
    """
    if not os.path.exists(glb_path):
        logger.log("Thumbnail", f"GLB not found: {glb_path}", "FAILED")
        return None

    # Generate output path
    if not output_path:
        output_path = str(Path(glb_path).with_suffix('')) + "_thumbnail.png"

    # Path to Blender
    blender_path = CONFIG.get("blender_path", "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe")

    if not os.path.exists(blender_path):
        logger.log("Thumbnail", f"Blender not found: {blender_path}", "FAILED")
        return None

    # Path to thumbnail script
    script_dir = Path(__file__).parent
    script_path = script_dir / "blender_thumbnail.py"

    if not script_path.exists():
        logger.log("Thumbnail", f"Script not found: {script_path}", "FAILED")
        return None

    try:
        logger.log("Thumbnail", f"Generating preview for {Path(glb_path).name}", "IN_PROGRESS")

        cmd = [
            blender_path,
            "--background",
            "--python", str(script_path),
            "--",
            "--input", glb_path,
            "--output", output_path,
            "--resolution", str(resolution)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and os.path.exists(output_path):
            logger.log("Thumbnail", f"Generated: {output_path}", "SUCCESS")
            return output_path
        else:
            logger.log("Thumbnail", "Blender render failed", "FAILED", {
                "returncode": result.returncode,
                "stderr": result.stderr[:500] if result.stderr else None
            })
            return None

    except subprocess.TimeoutExpired:
        logger.log("Thumbnail", "Blender timeout", "FAILED")
        return None
    except Exception as e:
        logger.log("Thumbnail", f"Exception: {e}", "FAILED")
        return None


# =============================================================================
# Human Approval Gate
# =============================================================================

def human_approval_gate(stage: str, asset_path: str, auto_approve: bool = False) -> Tuple[bool, str]:
    """
    Human approval gate - AI presents result, human approves/rejects.

    Approval priority chain:
    1. n8n workflow (Hostinger VPS at ziggie.cloud/n8n) - Interactive web form
    2. Discord bot (Ziggie-mini) - Reaction/button based approvals
    3. Console input - Fallback for local testing

    Args:
        stage: Stage name for logging
        asset_path: Path to asset for review
        auto_approve: Skip human review (for testing)

    Returns:
        Tuple[bool, str]: (approved: bool, decision: str)
        - decision contains the full decision string (e.g., "approved_tripo", "skip_3d")
    """
    if auto_approve:
        logger.log(stage, f"Auto-approved: {asset_path}", "APPROVED")
        return True, "approved"

    # Extract stage number from stage string (e.g., "Gate 2" -> 2)
    stage_number = None
    for word in stage.split():
        if word.isdigit():
            stage_number = int(word)
            break

    # Get asset name for display
    asset_name = Path(asset_path).stem if asset_path else "Unknown Asset"

    # Determine preview image path
    # For GLB files, generate a thumbnail since Discord can't display 3D models
    preview_path = None
    if asset_path and os.path.exists(asset_path):
        ext = Path(asset_path).suffix.lower()
        if ext in ['.glb', '.gltf']:
            # Generate thumbnail for 3D model
            print(f"[{stage}] Generating 3D model preview thumbnail...")
            thumbnail_path = generate_glb_thumbnail(asset_path)
            if thumbnail_path:
                preview_path = thumbnail_path
                print(f"[{stage}] Thumbnail generated: {thumbnail_path}")
            else:
                print(f"[{stage}] Warning: Could not generate thumbnail, no preview available")
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            preview_path = asset_path

    # Use notification system if available (Discord bot -> Console)
    # Skip n8n for now as workflow is not activated on Hostinger VPS
    if NOTIFICATIONS_ENABLED:
        print(f"\n[{stage}] Requesting approval via Discord bot...")
        decision, feedback = request_approval(
            title=f"{stage}: Review Required",
            description=f"Please review the output and approve, reject, or request regeneration.",
            image_path=preview_path,  # Use thumbnail for GLB files
            timeout_seconds=300,  # 5 minute timeout per gate
            stage_number=stage_number,
            asset_name=asset_name,
            use_n8n=False,  # Skip n8n (not activated)
            use_discord_bot=True
        )

        # Handle approval decisions - check for prefix matches
        # Discord decision views return: approved, approved_tripo, approved_meshy, approved_skip_3d, etc.
        if decision and decision.startswith("approved"):
            # Extract any specific choice from the decision (e.g., "tripo" from "approved_tripo")
            choice = decision.replace("approved_", "").replace("approved", "") if "_" in decision else None
            if choice:
                logger.log(stage, f"Approved with choice '{choice}': {asset_path}", "APPROVED")
                print(f"[{stage}] User selected: {choice}")
            else:
                logger.log(stage, f"Approved: {asset_path}", "APPROVED")
            return True, decision
        elif decision == "rejected":
            logger.log(stage, f"Rejected: {asset_path}", "REJECTED", {"feedback": feedback})
            return False, decision
        elif decision == "regenerate":
            logger.log(stage, f"Regeneration requested: {asset_path}", "REGENERATE", {"feedback": feedback})
            return False, decision
        elif decision and decision.startswith("skip"):
            # Handle skip decisions (skip_3d, skip_animation, etc.)
            logger.log(stage, f"Skipped: {asset_path}", "SKIPPED", {"decision": decision})
            print(f"[{stage}] User chose to skip: {decision}")
            return True, decision  # Treat skip as approval to continue pipeline
        else:
            # timeout or error - fall through to console
            print(f"[{stage}] Approval system returned: {decision}, falling back to console...")

    # Console fallback
    print(f"\n{'='*50}")
    print(f"APPROVAL REQUIRED: {stage}")
    print(f"Description: Please review the output and approve, reject, or request regeneration.")
    print(f"{'='*50}")
    print(f"Options: [a]pprove, [r]eject, [g]enerate again")

    # Check if stdin is interactive
    if not sys.stdin.isatty():
        print("[Approval] Non-interactive mode detected, auto-approving")
        logger.log(stage, f"Auto-approved (non-interactive): {asset_path}", "APPROVED")
        return True, "approved"

    while True:
        response = input("Your decision (a/r/g): ").strip().lower()
        if response in ['a', 'approve', 'y', 'yes']:
            logger.log(stage, f"Human approved: {asset_path}", "APPROVED")
            return True, "approved"
        elif response in ['r', 'reject', 'n', 'no']:
            logger.log(stage, f"Human rejected: {asset_path}", "REJECTED")
            return False, "rejected"
        elif response in ['g', 'regenerate']:
            logger.log(stage, f"Regeneration requested: {asset_path}", "REGENERATE")
            return False, "regenerate"
        print("Please enter 'a' (approve), 'r' (reject), or 'g' (regenerate)")


# =============================================================================
# Full Pipeline Execution
# =============================================================================

def run_pipeline_stage2_3(input_image: str, auto_approve: bool = False) -> Dict[str, Any]:
    """
    Run Stages 2-3 of the pipeline on an existing image.

    Stage 1 (generation) is skipped - we use existing concept art.

    Args:
        input_image: Path to concept image with background
        auto_approve: Skip human approval gates

    Returns:
        Dict with results from each stage
    """
    results = {
        "input": input_image,
        "stage2": {"success": False, "output": None},
        "stage3": {"success": False, "output": None},
        "final_output": None
    }

    print(f"\n{'='*60}")
    print(f"AUTOMATED PIPELINE - STAGES 2-3")
    print(f"Input: {input_image}")
    print(f"{'='*60}\n")

    # Stage 2: Background Removal
    success, stage2_output = stage2_remove_background(input_image)
    results["stage2"]["success"] = success
    results["stage2"]["output"] = stage2_output

    if not success:
        logger.log("Pipeline", "Stage 2 failed, aborting", "FAILED")
        logger.save()
        return results

    # Human Approval Gate 2
    approved, _ = human_approval_gate("Gate 2", stage2_output, auto_approve)
    if not approved:
        logger.log("Pipeline", "Rejected at Gate 2", "REJECTED")
        logger.save()
        return results

    # Stage 3: Upscaling
    success, stage3_output = stage3_upscale(stage2_output)
    results["stage3"]["success"] = success
    results["stage3"]["output"] = stage3_output

    if not success:
        logger.log("Pipeline", "Stage 3 failed", "FAILED")
        logger.save()
        return results

    # Human Approval Gate 3
    approved, _ = human_approval_gate("Gate 3", stage3_output, auto_approve)
    if not approved:
        logger.log("Pipeline", "Rejected at Gate 3", "REJECTED")
        logger.save()
        return results

    results["final_output"] = stage3_output
    logger.log("Pipeline", "Complete", "SUCCESS", {"final": stage3_output})
    logger.save()

    return results


def run_full_pipeline(prompt: str = None, input_image: str = None, auto_approve: bool = False) -> Dict[str, Any]:
    """
    Run full pipeline Stages 1-7 with all approval gates.

    Either provide a prompt (starts from Stage 1) or an input_image (starts from Stage 2).

    Args:
        prompt: Text prompt for Stage 1 (2D generation)
        input_image: Path to existing concept image (skips Stage 1)
        auto_approve: Skip human approval gates

    Returns:
        Dict with results from each stage
    """
    results = {
        "stage1": {"success": False, "output": None},
        "stage2": {"success": False, "output": None},
        "stage3": {"success": False, "output": None},
        "stage4": {"success": False, "output": None},
        "stage5": {"success": False, "output": None},
        "stage6": {"success": False, "output": None},
        "stage7": {"success": False, "output": None},
        "final_output": None
    }

    print(f"\n{'='*60}")
    print(f"FULL PIPELINE - STAGES 1-7 WITH APPROVAL GATES")
    if prompt:
        print(f"Prompt: {prompt[:80]}...")
    else:
        print(f"Input: {input_image}")
    print(f"{'='*60}\n")

    # Stage 1: 2D Generation (if prompt provided)
    if prompt:
        print("\n[Stage 1] 2D Generation via RunPod SDXL...")
        success, stage1_output = stage1_generate_2d(prompt)
        results["stage1"]["success"] = success
        results["stage1"]["output"] = stage1_output

        if not success:
            logger.log("Pipeline", "Stage 1 failed, aborting", "FAILED")
            logger.save()
            return results

        print(f"[Stage 1] SUCCESS: {stage1_output}")

        # Human Approval Gate 1
        approved, _ = human_approval_gate("Gate 1", stage1_output, auto_approve)
        if not approved:
            logger.log("Pipeline", "Rejected at Gate 1", "REJECTED")
            logger.save()
            return results

        input_image = stage1_output
    else:
        results["stage1"]["success"] = True
        results["stage1"]["output"] = "SKIPPED - using existing image"

    # Stage 2: Background Removal
    print("\n[Stage 2] Background Removal via BRIA RMBG...")
    success, stage2_output = stage2_remove_background(input_image)
    results["stage2"]["success"] = success
    results["stage2"]["output"] = stage2_output

    if not success:
        logger.log("Pipeline", "Stage 2 failed, aborting", "FAILED")
        logger.save()
        return results

    print(f"[Stage 2] SUCCESS: {stage2_output}")

    # Human Approval Gate 2
    approved, _ = human_approval_gate("Gate 2", stage2_output, auto_approve)
    if not approved:
        logger.log("Pipeline", "Rejected at Gate 2", "REJECTED")
        logger.save()
        return results

    # Stage 3: Upscaling
    print("\n[Stage 3] 4x Upscaling via PIL Lanczos...")
    success, stage3_output = stage3_upscale(stage2_output)
    results["stage3"]["success"] = success
    results["stage3"]["output"] = stage3_output

    if not success:
        logger.log("Pipeline", "Stage 3 failed", "FAILED")
        logger.save()
        return results

    print(f"[Stage 3] SUCCESS: {stage3_output}")

    # Human Approval Gate 3 (with 3D service choice)
    approved, gate3_decision = human_approval_gate("Gate 3", stage3_output, auto_approve)
    if not approved:
        logger.log("Pipeline", "Rejected at Gate 3", "REJECTED")
        logger.save()
        return results

    # Extract 3D service choice from Gate 3 decision
    # Possible decisions: approved_tripo, approved_meshy, approved_triposr, skip_3d, approved
    service_3d = "meshy"  # Default
    if "tripo" in gate3_decision.lower() and "triposr" not in gate3_decision.lower():
        service_3d = "tripo"
    elif "triposr" in gate3_decision.lower():
        service_3d = "triposr"
    elif "skip" in gate3_decision.lower():
        service_3d = "skip"

    print(f"[Gate 3] 3D service selected: {service_3d}")

    # Stage 4: 2D to 3D (based on Gate 3 choice)
    if service_3d == "skip":
        print("\n[Stage 4] SKIPPED - User chose 2D sprites only")
        results["stage4"]["success"] = True
        results["stage4"]["output"] = "SKIPPED"
        results["stage4"]["source"] = "skip"
        stage4_output = None
    elif service_3d == "tripo":
        # Check if Tripo API key is available
        if CONFIG.get("tripo_api_key"):
            print("\n[Stage 4] 2D to 3D via Tripo AI (with rigging support)...")
            success, stage4_output = stage4_tripo_with_rigging(stage3_output)
            results["stage4"]["success"] = success
            results["stage4"]["output"] = stage4_output
            results["stage4"]["source"] = "tripo"
        else:
            # Fallback to Meshy if Tripo API key not configured
            print("\n[Stage 4] Warning: TRIPO_API_KEY not configured")
            print("[Stage 4] Falling back to Meshy.ai for 3D generation")
            print("[Stage 4] Note: Meshy models require manual rigging (Mixamo/Cascadeur)")
            success, stage4_output = stage4_2d_to_3d(stage3_output)
            results["stage4"]["success"] = success
            results["stage4"]["output"] = stage4_output
            results["stage4"]["source"] = "tripo_fallback_meshy"
            logger.log("Stage 4", "Tripo selected but API key not configured, using Meshy fallback", "WARNING")
    elif service_3d == "triposr":
        print("\n[Stage 4] 2D to 3D via TripoSR (manual Colab)...")
        # TripoSR requires manual upload - for now, fall back to Meshy
        print("[Stage 4] Note: TripoSR manual mode - using Meshy.ai as automated fallback")
        success, stage4_output = stage4_2d_to_3d(stage3_output)
        results["stage4"]["success"] = success
        results["stage4"]["output"] = stage4_output
        results["stage4"]["source"] = "triposr_fallback_meshy"
    else:  # meshy (default)
        print("\n[Stage 4] 2D to 3D via Meshy.ai...")
        success, stage4_output = stage4_2d_to_3d(stage3_output)
        results["stage4"]["success"] = success
        results["stage4"]["output"] = stage4_output
        results["stage4"]["source"] = "meshy"

    # Handle Stage 4 skip case
    if service_3d == "skip":
        # Skip Stage 4 and 5 (no 3D model to render)
        print("[Stage 4] Skipped - proceeding to Stage 6 (2D sprite sheet from upscaled image)")
        results["stage5"]["success"] = True
        results["stage5"]["output"] = "SKIPPED - 2D only mode"

        # Stage 6: Create sprite sheet directly from 2D image
        print("\n[Stage 6] Sprite Sheet Assembly from 2D image...")
        # For 2D-only mode, we'd need a different sprite sheet approach
        # For now, mark as skipped and continue to Stage 7
        results["stage6"]["success"] = True
        results["stage6"]["output"] = stage3_output  # Use upscaled image as the "sheet"
        stage6_output = stage3_output
    else:
        if not results["stage4"]["success"]:
            logger.log("Pipeline", "Stage 4 failed", "FAILED")
            logger.save()
            return results

        print(f"[Stage 4] SUCCESS: {stage4_output}")

        # Human Approval Gate 4 (with animation decision)
        # Pass the 3D source info for proper rigging options
        approved, gate4_decision = human_approval_gate("Gate 4", stage4_output, auto_approve)
        if not approved:
            logger.log("Pipeline", "Rejected at Gate 4", "REJECTED")
            logger.save()
            return results

        # Stage 5: 8-Direction Sprites
        print("\n[Stage 5] 8-Direction Sprite Rendering via Blender...")
        success, stage5_outputs = stage5_render_sprites(stage4_output)
        results["stage5"]["success"] = success
        results["stage5"]["output"] = stage5_outputs

        if not success:
            logger.log("Pipeline", "Stage 5 failed", "FAILED")
            logger.save()
            return results

        print(f"[Stage 5] SUCCESS: {len(stage5_outputs)} sprites rendered")

        # Human Approval Gate 5 (preview first sprite)
        preview_sprite = stage5_outputs[0] if stage5_outputs else None
        approved, _ = human_approval_gate("Gate 5", preview_sprite, auto_approve)
        if not approved:
            logger.log("Pipeline", "Rejected at Gate 5", "REJECTED")
            logger.save()
            return results

        # Stage 6: Sprite Sheet Assembly
        print("\n[Stage 6] Sprite Sheet Assembly...")
        sprite_dir = os.path.dirname(stage5_outputs[0]) if stage5_outputs else CONFIG["stage5_output"]
        success, stage6_output = stage6_from_directory(sprite_dir)
        results["stage6"]["success"] = success
        results["stage6"]["output"] = stage6_output

        if not success:
            logger.log("Pipeline", "Stage 6 failed", "FAILED")
            logger.save()
            return results

        print(f"[Stage 6] SUCCESS: {stage6_output}")

        # Human Approval Gate 6
        approved, _ = human_approval_gate("Gate 6", stage6_output, auto_approve)
        if not approved:
            logger.log("Pipeline", "Rejected at Gate 6", "REJECTED")
            logger.save()
            return results

    # Stage 7: Faction Color Variants
    print("\n[Stage 7] Faction Color Variants...")
    success, stage7_results = stage7_create_faction_variants(stage6_output)
    results["stage7"]["success"] = success
    results["stage7"]["output"] = stage7_results

    if not success:
        logger.log("Pipeline", "Stage 7 failed", "FAILED")
        logger.save()
        return results

    print(f"[Stage 7] SUCCESS: {len(stage7_results)} faction variants created")

    # Human Approval Gate 7 (preview red variant)
    preview_variant = stage7_results.get('red') or list(stage7_results.values())[0]
    approved, _ = human_approval_gate("Gate 7", preview_variant, auto_approve)
    if not approved:
        logger.log("Pipeline", "Rejected at Gate 7", "REJECTED")
        logger.save()
        return results

    results["final_output"] = stage7_results
    logger.log("Pipeline", "FULL PIPELINE COMPLETE", "SUCCESS", {
        "stages_completed": 7,
        "faction_variants": list(stage7_results.keys())
    })
    logger.save()

    print(f"\n{'='*60}")
    print(f"FULL PIPELINE COMPLETE - ALL 7 STAGES PASSED")
    print(f"Final outputs: {list(stage7_results.keys())} faction variants")
    print(f"{'='*60}\n")

    return results


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command line interface for the pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Asset Pipeline Stages 1-7")
    parser.add_argument("--input", "-i", help="Input file path (image or GLB)")
    parser.add_argument("--prompt", "-p", help="Text prompt for Stage 1 (2D generation)")
    parser.add_argument("--stage", "-s", type=int, choices=[1, 2, 3, 4, 5, 6, 7], help="Run single stage")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Auto-approve all gates")
    parser.add_argument("--remote", "-r", action="store_true", help="Use remote VPS for Stage 5 rendering")
    parser.add_argument("--test", "-t", action="store_true", help="Run test with default asset")
    parser.add_argument("--test-stage1", action="store_true", help="Test Stage 1 (2D generation) with sample prompt")
    parser.add_argument("--test-stage4", action="store_true", help="Test Stage 4 (2D to 3D) with existing nobg asset")
    parser.add_argument("--test-stage5", action="store_true", help="Test Stage 5 (8-dir sprites) with existing GLB (local)")
    parser.add_argument("--test-stage5-remote", action="store_true", help="Test Stage 5 on Hostinger VPS (remote)")
    parser.add_argument("--test-stage6", action="store_true", help="Test Stage 6 (sprite sheet) with existing sprites")
    parser.add_argument("--test-stage7", action="store_true", help="Test Stage 7 (faction colors) with existing sprite sheet")
    parser.add_argument("--full-pipeline", action="store_true", help="Run full pipeline (Stages 1-7) with all approval gates")

    args = parser.parse_args()

    if args.test_stage1:
        # Test Stage 1 with sample prompt
        test_prompt = "A medieval cat warrior knight, full body, front view, fantasy game character, stylized art, clean edges, solid color background"
        print(f"Testing Stage 1 (2D Generation) with prompt:")
        print(f"  '{test_prompt}'")
        print(f"\nThis will use RunPod SDXL Serverless API (~2-4 min including cold start)")

        success, output = stage1_generate_2d(test_prompt)
        print(f"\nStage 1: {'SUCCESS' if success else 'FAILED'}")
        if success:
            print(f"Output: {output}")
            print(f"Size: {os.path.getsize(output):,} bytes")

            # Approval gate for Stage 1
            if not args.auto_approve:
                approved, _ = human_approval_gate("Gate 1", output, auto_approve=False)
                if not approved:
                    print("[Gate 1] Rejected - stopping pipeline")
                    sys.exit(1)
                print("[Gate 1] APPROVED - ready for Stage 2")
        else:
            print("Stage 1 failed - check RunPod API key and endpoint")

    elif args.test_stage4:
        # Test Stage 4 with an existing background-removed asset
        test_inputs = [
            "C:/Ziggie/assets/test-results/stage2_nobg",
            "C:/Ziggie/assets/test-results/stage3_upscaled"
        ]
        test_file = None
        for dir_path in test_inputs:
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.png')]
                if files:
                    test_file = f"{dir_path}/{files[0]}"
                    break

        if test_file:
            print(f"Testing Stage 4 with: {test_file}")
            success, output = stage4_2d_to_3d(test_file)
            print(f"\nStage 4: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Output: {output}")
                print(f"Size: {os.path.getsize(output):,} bytes")
        else:
            print("No test files found. Run Stages 2-3 first to generate assets.")

    elif args.test_stage5:
        # Test Stage 5 with an existing GLB model (local Blender)
        test_dir = CONFIG["stage4_output"]
        test_file = None
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.glb')]
            if files:
                test_file = f"{test_dir}/{files[0]}"

        if test_file:
            print(f"Testing Stage 5 (LOCAL) with: {test_file}")
            success, outputs = stage5_render_sprites(test_file)
            print(f"\nStage 5: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Rendered {len(outputs)} sprites:")
                for sprite in outputs:
                    print(f"  - {sprite} ({os.path.getsize(sprite):,} bytes)")
        else:
            print("No GLB files found. Run Stage 4 first to generate 3D models.")

    elif args.test_stage5_remote:
        # Test Stage 5 on Hostinger VPS (remote Blender)
        test_dir = CONFIG["stage4_output"]
        test_file = None
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.glb')]
            if files:
                test_file = f"{test_dir}/{files[0]}"

        if test_file:
            print(f"Testing Stage 5 (REMOTE VPS: {CONFIG['vps_host']}) with: {test_file}")
            success, outputs = stage5_render_sprites_remote(test_file)
            print(f"\nStage 5 Remote: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Rendered {len(outputs)} sprites on VPS:")
                for sprite in outputs:
                    print(f"  - {sprite} ({os.path.getsize(sprite):,} bytes)")
        else:
            print("No GLB files found. Run Stage 4 first to generate 3D models.")

    elif args.test_stage6:
        # Test Stage 6 with existing sprites
        sprite_dir = CONFIG["stage5_output"]
        print(f"Testing Stage 6 with sprites from: {sprite_dir}")
        success, output = stage6_from_directory(sprite_dir)
        print(f"\nStage 6: {'SUCCESS' if success else 'FAILED'}")
        if success:
            print(f"Sprite sheet: {output}")
            print(f"Size: {os.path.getsize(output):,} bytes")
            # Show dimensions
            from PIL import Image
            img = Image.open(output)
            print(f"Dimensions: {img.size[0]}x{img.size[1]}")

    elif args.test_stage7:
        # Test Stage 7 with existing sprite sheet
        sprite_dir = CONFIG["stage5_output"]
        # Find sprite sheet from Stage 6
        sprite_sheets = [f for f in os.listdir(sprite_dir) if f.endswith('_spritesheet.png')]
        if sprite_sheets:
            test_file = f"{sprite_dir}/{sprite_sheets[0]}"
            print(f"Testing Stage 7 with: {test_file}")
            success, results = stage7_create_faction_variants(test_file)
            print(f"\nStage 7: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Created {len(results)} faction variants:")
                for faction, path in results.items():
                    print(f"  - {faction}: {path} ({os.path.getsize(path):,} bytes)")
        else:
            print("No sprite sheets found. Run Stage 6 first.")

    elif args.test:
        # Use default test asset
        test_input = "C:/Ziggie/assets/concepts/salvage_warrior_v2.jpg"
        print(f"Running test with: {test_input}")
        results = run_pipeline_stage2_3(test_input, auto_approve=args.auto_approve)
        print(f"\nResults: {json.dumps(results, indent=2)}")

    elif args.full_pipeline:
        # Run full pipeline Stages 1-7
        if args.prompt:
            # Start from Stage 1 with prompt
            print(f"Running FULL PIPELINE (Stages 1-7) with prompt:")
            print(f"  '{args.prompt[:80]}...'")
            results = run_full_pipeline(prompt=args.prompt, auto_approve=args.auto_approve)
        elif args.input:
            # Start from Stage 2 with input image
            print(f"Running FULL PIPELINE (Stages 2-7) with input image:")
            print(f"  {args.input}")
            results = run_full_pipeline(input_image=args.input, auto_approve=args.auto_approve)
        else:
            print("Error: --full-pipeline requires --prompt (for Stage 1) or --input (to start from Stage 2)")
            print("Examples:")
            print("  python automated_pipeline.py --full-pipeline --prompt 'A medieval cat warrior knight...'")
            print("  python automated_pipeline.py --full-pipeline --input /path/to/concept.png")
            sys.exit(1)
        print(f"\nFull Pipeline Results: {json.dumps(results, indent=2, default=str)}")

    elif args.prompt and args.stage == 1:
        # Stage 1: 2D Generation with prompt
        print(f"Stage 1: Generating 2D concept from prompt...")
        print(f"  Prompt: {args.prompt[:100]}...")
        success, output = stage1_generate_2d(args.prompt)
        print(f"Stage 1: {'SUCCESS' if success else 'FAILED'} - {output}")

        # Approval gate for Stage 1
        if success and not args.auto_approve:
            approved, _ = human_approval_gate("Gate 1", output, auto_approve=False)
            if not approved:
                print("[Gate 1] Rejected - stopping pipeline")
                sys.exit(1)
            print("[Gate 1] APPROVED - ready for Stage 2")

    elif args.input:
        if args.stage == 1:
            print("Error: Stage 1 requires --prompt, not --input")
            print("Usage: python automated_pipeline.py --stage 1 --prompt 'A cat warrior knight...'")
            sys.exit(1)
        elif args.stage == 2:
            success, output = stage2_remove_background(args.input)
            print(f"Stage 2: {'SUCCESS' if success else 'FAILED'} - {output}")

            # Approval gate for Stage 2
            if success and not args.auto_approve:
                approved, _ = human_approval_gate("Gate 2", output, auto_approve=False)
                if not approved:
                    print("[Gate 2] Rejected - stopping pipeline")
                    sys.exit(1)

        elif args.stage == 3:
            success, output = stage3_upscale(args.input)
            print(f"Stage 3: {'SUCCESS' if success else 'FAILED'} - {output}")

            # Approval gate for Stage 3
            if success and not args.auto_approve:
                approved, _ = human_approval_gate("Gate 3", output, auto_approve=False)
                if not approved:
                    print("[Gate 3] Rejected - stopping pipeline")
                    sys.exit(1)
        elif args.stage == 4:
            success, output = stage4_2d_to_3d(args.input)
            print(f"Stage 4: {'SUCCESS' if success else 'FAILED'} - {output}")

            # Approval gate for Stage 4
            if success and not args.auto_approve:
                approved, _ = human_approval_gate("Gate 4", output, auto_approve=False)
                if not approved:
                    print("[Gate 4] Rejected - stopping pipeline")
                    sys.exit(1)
        elif args.stage == 5:
            if args.remote:
                print(f"Using remote VPS ({CONFIG['vps_host']}) for rendering...")
                success, outputs = stage5_render_sprites_remote(args.input)
            else:
                success, outputs = stage5_render_sprites(args.input)
            print(f"Stage 5: {'SUCCESS' if success else 'FAILED'}")
            if success:
                for sprite in outputs:
                    print(f"  - {sprite}")

                # Approval gate for Stage 5 - use first sprite (South) as preview
                if not args.auto_approve:
                    preview_sprite = outputs[0] if outputs else None
                    approved, _ = human_approval_gate("Gate 5", preview_sprite, auto_approve=False)
                    if not approved:
                        print("[Gate 5] Rejected - stopping pipeline")
                        sys.exit(1)
        elif args.stage == 6:
            # Input is directory containing sprites
            success, output = stage6_from_directory(args.input)
            print(f"Stage 6: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Sprite sheet: {output}")

                # Approval gate for Stage 6
                if not args.auto_approve:
                    approved, _ = human_approval_gate("Gate 6", output, auto_approve=False)
                    if not approved:
                        print("[Gate 6] Rejected - stopping pipeline")
                        sys.exit(1)
        elif args.stage == 7:
            # Input is sprite sheet PNG
            success, results = stage7_create_faction_variants(args.input)
            print(f"Stage 7: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"Created {len(results)} faction variants:")
                for faction, path in results.items():
                    print(f"  - {faction}: {path}")

                # Approval gate for Stage 7 - use red variant as preview
                if not args.auto_approve:
                    preview_path = results.get('red') or list(results.values())[0]
                    approved, _ = human_approval_gate("Gate 7", preview_path, auto_approve=False)
                    if not approved:
                        print("[Gate 7] Rejected - stopping pipeline")
                        sys.exit(1)
        else:
            results = run_pipeline_stage2_3(args.input, auto_approve=args.auto_approve)
            print(f"\nResults: {json.dumps(results, indent=2)}")
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python automated_pipeline.py --test")
        print("  python automated_pipeline.py --test-stage4")
        print("  python automated_pipeline.py --test-stage5         # Local Blender")
        print("  python automated_pipeline.py --test-stage5-remote  # Hostinger VPS")
        print("  python automated_pipeline.py --test-stage6         # Sprite sheet")
        print("  python automated_pipeline.py --test-stage7         # Faction colors")
        print("  python automated_pipeline.py --input image.jpg")
        print("  python automated_pipeline.py --input image.jpg --stage 2")
        print("  python automated_pipeline.py --input image.png --stage 3")
        print("  python automated_pipeline.py --input image_nobg.png --stage 4")
        print("  python automated_pipeline.py --input model.glb --stage 5          # Local")
        print("  python automated_pipeline.py --input model.glb --stage 5 --remote # VPS")
        print("  python automated_pipeline.py --input ./sprites/ --stage 6         # Sheet")
        print("  python automated_pipeline.py --input sheet.png --stage 7          # Factions")


if __name__ == "__main__":
    main()

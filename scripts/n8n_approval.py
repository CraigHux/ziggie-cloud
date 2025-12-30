"""
n8n Human-in-the-Loop Approval System
======================================
Interactive approval workflow using n8n forms.

Flow:
1. Pipeline calls n8n webhook with asset details
2. n8n sends Discord notification with form link
3. User clicks link and submits approval form
4. Pipeline receives decision and continues

Setup:
1. Import workflow from n8n-workflows/pipeline-approval-workflow.json into n8n
2. Activate the workflow in n8n
3. Set N8N_WEBHOOK_URL in environment or .env.local
4. Optionally set N8N_BASE_URL for form link generation

Usage:
    from n8n_approval import request_n8n_approval

    decision = request_n8n_approval(
        stage_name="Stage 4: 2D to 3D",
        asset_name="warrior_concept",
        image_path="/path/to/preview.png",
        description="Review the 3D model conversion"
    )

    if decision == "approved":
        # Continue pipeline
    elif decision == "rejected":
        # Stop pipeline
    elif decision == "regenerate":
        # Re-run stage with feedback
"""

import os
import time
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime


# Configuration
N8N_CONFIG = {
    "webhook_url": os.getenv("N8N_WEBHOOK_URL"),
    "base_url": os.getenv("N8N_BASE_URL", "http://localhost:5678"),
    "timeout_seconds": 3600,  # 1 hour default timeout
    "poll_interval": 5,  # For polling-based approach
}


def get_n8n_webhook_url() -> Optional[str]:
    """Get n8n webhook URL from environment or config file."""
    url = N8N_CONFIG["webhook_url"]

    if not url:
        # Check .env.local file
        env_file = Path("C:/Ziggie/.secrets/.env.local")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("N8N_WEBHOOK_URL="):
                        url = line.split("=", 1)[1].strip()
                        break

    return url


def image_to_data_url(image_path: str) -> Optional[str]:
    """Convert local image to base64 data URL for embedding."""
    if not os.path.exists(image_path):
        return None

    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }

    mime_type = mime_types.get(ext, 'image/png')

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:{mime_type};base64,{image_data}"


def upload_to_temp_hosting(image_path: str) -> Optional[str]:
    """
    Upload image to temporary hosting for Discord embed.

    Options:
    1. Use existing S3 bucket (if configured)
    2. Use imgbb.com free API
    3. Use local file server

    Returns public URL or None if failed.
    """
    if not os.path.exists(image_path):
        return None

    # Try imgbb (free image hosting)
    imgbb_key = os.getenv("IMGBB_API_KEY")
    if imgbb_key:
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": imgbb_key,
                    "image": image_data,
                    "expiration": 86400  # 24 hours
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["data"]["url"]
        except Exception as e:
            print(f"[n8n] imgbb upload failed: {e}")

    # Fallback: no image URL (form will work without preview)
    return None


def request_n8n_approval(
    stage_name: str,
    asset_name: str = None,
    image_path: str = None,
    description: str = None,
    stage_number: int = None,
    timeout_seconds: int = None,
    webhook_url: str = None
) -> Tuple[str, Optional[str]]:
    """
    Request approval via n8n Human-in-the-Loop workflow.

    This sends a request to n8n which:
    1. Sends Discord notification with form link
    2. Waits for user to submit the form
    3. Returns the decision to this function

    Args:
        stage_name: Name of the pipeline stage (e.g., "Stage 4: 2D to 3D")
        asset_name: Name of the asset being processed
        image_path: Path to preview image (will be uploaded for Discord embed)
        description: Description of what needs approval
        stage_number: Stage number (1-7)
        timeout_seconds: How long to wait for response (default: 1 hour)
        webhook_url: Override n8n webhook URL

    Returns:
        Tuple of (decision: str, feedback: Optional[str])
        Decision is one of: "approved", "rejected", "regenerate", "timeout", "error"
    """
    url = webhook_url or get_n8n_webhook_url()

    if not url:
        print("[n8n] No webhook URL configured. Set N8N_WEBHOOK_URL environment variable.")
        print("[n8n] Falling back to console input...")
        return _console_fallback(stage_name, description)

    timeout = timeout_seconds or N8N_CONFIG["timeout_seconds"]

    # Prepare image URL for Discord embed
    image_url = None
    if image_path:
        # Try to get a public URL for the image
        image_url = upload_to_temp_hosting(image_path)
        if not image_url:
            print(f"[n8n] Could not upload image for preview. Form will work without image.")

    # Build request payload
    payload = {
        "stage_name": stage_name,
        "asset_name": asset_name or "Unknown Asset",
        "description": description or f"Review {stage_name} output",
        "stage_number": stage_number,
        "image_url": image_url,
        "request_id": f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat()
    }

    print(f"[n8n] Sending approval request for: {stage_name}")
    print(f"[n8n] Waiting for human response (timeout: {timeout//60} minutes)...")
    print(f"[n8n] Check Discord for the approval form link")

    try:
        # Make request to n8n webhook
        # The workflow uses responseMode="responseNode" which means it waits
        # for the form submission before responding
        response = requests.post(
            url,
            json=payload,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            decision = result.get("decision", "error")
            feedback = result.get("feedback", "")

            print(f"[n8n] Received decision: {decision}")
            if feedback:
                print(f"[n8n] Feedback: {feedback}")

            return decision, feedback
        else:
            print(f"[n8n] Webhook returned error: {response.status_code}")
            print(f"[n8n] Response: {response.text[:500]}")
            return "error", f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        print(f"[n8n] Approval request timed out after {timeout//60} minutes")
        return "timeout", None

    except requests.exceptions.ConnectionError as e:
        print(f"[n8n] Could not connect to n8n: {e}")
        print("[n8n] Is n8n running? Check N8N_WEBHOOK_URL configuration.")
        print("[n8n] Falling back to console input...")
        return _console_fallback(stage_name, description)

    except Exception as e:
        print(f"[n8n] Error: {e}")
        return "error", str(e)


def _console_fallback(stage_name: str, description: str = None) -> Tuple[str, Optional[str]]:
    """Fallback to console input if n8n is not available."""
    print(f"\n{'='*50}")
    print(f"APPROVAL REQUIRED: {stage_name}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*50}")
    print("Options: [a]pprove, [r]eject, [g]enerate again")

    while True:
        response = input("Your decision (a/r/g): ").strip().lower()
        if response in ['a', 'approve']:
            return "approved", None
        elif response in ['r', 'reject']:
            feedback = input("Rejection reason (optional): ").strip()
            return "rejected", feedback or None
        elif response in ['g', 'regenerate']:
            feedback = input("Regeneration instructions (optional): ").strip()
            return "regenerate", feedback or None
        else:
            print("Invalid input. Please enter 'a', 'r', or 'g'")


def check_n8n_status() -> bool:
    """Check if n8n is running and accessible."""
    base_url = N8N_CONFIG["base_url"]

    try:
        # n8n health endpoint
        response = requests.get(f"{base_url}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_workflow_status(workflow_id: str = None) -> Dict[str, Any]:
    """Get status of the approval workflow in n8n."""
    base_url = N8N_CONFIG["base_url"]

    try:
        # This would require n8n API access with credentials
        # For now, just return basic connectivity status
        return {
            "n8n_accessible": check_n8n_status(),
            "webhook_configured": bool(get_n8n_webhook_url())
        }
    except Exception as e:
        return {"error": str(e)}


# Test function
def test_n8n_approval():
    """Test the n8n approval system."""
    print("Testing n8n approval system...")

    # Check n8n status
    status = get_workflow_status()
    print(f"n8n Status: {json.dumps(status, indent=2)}")

    if not status.get("webhook_configured"):
        print("\nNo webhook URL configured!")
        print("Set N8N_WEBHOOK_URL in environment or C:/Ziggie/.secrets/.env.local")
        print("\nExample:")
        print("  N8N_WEBHOOK_URL=http://localhost:5678/webhook/pipeline-approval")
        return False

    # Test approval request (will wait for form submission)
    print("\nSending test approval request...")
    decision, feedback = request_n8n_approval(
        stage_name="Test Stage",
        asset_name="test_asset",
        description="This is a test approval request",
        stage_number=0
    )

    print(f"\nTest result: {decision}")
    if feedback:
        print(f"Feedback: {feedback}")

    return decision in ["approved", "rejected", "regenerate"]


if __name__ == "__main__":
    test_n8n_approval()

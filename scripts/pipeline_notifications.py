"""
Pipeline Notification System
=============================
Discord webhook notifications with image embeds for pipeline stage completions.

Features:
- Embed images directly in Discord messages
- Color-coded status (green=success, red=fail, yellow=pending)
- Stage completion notifications with file previews
- n8n Human-in-the-Loop approval system (interactive web forms)
- Fallback to console input when n8n unavailable

Setup:
1. Create a Discord webhook in your server (Server Settings > Integrations > Webhooks)
2. Set DISCORD_WEBHOOK_URL environment variable or pass to functions
3. For interactive approvals: Set N8N_WEBHOOK_URL and import workflow into n8n

Usage:
    from pipeline_notifications import notify_stage_complete, request_approval

    # Simple notification
    notify_stage_complete("Stage 5", True, "path/to/sprite.png")

    # Request approval with n8n form (falls back to console)
    decision, feedback = request_approval("Stage 4 Complete", "path/to/model_preview.png")
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("Warning: discord-webhook not installed. Run: pip install discord-webhook")

# Try to import n8n approval system
try:
    from n8n_approval import request_n8n_approval, check_n8n_status
    N8N_AVAILABLE = True
except ImportError:
    N8N_AVAILABLE = False

# Try to import Discord bot approval system
try:
    from discord_bot import request_discord_approval, check_bot_status
    DISCORD_BOT_AVAILABLE = True
except ImportError:
    DISCORD_BOT_AVAILABLE = False


# Configuration
DISCORD_CONFIG = {
    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
    "approval_webhook_url": os.getenv("DISCORD_APPROVAL_WEBHOOK_URL"),  # Optional separate channel
    "bot_name": "Ziggie Pipeline",
    "bot_avatar": "https://raw.githubusercontent.com/github/explore/main/topics/python/python.png",
}

# Stage colors (Discord embed colors are decimal)
STAGE_COLORS = {
    "success": 0x00FF00,   # Green
    "failed": 0xFF0000,    # Red
    "pending": 0xFFFF00,   # Yellow
    "info": 0x0099FF,      # Blue
    "warning": 0xFF9900,   # Orange
}

# Stage icons
STAGE_ICONS = {
    1: "🎨",  # 2D Generation
    2: "✂️",  # Background Removal
    3: "🔍",  # Upscaling
    4: "🧊",  # 2D to 3D
    5: "📸",  # Sprite Rendering
    6: "📋",  # Sprite Sheet
    7: "🎭",  # Faction Colors
}


def get_webhook_url() -> Optional[str]:
    """Get webhook URL from environment or config."""
    url = DISCORD_CONFIG["webhook_url"]
    if not url:
        # Check .env.local file
        env_file = Path("C:/Ziggie/.secrets/.env.local")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("DISCORD_WEBHOOK_URL="):
                        url = line.split("=", 1)[1].strip()
                        break
    return url


def notify_stage_complete(
    stage_name: str,
    success: bool,
    output_path: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send Discord notification for stage completion.

    Args:
        stage_name: Name of the completed stage (e.g., "Stage 5: Sprite Rendering")
        success: Whether the stage succeeded
        output_path: Path to output file (image will be attached if PNG/JPG)
        details: Additional details to include in embed
        webhook_url: Override webhook URL

    Returns:
        True if notification sent successfully
    """
    if not DISCORD_AVAILABLE:
        print(f"[Discord] Would notify: {stage_name} - {'SUCCESS' if success else 'FAILED'}")
        return False

    url = webhook_url or get_webhook_url()
    if not url:
        print("[Discord] No webhook URL configured. Set DISCORD_WEBHOOK_URL environment variable.")
        return False

    try:
        # Create webhook
        webhook = DiscordWebhook(
            url=url,
            username=DISCORD_CONFIG["bot_name"],
            avatar_url=DISCORD_CONFIG["bot_avatar"]
        )

        # Determine stage number from name
        stage_num = None
        for num in range(1, 8):
            if f"Stage {num}" in stage_name or f"stage{num}" in stage_name.lower():
                stage_num = num
                break

        # Create embed
        color = STAGE_COLORS["success"] if success else STAGE_COLORS["failed"]
        icon = STAGE_ICONS.get(stage_num, "⚙️")
        status = "✅ SUCCESS" if success else "❌ FAILED"

        embed = DiscordEmbed(
            title=f"{icon} {stage_name}",
            description=f"**Status:** {status}",
            color=color
        )

        # Add timestamp
        embed.set_timestamp()

        # Add details as fields
        if details:
            for key, value in details.items():
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 100:
                    str_value = str_value[:97] + "..."
                embed.add_embed_field(name=key, value=str_value, inline=True)

        # Add output file info
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            file_name = os.path.basename(output_path)
            embed.add_embed_field(
                name="Output",
                value=f"`{file_name}`\n{file_size:,} bytes",
                inline=False
            )

            # Attach image if it's a supported format
            ext = Path(output_path).suffix.lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                with open(output_path, 'rb') as f:
                    webhook.add_file(file=f.read(), filename=file_name)
                embed.set_image(url=f"attachment://{file_name}")

        # Add embed to webhook
        webhook.add_embed(embed)

        # Send
        response = webhook.execute()

        if response.status_code in [200, 204]:
            print(f"[Discord] Notification sent: {stage_name}")
            return True
        else:
            print(f"[Discord] Failed to send: {response.status_code}")
            return False

    except Exception as e:
        print(f"[Discord] Error sending notification: {e}")
        return False


def notify_pipeline_start(
    asset_name: str,
    stages: List[str],
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send notification that pipeline is starting.

    Args:
        asset_name: Name of the asset being processed
        stages: List of stages to run
        webhook_url: Override webhook URL
    """
    if not DISCORD_AVAILABLE:
        return False

    url = webhook_url or get_webhook_url()
    if not url:
        return False

    try:
        webhook = DiscordWebhook(
            url=url,
            username=DISCORD_CONFIG["bot_name"],
            avatar_url=DISCORD_CONFIG["bot_avatar"]
        )

        embed = DiscordEmbed(
            title="🚀 Pipeline Started",
            description=f"Processing **{asset_name}**",
            color=STAGE_COLORS["info"]
        )

        embed.set_timestamp()

        # Add stages as checklist
        stages_text = "\n".join([f"⬜ {stage}" for stage in stages])
        embed.add_embed_field(name="Stages", value=stages_text, inline=False)

        webhook.add_embed(embed)
        response = webhook.execute()

        return response.status_code in [200, 204]

    except Exception as e:
        print(f"[Discord] Error: {e}")
        return False


def notify_pipeline_complete(
    asset_name: str,
    results: Dict[str, bool],
    total_time: float,
    final_outputs: List[str],
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send summary notification when pipeline completes.

    Args:
        asset_name: Name of the asset processed
        results: Dict of stage_name -> success
        total_time: Total processing time in seconds
        final_outputs: List of final output file paths
        webhook_url: Override webhook URL
    """
    if not DISCORD_AVAILABLE:
        return False

    url = webhook_url or get_webhook_url()
    if not url:
        return False

    try:
        webhook = DiscordWebhook(
            url=url,
            username=DISCORD_CONFIG["bot_name"],
            avatar_url=DISCORD_CONFIG["bot_avatar"]
        )

        # Determine overall success
        all_success = all(results.values())
        color = STAGE_COLORS["success"] if all_success else STAGE_COLORS["failed"]
        status_icon = "✅" if all_success else "⚠️"

        embed = DiscordEmbed(
            title=f"{status_icon} Pipeline Complete: {asset_name}",
            description=f"Total time: **{total_time:.1f}s** ({total_time/60:.1f} min)",
            color=color
        )

        embed.set_timestamp()

        # Stage results
        results_text = "\n".join([
            f"{'✅' if success else '❌'} {stage}"
            for stage, success in results.items()
        ])
        embed.add_embed_field(name="Stage Results", value=results_text, inline=False)

        # Final outputs
        if final_outputs:
            outputs_text = "\n".join([f"📁 `{os.path.basename(f)}`" for f in final_outputs[:5]])
            if len(final_outputs) > 5:
                outputs_text += f"\n... and {len(final_outputs) - 5} more"
            embed.add_embed_field(name="Outputs", value=outputs_text, inline=False)

            # Attach first image if available
            for output in final_outputs:
                ext = Path(output).suffix.lower()
                if ext in ['.png', '.jpg', '.jpeg'] and os.path.exists(output):
                    with open(output, 'rb') as f:
                        webhook.add_file(file=f.read(), filename=os.path.basename(output))
                    embed.set_image(url=f"attachment://{os.path.basename(output)}")
                    break

        webhook.add_embed(embed)
        response = webhook.execute()

        return response.status_code in [200, 204]

    except Exception as e:
        print(f"[Discord] Error: {e}")
        return False


def request_approval(
    title: str,
    description: str = None,
    image_path: Optional[str] = None,
    timeout_seconds: int = 3600,
    webhook_url: Optional[str] = None,
    stage_number: int = None,
    asset_name: str = None,
    use_n8n: bool = True,
    use_discord_bot: bool = True
) -> Tuple[str, Optional[str]]:
    """
    Request approval via n8n, Discord bot, or fallback to console.

    Priority:
    1. n8n workflow (if available and use_n8n=True) - Interactive web form
    2. Discord bot (if available and use_discord_bot=True) - Reaction/button based
    3. Console input - Direct terminal input (with Discord webhook preview)

    Args:
        title: Approval request title (e.g., "Stage 4: 2D to 3D")
        description: What needs approval
        image_path: Path to preview image
        timeout_seconds: How long to wait (default 1 hour)
        webhook_url: Override n8n webhook URL
        stage_number: Pipeline stage number (1-7)
        asset_name: Name of the asset being processed
        use_n8n: Whether to try n8n first (default True)
        use_discord_bot: Whether to try Discord bot (default True)

    Returns:
        Tuple of (decision: str, feedback: Optional[str])
        Decision is one of: "approved", "rejected", "regenerate", "timeout", "error"
    """
    # Try n8n first if available and enabled
    if use_n8n and N8N_AVAILABLE:
        try:
            decision, feedback = request_n8n_approval(
                stage_name=title,
                asset_name=asset_name or "Unknown Asset",
                image_path=image_path,
                description=description or f"Review {title} output",
                stage_number=stage_number,
                timeout_seconds=timeout_seconds,
                webhook_url=webhook_url
            )
            return decision, feedback
        except Exception as e:
            print(f"[n8n] Error: {e}")
            print("[n8n] Falling back to Discord bot...")

    # Try Discord bot if available and enabled
    if use_discord_bot and DISCORD_BOT_AVAILABLE:
        try:
            if check_bot_status():
                print("[Discord Bot] Sending approval request...")
                decision, feedback = request_discord_approval(
                    stage_name=title,
                    asset_name=asset_name or "Unknown Asset",
                    description=description or f"Review {title} output",
                    image_path=image_path,
                    stage_number=stage_number,
                    timeout_seconds=timeout_seconds
                )
                if decision not in ["error", "timeout"]:
                    return decision, feedback
                print(f"[Discord Bot] Result: {decision}, falling back to console...")
            else:
                print("[Discord Bot] Bot not connected, falling back to console...")
        except Exception as e:
            print(f"[Discord Bot] Error: {e}")
            print("[Discord Bot] Falling back to console input...")

    # Send Discord notification for visual preview (view-only via webhook)
    if DISCORD_AVAILABLE:
        url = DISCORD_CONFIG["approval_webhook_url"] or get_webhook_url()
        if url:
            try:
                webhook = DiscordWebhook(
                    url=url,
                    username=DISCORD_CONFIG["bot_name"],
                    avatar_url=DISCORD_CONFIG["bot_avatar"]
                )

                embed = DiscordEmbed(
                    title=f"Approval Required: {title}",
                    description=f"{description or 'Review required'}\n\n**Respond via console**",
                    color=STAGE_COLORS["pending"]
                )

                embed.set_timestamp()

                # Attach image if provided
                if image_path and os.path.exists(image_path):
                    ext = Path(image_path).suffix.lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                        with open(image_path, 'rb') as f:
                            webhook.add_file(file=f.read(), filename=os.path.basename(image_path))
                        embed.set_image(url=f"attachment://{os.path.basename(image_path)}")

                webhook.add_embed(embed)
                webhook.execute()
                print(f"[Discord] Preview sent: {title}")
            except Exception as e:
                print(f"[Discord] Preview notification failed: {e}")

    # Fallback to console input
    return _console_approval(title, description)


def _console_approval(title: str, description: str = None) -> Tuple[str, Optional[str]]:
    """Console-based approval input."""
    print(f"\n{'='*50}")
    print(f"APPROVAL REQUIRED: {title}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*50}")
    print("Options: [a]pprove, [r]eject, [g]enerate again")

    while True:
        try:
            response = input("Your decision (a/r/g): ").strip().lower()
            if response in ['a', 'approve', 'y', 'yes']:
                return "approved", None
            elif response in ['r', 'reject', 'n', 'no']:
                feedback = input("Rejection reason (optional): ").strip()
                return "rejected", feedback or None
            elif response in ['g', 'regenerate', 'regen']:
                feedback = input("Regeneration instructions (optional): ").strip()
                return "regenerate", feedback or None
            else:
                print("Invalid input. Please enter 'a' (approve), 'r' (reject), or 'g' (regenerate)")
        except EOFError:
            # Non-interactive mode
            print("[Approval] Non-interactive mode detected, auto-approving")
            return "approved", None


# Test functions
def test_notification():
    """Test the Discord notification system."""
    print("Testing Discord notifications...")

    url = get_webhook_url()
    if not url:
        print("No webhook URL configured!")
        print("Set DISCORD_WEBHOOK_URL in environment or .env.local file")
        return False

    # Test simple notification
    success = notify_stage_complete(
        "Stage 7: Faction Colors",
        True,
        details={
            "Variants": "red, blue, green, gold",
            "Time": "0.8s"
        }
    )

    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")
    return success


def test_approval():
    """Test the approval system (n8n + console fallback)."""
    print("Testing approval system...")
    print(f"n8n available: {N8N_AVAILABLE}")

    if N8N_AVAILABLE:
        try:
            n8n_status = check_n8n_status()
            print(f"n8n accessible: {n8n_status}")
        except:
            print("n8n status check failed")

    # Test approval request
    decision, feedback = request_approval(
        title="Test Approval",
        description="This is a test approval request. Approve, reject, or regenerate.",
        stage_number=0,
        asset_name="test_asset"
    )

    print(f"\nDecision: {decision}")
    if feedback:
        print(f"Feedback: {feedback}")

    return decision in ["approved", "rejected", "regenerate"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--approval":
        test_approval()
    else:
        test_notification()

"""
Discord Notification Examples for Ziggie Ecosystem

Run this file to see example notifications for each type.
Requires DISCORD_WEBHOOK_URL environment variable or .env file.
"""

import asyncio
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from integrations.discord import (
    DiscordWebhook,
    NotificationType,
    notify_asset_generated,
    notify_deployment,
    notify_error,
    notify_cost_alert,
    notify_backup,
)
from integrations.discord.templates import (
    AssetGeneratedTemplate,
    DeploymentSuccessTemplate,
    DeploymentFailedTemplate,
    CriticalErrorTemplate,
    ServiceDownTemplate,
    CostAlertTemplate,
    BackupCompleteTemplate,
    AgentStatusTemplate,
    BatchNotificationTemplate,
    HighResourceUsageTemplate,
)


async def example_asset_generated():
    """Example: Asset generation notification."""
    print("\n--- Asset Generated Notification ---")

    webhook = DiscordWebhook()

    # Method 1: Using convenience function
    await notify_asset_generated(
        webhook,
        asset_name="cat_archer_blue",
        asset_type="Unit Sprite",
        quality_rating="AAA",
        preview_url="https://via.placeholder.com/512x512/9B59B6/ffffff?text=Cat+Archer",
        details={
            "Faction": "Blue",
            "Animations": "8 directions",
            "File Size": "256 KB"
        }
    )

    # Method 2: Using template
    template = AssetGeneratedTemplate(
        asset_name="stone_wall_texture",
        asset_type="Texture",
        quality="AA",
        dimensions="1024x1024",
        generation_time=4.5,
        model_used="SDXL 1.0"
    )
    await webhook.send_message(embeds=[template.to_dict()["embeds"][0]])

    await webhook.close()
    print("Asset notifications sent!")


async def example_deployment():
    """Example: Deployment notifications (success and failure)."""
    print("\n--- Deployment Notifications ---")

    webhook = DiscordWebhook()

    # Success notification
    await notify_deployment(
        webhook,
        environment="production",
        version="v1.2.3",
        status="Success",
        services=["ziggie-api", "mcp-gateway", "nginx", "redis"],
        duration="2m 34s"
    )

    await asyncio.sleep(1)  # Prevent rate limiting

    # Using template for failed deployment
    template = DeploymentFailedTemplate(
        environment="staging",
        version="v1.2.4-beta",
        error_message="Container failed health check after 3 retries",
        failed_step="Health Check",
        logs_url="https://logs.example.com/deploy/12345"
    )
    payload = template.to_dict()
    await webhook.send_message(
        content=payload.get("content"),
        embeds=[embed for embed in payload.get("embeds", [])]
    )

    await webhook.close()
    print("Deployment notifications sent!")


async def example_error():
    """Example: Error notifications (regular and critical)."""
    print("\n--- Error Notifications ---")

    webhook = DiscordWebhook()

    # Regular error
    await notify_error(
        webhook,
        error_type="DatabaseConnectionError",
        error_message="Connection to PostgreSQL failed: timeout after 30 seconds",
        source="ziggie-api/database.py",
        severity="ERROR",
        trace="""Traceback (most recent call last):
  File "database.py", line 42, in connect
    connection = await asyncpg.connect(...)
  File "asyncpg/connect.py", line 127, in connect
    await asyncio.wait_for(...)
asyncio.TimeoutError: Connection timed out"""
    )

    await asyncio.sleep(1)

    # Critical error using template
    template = CriticalErrorTemplate(
        error_type="SecurityBreach",
        error_message="Unauthorized access attempt detected from IP 192.168.1.100",
        source="nginx/access.log",
        context={
            "IP Address": "192.168.1.100",
            "Attempts": "47",
            "Target": "/admin/users"
        }
    )
    payload = template.to_dict()
    await webhook.send_message(
        content=payload.get("content"),
        embeds=[embed for embed in payload.get("embeds", [])]
    )

    await asyncio.sleep(1)

    # Service down notification
    template = ServiceDownTemplate(
        service_name="ComfyUI",
        last_seen=datetime.utcnow() - timedelta(minutes=15),
        health_check_url="http://localhost:8188/system_stats"
    )
    payload = template.to_dict()
    await webhook.send_message(
        content=payload.get("content"),
        embeds=[embed for embed in payload.get("embeds", [])]
    )

    await webhook.close()
    print("Error notifications sent!")


async def example_cost_alert():
    """Example: Cost alert notifications."""
    print("\n--- Cost Alert Notifications ---")

    webhook = DiscordWebhook()

    # Medium threshold alert
    await notify_cost_alert(
        webhook,
        service="AWS S3",
        current_cost=45.50,
        budget_limit=50.00,
        threshold_percent=80,
        period="monthly"
    )

    await asyncio.sleep(1)

    # Exceeded budget using template
    template = CostAlertTemplate(
        service="AWS EC2 (GPU)",
        current_cost=125.00,
        budget_limit=100.00,
        period="monthly",
        forecast=180.00,
        breakdown={
            "g4dn.xlarge (spot)": 85.00,
            "g4dn.xlarge (on-demand)": 30.00,
            "Data Transfer": 10.00
        }
    )
    payload = template.to_dict()
    await webhook.send_message(
        content=payload.get("content"),
        embeds=[embed for embed in payload.get("embeds", [])]
    )

    await webhook.close()
    print("Cost notifications sent!")


async def example_backup():
    """Example: Backup notifications."""
    print("\n--- Backup Notifications ---")

    webhook = DiscordWebhook()

    # Successful backup
    await notify_backup(
        webhook,
        backup_type="PostgreSQL Full",
        status="Complete",
        size="2.3 GB",
        duration="5m 12s",
        destination="s3://ziggie-backups/postgres/2025-12-27/"
    )

    await asyncio.sleep(1)

    # Using template with more details
    template = BackupCompleteTemplate(
        backup_type="MongoDB Incremental",
        size=512 * 1024 * 1024,  # 512 MB in bytes
        duration=125.5,  # seconds
        destination="s3://ziggie-backups/mongodb/incremental/2025-12-27-1200/",
        files_count=1247,
        retention_days=30
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await webhook.close()
    print("Backup notifications sent!")


async def example_agent_status():
    """Example: Agent status notifications."""
    print("\n--- Agent Status Notifications ---")

    webhook = DiscordWebhook()

    # Agent completed task
    template = AgentStatusTemplate(
        agent_name="HEPHAESTUS",
        agent_tier="L1",
        status="Completed",
        task="Optimize 3D model LOD pipeline",
        duration=345.7,
        tokens_used=12500,
        output_summary="Successfully optimized 23 models. Average polygon reduction: 65%. All LOD levels generated and validated."
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await asyncio.sleep(1)

    # Agent error
    template = AgentStatusTemplate(
        agent_name="DAEDALUS",
        agent_tier="L1",
        status="Error",
        task="Configure CI/CD pipeline",
        duration=89.2,
        tokens_used=4200,
        output_summary="Failed to authenticate with GitHub Actions. Error: Invalid PAT token."
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await webhook.close()
    print("Agent notifications sent!")


async def example_batch_operation():
    """Example: Batch operation notifications."""
    print("\n--- Batch Operation Notifications ---")

    webhook = DiscordWebhook()

    # Successful batch
    template = BatchNotificationTemplate(
        operation="Asset Migration to S3",
        total_items=150,
        successful=148,
        failed=2,
        duration=892.5,
        details=[
            "148 assets uploaded successfully",
            "2 failures: invalid file format",
            "Total size: 1.2 GB"
        ]
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await asyncio.sleep(1)

    # Partial failure batch
    template = BatchNotificationTemplate(
        operation="E2E Test Suite",
        total_items=130,
        successful=95,
        failed=35,
        duration=456.8,
        details=[
            "95 tests passed",
            "35 tests failed (auth module)",
            "Coverage: 73%",
            "See logs for details"
        ]
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await webhook.close()
    print("Batch notifications sent!")


async def example_resource_alert():
    """Example: Resource usage alerts."""
    print("\n--- Resource Alert Notifications ---")

    webhook = DiscordWebhook()

    template = HighResourceUsageTemplate(
        resource_type="CPU",
        usage_percent=92.5,
        threshold_percent=80,
        host="ziggie-prod-01",
        details={
            "Process": "comfyui (PID 12345)",
            "Cores Used": "7/8",
            "Load Average": "7.2, 6.8, 5.9"
        }
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await asyncio.sleep(1)

    template = HighResourceUsageTemplate(
        resource_type="Memory",
        usage_percent=88.3,
        threshold_percent=85,
        host="ziggie-prod-01",
        details={
            "Used": "14.1 GB / 16 GB",
            "Available": "1.9 GB",
            "Top Process": "ollama (8.2 GB)"
        }
    )
    payload = template.to_dict()
    await webhook.send_message(embeds=[embed for embed in payload.get("embeds", [])])

    await webhook.close()
    print("Resource notifications sent!")


async def run_all_examples():
    """Run all example notifications."""
    print("=" * 60)
    print("Discord Notification Examples")
    print("=" * 60)
    print("\nThis will send example notifications to your Discord webhook.")
    print("Make sure DISCORD_WEBHOOK_URL is set in your environment.\n")

    try:
        await example_asset_generated()
        await asyncio.sleep(2)

        await example_deployment()
        await asyncio.sleep(2)

        await example_error()
        await asyncio.sleep(2)

        await example_cost_alert()
        await asyncio.sleep(2)

        await example_backup()
        await asyncio.sleep(2)

        await example_agent_status()
        await asyncio.sleep(2)

        await example_batch_operation()
        await asyncio.sleep(2)

        await example_resource_alert()

        print("\n" + "=" * 60)
        print("All example notifications sent successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure DISCORD_WEBHOOK_URL is set correctly.")


if __name__ == "__main__":
    asyncio.run(run_all_examples())

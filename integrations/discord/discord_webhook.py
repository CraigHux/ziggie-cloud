"""
Discord Webhook Integration Module for Ziggie Ecosystem

Sends notifications to Discord channels via webhooks.
Supports: Asset generation, deployments, errors, cost alerts, backups.

Webhook URL stored in AWS Secrets Manager: ziggie/discord-webhook-url
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import aiohttp
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification severity levels with corresponding Discord colors."""
    SUCCESS = 0x28A745  # Green
    ERROR = 0xDC3545    # Red
    WARNING = 0xFFC107  # Yellow
    INFO = 0x17A2B8     # Blue
    ASSET = 0x9B59B6    # Purple (for asset generation)
    DEPLOY = 0x3498DB   # Light Blue (for deployments)
    COST = 0xE67E22     # Orange (for cost alerts)
    BACKUP = 0x1ABC9C   # Teal (for backups)


@dataclass
class DiscordEmbed:
    """Discord embed structure."""
    title: str
    description: Optional[str] = None
    color: int = 0x7289DA  # Discord blurple default
    fields: Optional[List[Dict[str, Any]]] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    footer_text: Optional[str] = None
    timestamp: Optional[str] = None
    author_name: Optional[str] = None
    author_icon_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Discord API format."""
        embed = {
            "title": self.title,
            "color": self.color,
        }

        if self.description:
            embed["description"] = self.description

        if self.fields:
            embed["fields"] = self.fields

        if self.thumbnail_url:
            embed["thumbnail"] = {"url": self.thumbnail_url}

        if self.image_url:
            embed["image"] = {"url": self.image_url}

        if self.footer_text:
            embed["footer"] = {"text": self.footer_text}

        if self.timestamp:
            embed["timestamp"] = self.timestamp
        else:
            embed["timestamp"] = datetime.utcnow().isoformat()

        if self.author_name:
            author = {"name": self.author_name}
            if self.author_icon_url:
                author["icon_url"] = self.author_icon_url
            embed["author"] = author

        return embed


class DiscordWebhook:
    """
    Discord webhook client for sending notifications.

    Usage:
        webhook = DiscordWebhook()
        await webhook.send_notification(
            NotificationType.SUCCESS,
            title="Asset Generated",
            description="New unit sprite created",
            image_url="https://cdn.example.com/preview.png"
        )
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        use_secrets_manager: bool = True,
        secret_name: str = "ziggie/discord-webhook-url",
        region: str = "eu-north-1"
    ):
        """
        Initialize Discord webhook client.

        Args:
            webhook_url: Direct webhook URL (overrides Secrets Manager)
            use_secrets_manager: Whether to fetch URL from AWS Secrets Manager
            secret_name: Name of the secret in AWS Secrets Manager
            region: AWS region for Secrets Manager
        """
        self._webhook_url = webhook_url
        self._use_secrets_manager = use_secrets_manager
        self._secret_name = secret_name
        self._region = region
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_webhook_url_from_secrets(self) -> str:
        """Fetch webhook URL from AWS Secrets Manager."""
        try:
            client = boto3.client(
                "secretsmanager",
                region_name=self._region
            )
            response = client.get_secret_value(SecretId=self._secret_name)

            # Handle both string and JSON secret formats
            secret = response.get("SecretString", "")
            try:
                secret_dict = json.loads(secret)
                return secret_dict.get("webhook_url", secret_dict.get("url", secret))
            except json.JSONDecodeError:
                return secret

        except ClientError as e:
            logger.error(f"Failed to fetch webhook URL from Secrets Manager: {e}")
            raise

    def _get_webhook_url(self) -> str:
        """Get webhook URL from configured source."""
        if self._webhook_url:
            return self._webhook_url

        # Try environment variable
        env_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if env_url:
            return env_url

        # Try AWS Secrets Manager
        if self._use_secrets_manager:
            return self._get_webhook_url_from_secrets()

        raise ValueError(
            "No webhook URL configured. Set DISCORD_WEBHOOK_URL env var, "
            "pass webhook_url parameter, or enable use_secrets_manager."
        )

    async def send_message(
        self,
        content: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
        username: Optional[str] = "Ziggie Bot",
        avatar_url: Optional[str] = None
    ) -> bool:
        """
        Send a message to Discord.

        Args:
            content: Plain text message content
            embeds: List of DiscordEmbed objects
            username: Override bot username
            avatar_url: Override bot avatar

        Returns:
            True if message sent successfully
        """
        webhook_url = self._get_webhook_url()
        session = await self._get_session()

        payload = {}

        if content:
            payload["content"] = content

        if embeds:
            payload["embeds"] = [e.to_dict() for e in embeds]

        if username:
            payload["username"] = username

        if avatar_url:
            payload["avatar_url"] = avatar_url

        try:
            async with session.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 204:
                    logger.info("Discord notification sent successfully")
                    return True
                elif response.status == 429:
                    # Rate limited
                    retry_after = response.headers.get("Retry-After", "1")
                    logger.warning(f"Rate limited. Retry after {retry_after}s")
                    await asyncio.sleep(float(retry_after))
                    return await self.send_message(content, embeds, username, avatar_url)
                else:
                    text = await response.text()
                    logger.error(f"Discord API error {response.status}: {text}")
                    return False

        except aiohttp.ClientError as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False

    async def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        description: Optional[str] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        footer: Optional[str] = None
    ) -> bool:
        """
        Send a formatted notification to Discord.

        Args:
            notification_type: Type/severity of notification
            title: Embed title
            description: Embed description
            fields: List of field dicts with name, value, inline keys
            image_url: Main image URL (for asset previews)
            thumbnail_url: Thumbnail image URL
            footer: Footer text

        Returns:
            True if notification sent successfully
        """
        embed = DiscordEmbed(
            title=title,
            description=description,
            color=notification_type.value,
            fields=fields,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            footer_text=footer or f"Ziggie Ecosystem | {notification_type.name}",
            author_name="Ziggie",
            author_icon_url="https://i.imgur.com/placeholder.png"  # Replace with actual icon
        )

        return await self.send_message(embeds=[embed])


# Convenience functions for common notification types

async def notify_asset_generated(
    webhook: DiscordWebhook,
    asset_name: str,
    asset_type: str,
    quality_rating: str,
    preview_url: Optional[str] = None,
    details: Optional[Dict[str, str]] = None
) -> bool:
    """Send notification for generated asset."""
    fields = [
        {"name": "Asset Name", "value": asset_name, "inline": True},
        {"name": "Type", "value": asset_type, "inline": True},
        {"name": "Quality", "value": quality_rating, "inline": True},
    ]

    if details:
        for key, value in details.items():
            fields.append({"name": key, "value": str(value), "inline": True})

    return await webhook.send_notification(
        NotificationType.ASSET,
        title="Asset Generated",
        description=f"New {asset_type} asset created: **{asset_name}**",
        fields=fields,
        image_url=preview_url,
        footer="Asset Pipeline | Ziggie"
    )


async def notify_deployment(
    webhook: DiscordWebhook,
    environment: str,
    version: str,
    status: str,
    services: Optional[List[str]] = None,
    duration: Optional[str] = None
) -> bool:
    """Send notification for deployment completion."""
    success = status.lower() in ["success", "complete", "deployed"]
    notification_type = NotificationType.DEPLOY if success else NotificationType.ERROR

    fields = [
        {"name": "Environment", "value": environment, "inline": True},
        {"name": "Version", "value": version, "inline": True},
        {"name": "Status", "value": status, "inline": True},
    ]

    if duration:
        fields.append({"name": "Duration", "value": duration, "inline": True})

    if services:
        fields.append({
            "name": "Services",
            "value": "\n".join(f"- {s}" for s in services),
            "inline": False
        })

    return await webhook.send_notification(
        notification_type,
        title=f"Deployment {'Complete' if success else 'Failed'}",
        description=f"Deployment to **{environment}** {status.lower()}",
        fields=fields,
        footer="DevOps | Ziggie"
    )


async def notify_error(
    webhook: DiscordWebhook,
    error_type: str,
    error_message: str,
    source: str,
    severity: str = "ERROR",
    trace: Optional[str] = None
) -> bool:
    """Send notification for error alert."""
    fields = [
        {"name": "Error Type", "value": error_type, "inline": True},
        {"name": "Source", "value": source, "inline": True},
        {"name": "Severity", "value": severity, "inline": True},
        {"name": "Message", "value": error_message[:1024], "inline": False},
    ]

    if trace:
        # Truncate trace to fit Discord limits
        truncated_trace = trace[:1000] + "..." if len(trace) > 1000 else trace
        fields.append({
            "name": "Stack Trace",
            "value": f"```\n{truncated_trace}\n```",
            "inline": False
        })

    return await webhook.send_notification(
        NotificationType.ERROR,
        title=f"Error Alert: {error_type}",
        description=f"An error occurred in **{source}**",
        fields=fields,
        footer=f"Error Monitoring | Severity: {severity}"
    )


async def notify_cost_alert(
    webhook: DiscordWebhook,
    service: str,
    current_cost: float,
    budget_limit: float,
    threshold_percent: int,
    period: str = "monthly"
) -> bool:
    """Send notification for cost alert."""
    percent_used = (current_cost / budget_limit) * 100

    # Determine severity
    if percent_used >= 100:
        notification_type = NotificationType.ERROR
        status = "EXCEEDED"
    elif percent_used >= 80:
        notification_type = NotificationType.WARNING
        status = "WARNING"
    else:
        notification_type = NotificationType.COST
        status = "ALERT"

    fields = [
        {"name": "Service", "value": service, "inline": True},
        {"name": "Period", "value": period.capitalize(), "inline": True},
        {"name": "Threshold", "value": f"{threshold_percent}%", "inline": True},
        {"name": "Current Cost", "value": f"${current_cost:.2f}", "inline": True},
        {"name": "Budget Limit", "value": f"${budget_limit:.2f}", "inline": True},
        {"name": "Usage", "value": f"{percent_used:.1f}%", "inline": True},
    ]

    return await webhook.send_notification(
        notification_type,
        title=f"Cost Alert: {status}",
        description=f"**{service}** has reached {percent_used:.1f}% of {period} budget",
        fields=fields,
        footer="Cost Management | Ziggie"
    )


async def notify_backup(
    webhook: DiscordWebhook,
    backup_type: str,
    status: str,
    size: Optional[str] = None,
    duration: Optional[str] = None,
    destination: Optional[str] = None
) -> bool:
    """Send notification for backup completion."""
    success = status.lower() in ["success", "complete", "completed"]
    notification_type = NotificationType.BACKUP if success else NotificationType.ERROR

    fields = [
        {"name": "Backup Type", "value": backup_type, "inline": True},
        {"name": "Status", "value": status, "inline": True},
    ]

    if size:
        fields.append({"name": "Size", "value": size, "inline": True})

    if duration:
        fields.append({"name": "Duration", "value": duration, "inline": True})

    if destination:
        fields.append({"name": "Destination", "value": destination, "inline": False})

    return await webhook.send_notification(
        notification_type,
        title=f"Backup {'Complete' if success else 'Failed'}",
        description=f"**{backup_type}** backup {status.lower()}",
        fields=fields,
        footer="Backup System | Ziggie"
    )


# Synchronous wrapper for non-async contexts
def send_notification_sync(
    notification_type: NotificationType,
    title: str,
    description: Optional[str] = None,
    **kwargs
) -> bool:
    """Synchronous wrapper for send_notification."""
    async def _send():
        webhook = DiscordWebhook()
        try:
            return await webhook.send_notification(
                notification_type, title, description, **kwargs
            )
        finally:
            await webhook.close()

    return asyncio.run(_send())


if __name__ == "__main__":
    # Example usage
    async def main():
        webhook = DiscordWebhook()

        try:
            # Test asset notification
            await notify_asset_generated(
                webhook,
                asset_name="cat_archer_blue",
                asset_type="Unit Sprite",
                quality_rating="AAA",
                preview_url="https://example.com/preview.png",
                details={"Faction": "Blue", "Animation": "8 directions"}
            )

            # Test deployment notification
            await notify_deployment(
                webhook,
                environment="production",
                version="v1.2.3",
                status="Success",
                services=["ziggie-api", "mcp-gateway", "nginx"],
                duration="2m 34s"
            )

            # Test error notification
            await notify_error(
                webhook,
                error_type="ConnectionError",
                error_message="Failed to connect to database",
                source="ziggie-api",
                severity="CRITICAL",
                trace="Traceback (most recent call last):\n  File 'app.py', line 42..."
            )

            # Test cost alert
            await notify_cost_alert(
                webhook,
                service="AWS S3",
                current_cost=45.50,
                budget_limit=50.00,
                threshold_percent=80,
                period="monthly"
            )

            # Test backup notification
            await notify_backup(
                webhook,
                backup_type="PostgreSQL Full",
                status="Complete",
                size="2.3 GB",
                duration="5m 12s",
                destination="s3://ziggie-backups/postgres/2025-12-27/"
            )

        finally:
            await webhook.close()

    asyncio.run(main())

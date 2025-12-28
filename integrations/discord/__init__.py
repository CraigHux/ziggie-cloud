"""
Ziggie Discord Integration Module

Provides Discord webhook notifications for the Ziggie ecosystem.
Supports: Asset generation, deployments, errors, cost alerts, backups, agent status.

Usage:
    from integrations.discord import DiscordWebhook, NotificationType
    from integrations.discord import notify_asset_generated, notify_deployment

    # Async usage
    webhook = DiscordWebhook()
    await webhook.send_notification(
        NotificationType.SUCCESS,
        title="Task Complete",
        description="Operation finished successfully"
    )

    # Convenience functions
    await notify_asset_generated(webhook, "cat_archer", "Unit Sprite", "AAA")
    await notify_deployment(webhook, "production", "v1.0.0", "Success")

    # Sync wrapper
    from integrations.discord import send_notification_sync
    send_notification_sync(NotificationType.INFO, "Test", "This is a test")
"""

from .discord_webhook import (
    DiscordWebhook,
    DiscordEmbed,
    NotificationType,
    notify_asset_generated,
    notify_deployment,
    notify_error,
    notify_cost_alert,
    notify_backup,
    send_notification_sync
)

from .formatters import (
    NotificationFormatter,
    AssetNotificationFormatter,
    DeploymentNotificationFormatter,
    ErrorNotificationFormatter,
    CostNotificationFormatter,
    BackupNotificationFormatter,
    AgentNotificationFormatter,
    EmojiSet
)

from .templates import (
    # Success templates
    SuccessTemplate,
    AssetGeneratedTemplate,
    DeploymentSuccessTemplate,
    BackupCompleteTemplate,
    # Error templates
    ErrorTemplate,
    CriticalErrorTemplate,
    ServiceDownTemplate,
    DeploymentFailedTemplate,
    # Warning templates
    WarningTemplate,
    CostAlertTemplate,
    HighResourceUsageTemplate,
    # Info templates
    InfoTemplate,
    AgentStatusTemplate,
    ScheduledTaskTemplate,
    # Batch templates
    BatchNotificationTemplate
)

__all__ = [
    # Core webhook
    "DiscordWebhook",
    "DiscordEmbed",
    "NotificationType",
    # Convenience functions
    "notify_asset_generated",
    "notify_deployment",
    "notify_error",
    "notify_cost_alert",
    "notify_backup",
    "send_notification_sync",
    # Formatters
    "NotificationFormatter",
    "AssetNotificationFormatter",
    "DeploymentNotificationFormatter",
    "ErrorNotificationFormatter",
    "CostNotificationFormatter",
    "BackupNotificationFormatter",
    "AgentNotificationFormatter",
    "EmojiSet",
    # Templates
    "SuccessTemplate",
    "AssetGeneratedTemplate",
    "DeploymentSuccessTemplate",
    "BackupCompleteTemplate",
    "ErrorTemplate",
    "CriticalErrorTemplate",
    "ServiceDownTemplate",
    "DeploymentFailedTemplate",
    "WarningTemplate",
    "CostAlertTemplate",
    "HighResourceUsageTemplate",
    "InfoTemplate",
    "AgentStatusTemplate",
    "ScheduledTaskTemplate",
    "BatchNotificationTemplate"
]

__version__ = "1.0.0"

"""
Discord Notification Templates for Ziggie Ecosystem

Pre-built templates for common notification scenarios.
Each template provides consistent formatting and messaging.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

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


class NotificationTemplate:
    """Base class for notification templates."""

    def __init__(self):
        self.formatter = NotificationFormatter()

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to Discord API format."""
        raise NotImplementedError


# =============================================================================
# SUCCESS TEMPLATES
# =============================================================================

class SuccessTemplate(NotificationTemplate):
    """Generic success notification template."""

    def __init__(
        self,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[str] = None
    ):
        super().__init__()
        self.title = f"{EmojiSet.SUCCESS} {title}"
        self.description = description
        self.fields = fields or []
        self.footer = footer or "Ziggie Ecosystem"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embeds": [{
                "title": self.title,
                "description": self.description,
                "color": 0x28A745,  # Green
                "fields": self.fields,
                "footer": {"text": self.footer},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class AssetGeneratedTemplate(NotificationTemplate):
    """Template for asset generation success."""

    def __init__(
        self,
        asset_name: str,
        asset_type: str,
        quality: str,
        preview_url: Optional[str] = None,
        faction: Optional[str] = None,
        dimensions: Optional[str] = None,
        generation_time: Optional[float] = None,
        model_used: Optional[str] = None
    ):
        super().__init__()
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.quality = quality
        self.preview_url = preview_url
        self.faction = faction
        self.dimensions = dimensions
        self.generation_time = generation_time
        self.model_used = model_used

    def to_dict(self) -> Dict[str, Any]:
        formatter = AssetNotificationFormatter()

        embed = {
            "title": formatter.format_title(self.asset_name),
            "description": f"New **{self.asset_type}** asset created successfully",
            "color": 0x9B59B6,  # Purple
            "fields": formatter.format_fields(
                self.asset_name,
                self.asset_type,
                self.quality,
                faction=self.faction,
                dimensions=self.dimensions,
                generation_time=self.generation_time,
                model_used=self.model_used
            ),
            "footer": {"text": "Asset Pipeline | Ziggie"},
            "timestamp": datetime.utcnow().isoformat()
        }

        if self.preview_url:
            embed["image"] = {"url": self.preview_url}

        return {"embeds": [embed]}


class DeploymentSuccessTemplate(NotificationTemplate):
    """Template for successful deployment."""

    def __init__(
        self,
        environment: str,
        version: str,
        services: List[str],
        duration: Optional[float] = None,
        commit_sha: Optional[str] = None,
        deployed_by: Optional[str] = None
    ):
        super().__init__()
        self.environment = environment
        self.version = version
        self.services = services
        self.duration = duration
        self.commit_sha = commit_sha
        self.deployed_by = deployed_by

    def to_dict(self) -> Dict[str, Any]:
        formatter = DeploymentNotificationFormatter()

        return {
            "embeds": [{
                "title": formatter.format_title(self.environment, "Success"),
                "description": f"Successfully deployed to **{self.environment.upper()}**",
                "color": 0x3498DB,  # Light blue
                "fields": formatter.format_fields(
                    self.environment,
                    self.version,
                    "Success",
                    services=self.services,
                    duration=self.duration,
                    commit_sha=self.commit_sha,
                    deployed_by=self.deployed_by
                ),
                "footer": {"text": "DevOps | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class BackupCompleteTemplate(NotificationTemplate):
    """Template for successful backup."""

    def __init__(
        self,
        backup_type: str,
        size: int,
        duration: float,
        destination: str,
        files_count: Optional[int] = None,
        retention_days: int = 30
    ):
        super().__init__()
        self.backup_type = backup_type
        self.size = size
        self.duration = duration
        self.destination = destination
        self.files_count = files_count
        self.retention_days = retention_days

    def to_dict(self) -> Dict[str, Any]:
        formatter = BackupNotificationFormatter()

        return {
            "embeds": [{
                "title": formatter.format_title(self.backup_type, "Complete"),
                "description": f"**{self.backup_type.capitalize()}** backup completed successfully",
                "color": 0x1ABC9C,  # Teal
                "fields": formatter.format_fields(
                    self.backup_type,
                    "Complete",
                    size=self.size,
                    duration=self.duration,
                    destination=self.destination,
                    files_count=self.files_count,
                    retention_days=self.retention_days
                ),
                "footer": {"text": "Backup System | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


# =============================================================================
# ERROR TEMPLATES
# =============================================================================

class ErrorTemplate(NotificationTemplate):
    """Generic error notification template."""

    def __init__(
        self,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[str] = None
    ):
        super().__init__()
        self.title = f"{EmojiSet.ERROR} {title}"
        self.description = description
        self.fields = fields or []
        self.footer = footer or "Error Monitoring | Ziggie"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embeds": [{
                "title": self.title,
                "description": self.description,
                "color": 0xDC3545,  # Red
                "fields": self.fields,
                "footer": {"text": self.footer},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class CriticalErrorTemplate(NotificationTemplate):
    """Template for critical errors requiring immediate attention."""

    def __init__(
        self,
        error_type: str,
        error_message: str,
        source: str,
        trace: Optional[str] = None,
        context: Optional[Dict[str, str]] = None
    ):
        super().__init__()
        self.error_type = error_type
        self.error_message = error_message
        self.source = source
        self.trace = trace
        self.context = context

    def to_dict(self) -> Dict[str, Any]:
        formatter = ErrorNotificationFormatter()

        return {
            "content": "@here **CRITICAL ERROR** - Immediate attention required!",
            "embeds": [{
                "title": formatter.format_title(self.error_type, "critical"),
                "description": f":rotating_light: Critical error detected in **{self.source}**",
                "color": 0xFF0000,  # Bright red
                "fields": formatter.format_fields(
                    self.error_type,
                    self.error_message,
                    self.source,
                    severity="CRITICAL",
                    trace=self.trace,
                    context=self.context
                ),
                "footer": {"text": "Critical Alert | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class ServiceDownTemplate(NotificationTemplate):
    """Template for service downtime alerts."""

    def __init__(
        self,
        service_name: str,
        last_seen: datetime,
        health_check_url: Optional[str] = None,
        expected_response: Optional[str] = None
    ):
        super().__init__()
        self.service_name = service_name
        self.last_seen = last_seen
        self.health_check_url = health_check_url
        self.expected_response = expected_response

    def to_dict(self) -> Dict[str, Any]:
        downtime = datetime.utcnow() - self.last_seen
        downtime_str = NotificationFormatter.format_duration(downtime.total_seconds())

        fields = [
            {"name": "Service", "value": self.service_name, "inline": True},
            {"name": "Status", "value": ":red_circle: DOWN", "inline": True},
            {"name": "Downtime", "value": downtime_str, "inline": True},
            {
                "name": "Last Seen",
                "value": NotificationFormatter.format_timestamp(self.last_seen),
                "inline": False
            }
        ]

        if self.health_check_url:
            fields.append({
                "name": "Health Check",
                "value": f"`{self.health_check_url}`",
                "inline": False
            })

        return {
            "content": f"@here **SERVICE DOWN**: {self.service_name}",
            "embeds": [{
                "title": f":rotating_light: Service Down: {self.service_name}",
                "description": f"**{self.service_name}** is not responding",
                "color": 0xFF0000,
                "fields": fields,
                "footer": {"text": "Health Monitoring | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class DeploymentFailedTemplate(NotificationTemplate):
    """Template for failed deployment."""

    def __init__(
        self,
        environment: str,
        version: str,
        error_message: str,
        failed_step: Optional[str] = None,
        logs_url: Optional[str] = None
    ):
        super().__init__()
        self.environment = environment
        self.version = version
        self.error_message = error_message
        self.failed_step = failed_step
        self.logs_url = logs_url

    def to_dict(self) -> Dict[str, Any]:
        fields = [
            {"name": "Environment", "value": self.environment.upper(), "inline": True},
            {"name": "Version", "value": f"`{self.version}`", "inline": True},
            {"name": "Status", "value": ":x: FAILED", "inline": True},
            {"name": "Error", "value": self.error_message[:1024], "inline": False}
        ]

        if self.failed_step:
            fields.append({
                "name": "Failed Step",
                "value": self.failed_step,
                "inline": True
            })

        if self.logs_url:
            fields.append({
                "name": "Logs",
                "value": f"[View Logs]({self.logs_url})",
                "inline": True
            })

        return {
            "content": f"@here **DEPLOYMENT FAILED** to {self.environment.upper()}",
            "embeds": [{
                "title": f":x: Deployment Failed: {self.environment.upper()}",
                "description": f"Deployment of **{self.version}** to **{self.environment}** failed",
                "color": 0xDC3545,
                "fields": fields,
                "footer": {"text": "DevOps | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


# =============================================================================
# WARNING TEMPLATES
# =============================================================================

class WarningTemplate(NotificationTemplate):
    """Generic warning notification template."""

    def __init__(
        self,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[str] = None
    ):
        super().__init__()
        self.title = f"{EmojiSet.WARNING} {title}"
        self.description = description
        self.fields = fields or []
        self.footer = footer or "Ziggie Ecosystem"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embeds": [{
                "title": self.title,
                "description": self.description,
                "color": 0xFFC107,  # Yellow
                "fields": self.fields,
                "footer": {"text": self.footer},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class CostAlertTemplate(NotificationTemplate):
    """Template for cost threshold alerts."""

    def __init__(
        self,
        service: str,
        current_cost: float,
        budget_limit: float,
        period: str = "monthly",
        forecast: Optional[float] = None,
        breakdown: Optional[Dict[str, float]] = None
    ):
        super().__init__()
        self.service = service
        self.current_cost = current_cost
        self.budget_limit = budget_limit
        self.period = period
        self.forecast = forecast
        self.breakdown = breakdown

    def to_dict(self) -> Dict[str, Any]:
        formatter = CostNotificationFormatter()
        percentage = (self.current_cost / self.budget_limit) * 100
        level = formatter.get_threshold_level(percentage)

        # Determine color based on level
        colors = {
            "low": 0x17A2B8,
            "medium": 0xE67E22,
            "high": 0xFFC107,
            "exceeded": 0xDC3545
        }

        # Add @here mention for exceeded budgets
        content = None
        if level == "exceeded":
            content = f"@here **BUDGET EXCEEDED**: {self.service}"

        return {
            "content": content,
            "embeds": [{
                "title": formatter.format_title(self.service, percentage),
                "description": f"**{self.service}** has reached **{percentage:.1f}%** of {self.period} budget",
                "color": colors.get(level, 0xE67E22),
                "fields": formatter.format_fields(
                    self.service,
                    self.current_cost,
                    self.budget_limit,
                    period=self.period,
                    forecast=self.forecast,
                    breakdown=self.breakdown
                ),
                "footer": {"text": "Cost Management | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class HighResourceUsageTemplate(NotificationTemplate):
    """Template for high resource usage alerts."""

    def __init__(
        self,
        resource_type: str,
        usage_percent: float,
        threshold_percent: float,
        host: str,
        details: Optional[Dict[str, str]] = None
    ):
        super().__init__()
        self.resource_type = resource_type
        self.usage_percent = usage_percent
        self.threshold_percent = threshold_percent
        self.host = host
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        formatter = NotificationFormatter()

        fields = [
            {"name": "Resource", "value": self.resource_type.upper(), "inline": True},
            {"name": "Host", "value": self.host, "inline": True},
            {"name": "Threshold", "value": f"{self.threshold_percent}%", "inline": True},
            {
                "name": "Current Usage",
                "value": CostNotificationFormatter.format_progress_bar(self.usage_percent),
                "inline": False
            }
        ]

        for key, value in self.details.items():
            fields.append({"name": key, "value": value, "inline": True})

        return {
            "embeds": [{
                "title": f":warning: High {self.resource_type.upper()} Usage: {self.host}",
                "description": f"**{self.resource_type}** usage on **{self.host}** has exceeded {self.threshold_percent}%",
                "color": 0xFFC107,
                "fields": fields,
                "footer": {"text": "Resource Monitoring | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


# =============================================================================
# INFO TEMPLATES
# =============================================================================

class InfoTemplate(NotificationTemplate):
    """Generic info notification template."""

    def __init__(
        self,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[str] = None
    ):
        super().__init__()
        self.title = f"{EmojiSet.INFO} {title}"
        self.description = description
        self.fields = fields or []
        self.footer = footer or "Ziggie Ecosystem"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embeds": [{
                "title": self.title,
                "description": self.description,
                "color": 0x17A2B8,  # Blue
                "fields": self.fields,
                "footer": {"text": self.footer},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class AgentStatusTemplate(NotificationTemplate):
    """Template for agent status updates."""

    def __init__(
        self,
        agent_name: str,
        agent_tier: str,
        status: str,
        task: Optional[str] = None,
        duration: Optional[float] = None,
        tokens_used: Optional[int] = None,
        output_summary: Optional[str] = None
    ):
        super().__init__()
        self.agent_name = agent_name
        self.agent_tier = agent_tier
        self.status = status
        self.task = task
        self.duration = duration
        self.tokens_used = tokens_used
        self.output_summary = output_summary

    def to_dict(self) -> Dict[str, Any]:
        formatter = AgentNotificationFormatter()

        # Determine color based on status
        status_colors = {
            "active": 0x28A745,
            "idle": 0xFFC107,
            "completed": 0x3498DB,
            "error": 0xDC3545,
            "timeout": 0xE67E22
        }

        return {
            "embeds": [{
                "title": formatter.format_title(self.agent_name, self.status.capitalize()),
                "description": f"Agent **{self.agent_name}** status update",
                "color": status_colors.get(self.status.lower(), 0x17A2B8),
                "fields": formatter.format_fields(
                    self.agent_name,
                    self.agent_tier,
                    self.status,
                    task=self.task,
                    duration=self.duration,
                    tokens_used=self.tokens_used,
                    output_summary=self.output_summary
                ),
                "footer": {"text": "Agent Orchestration | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


class ScheduledTaskTemplate(NotificationTemplate):
    """Template for scheduled task notifications."""

    def __init__(
        self,
        task_name: str,
        action: str,  # "started", "completed", "scheduled"
        next_run: Optional[datetime] = None,
        duration: Optional[float] = None,
        result: Optional[str] = None
    ):
        super().__init__()
        self.task_name = task_name
        self.action = action
        self.next_run = next_run
        self.duration = duration
        self.result = result

    def to_dict(self) -> Dict[str, Any]:
        action_emojis = {
            "started": ":arrow_forward:",
            "completed": EmojiSet.SUCCESS,
            "scheduled": EmojiSet.CLOCK,
            "cancelled": EmojiSet.CROSSMARK
        }

        fields = [
            {"name": "Task", "value": self.task_name, "inline": True},
            {"name": "Action", "value": self.action.capitalize(), "inline": True},
        ]

        if self.duration:
            fields.append({
                "name": "Duration",
                "value": NotificationFormatter.format_duration(self.duration),
                "inline": True
            })

        if self.next_run:
            fields.append({
                "name": "Next Run",
                "value": NotificationFormatter.format_timestamp(self.next_run),
                "inline": False
            })

        if self.result:
            fields.append({
                "name": "Result",
                "value": self.result,
                "inline": False
            })

        emoji = action_emojis.get(self.action, EmojiSet.INFO)

        return {
            "embeds": [{
                "title": f"{emoji} Scheduled Task: {self.task_name}",
                "description": f"Task **{self.task_name}** {self.action}",
                "color": 0x17A2B8,
                "fields": fields,
                "footer": {"text": "Task Scheduler | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }


# =============================================================================
# BATCH NOTIFICATION TEMPLATE
# =============================================================================

class BatchNotificationTemplate(NotificationTemplate):
    """Template for batch operation summaries."""

    def __init__(
        self,
        operation: str,
        total_items: int,
        successful: int,
        failed: int,
        duration: float,
        details: Optional[List[str]] = None
    ):
        super().__init__()
        self.operation = operation
        self.total_items = total_items
        self.successful = successful
        self.failed = failed
        self.duration = duration
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        success_rate = (self.successful / self.total_items * 100) if self.total_items > 0 else 0

        # Determine color based on success rate
        if success_rate == 100:
            color = 0x28A745  # Green
            emoji = EmojiSet.SUCCESS
        elif success_rate >= 80:
            color = 0xFFC107  # Yellow
            emoji = EmojiSet.WARNING
        else:
            color = 0xDC3545  # Red
            emoji = EmojiSet.ERROR

        fields = [
            {"name": "Total Items", "value": str(self.total_items), "inline": True},
            {"name": "Successful", "value": f":white_check_mark: {self.successful}", "inline": True},
            {"name": "Failed", "value": f":x: {self.failed}", "inline": True},
            {
                "name": "Success Rate",
                "value": CostNotificationFormatter.format_progress_bar(success_rate),
                "inline": False
            },
            {
                "name": "Duration",
                "value": NotificationFormatter.format_duration(self.duration),
                "inline": True
            }
        ]

        if self.details:
            details_str = "\n".join(f"- {d}" for d in self.details[:10])
            if len(self.details) > 10:
                details_str += f"\n... and {len(self.details) - 10} more"
            fields.append({
                "name": "Details",
                "value": details_str,
                "inline": False
            })

        return {
            "embeds": [{
                "title": f"{emoji} Batch Operation: {self.operation}",
                "description": f"**{self.operation}** batch processing complete",
                "color": color,
                "fields": fields,
                "footer": {"text": "Batch Processing | Ziggie"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

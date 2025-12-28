"""
Discord Notification Formatters for Ziggie Ecosystem

Provides structured formatting for different notification types.
Ensures consistent, professional Discord messages across the ecosystem.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class EmojiSet:
    """Standard emojis for notification types."""
    SUCCESS = ":white_check_mark:"
    ERROR = ":x:"
    WARNING = ":warning:"
    INFO = ":information_source:"
    ASSET = ":art:"
    DEPLOY = ":rocket:"
    COST = ":moneybag:"
    BACKUP = ":floppy_disk:"
    GPU = ":video_game:"
    AGENT = ":robot:"
    BUILD = ":hammer:"
    TEST = ":test_tube:"
    SECURITY = ":shield:"
    DATABASE = ":file_cabinet:"
    NETWORK = ":globe_with_meridians:"
    CLOCK = ":clock:"
    CHART = ":chart_with_upwards_trend:"
    FIRE = ":fire:"
    STAR = ":star:"
    CHECKMARK = ":heavy_check_mark:"
    CROSSMARK = ":heavy_multiplication_x:"


class NotificationFormatter:
    """
    Base formatter for Discord notifications.

    Formats messages with consistent structure and styling.
    """

    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None) -> str:
        """Format datetime for Discord display."""
        if dt is None:
            dt = datetime.utcnow()
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{int(minutes)}m {int(secs)}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"

    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"

    @staticmethod
    def format_cost(amount: float, currency: str = "USD") -> str:
        """Format currency amount."""
        symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
        symbol = symbols.get(currency, currency + " ")
        return f"{symbol}{amount:.2f}"

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage value."""
        return f"{value:.{decimals}f}%"

    @staticmethod
    def format_list(items: List[str], bullet: str = "-") -> str:
        """Format list items with bullets."""
        return "\n".join(f"{bullet} {item}" for item in items)

    @staticmethod
    def format_code_block(text: str, language: str = "") -> str:
        """Format text as code block."""
        return f"```{language}\n{text}\n```"

    @staticmethod
    def truncate(text: str, max_length: int = 1024, suffix: str = "...") -> str:
        """Truncate text to max length with suffix."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class AssetNotificationFormatter(NotificationFormatter):
    """Formatter for asset generation notifications."""

    QUALITY_EMOJIS = {
        "AAA": ":star: :star: :star:",
        "AA": ":star: :star:",
        "A": ":star:",
        "Poor": ":x:"
    }

    ASSET_TYPE_EMOJIS = {
        "unit": ":crossed_swords:",
        "building": ":house:",
        "hero": ":crown:",
        "terrain": ":mountain:",
        "prop": ":package:",
        "effect": ":sparkles:",
        "sprite": ":framed_picture:",
        "texture": ":art:",
        "model": ":statue_of_liberty:"
    }

    @classmethod
    def format_title(cls, asset_name: str, status: str = "generated") -> str:
        """Format asset notification title."""
        return f"{EmojiSet.ASSET} Asset {status.capitalize()}: {asset_name}"

    @classmethod
    def format_quality(cls, rating: str) -> str:
        """Format quality rating with stars."""
        emoji = cls.QUALITY_EMOJIS.get(rating, "")
        return f"{rating} {emoji}"

    @classmethod
    def format_asset_type(cls, asset_type: str) -> str:
        """Format asset type with emoji."""
        emoji = cls.ASSET_TYPE_EMOJIS.get(asset_type.lower(), ":file_folder:")
        return f"{emoji} {asset_type}"

    @classmethod
    def format_fields(
        cls,
        asset_name: str,
        asset_type: str,
        quality: str,
        faction: Optional[str] = None,
        biome: Optional[str] = None,
        dimensions: Optional[str] = None,
        generation_time: Optional[float] = None,
        model_used: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Format standard asset fields."""
        fields = [
            {"name": "Asset Name", "value": asset_name, "inline": True},
            {"name": "Type", "value": cls.format_asset_type(asset_type), "inline": True},
            {"name": "Quality", "value": cls.format_quality(quality), "inline": True},
        ]

        if faction:
            fields.append({"name": "Faction", "value": faction, "inline": True})

        if biome:
            fields.append({"name": "Biome", "value": biome, "inline": True})

        if dimensions:
            fields.append({"name": "Dimensions", "value": dimensions, "inline": True})

        if generation_time:
            fields.append({
                "name": "Generation Time",
                "value": cls.format_duration(generation_time),
                "inline": True
            })

        if model_used:
            fields.append({"name": "Model", "value": model_used, "inline": True})

        return fields


class DeploymentNotificationFormatter(NotificationFormatter):
    """Formatter for deployment notifications."""

    STATUS_EMOJIS = {
        "success": EmojiSet.SUCCESS,
        "complete": EmojiSet.SUCCESS,
        "deployed": EmojiSet.SUCCESS,
        "failed": EmojiSet.ERROR,
        "error": EmojiSet.ERROR,
        "pending": EmojiSet.CLOCK,
        "in_progress": ":hourglass:",
        "rollback": ":rewind:"
    }

    ENVIRONMENT_EMOJIS = {
        "production": ":rocket:",
        "staging": ":hammer_and_wrench:",
        "development": ":computer:",
        "test": ":test_tube:"
    }

    @classmethod
    def format_title(cls, environment: str, status: str) -> str:
        """Format deployment notification title."""
        status_emoji = cls.STATUS_EMOJIS.get(status.lower(), EmojiSet.INFO)
        env_emoji = cls.ENVIRONMENT_EMOJIS.get(environment.lower(), ":cloud:")
        return f"{env_emoji} Deployment {status.capitalize()} {status_emoji}"

    @classmethod
    def format_service_list(cls, services: List[str], status: str = "deployed") -> str:
        """Format list of deployed services."""
        emoji = EmojiSet.CHECKMARK if status.lower() in ["success", "deployed"] else EmojiSet.CROSSMARK
        return "\n".join(f"{emoji} {service}" for service in services)

    @classmethod
    def format_fields(
        cls,
        environment: str,
        version: str,
        status: str,
        services: Optional[List[str]] = None,
        duration: Optional[float] = None,
        commit_sha: Optional[str] = None,
        deployed_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Format standard deployment fields."""
        fields = [
            {"name": "Environment", "value": environment.capitalize(), "inline": True},
            {"name": "Version", "value": f"`{version}`", "inline": True},
            {"name": "Status", "value": status.capitalize(), "inline": True},
        ]

        if duration:
            fields.append({
                "name": "Duration",
                "value": cls.format_duration(duration),
                "inline": True
            })

        if commit_sha:
            fields.append({
                "name": "Commit",
                "value": f"`{commit_sha[:7]}`",
                "inline": True
            })

        if deployed_by:
            fields.append({"name": "Deployed By", "value": deployed_by, "inline": True})

        if services:
            fields.append({
                "name": "Services",
                "value": cls.format_service_list(services, status),
                "inline": False
            })

        return fields


class ErrorNotificationFormatter(NotificationFormatter):
    """Formatter for error notifications."""

    SEVERITY_EMOJIS = {
        "critical": ":rotating_light:",
        "error": EmojiSet.ERROR,
        "warning": EmojiSet.WARNING,
        "info": EmojiSet.INFO,
        "debug": ":mag:"
    }

    SEVERITY_COLORS = {
        "critical": 0xFF0000,  # Bright red
        "error": 0xDC3545,     # Red
        "warning": 0xFFC107,   # Yellow
        "info": 0x17A2B8,      # Blue
        "debug": 0x6C757D      # Gray
    }

    @classmethod
    def format_title(cls, error_type: str, severity: str = "error") -> str:
        """Format error notification title."""
        emoji = cls.SEVERITY_EMOJIS.get(severity.lower(), EmojiSet.ERROR)
        return f"{emoji} {severity.upper()}: {error_type}"

    @classmethod
    def format_stack_trace(cls, trace: str, max_lines: int = 10) -> str:
        """Format stack trace for Discord display."""
        lines = trace.strip().split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more lines)"]
        return cls.format_code_block("\n".join(lines), "python")

    @classmethod
    def format_fields(
        cls,
        error_type: str,
        error_message: str,
        source: str,
        severity: str = "ERROR",
        trace: Optional[str] = None,
        context: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Format standard error fields."""
        fields = [
            {"name": "Error Type", "value": f"`{error_type}`", "inline": True},
            {"name": "Source", "value": source, "inline": True},
            {"name": "Severity", "value": severity.upper(), "inline": True},
            {"name": "Message", "value": cls.truncate(error_message), "inline": False},
        ]

        if trace:
            fields.append({
                "name": "Stack Trace",
                "value": cls.format_stack_trace(trace),
                "inline": False
            })

        if context:
            context_str = "\n".join(f"**{k}**: {v}" for k, v in context.items())
            fields.append({
                "name": "Context",
                "value": context_str,
                "inline": False
            })

        return fields


class CostNotificationFormatter(NotificationFormatter):
    """Formatter for cost alert notifications."""

    THRESHOLD_EMOJIS = {
        "low": EmojiSet.INFO,      # < 50%
        "medium": EmojiSet.COST,   # 50-79%
        "high": EmojiSet.WARNING,  # 80-99%
        "exceeded": EmojiSet.ERROR # >= 100%
    }

    @classmethod
    def get_threshold_level(cls, percentage: float) -> str:
        """Determine threshold level from percentage."""
        if percentage >= 100:
            return "exceeded"
        elif percentage >= 80:
            return "high"
        elif percentage >= 50:
            return "medium"
        return "low"

    @classmethod
    def format_title(cls, service: str, percentage: float) -> str:
        """Format cost alert title."""
        level = cls.get_threshold_level(percentage)
        emoji = cls.THRESHOLD_EMOJIS.get(level, EmojiSet.COST)
        return f"{emoji} Cost Alert: {service}"

    @classmethod
    def format_progress_bar(cls, percentage: float, width: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int(min(percentage / 100, 1.0) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"

    @classmethod
    def format_fields(
        cls,
        service: str,
        current_cost: float,
        budget_limit: float,
        period: str = "monthly",
        forecast: Optional[float] = None,
        breakdown: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Format standard cost alert fields."""
        percentage = (current_cost / budget_limit) * 100

        fields = [
            {"name": "Service", "value": service, "inline": True},
            {"name": "Period", "value": period.capitalize(), "inline": True},
            {
                "name": "Usage",
                "value": cls.format_progress_bar(percentage),
                "inline": True
            },
            {
                "name": "Current Cost",
                "value": cls.format_cost(current_cost),
                "inline": True
            },
            {
                "name": "Budget Limit",
                "value": cls.format_cost(budget_limit),
                "inline": True
            },
            {
                "name": "Remaining",
                "value": cls.format_cost(max(0, budget_limit - current_cost)),
                "inline": True
            },
        ]

        if forecast:
            fields.append({
                "name": "Forecasted Total",
                "value": cls.format_cost(forecast),
                "inline": True
            })

        if breakdown:
            breakdown_str = "\n".join(
                f"• {k}: {cls.format_cost(v)}"
                for k, v in sorted(breakdown.items(), key=lambda x: -x[1])
            )
            fields.append({
                "name": "Cost Breakdown",
                "value": breakdown_str,
                "inline": False
            })

        return fields


class BackupNotificationFormatter(NotificationFormatter):
    """Formatter for backup notifications."""

    BACKUP_TYPE_EMOJIS = {
        "full": ":file_cabinet:",
        "incremental": ":arrow_up:",
        "differential": ":arrows_counterclockwise:",
        "snapshot": ":camera:",
        "database": EmojiSet.DATABASE,
        "files": ":open_file_folder:"
    }

    @classmethod
    def format_title(cls, backup_type: str, status: str) -> str:
        """Format backup notification title."""
        status_emoji = EmojiSet.SUCCESS if status.lower() in ["success", "complete", "completed"] else EmojiSet.ERROR
        type_emoji = cls.BACKUP_TYPE_EMOJIS.get(backup_type.lower(), EmojiSet.BACKUP)
        return f"{type_emoji} Backup {status.capitalize()} {status_emoji}"

    @classmethod
    def format_fields(
        cls,
        backup_type: str,
        status: str,
        size: Optional[int] = None,
        duration: Optional[float] = None,
        destination: Optional[str] = None,
        files_count: Optional[int] = None,
        retention_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Format standard backup fields."""
        fields = [
            {"name": "Backup Type", "value": backup_type.capitalize(), "inline": True},
            {"name": "Status", "value": status.capitalize(), "inline": True},
        ]

        if size:
            fields.append({
                "name": "Size",
                "value": cls.format_size(size),
                "inline": True
            })

        if duration:
            fields.append({
                "name": "Duration",
                "value": cls.format_duration(duration),
                "inline": True
            })

        if files_count:
            fields.append({
                "name": "Files",
                "value": f"{files_count:,}",
                "inline": True
            })

        if retention_days:
            fields.append({
                "name": "Retention",
                "value": f"{retention_days} days",
                "inline": True
            })

        if destination:
            fields.append({
                "name": "Destination",
                "value": f"`{destination}`",
                "inline": False
            })

        return fields


class AgentNotificationFormatter(NotificationFormatter):
    """Formatter for AI agent notifications."""

    AGENT_STATUS_EMOJIS = {
        "active": ":green_circle:",
        "idle": ":yellow_circle:",
        "error": ":red_circle:",
        "completed": EmojiSet.SUCCESS,
        "timeout": ":alarm_clock:"
    }

    AGENT_TIER_EMOJIS = {
        "L0": ":crown:",       # Executive
        "L1": ":star:",        # Director
        "L2": ":gear:",        # Specialist
        "L3": ":hammer:"       # Worker
    }

    @classmethod
    def format_title(cls, agent_name: str, action: str) -> str:
        """Format agent notification title."""
        return f"{EmojiSet.AGENT} Agent {action}: {agent_name}"

    @classmethod
    def format_agent_tier(cls, tier: str) -> str:
        """Format agent tier with emoji."""
        emoji = cls.AGENT_TIER_EMOJIS.get(tier, ":robot:")
        return f"{emoji} {tier}"

    @classmethod
    def format_fields(
        cls,
        agent_name: str,
        agent_tier: str,
        status: str,
        task: Optional[str] = None,
        duration: Optional[float] = None,
        tokens_used: Optional[int] = None,
        output_summary: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Format standard agent fields."""
        status_emoji = cls.AGENT_STATUS_EMOJIS.get(status.lower(), ":robot:")

        fields = [
            {"name": "Agent", "value": agent_name, "inline": True},
            {"name": "Tier", "value": cls.format_agent_tier(agent_tier), "inline": True},
            {"name": "Status", "value": f"{status_emoji} {status}", "inline": True},
        ]

        if task:
            fields.append({"name": "Task", "value": task, "inline": False})

        if duration:
            fields.append({
                "name": "Duration",
                "value": cls.format_duration(duration),
                "inline": True
            })

        if tokens_used:
            fields.append({
                "name": "Tokens Used",
                "value": f"{tokens_used:,}",
                "inline": True
            })

        if output_summary:
            fields.append({
                "name": "Output Summary",
                "value": cls.truncate(output_summary, 500),
                "inline": False
            })

        return fields

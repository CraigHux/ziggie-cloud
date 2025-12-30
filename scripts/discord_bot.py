"""
Discord Bot for Pipeline Approvals
===================================
A full Discord bot that can read reactions and button interactions
for human-in-the-loop pipeline approvals.

Features:
- Reaction-based approvals (green checkmark, red X, refresh)
- Button-based approvals (modern Discord UI)
- Tracks pending approvals with timeout
- Integrates with the Ziggie asset pipeline
- Can run as standalone service or be imported

Setup:
1. Create bot at https://discord.com/developers/applications
2. Enable MESSAGE CONTENT INTENT in Bot settings
3. Enable SERVER MEMBERS INTENT in Bot settings
4. Generate bot token and add to .env.local
5. Invite bot to server with permissions: Send Messages, Add Reactions,
   Read Message History, Use Slash Commands, Attach Files, Embed Links

Usage:
    # As standalone bot service
    python discord_bot.py

    # Import for pipeline integration
    from discord_bot import DiscordApprovalBot, request_discord_approval

Environment Variables:
    DISCORD_BOT_TOKEN - Bot token from Discord Developer Portal
    DISCORD_APPROVAL_CHANNEL_ID - Channel ID for approval messages
    DISCORD_WEBHOOK_URL - Fallback webhook (optional)
"""

import os
import sys
import asyncio
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import queue

# Try to import discord.py
try:
    import discord
    from discord import app_commands
    from discord.ext import commands
    DISCORD_PY_AVAILABLE = True
except ImportError:
    DISCORD_PY_AVAILABLE = False
    print("Warning: discord.py not installed. Run: pip install discord.py")


# =============================================================================
# Configuration
# =============================================================================

def load_env():
    """Load environment variables from .env file."""
    # Try python-dotenv first (more robust)
    try:
        from dotenv import load_dotenv
        env_paths = [
            Path("/opt/ziggie/configs/.env"),  # VPS path
            Path("/opt/ziggie/.env"),          # VPS alt path
            Path("C:/Ziggie/.secrets/.env.local"),  # Windows local
            Path(__file__).parent.parent / "configs" / ".env",
            Path(".env.local"),
            Path(".env"),
        ]
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"[Discord Bot] Loaded config from: {env_path}")
                return
    except ImportError:
        pass

    # Fallback: manual parsing
    env_paths = [
        Path("/opt/ziggie/configs/.env"),  # VPS path
        Path("/opt/ziggie/.env"),          # VPS alt path
        Path("C:/Ziggie/.secrets/.env.local"),
        Path(".env.local"),
        Path("../.secrets/.env.local"),
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
            print(f"[Discord Bot] Loaded config from: {env_path}")
            break

load_env()


# Bot configuration
BOT_CONFIG = {
    "token": os.getenv("DISCORD_BOT_TOKEN"),
    "channel_id": os.getenv("DISCORD_APPROVAL_CHANNEL_ID"),
    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
    "command_prefix": "!ziggie ",
    "approval_timeout": 3600,  # 1 hour default
}

# Reaction emoji mappings (Unicode characters for reactions)
REACTION_DECISIONS = {
    "approve": "\u2705",      # White checkmark
    "reject": "\u274C",       # Red X
    "regenerate": "\U0001F504",  # Counterclockwise arrows
}

# Reverse mapping
EMOJI_TO_DECISION = {v: k for k, v in REACTION_DECISIONS.items()}


# =============================================================================
# Data Classes
# =============================================================================

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REGENERATE = "regenerate"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ApprovalRequest:
    """Represents a pending approval request."""
    request_id: str
    stage_name: str
    asset_name: str
    description: str
    image_path: Optional[str]
    message_id: Optional[int] = None
    channel_id: Optional[int] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    feedback: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    timeout_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    def is_expired(self) -> bool:
        if self.timeout_at is None:
            return False
        return datetime.now() > self.timeout_at


# =============================================================================
# Discord Bot Class
# =============================================================================

if DISCORD_PY_AVAILABLE:

    class ApprovalView(discord.ui.View):
        """Discord UI View with approval buttons."""

        def __init__(self, request_id: str, bot: 'DiscordApprovalBot', timeout: float = 3600):
            super().__init__(timeout=timeout)
            self.request_id = request_id
            self.bot = bot
            self.value = None
            self.feedback = None

        @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
        async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = "approved"
            await self._handle_decision(interaction, "approved")

        @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
        async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = "rejected"
            # Create modal for feedback
            modal = FeedbackModal(title="Rejection Reason", request_id=self.request_id, decision="rejected", bot=self.bot)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Regenerate", style=discord.ButtonStyle.blurple)
        async def regenerate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = "regenerate"
            # Create modal for feedback
            modal = FeedbackModal(title="Regeneration Instructions", request_id=self.request_id, decision="regenerate", bot=self.bot)
            await interaction.response.send_modal(modal)

        async def _handle_decision(self, interaction: discord.Interaction, decision: str, feedback: str = None):
            """Handle the decision and update the message."""
            # Defer immediately to prevent "This interaction failed" error
            # Discord requires response within 3 seconds - defer acknowledges instantly
            await interaction.response.defer()

            request = self.bot.pending_requests.get(self.request_id)
            if request:
                request.status = ApprovalStatus(decision)
                request.feedback = feedback
                request.resolved_at = datetime.now()
                request.resolved_by = str(interaction.user)

                # Put result in queue for sync callers
                if self.request_id in self.bot.result_queues:
                    self.bot.result_queues[self.request_id].put((decision, feedback))

            # Update message
            embed = interaction.message.embeds[0] if interaction.message.embeds else None
            if embed:
                color_map = {
                    "approved": discord.Color.green(),
                    "rejected": discord.Color.red(),
                    "regenerate": discord.Color.orange(),
                }
                embed.color = color_map.get(decision, discord.Color.grey())
                embed.add_field(
                    name="Decision",
                    value=f"**{decision.upper()}** by {interaction.user.mention}",
                    inline=False
                )
                if feedback:
                    embed.add_field(name="Feedback", value=feedback, inline=False)

            # Disable all buttons
            for child in self.children:
                child.disabled = True

            # Use message.edit() since we already deferred the interaction response
            await interaction.message.edit(embed=embed, view=self)
            self.stop()


    # =============================================================================
    # Stage 3→4 Decision View: Choose 3D Generation Service
    # =============================================================================

    class Stage3To4DecisionView(discord.ui.View):
        """
        Decision view shown after Stage 3 completes.
        Allows user to choose which 3D generation service to use for Stage 4.

        Options:
        - Meshy.ai: Fast, good quality, BUT animation requires manual tools
        - Tripo AI: Full pipeline support (3D + auto-rig + animate in one)
        - TripoSR (Colab): Free, manual upload required
        - Skip 3D: Continue with 2D sprites only
        """

        def __init__(self, request_id: str, bot: 'DiscordApprovalBot', timeout: float = 3600):
            super().__init__(timeout=timeout)
            self.request_id = request_id
            self.bot = bot
            self.value = None
            self.service_choice = None

        @discord.ui.button(label="Meshy.ai", style=discord.ButtonStyle.primary, emoji="🔷", row=0)
        async def meshy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.service_choice = "meshy"
            await self._handle_decision(interaction, "meshy",
                "Meshy.ai selected\n⚠️ Animation will require manual tools (Mixamo/Cascadeur/Blender)")

        @discord.ui.button(label="Tripo AI", style=discord.ButtonStyle.primary, emoji="🔶", row=0)
        async def tripo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.service_choice = "tripo"
            await self._handle_decision(interaction, "tripo",
                "Tripo AI selected\n✅ Full pipeline: 3D + Auto-rig + Animation available")

        @discord.ui.button(label="TripoSR (Colab)", style=discord.ButtonStyle.secondary, emoji="🟢", row=1)
        async def triposr_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.service_choice = "triposr_colab"
            await self._handle_decision(interaction, "triposr_colab",
                "TripoSR (Colab) selected\n⚠️ Manual upload required, animation needs manual tools")

        @discord.ui.button(label="Skip 3D (2D Only)", style=discord.ButtonStyle.secondary, emoji="⏭️", row=1)
        async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.service_choice = "skip_3d"
            await self._handle_decision(interaction, "skip_3d",
                "Skipping 3D generation\n→ Proceeding with 2D sprites only")

        @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="❌", row=2)
        async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = FeedbackModal(title="Rejection Reason", request_id=self.request_id, decision="rejected", bot=self.bot)
            await interaction.response.send_modal(modal)

        async def _handle_decision(self, interaction: discord.Interaction, choice: str, description: str):
            """Handle the service selection and update the message."""
            await interaction.response.defer()

            request = self.bot.pending_requests.get(self.request_id)
            if request:
                # Store the service choice in the decision
                request.status = ApprovalStatus.APPROVED
                request.feedback = f"3d_service:{choice}"  # Encode choice in feedback
                request.resolved_at = datetime.now()
                request.resolved_by = str(interaction.user)

                # Put result in queue
                if self.request_id in self.bot.result_queues:
                    self.bot.result_queues[self.request_id].put((f"approved_{choice}", description))

            # Update message
            embed = interaction.message.embeds[0] if interaction.message.embeds else None
            if embed:
                embed.color = discord.Color.green()
                embed.add_field(
                    name="Decision",
                    value=f"**{choice.upper()}** selected by {interaction.user.mention}",
                    inline=False
                )
                embed.add_field(name="Details", value=description, inline=False)

            # Disable all buttons
            for child in self.children:
                child.disabled = True

            await interaction.message.edit(embed=embed, view=self)
            self.stop()


    # =============================================================================
    # Stage 4→4.5 Decision View: Animation Decision
    # =============================================================================

    class Stage4To4_5DecisionView(discord.ui.View):
        """
        Decision view shown after Stage 4 (3D model) completes.
        Asks if the asset needs animation before sprite rendering.
        """

        def __init__(self, request_id: str, bot: 'DiscordApprovalBot',
                     model_source: str = "meshy", timeout: float = 3600):
            super().__init__(timeout=timeout)
            self.request_id = request_id
            self.bot = bot
            self.model_source = model_source  # "meshy", "tripo", "triposr_colab"
            self.value = None

        @discord.ui.button(label="Yes, Add Animation", style=discord.ButtonStyle.green, emoji="✅", row=0)
        async def yes_animation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Show rigging method selection
            view = RiggingMethodView(
                request_id=self.request_id,
                bot=self.bot,
                model_source=self.model_source
            )

            embed = discord.Embed(
                title="🦴 Choose Rigging Method",
                description=f"**Model Source**: {self.model_source.upper()}\n\n" +
                           ("✅ Tripo API rigging available (full pipeline)\n" if self.model_source == "tripo" else
                            "⚠️ External GLB - Tripo API cannot rig this model.\nManual rigging options available below."),
                color=discord.Color.blue()
            )

            # Disable buttons on this view
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)

            await interaction.response.send_message(embed=embed, view=view)

        @discord.ui.button(label="No, Static Sprites", style=discord.ButtonStyle.secondary, emoji="⏭️", row=0)
        async def no_animation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self._handle_decision(interaction, "skip_animation",
                "Stage 4.5 SKIPPED\n→ Proceeding with static sprite rendering (Stage 5)")

        @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="❌", row=1)
        async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = FeedbackModal(title="Rejection Reason", request_id=self.request_id, decision="rejected", bot=self.bot)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Regenerate 3D", style=discord.ButtonStyle.blurple, emoji="🔄", row=1)
        async def regenerate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = FeedbackModal(title="Regeneration Instructions", request_id=self.request_id, decision="regenerate", bot=self.bot)
            await interaction.response.send_modal(modal)

        async def _handle_decision(self, interaction: discord.Interaction, choice: str, description: str):
            """Handle the decision."""
            await interaction.response.defer()

            request = self.bot.pending_requests.get(self.request_id)
            if request:
                request.status = ApprovalStatus.APPROVED
                request.feedback = f"animation:{choice}"
                request.resolved_at = datetime.now()
                request.resolved_by = str(interaction.user)

                if self.request_id in self.bot.result_queues:
                    self.bot.result_queues[self.request_id].put((f"approved_{choice}", description))

            embed = interaction.message.embeds[0] if interaction.message.embeds else None
            if embed:
                embed.color = discord.Color.green()
                embed.add_field(name="Decision", value=f"**{choice.upper()}** by {interaction.user.mention}", inline=False)
                embed.add_field(name="Details", value=description, inline=False)

            for child in self.children:
                child.disabled = True

            await interaction.message.edit(embed=embed, view=self)
            self.stop()


    # =============================================================================
    # Rigging Method Selection View
    # =============================================================================

    class RiggingMethodView(discord.ui.View):
        """
        Rigging method selection shown when animation is requested.

        Options depend on model source:
        - Tripo models: All options including Tripo API
        - External GLBs (Meshy/TripoSR): Manual options only (Mixamo, Cascadeur, Blender)
        """

        def __init__(self, request_id: str, bot: 'DiscordApprovalBot',
                     model_source: str = "meshy", timeout: float = 3600):
            super().__init__(timeout=timeout)
            self.request_id = request_id
            self.bot = bot
            self.model_source = model_source

        @discord.ui.button(label="Tripo Full Pipeline", style=discord.ButtonStyle.green, emoji="🤖", row=0)
        async def tripo_full_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.model_source == "tripo":
                await self._handle_decision(interaction, "tripo_full_pipeline",
                    "Tripo Full Pipeline selected\n→ Will use Tripo AI for auto-rigging and animation")
            else:
                # For external GLBs, show warning and offer alternative
                await interaction.response.send_message(
                    "⚠️ **Tripo API Limitation**\n\n"
                    "The current 3D model was generated by **" + self.model_source.upper() + "**, not Tripo.\n"
                    "Tripo API can only rig models created through their own pipeline.\n\n"
                    "**Alternatives:**\n"
                    "• Use **Tripo Full Pipeline** from Stage 3→4 to regenerate 3D via Tripo\n"
                    "• Use **Mixamo**, **Cascadeur**, or **Blender** for manual rigging\n",
                    ephemeral=True
                )

        @discord.ui.button(label="Mixamo (Web)", style=discord.ButtonStyle.primary, emoji="👤", row=0)
        async def mixamo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self._handle_decision(interaction, "mixamo",
                "Mixamo selected\n→ Manual: Upload GLB to mixamo.com for auto-rigging\n"
                "📋 Instructions will be provided after approval")

        @discord.ui.button(label="Cascadeur (Desktop)", style=discord.ButtonStyle.primary, emoji="🎬", row=1)
        async def cascadeur_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self._handle_decision(interaction, "cascadeur",
                "Cascadeur selected\n→ AI-assisted animation in desktop app\n"
                "📋 Download: cascadeur.com (free tier available)")

        @discord.ui.button(label="Blender Manual", style=discord.ButtonStyle.secondary, emoji="🔧", row=1)
        async def blender_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self._handle_decision(interaction, "blender_manual",
                "Blender Manual selected\n→ Script-based rigging in Blender\n"
                "📋 Will use C:\\Ziggie\\scripts\\blender_rig.py (if available)")

        @discord.ui.button(label="Cancel (Static)", style=discord.ButtonStyle.secondary, emoji="⏭️", row=2)
        async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self._handle_decision(interaction, "skip_animation",
                "Animation cancelled\n→ Proceeding with static sprite rendering")

        async def _handle_decision(self, interaction: discord.Interaction, choice: str, description: str):
            """Handle the rigging method selection."""
            await interaction.response.defer()

            request = self.bot.pending_requests.get(self.request_id)
            if request:
                request.status = ApprovalStatus.APPROVED
                request.feedback = f"rigging:{choice}"
                request.resolved_at = datetime.now()
                request.resolved_by = str(interaction.user)

                if self.request_id in self.bot.result_queues:
                    self.bot.result_queues[self.request_id].put((f"approved_{choice}", description))

            embed = discord.Embed(
                title="🦴 Rigging Method Selected",
                description=description,
                color=discord.Color.green()
            )
            embed.add_field(name="Selected by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Model Source", value=self.model_source.upper(), inline=True)

            for child in self.children:
                child.disabled = True

            await interaction.message.edit(embed=embed, view=self)
            self.stop()


    # =============================================================================
    # Feedback Modal
    # =============================================================================

    class FeedbackModal(discord.ui.Modal):
        """Modal for collecting feedback on reject/regenerate decisions."""

        def __init__(self, title: str, request_id: str, decision: str, bot: 'DiscordApprovalBot'):
            super().__init__(title=title)
            self.request_id = request_id
            self.decision = decision
            self.bot = bot

            placeholder = "Why are you rejecting this?" if decision == "rejected" else "What changes should be made?"
            self.feedback_input = discord.ui.TextInput(
                label="Feedback (optional)",
                style=discord.TextStyle.paragraph,
                placeholder=placeholder,
                required=False,
                max_length=1000
            )
            self.add_item(self.feedback_input)

        async def on_submit(self, interaction: discord.Interaction):
            feedback = self.feedback_input.value or None

            request = self.bot.pending_requests.get(self.request_id)
            if request:
                request.status = ApprovalStatus(self.decision)
                request.feedback = feedback
                request.resolved_at = datetime.now()
                request.resolved_by = str(interaction.user)

                # Put result in queue
                if self.request_id in self.bot.result_queues:
                    self.bot.result_queues[self.request_id].put((self.decision, feedback))

            # Update original message
            message = await interaction.channel.fetch_message(request.message_id)
            if message:
                embed = message.embeds[0] if message.embeds else None
                if embed:
                    color_map = {
                        "rejected": discord.Color.red(),
                        "regenerate": discord.Color.orange(),
                    }
                    embed.color = color_map.get(self.decision, discord.Color.grey())
                    embed.add_field(
                        name="Decision",
                        value=f"**{self.decision.upper()}** by {interaction.user.mention}",
                        inline=False
                    )
                    if feedback:
                        embed.add_field(name="Feedback", value=feedback, inline=False)

                # Disable buttons on original view
                view = discord.ui.View()
                for child in message.components[0].children if message.components else []:
                    button = discord.ui.Button(
                        label=child.label,
                        style=child.style,
                        emoji=child.emoji,
                        disabled=True
                    )
                    view.add_item(button)

                await message.edit(embed=embed, view=view)

            await interaction.response.send_message(
                f"Decision recorded: **{self.decision.upper()}**" + (f"\nFeedback: {feedback}" if feedback else ""),
                ephemeral=True
            )


    class DiscordApprovalBot(commands.Bot):
        """Discord bot for handling pipeline approval requests."""

        def __init__(self, token: str = None, channel_id: int = None):
            intents = discord.Intents.default()
            intents.message_content = True
            intents.reactions = True
            intents.guilds = True

            super().__init__(
                command_prefix=BOT_CONFIG["command_prefix"],
                intents=intents,
                help_command=None
            )

            self.bot_token = token or BOT_CONFIG["token"]
            self.approval_channel_id = int(channel_id or BOT_CONFIG["channel_id"] or 0)
            self.pending_requests: Dict[str, ApprovalRequest] = {}
            self.result_queues: Dict[str, queue.Queue] = {}
            self._ready = asyncio.Event()
            self._loop = None

        async def setup_hook(self):
            """Called when the bot is ready to set up slash commands."""
            # Register slash commands
            @self.tree.command(name="approve", description="Approve a pending pipeline request")
            async def slash_approve(interaction: discord.Interaction, request_id: str):
                if request_id in self.pending_requests:
                    request = self.pending_requests[request_id]
                    request.status = ApprovalStatus.APPROVED
                    request.resolved_at = datetime.now()
                    request.resolved_by = str(interaction.user)
                    if request_id in self.result_queues:
                        self.result_queues[request_id].put(("approved", None))
                    await interaction.response.send_message(f"Approved request {request_id}")
                else:
                    await interaction.response.send_message(f"Request {request_id} not found", ephemeral=True)

            @self.tree.command(name="reject", description="Reject a pending pipeline request")
            async def slash_reject(interaction: discord.Interaction, request_id: str, reason: str = None):
                if request_id in self.pending_requests:
                    request = self.pending_requests[request_id]
                    request.status = ApprovalStatus.REJECTED
                    request.feedback = reason
                    request.resolved_at = datetime.now()
                    request.resolved_by = str(interaction.user)
                    if request_id in self.result_queues:
                        self.result_queues[request_id].put(("rejected", reason))
                    await interaction.response.send_message(f"Rejected request {request_id}" + (f": {reason}" if reason else ""))
                else:
                    await interaction.response.send_message(f"Request {request_id} not found", ephemeral=True)

            @self.tree.command(name="pending", description="List pending approval requests")
            async def slash_pending(interaction: discord.Interaction):
                pending = [r for r in self.pending_requests.values() if r.status == ApprovalStatus.PENDING]
                if pending:
                    embed = discord.Embed(title="Pending Approvals", color=discord.Color.yellow())
                    for req in pending[:10]:  # Limit to 10
                        embed.add_field(
                            name=f"{req.stage_name} - {req.asset_name}",
                            value=f"ID: `{req.request_id}`\nCreated: {req.created_at.strftime('%H:%M:%S')}",
                            inline=False
                        )
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("No pending approvals", ephemeral=True)

            # Sync commands
            try:
                synced = await self.tree.sync()
                print(f"[Discord Bot] Synced {len(synced)} slash commands")
            except Exception as e:
                print(f"[Discord Bot] Failed to sync commands: {e}")

        async def on_ready(self):
            """Called when the bot is connected and ready."""
            print(f"[Discord Bot] Logged in as {self.user} (ID: {self.user.id})")
            print(f"[Discord Bot] Approval channel: {self.approval_channel_id}")
            self._ready.set()

        async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
            """Handle reaction additions for approval decisions."""
            # Ignore bot's own reactions
            if payload.user_id == self.user.id:
                return

            # Check if this is a tracked message
            for request_id, request in self.pending_requests.items():
                if request.message_id == payload.message_id and request.status == ApprovalStatus.PENDING:
                    emoji = str(payload.emoji)

                    if emoji in EMOJI_TO_DECISION:
                        decision = EMOJI_TO_DECISION[emoji]
                        request.status = ApprovalStatus(decision)
                        request.resolved_at = datetime.now()

                        # Get user info
                        guild = self.get_guild(payload.guild_id)
                        if guild:
                            member = guild.get_member(payload.user_id)
                            request.resolved_by = str(member) if member else str(payload.user_id)

                        # Put result in queue
                        if request_id in self.result_queues:
                            self.result_queues[request_id].put((decision, None))

                        # Update message
                        channel = self.get_channel(payload.channel_id)
                        if channel:
                            try:
                                message = await channel.fetch_message(payload.message_id)
                                embed = message.embeds[0] if message.embeds else None
                                if embed:
                                    color_map = {
                                        "approved": discord.Color.green(),
                                        "rejected": discord.Color.red(),
                                        "regenerate": discord.Color.orange(),
                                    }
                                    embed.color = color_map.get(decision, discord.Color.grey())
                                    embed.add_field(
                                        name="Decision",
                                        value=f"**{decision.upper()}** by <@{payload.user_id}> (via reaction)",
                                        inline=False
                                    )
                                    await message.edit(embed=embed)
                            except Exception as e:
                                print(f"[Discord Bot] Failed to update message: {e}")

                        print(f"[Discord Bot] Request {request_id} {decision} via reaction")
                        break

        async def send_approval_request(
            self,
            stage_name: str,
            asset_name: str,
            description: str = None,
            image_path: str = None,
            stage_number: int = None,
            timeout_seconds: int = 3600,
            channel_id: int = None,
            model_source: str = None  # For Stage 4: "meshy", "tripo", "triposr_colab"
        ) -> ApprovalRequest:
            """Send an approval request message with stage-appropriate buttons.

            Stage-specific views:
            - Stage 3: Stage3To4DecisionView (choose 3D service)
            - Stage 4: Stage4To4_5DecisionView (animation decision)
            - Other stages: ApprovalView (standard approve/reject/regenerate)
            """
            await self._ready.wait()

            # Generate unique request ID
            request_id = f"{stage_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"

            # Create request object
            request = ApprovalRequest(
                request_id=request_id,
                stage_name=stage_name,
                asset_name=asset_name,
                description=description or f"Review {stage_name} output",
                image_path=image_path,
                timeout_at=datetime.now() + timedelta(seconds=timeout_seconds),
                channel_id=channel_id or self.approval_channel_id
            )

            # Store request
            self.pending_requests[request_id] = request
            self.result_queues[request_id] = queue.Queue()

            # Get channel
            channel = self.get_channel(request.channel_id)
            if not channel:
                print(f"[Discord Bot] Channel {request.channel_id} not found")
                request.status = ApprovalStatus.ERROR
                return request

            # Determine which view to use based on stage
            if stage_number == 3:
                # Stage 3 complete → Choose 3D generation service
                embed = discord.Embed(
                    title=f"🎨 Stage 3 Complete - Choose 3D Service",
                    description=(
                        f"**Asset**: {asset_name}\n\n"
                        "The 2D image has been upscaled. Choose how to generate the 3D model:\n\n"
                        "🔷 **Meshy.ai** - Fast, good quality\n"
                        "    ⚠️ Animation requires manual tools\n\n"
                        "🔶 **Tripo AI** - Full pipeline support\n"
                        "    ✅ Auto-rig + animation available\n\n"
                        "🟢 **TripoSR (Colab)** - Free, manual upload\n"
                        "    ⚠️ Animation requires manual tools\n\n"
                        "⏭️ **Skip 3D** - Continue with 2D sprites only"
                    ),
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                view = Stage3To4DecisionView(request_id=request_id, bot=self, timeout=float(timeout_seconds))

            elif stage_number == 4:
                # Stage 4 complete → Animation decision
                source_display = (model_source or "unknown").upper()
                source_note = "✅ Tripo API rigging available" if model_source == "tripo" else "⚠️ Manual rigging required (external GLB)"

                embed = discord.Embed(
                    title=f"🎮 Stage 4 Complete - Animation Decision",
                    description=(
                        f"**Asset**: {asset_name}\n"
                        f"**3D Model Source**: {source_display}\n"
                        f"**Note**: {source_note}\n\n"
                        "Does this asset need animation before sprite rendering?\n\n"
                        "✅ **Yes** → Choose rigging method (Tripo/Mixamo/Cascadeur/Blender)\n"
                        "⏭️ **No** → Skip Stage 4.5, render static sprites"
                    ),
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                view = Stage4To4_5DecisionView(
                    request_id=request_id,
                    bot=self,
                    model_source=model_source or "meshy",
                    timeout=float(timeout_seconds)
                )

            else:
                # Standard approval view for other stages
                embed = discord.Embed(
                    title=f"Approval Required: {stage_name}",
                    description=request.description,
                    color=discord.Color.yellow(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Asset", value=asset_name, inline=True)
                if stage_number:
                    embed.add_field(name="Stage", value=str(stage_number), inline=True)
                embed.add_field(name="Request ID", value=f"`{request_id}`", inline=True)
                embed.set_footer(text=f"React or click a button to decide | Timeout: {timeout_seconds//60} minutes")
                view = ApprovalView(request_id=request_id, bot=self, timeout=float(timeout_seconds))

            # Send message
            try:
                # If image provided, attach it
                if image_path and os.path.exists(image_path):
                    file = discord.File(image_path, filename=os.path.basename(image_path))
                    embed.set_image(url=f"attachment://{os.path.basename(image_path)}")
                    message = await channel.send(embed=embed, file=file, view=view)
                else:
                    message = await channel.send(embed=embed, view=view)

                request.message_id = message.id

                # Note: Removed bot self-reactions to avoid confusing "1" count on emojis
                # Users should use the buttons instead of reactions

                print(f"[Discord Bot] Sent approval request {request_id} to channel {channel.name}")

            except Exception as e:
                print(f"[Discord Bot] Failed to send message: {e}")
                request.status = ApprovalStatus.ERROR

            return request

        async def wait_for_decision(self, request_id: str, timeout: float = 3600) -> Tuple[str, Optional[str]]:
            """Wait for a decision on an approval request (async version)."""
            request = self.pending_requests.get(request_id)
            if not request:
                return "error", "Request not found"

            result_queue = self.result_queues.get(request_id)
            if not result_queue:
                return "error", "No result queue"

            # Poll for result
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    decision, feedback = result_queue.get_nowait()
                    return decision, feedback
                except queue.Empty:
                    await asyncio.sleep(1)

            return "timeout", None

        def wait_for_decision_sync(self, request_id: str, timeout: float = 3600) -> Tuple[str, Optional[str]]:
            """Wait for a decision on an approval request (sync version for pipeline integration)."""
            result_queue = self.result_queues.get(request_id)
            if not result_queue:
                return "error", "No result queue"

            try:
                decision, feedback = result_queue.get(timeout=timeout)
                return decision, feedback
            except queue.Empty:
                return "timeout", None

        def run_bot(self):
            """Run the bot (blocking)."""
            if not self.bot_token:
                print("[Discord Bot] No token provided. Set DISCORD_BOT_TOKEN in environment.")
                return

            self.run(self.bot_token)

        def start_background(self):
            """Start the bot in a background thread."""
            def run_in_thread():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                self._loop.run_until_complete(self.start(self.bot_token))

            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()
            return thread


# =============================================================================
# Synchronous API for Pipeline Integration
# =============================================================================

_bot_instance: Optional['DiscordApprovalBot'] = None
_bot_thread: Optional[threading.Thread] = None


def get_bot() -> Optional['DiscordApprovalBot']:
    """Get or create the global bot instance."""
    global _bot_instance, _bot_thread

    if not DISCORD_PY_AVAILABLE:
        return None

    if _bot_instance is None:
        token = BOT_CONFIG["token"]
        channel_id = BOT_CONFIG["channel_id"]

        if not token:
            print("[Discord Bot] No DISCORD_BOT_TOKEN configured")
            return None

        _bot_instance = DiscordApprovalBot(token=token, channel_id=channel_id)
        _bot_thread = _bot_instance.start_background()

        # Wait for bot to be ready
        import time
        for _ in range(30):  # Wait up to 30 seconds
            if _bot_instance._ready.is_set():
                break
            time.sleep(1)

    return _bot_instance


def request_discord_approval(
    stage_name: str,
    asset_name: str,
    description: str = None,
    image_path: str = None,
    stage_number: int = None,
    timeout_seconds: int = 3600,
    model_source: str = None  # For Stage 4: "meshy", "tripo", "triposr_colab"
) -> Tuple[str, Optional[str]]:
    """
    Request approval via Discord bot with reactions/buttons.

    This is the main entry point for pipeline integration.

    Args:
        stage_name: Name of the pipeline stage (e.g., "Stage 4: 2D to 3D")
        asset_name: Name of the asset being processed
        description: Optional description of what needs approval
        image_path: Optional path to preview image
        stage_number: Optional stage number (1-7)
        timeout_seconds: How long to wait for decision (default 1 hour)
        model_source: For Stage 4 - which 3D service was used ("meshy", "tripo", "triposr_colab")

    Returns:
        Tuple of (decision: str, feedback: Optional[str])
        Decision is one of: "approved", "rejected", "regenerate", "timeout", "error"

        For Stage 3, decision may be: "approved_meshy", "approved_tripo", "approved_triposr_colab", "approved_skip_3d"
        For Stage 4, decision may be: "approved_skip_animation", "approved_tripo_full_pipeline",
                                      "approved_mixamo", "approved_cascadeur", "approved_blender_manual"
    """
    bot = get_bot()
    if not bot:
        return "error", "Bot not available"

    # Send request in event loop
    try:
        future = asyncio.run_coroutine_threadsafe(
            bot.send_approval_request(
                stage_name=stage_name,
                asset_name=asset_name,
                description=description,
                image_path=image_path,
                stage_number=stage_number,
                timeout_seconds=timeout_seconds,
                model_source=model_source
            ),
            bot._loop
        )
        request = future.result(timeout=30)  # Wait up to 30s to send message

        if request.status == ApprovalStatus.ERROR:
            return "error", "Failed to send approval request"

        # Wait for decision
        decision, feedback = bot.wait_for_decision_sync(request.request_id, timeout_seconds)
        return decision, feedback

    except Exception as e:
        print(f"[Discord Bot] Error: {e}")
        return "error", str(e)


def check_bot_status() -> bool:
    """Check if the Discord bot is available and connected."""
    bot = get_bot()
    return bot is not None and bot._ready.is_set()


# =============================================================================
# Command Line Interface
# =============================================================================

def main():
    """Run the Discord bot as a standalone service."""
    import argparse

    parser = argparse.ArgumentParser(description="Discord Approval Bot for Ziggie Pipeline")
    parser.add_argument("--test", action="store_true", help="Send a test approval request")
    parser.add_argument("--channel", type=int, help="Override approval channel ID")
    args = parser.parse_args()

    if not DISCORD_PY_AVAILABLE:
        print("Error: discord.py not installed")
        print("Install with: pip install discord.py")
        sys.exit(1)

    token = BOT_CONFIG["token"]
    if not token:
        print("Error: DISCORD_BOT_TOKEN not set")
        print("\nSetup instructions:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create New Application -> 'Ziggie Pipeline Bot'")
        print("3. Go to Bot section -> Reset Token -> Copy token")
        print("4. Enable MESSAGE CONTENT INTENT")
        print("5. Enable SERVER MEMBERS INTENT")
        print("6. Add to .env.local:")
        print("   DISCORD_BOT_TOKEN=your_token_here")
        print("   DISCORD_APPROVAL_CHANNEL_ID=channel_id")
        print("\n7. Invite bot to server with this URL (replace CLIENT_ID):")
        print("   https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=274878024768&scope=bot%20applications.commands")
        sys.exit(1)

    channel_id = args.channel or BOT_CONFIG["channel_id"]

    print("[Discord Bot] Starting Ziggie Pipeline Approval Bot...")
    print(f"[Discord Bot] Token: {token[:20]}...")
    print(f"[Discord Bot] Channel: {channel_id}")

    bot = DiscordApprovalBot(token=token, channel_id=channel_id)

    if args.test:
        @bot.event
        async def on_ready():
            print(f"[Discord Bot] Connected as {bot.user}")
            print("[Discord Bot] Sending test approval request...")

            request = await bot.send_approval_request(
                stage_name="Test Stage",
                asset_name="test_asset.png",
                description="This is a test approval request. Click a button or react to approve/reject.",
                stage_number=0,
                timeout_seconds=300
            )

            print(f"[Discord Bot] Test request sent: {request.request_id}")
            print("[Discord Bot] Waiting for decision...")

            decision, feedback = await bot.wait_for_decision(request.request_id, timeout=300)
            print(f"[Discord Bot] Decision: {decision}")
            if feedback:
                print(f"[Discord Bot] Feedback: {feedback}")

            print("[Discord Bot] Test complete. Bot will continue running.")

    bot.run_bot()


if __name__ == "__main__":
    main()

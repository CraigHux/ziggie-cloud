"""
Configuration loader for Knowledge Base Pipeline
Loads settings from .env file and provides defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
KB_ROOT = Path(__file__).parent.parent
load_dotenv(KB_ROOT / ".env")


class Config:
    """Pipeline configuration"""

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Paths
    KB_PATH = Path(os.getenv("KB_PATH", str(KB_ROOT)))
    LOG_PATH = Path(os.getenv("LOG_PATH", str(KB_ROOT / "logs")))
    METADATA_PATH = Path(os.getenv("METADATA_PATH", str(KB_ROOT / "metadata")))
    TEMP_PATH = Path(os.getenv("TEMP_PATH", str(KB_ROOT / "temp")))

    # Scanning
    SCAN_SCHEDULE_CRITICAL = os.getenv("SCAN_SCHEDULE_CRITICAL", "every_3_days")
    SCAN_SCHEDULE_HIGH = os.getenv("SCAN_SCHEDULE_HIGH", "weekly")
    SCAN_SCHEDULE_MEDIUM = os.getenv("SCAN_SCHEDULE_MEDIUM", "biweekly")
    SCAN_SCHEDULE_LOW = os.getenv("SCAN_SCHEDULE_LOW", "monthly")
    MAX_VIDEOS_PER_SCAN = int(os.getenv("MAX_VIDEOS_PER_SCAN", "10"))
    SCAN_LOOKBACK_DAYS = int(os.getenv("SCAN_LOOKBACK_DAYS", "7"))

    # Extraction
    TRANSCRIPT_METHODS = os.getenv("TRANSCRIPT_METHODS", "youtube_auto,youtube_manual").split(",")
    MAX_TRANSCRIPT_LENGTH = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "50000"))
    MIN_VIDEO_DURATION = int(os.getenv("MIN_VIDEO_DURATION", "120"))
    MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "3600"))

    # AI Analysis
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.3"))
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
    ANALYSIS_RETRY_COUNT = int(os.getenv("ANALYSIS_RETRY_COUNT", "3"))

    # Validation
    CONFIDENCE_THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", "80"))
    HUMAN_REVIEW_THRESHOLD = int(os.getenv("HUMAN_REVIEW_THRESHOLD", "60"))
    AUTO_REJECT_THRESHOLD = int(os.getenv("AUTO_REJECT_THRESHOLD", "40"))
    REQUIRE_MULTI_SOURCE_VALIDATION = os.getenv("REQUIRE_MULTI_SOURCE_VALIDATION", "true").lower() == "true"
    MIN_SOURCES_FOR_VALIDATION = int(os.getenv("MIN_SOURCES_FOR_VALIDATION", "2"))
    MULTI_SOURCE_CONFIDENCE_BOOST = int(os.getenv("MULTI_SOURCE_CONFIDENCE_BOOST", "10"))

    # Storage
    KB_FILE_FORMAT = os.getenv("KB_FILE_FORMAT", "markdown")
    INCLUDE_TIMESTAMPS = os.getenv("INCLUDE_TIMESTAMPS", "true").lower() == "true"
    INCLUDE_CITATIONS = os.getenv("INCLUDE_CITATIONS", "true").lower() == "true"
    BACKUP_BEFORE_UPDATE = os.getenv("BACKUP_BEFORE_UPDATE", "true").lower() == "true"

    # Performance
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "3"))
    API_CALL_DELAY = float(os.getenv("API_CALL_DELAY", "1"))
    YOUTUBE_API_DAILY_QUOTA = int(os.getenv("YOUTUBE_API_DAILY_QUOTA", "10000"))
    ANTHROPIC_RPM_LIMIT = int(os.getenv("ANTHROPIC_RPM_LIMIT", "50"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    MAX_LOG_FILE_SIZE = int(os.getenv("MAX_LOG_FILE_SIZE", "10")) * 1024 * 1024  # Convert to bytes
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Testing & Debug
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
    SAVE_RAW_TRANSCRIPTS = os.getenv("SAVE_RAW_TRANSCRIPTS", "false").lower() == "true"
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")

        if not cls.YOUTUBE_API_KEY:
            errors.append("YOUTUBE_API_KEY is required (optional if only processing URLs directly)")

        if not cls.KB_PATH.exists():
            errors.append(f"KB_PATH does not exist: {cls.KB_PATH}")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        # Create directories if they don't exist
        cls.LOG_PATH.mkdir(parents=True, exist_ok=True)
        cls.TEMP_PATH.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def summary(cls):
        """Print configuration summary"""
        return f"""
Knowledge Base Pipeline Configuration
======================================
Paths:
  KB Path: {cls.KB_PATH}
  Logs: {cls.LOG_PATH}
  Metadata: {cls.METADATA_PATH}

API Keys:
  Anthropic: {'[OK] Set' if cls.ANTHROPIC_API_KEY else '[X] Missing'}
  YouTube: {'[OK] Set' if cls.YOUTUBE_API_KEY else '[X] Missing'}
  OpenAI: {'[OK] Set' if cls.OPENAI_API_KEY else '[X] Not set (optional)'}

Scanning:
  Max videos per scan: {cls.MAX_VIDEOS_PER_SCAN}
  Lookback days: {cls.SCAN_LOOKBACK_DAYS}

Analysis:
  Model: {cls.CLAUDE_MODEL}
  Temperature: {cls.CLAUDE_TEMPERATURE}
  Max tokens: {cls.CLAUDE_MAX_TOKENS}

Validation:
  Confidence threshold: {cls.CONFIDENCE_THRESHOLD}%
  Human review threshold: {cls.HUMAN_REVIEW_THRESHOLD}%
  Auto-reject threshold: {cls.AUTO_REJECT_THRESHOLD}%

Mode:
  Dry run: {cls.DRY_RUN}
  Test mode: {cls.TEST_MODE}
  Verbose: {cls.VERBOSE}
======================================
"""


# Validate on import (optional, can comment out for development)
# Config.validate()

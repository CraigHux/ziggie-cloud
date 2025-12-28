"""Configuration management for Control Center backend."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import Any


class Settings(BaseSettings):
    """Application settings."""

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 54112
    DEBUG: bool = True
    OLLAMA_URL: str = "http://localhost:11434"

    # CORS configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]

    # Database configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///control-center.db"

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    COMFYUI_DIR: Path = Path(r"C:\ComfyUI")
    MEOWPING_DIR: Path = Path(r"C:\Ziggie")
    AI_AGENTS_ROOT: Path = Path(r"C:\Ziggie\ai-agents")

    # Service-specific paths
    COMFYUI_PYTHON_PATH: Path = Path(r"C:\ComfyUI\python_embeded\python.exe")
    KB_SCHEDULER_PATH: Path = Path(r"C:\Ziggie\ai-agents\knowledge-base")

    # API Keys
    KEYS_API_DIR: Path = Path(r"C:\Ziggie\Keys-api")
    YOUTUBE_API_KEY_FILE: Path = Path(r"C:\Ziggie\Keys-api\meowping-youtube-api.txt")

    # WebSocket update interval (seconds)
    WS_UPDATE_INTERVAL: int = 2

    # Port scanning range
    PORT_SCAN_START: int = 3000
    PORT_SCAN_END: int = 9000

    # Authentication settings
    JWT_SECRET: str = "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Default admin credentials (for initial setup)
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"  # CHANGE IN PRODUCTION!

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def SERVICES(self) -> dict:
        """Service configurations built from environment variables."""
        return {
            "comfyui": {
                "name": "ComfyUI",
                "command": [
                    str(self.COMFYUI_PYTHON_PATH),
                    "-s",
                    "main.py",
                    "--windows-standalone-build",
                    "--cpu"
                ],
                "cwd": str(self.COMFYUI_DIR),
                "port": 8188,
                "log_file": "comfyui.log"
            },
            "kb_scheduler": {
                "name": "Knowledge Base Scheduler",
                "command": ["python", "manage.py", "schedule"],
                "cwd": str(self.KB_SCHEDULER_PATH),
                "port": None,
                "log_file": "kb_scheduler.log"
            }
        }

    def load_youtube_api_key(self) -> str:
        """Load YouTube API key from file."""
        try:
            with open(self.YOUTUBE_API_KEY_FILE, 'r') as f:
                # Read the file and extract the API key (line 5 in the file)
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('AIza'):
                        return line.strip()
                raise ValueError("YouTube API key not found in file")
        except Exception as e:
            raise RuntimeError(f"Failed to load YouTube API key: {e}")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment


# Global settings instance
settings = Settings()

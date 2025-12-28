"""
Meshy.ai Configuration Module

Handles configuration loading from environment variables and AWS Secrets Manager.
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Literal
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MeshyConfig:
    """
    Configuration for Meshy.ai API integration.

    Attributes:
        api_key: Meshy.ai API key (from AWS Secrets Manager or env)
        base_url: Meshy.ai API base URL
        output_formats: Supported output formats (glb, fbx, obj, stl)
        default_format: Default output format
        quality_preset: Quality preset (low, medium, high)
        timeout: API request timeout in seconds
        max_retries: Maximum retry attempts for failed requests
        output_dir: Directory for downloaded models
        enable_texture: Enable texture generation
        enable_pbr: Enable PBR material generation
    """

    api_key: str = ""
    base_url: str = "https://api.meshy.ai"
    output_formats: List[str] = field(default_factory=lambda: ["glb", "fbx", "obj", "stl"])
    default_format: str = "glb"
    quality_preset: Literal["low", "medium", "high"] = "medium"
    timeout: int = 300  # 5 minutes for 3D generation
    max_retries: int = 3
    output_dir: str = "C:/Ziggie/assets/3d_models"
    enable_texture: bool = True
    enable_pbr: bool = True

    # Rate limiting
    requests_per_minute: int = 10
    max_concurrent: int = 3

    # AWS Secrets Manager settings
    aws_region: str = "eu-north-1"
    secret_name: str = "ziggie/meshy-api-key"

    @classmethod
    def from_env(cls) -> "MeshyConfig":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("MESHY_API_KEY", ""),
            base_url=os.getenv("MESHY_BASE_URL", "https://api.meshy.ai"),
            default_format=os.getenv("MESHY_DEFAULT_FORMAT", "glb"),
            quality_preset=os.getenv("MESHY_QUALITY", "medium"),
            timeout=int(os.getenv("MESHY_TIMEOUT", "300")),
            output_dir=os.getenv("MESHY_OUTPUT_DIR", "C:/Ziggie/assets/3d_models"),
            enable_texture=os.getenv("MESHY_ENABLE_TEXTURE", "true").lower() == "true",
            enable_pbr=os.getenv("MESHY_ENABLE_PBR", "true").lower() == "true",
        )

    @classmethod
    def from_aws_secrets(cls, secret_name: str = None, region: str = None) -> "MeshyConfig":
        """
        Load configuration with API key from AWS Secrets Manager.

        Args:
            secret_name: Override default secret name
            region: Override default AWS region

        Returns:
            MeshyConfig with API key loaded from AWS Secrets Manager
        """
        config = cls.from_env()

        if secret_name:
            config.secret_name = secret_name
        if region:
            config.aws_region = region

        try:
            import boto3
            from botocore.exceptions import ClientError

            client = boto3.client(
                service_name="secretsmanager",
                region_name=config.aws_region
            )

            response = client.get_secret_value(SecretId=config.secret_name)

            if "SecretString" in response:
                secret = json.loads(response["SecretString"])
                config.api_key = secret.get("api_key", secret.get("MESHY_API_KEY", ""))
                logger.info(f"Loaded Meshy API key from AWS Secrets Manager: {config.secret_name}")
            else:
                logger.warning("Secret found but no SecretString present")

        except ImportError:
            logger.warning("boto3 not installed. Install with: pip install boto3")
        except ClientError as e:
            logger.error(f"Failed to load secret from AWS: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading AWS secret: {e}")

        return config

    @classmethod
    def from_file(cls, config_path: str) -> "MeshyConfig":
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path, "r") as f:
            data = json.load(f)

        return cls(**data)

    def to_dict(self) -> dict:
        """Convert config to dictionary (excludes sensitive data)."""
        return {
            "base_url": self.base_url,
            "output_formats": self.output_formats,
            "default_format": self.default_format,
            "quality_preset": self.quality_preset,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "output_dir": self.output_dir,
            "enable_texture": self.enable_texture,
            "enable_pbr": self.enable_pbr,
            "requests_per_minute": self.requests_per_minute,
            "max_concurrent": self.max_concurrent,
            "api_key_configured": bool(self.api_key),
        }

    def validate(self) -> bool:
        """Validate configuration."""
        errors = []

        if not self.api_key:
            errors.append("API key not configured")

        if self.default_format not in self.output_formats:
            errors.append(f"Default format '{self.default_format}' not in supported formats")

        if self.quality_preset not in ["low", "medium", "high"]:
            errors.append(f"Invalid quality preset: {self.quality_preset}")

        if errors:
            for error in errors:
                logger.error(f"Config validation error: {error}")
            return False

        return True


# Template for creating meshy-config.json
CONFIG_TEMPLATE = """
{
    "api_key": "",
    "base_url": "https://api.meshy.ai",
    "output_formats": ["glb", "fbx", "obj", "stl"],
    "default_format": "glb",
    "quality_preset": "medium",
    "timeout": 300,
    "max_retries": 3,
    "output_dir": "C:/Ziggie/assets/3d_models",
    "enable_texture": true,
    "enable_pbr": true,
    "requests_per_minute": 10,
    "max_concurrent": 3,
    "aws_region": "eu-north-1",
    "secret_name": "ziggie/meshy-api-key"
}
"""


def create_config_template(output_path: str = "C:/Ziggie/integrations/meshy/meshy-config.json"):
    """Create a configuration template file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        f.write(CONFIG_TEMPLATE.strip())

    logger.info(f"Created config template at: {output_path}")
    return output_path


if __name__ == "__main__":
    # Create config template
    create_config_template()
    print("Config template created successfully")

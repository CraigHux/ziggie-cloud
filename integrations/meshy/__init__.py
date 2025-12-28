"""
Meshy.ai Integration Module for Ziggie

This module provides integration with Meshy.ai's Image-to-3D and Text-to-3D APIs
for automated game asset generation.

Components:
- meshy_client.py: Core API wrapper
- image_to_3d.py: Image to 3D model conversion
- batch_processor.py: Batch processing for multiple images
- config.py: Configuration management with AWS Secrets Manager

Usage:
    from integrations.meshy import MeshyClient, ImageTo3D, BatchProcessor

    client = MeshyClient()
    converter = ImageTo3D(client)
    result = await converter.convert("path/to/image.png")
"""

from .meshy_client import MeshyClient
from .image_to_3d import ImageTo3D
from .batch_processor import BatchProcessor
from .config import MeshyConfig

__version__ = "1.0.0"
__all__ = ["MeshyClient", "ImageTo3D", "BatchProcessor", "MeshyConfig"]

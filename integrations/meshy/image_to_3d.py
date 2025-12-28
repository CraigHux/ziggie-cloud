"""
Image-to-3D Conversion Module

High-level interface for converting 2D concept art to 3D game models.
Handles preprocessing, conversion, and post-processing workflows.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import json

from .meshy_client import MeshyClient, TaskResult, TaskStatus, MeshyAPIError
from .config import MeshyConfig

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of an image-to-3D conversion."""
    success: bool
    input_path: str
    output_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    task_id: Optional[str] = None
    duration_seconds: float = 0.0
    credits_used: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "thumbnail_path": self.thumbnail_path,
            "task_id": self.task_id,
            "duration_seconds": self.duration_seconds,
            "credits_used": self.credits_used,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class ImageTo3D:
    """
    High-level interface for image-to-3D conversion.

    Provides:
    - Automatic file naming based on input
    - Progress callbacks
    - Retry logic
    - Thumbnail download
    - Metadata tracking

    Usage:
        client = MeshyClient()
        converter = ImageTo3D(client)

        # Simple conversion
        result = await converter.convert("concept_art/cat_warrior.png")

        # With options
        result = await converter.convert(
            image_path="concept_art/building.png",
            output_dir="models/buildings",
            mode="refine",
            format="fbx",
            progress_callback=lambda p, s: print(f"{p}% - {s}")
        )
    """

    def __init__(self, client: Optional[MeshyClient] = None, config: Optional[MeshyConfig] = None):
        """
        Initialize converter.

        Args:
            client: MeshyClient instance. If None, creates one.
            config: MeshyConfig for new client. Ignored if client provided.
        """
        self.config = config or MeshyConfig.from_aws_secrets()
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self):
        if self._client is None:
            self._client = MeshyClient(self.config)
            await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owns_client and self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def client(self) -> MeshyClient:
        """Get the underlying client."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    async def convert(
        self,
        image_path: str,
        output_dir: Optional[str] = None,
        output_name: Optional[str] = None,
        mode: str = "preview",
        format: Optional[str] = None,
        ai_model: str = "meshy-4",
        topology: str = "quad",
        target_polycount: int = 30000,
        download_thumbnail: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        timeout: float = 600.0,
    ) -> ConversionResult:
        """
        Convert a 2D image to a 3D model.

        Args:
            image_path: Path to input image
            output_dir: Directory for output. Default: config.output_dir
            output_name: Output filename (without extension). Default: input filename
            mode: "preview" (fast) or "refine" (high quality)
            format: Output format (glb, fbx, obj, stl). Default: config.default_format
            ai_model: AI model version
            topology: Mesh topology type
            target_polycount: Target polygon count
            download_thumbnail: Whether to download preview thumbnail
            progress_callback: Optional callback(progress: int, status: str)
            timeout: Maximum wait time in seconds

        Returns:
            ConversionResult with paths and metadata
        """
        start_time = datetime.now()
        input_path = Path(image_path)

        if not input_path.exists():
            return ConversionResult(
                success=False,
                input_path=str(input_path),
                error_message=f"Input file not found: {image_path}"
            )

        # Determine output paths
        output_dir = Path(output_dir or self.config.output_dir)
        output_name = output_name or input_path.stem
        format = format or self.config.default_format
        output_path = output_dir / f"{output_name}.{format}"
        thumbnail_path = output_dir / f"{output_name}_thumb.png" if download_thumbnail else None

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Starting conversion: {input_path.name} -> {output_path.name}")

            # Create task
            task = await self.client.create_image_to_3d(
                image_path=str(input_path),
                mode=mode,
                ai_model=ai_model,
                topology=topology,
                target_polycount=target_polycount,
            )

            logger.info(f"Task created: {task.task_id}")

            # Wait for completion
            result = await self.client.wait_for_completion(
                task_id=task.task_id,
                task_type="image-to-3d",
                timeout=timeout,
                progress_callback=progress_callback,
            )

            # Download model
            model_path = await self.client.download_model(
                result=result,
                output_path=str(output_path),
                format=format,
            )

            # Download thumbnail if requested
            thumb_path = None
            if download_thumbnail and result.thumbnail_url:
                try:
                    thumb_path = await self.client.download_thumbnail(
                        result=result,
                        output_path=str(thumbnail_path),
                    )
                except Exception as e:
                    logger.warning(f"Failed to download thumbnail: {e}")

            duration = (datetime.now() - start_time).total_seconds()

            return ConversionResult(
                success=True,
                input_path=str(input_path),
                output_path=model_path,
                thumbnail_path=thumb_path,
                task_id=task.task_id,
                duration_seconds=duration,
                credits_used=result.credits_used,
                metadata={
                    "mode": mode,
                    "format": format,
                    "ai_model": ai_model,
                    "topology": topology,
                    "target_polycount": target_polycount,
                    "model_urls": result.model_urls,
                }
            )

        except MeshyAPIError as e:
            logger.error(f"API error during conversion: {e}")
            return ConversionResult(
                success=False,
                input_path=str(input_path),
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
            )
        except TimeoutError as e:
            logger.error(f"Timeout during conversion: {e}")
            return ConversionResult(
                success=False,
                input_path=str(input_path),
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
            )
        except Exception as e:
            logger.exception(f"Unexpected error during conversion: {e}")
            return ConversionResult(
                success=False,
                input_path=str(input_path),
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
            )

    async def convert_from_url(
        self,
        image_url: str,
        output_dir: Optional[str] = None,
        output_name: str = "model",
        mode: str = "preview",
        format: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        timeout: float = 600.0,
    ) -> ConversionResult:
        """
        Convert an image from URL to 3D model.

        Args:
            image_url: URL of the input image
            output_dir: Output directory
            output_name: Output filename (without extension)
            mode: "preview" or "refine"
            format: Output format
            progress_callback: Progress callback
            timeout: Maximum wait time

        Returns:
            ConversionResult
        """
        start_time = datetime.now()
        output_dir = Path(output_dir or self.config.output_dir)
        format = format or self.config.default_format
        output_path = output_dir / f"{output_name}.{format}"

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            task = await self.client.create_image_to_3d_from_url(
                image_url=image_url,
                mode=mode,
            )

            result = await self.client.wait_for_completion(
                task_id=task.task_id,
                timeout=timeout,
                progress_callback=progress_callback,
            )

            model_path = await self.client.download_model(
                result=result,
                output_path=str(output_path),
                format=format,
            )

            return ConversionResult(
                success=True,
                input_path=image_url,
                output_path=model_path,
                task_id=task.task_id,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                credits_used=result.credits_used,
            )

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConversionResult(
                success=False,
                input_path=image_url,
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
            )

    async def convert_with_refinement(
        self,
        image_path: str,
        output_dir: Optional[str] = None,
        output_name: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> ConversionResult:
        """
        Two-stage conversion: preview first, then refine.

        Creates higher quality output by using preview result
        as input for refined generation.

        Args:
            image_path: Input image path
            output_dir: Output directory
            output_name: Output filename
            progress_callback: Progress callback

        Returns:
            ConversionResult for the refined model
        """
        def stage_callback(stage: str):
            def callback(progress: int, status: str):
                if progress_callback:
                    progress_callback(progress, f"[{stage}] {status}")
            return callback

        # Stage 1: Preview
        logger.info("Stage 1: Creating preview...")
        preview_result = await self.convert(
            image_path=image_path,
            output_dir=output_dir,
            output_name=f"{output_name or Path(image_path).stem}_preview",
            mode="preview",
            progress_callback=stage_callback("Preview"),
        )

        if not preview_result.success:
            return preview_result

        # Stage 2: Refine
        logger.info("Stage 2: Refining model...")
        refine_result = await self.convert(
            image_path=image_path,
            output_dir=output_dir,
            output_name=output_name,
            mode="refine",
            progress_callback=stage_callback("Refine"),
        )

        # Add preview info to metadata
        if refine_result.success:
            refine_result.metadata["preview_path"] = preview_result.output_path
            refine_result.metadata["total_credits"] = (
                preview_result.credits_used + refine_result.credits_used
            )

        return refine_result


# Convenience functions for quick conversions

async def quick_convert(image_path: str, output_path: Optional[str] = None) -> str:
    """
    Quickly convert an image to 3D model.

    Args:
        image_path: Path to input image
        output_path: Optional output path. If None, saves next to input.

    Returns:
        Path to output model

    Raises:
        Exception if conversion fails
    """
    async with ImageTo3D() as converter:
        output_dir = str(Path(output_path).parent) if output_path else None
        output_name = Path(output_path).stem if output_path else None

        result = await converter.convert(
            image_path=image_path,
            output_dir=output_dir,
            output_name=output_name,
        )

        if not result.success:
            raise Exception(f"Conversion failed: {result.error_message}")

        return result.output_path


def convert_sync(image_path: str, output_path: Optional[str] = None) -> str:
    """Synchronous wrapper for quick_convert."""
    return asyncio.run(quick_convert(image_path, output_path))


if __name__ == "__main__":
    # Example usage
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python image_to_3d.py <image_path> [output_path]")
            sys.exit(1)

        image_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None

        def progress(p: int, s: str):
            print(f"  {p:3d}% | {s}")

        async with ImageTo3D() as converter:
            print(f"Converting: {image_path}")
            result = await converter.convert(
                image_path=image_path,
                output_dir=str(Path(output_path).parent) if output_path else None,
                progress_callback=progress,
            )

            if result.success:
                print(f"\nSuccess!")
                print(f"  Output: {result.output_path}")
                print(f"  Duration: {result.duration_seconds:.1f}s")
                print(f"  Credits: {result.credits_used}")
            else:
                print(f"\nFailed: {result.error_message}")
                sys.exit(1)

    asyncio.run(main())

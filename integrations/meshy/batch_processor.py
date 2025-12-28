"""
Batch Processing Module for Meshy.ai

Process multiple images in parallel with rate limiting,
progress tracking, and error handling.
"""

import asyncio
import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Union
from concurrent.futures import ThreadPoolExecutor
import csv

from .meshy_client import MeshyClient, MeshyAPIError
from .image_to_3d import ImageTo3D, ConversionResult
from .config import MeshyConfig

logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """A single job in a batch."""
    id: int
    input_path: str
    output_name: Optional[str] = None
    mode: str = "preview"
    format: str = "glb"
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[ConversionResult] = None


@dataclass
class BatchResult:
    """Result of a batch processing run."""
    total: int
    successful: int
    failed: int
    skipped: int
    total_credits: int
    total_duration_seconds: float
    jobs: List[BatchJob] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "total_credits": self.total_credits,
            "total_duration_seconds": self.total_duration_seconds,
            "success_rate": self.success_rate,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "jobs": [
                {
                    "id": job.id,
                    "input_path": job.input_path,
                    "output_name": job.output_name,
                    "status": job.status,
                    "result": job.result.to_dict() if job.result else None,
                }
                for job in self.jobs
            ],
        }

    def save_report(self, output_path: str):
        """Save batch report to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved batch report to: {output_path}")


class BatchProcessor:
    """
    Process multiple images in batches with concurrency control.

    Features:
    - Parallel processing with configurable concurrency
    - Rate limiting respecting API limits
    - Progress callbacks
    - Resume from checkpoint
    - Error handling with retry

    Usage:
        processor = BatchProcessor()

        # From directory
        result = await processor.process_directory(
            input_dir="concept_art/units",
            output_dir="models/units",
            pattern="*.png"
        )

        # From file list
        result = await processor.process_files(
            files=["cat1.png", "cat2.png", "cat3.png"],
            output_dir="models"
        )
    """

    def __init__(
        self,
        config: Optional[MeshyConfig] = None,
        max_concurrent: int = 3,
    ):
        """
        Initialize batch processor.

        Args:
            config: MeshyConfig instance
            max_concurrent: Maximum concurrent conversions (respects API limits)
        """
        self.config = config or MeshyConfig.from_aws_secrets()
        self.max_concurrent = min(max_concurrent, self.config.max_concurrent)
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def process_directory(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        pattern: str = "*.png",
        mode: str = "preview",
        format: str = "glb",
        recursive: bool = False,
        skip_existing: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        checkpoint_path: Optional[str] = None,
    ) -> BatchResult:
        """
        Process all images in a directory.

        Args:
            input_dir: Directory containing images
            output_dir: Output directory. Default: input_dir/3d_models
            pattern: Glob pattern for images (e.g., "*.png", "*.jpg")
            mode: Generation mode ("preview" or "refine")
            format: Output format
            recursive: Search subdirectories
            skip_existing: Skip if output already exists
            progress_callback: callback(completed: int, total: int, current: str)
            checkpoint_path: Path to save/load checkpoint for resume

        Returns:
            BatchResult with all job results
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all matching files
        if recursive:
            files = list(input_path.rglob(pattern))
        else:
            files = list(input_path.glob(pattern))

        if not files:
            logger.warning(f"No files matching '{pattern}' in {input_dir}")
            return BatchResult(total=0, successful=0, failed=0, skipped=0, total_credits=0, total_duration_seconds=0)

        # Sort for consistent ordering
        files = sorted(files)

        logger.info(f"Found {len(files)} files to process")

        return await self.process_files(
            files=[str(f) for f in files],
            output_dir=output_dir or str(input_path / "3d_models"),
            mode=mode,
            format=format,
            skip_existing=skip_existing,
            progress_callback=progress_callback,
            checkpoint_path=checkpoint_path,
        )

    async def process_files(
        self,
        files: List[str],
        output_dir: str,
        mode: str = "preview",
        format: str = "glb",
        skip_existing: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        checkpoint_path: Optional[str] = None,
    ) -> BatchResult:
        """
        Process a list of image files.

        Args:
            files: List of image file paths
            output_dir: Output directory for models
            mode: Generation mode
            format: Output format
            skip_existing: Skip if output exists
            progress_callback: Progress callback
            checkpoint_path: Checkpoint file path

        Returns:
            BatchResult
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create jobs
        jobs: List[BatchJob] = []
        for i, file_path in enumerate(files):
            input_path = Path(file_path)
            output_name = input_path.stem

            # Check if output already exists
            expected_output = output_path / f"{output_name}.{format}"
            if skip_existing and expected_output.exists():
                logger.debug(f"Skipping existing: {output_name}")
                jobs.append(BatchJob(
                    id=i,
                    input_path=file_path,
                    output_name=output_name,
                    mode=mode,
                    format=format,
                    status="skipped",
                ))
            else:
                jobs.append(BatchJob(
                    id=i,
                    input_path=file_path,
                    output_name=output_name,
                    mode=mode,
                    format=format,
                    status="pending",
                ))

        # Load checkpoint if exists
        completed_ids = set()
        if checkpoint_path and Path(checkpoint_path).exists():
            checkpoint = self._load_checkpoint(checkpoint_path)
            completed_ids = set(checkpoint.get("completed", []))
            logger.info(f"Loaded checkpoint: {len(completed_ids)} already completed")

        # Filter pending jobs
        pending_jobs = [j for j in jobs if j.status == "pending" and j.id not in completed_ids]

        result = BatchResult(
            total=len(jobs),
            successful=0,
            failed=0,
            skipped=len([j for j in jobs if j.status == "skipped"]),
            total_credits=0,
            total_duration_seconds=0,
            jobs=jobs,
            start_time=datetime.now(),
        )

        if not pending_jobs:
            logger.info("No pending jobs to process")
            result.end_time = datetime.now()
            return result

        logger.info(f"Processing {len(pending_jobs)} jobs ({result.skipped} skipped)")

        # Initialize semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

        # Process jobs concurrently
        async with MeshyClient(self.config) as client:
            converter = ImageTo3D(client=client, config=self.config)

            completed = len(completed_ids) + result.skipped
            total = len(jobs)

            async def process_job(job: BatchJob):
                nonlocal completed

                async with self._semaphore:
                    job.status = "processing"

                    if progress_callback:
                        progress_callback(completed, total, job.input_path)

                    try:
                        job.result = await converter.convert(
                            image_path=job.input_path,
                            output_dir=str(output_path),
                            output_name=job.output_name,
                            mode=job.mode,
                            format=job.format,
                        )

                        if job.result.success:
                            job.status = "completed"
                            result.successful += 1
                            result.total_credits += job.result.credits_used
                        else:
                            job.status = "failed"
                            result.failed += 1

                        result.total_duration_seconds += job.result.duration_seconds

                    except Exception as e:
                        logger.error(f"Job {job.id} failed: {e}")
                        job.status = "failed"
                        job.result = ConversionResult(
                            success=False,
                            input_path=job.input_path,
                            error_message=str(e),
                        )
                        result.failed += 1

                    completed += 1

                    # Save checkpoint
                    if checkpoint_path:
                        self._save_checkpoint(checkpoint_path, jobs)

            # Run all pending jobs
            await asyncio.gather(*[process_job(job) for job in pending_jobs])

        result.end_time = datetime.now()
        logger.info(
            f"Batch complete: {result.successful}/{result.total} successful, "
            f"{result.failed} failed, {result.skipped} skipped"
        )

        return result

    async def process_from_csv(
        self,
        csv_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> BatchResult:
        """
        Process images from a CSV file.

        CSV format:
            input_path,output_name,mode,format
            concept_art/cat.png,cat_warrior,preview,glb
            concept_art/dog.png,dog_knight,refine,fbx

        Args:
            csv_path: Path to CSV file
            output_dir: Output directory
            progress_callback: Progress callback

        Returns:
            BatchResult
        """
        jobs: List[BatchJob] = []

        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                jobs.append(BatchJob(
                    id=i,
                    input_path=row["input_path"],
                    output_name=row.get("output_name") or Path(row["input_path"]).stem,
                    mode=row.get("mode", "preview"),
                    format=row.get("format", "glb"),
                ))

        # Process using existing method
        return await self.process_files(
            files=[j.input_path for j in jobs],
            output_dir=output_dir,
            progress_callback=progress_callback,
        )

    def _save_checkpoint(self, path: str, jobs: List[BatchJob]):
        """Save checkpoint for resume."""
        checkpoint = {
            "completed": [j.id for j in jobs if j.status in ("completed", "failed", "skipped")],
            "timestamp": datetime.now().isoformat(),
        }
        with open(path, "w") as f:
            json.dump(checkpoint, f)

    def _load_checkpoint(self, path: str) -> Dict[str, Any]:
        """Load checkpoint for resume."""
        with open(path, "r") as f:
            return json.load(f)


# Cost estimation utilities

def estimate_batch_cost(
    num_images: int,
    mode: str = "preview",
    quality: str = "medium",
) -> Dict[str, Any]:
    """
    Estimate credits and cost for a batch.

    Args:
        num_images: Number of images to process
        mode: "preview" or "refine"
        quality: Quality preset

    Returns:
        Dictionary with credits and cost estimates
    """
    # Meshy.ai credit costs (approximate)
    CREDITS_PER_MODEL = {
        "preview": {"low": 1, "medium": 2, "high": 3},
        "refine": {"low": 3, "medium": 5, "high": 8},
    }

    # Cost per credit (approximate, based on paid plans)
    COST_PER_CREDIT = 0.08  # $0.08 per credit on average

    credits_per_model = CREDITS_PER_MODEL.get(mode, {}).get(quality, 2)
    total_credits = num_images * credits_per_model

    # Free tier: 200 credits/month
    free_credits = 200
    paid_credits = max(0, total_credits - free_credits)
    estimated_cost = paid_credits * COST_PER_CREDIT

    return {
        "num_images": num_images,
        "mode": mode,
        "quality": quality,
        "credits_per_model": credits_per_model,
        "total_credits": total_credits,
        "free_tier_credits": free_credits,
        "credits_from_free_tier": min(total_credits, free_credits),
        "paid_credits": paid_credits,
        "estimated_cost_usd": round(estimated_cost, 2),
        "note": "Free tier: 200 credits/month. Costs vary by subscription plan.",
    }


async def quick_batch(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.png",
) -> BatchResult:
    """
    Quick batch processing with defaults.

    Args:
        input_dir: Input directory
        output_dir: Output directory (default: input_dir/3d_models)
        pattern: File pattern

    Returns:
        BatchResult
    """
    processor = BatchProcessor()

    def progress(completed: int, total: int, current: str):
        print(f"[{completed}/{total}] Processing: {Path(current).name}")

    return await processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        pattern=pattern,
        progress_callback=progress,
    )


if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python batch_processor.py <input_dir> [output_dir] [pattern]")
            print("\nEstimate cost:")
            print("  python batch_processor.py --estimate <num_images> [mode] [quality]")
            sys.exit(1)

        if sys.argv[1] == "--estimate":
            num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            mode = sys.argv[3] if len(sys.argv) > 3 else "preview"
            quality = sys.argv[4] if len(sys.argv) > 4 else "medium"

            estimate = estimate_batch_cost(num_images, mode, quality)
            print("\nCost Estimate:")
            print(f"  Images: {estimate['num_images']}")
            print(f"  Mode: {estimate['mode']}")
            print(f"  Quality: {estimate['quality']}")
            print(f"  Credits per model: {estimate['credits_per_model']}")
            print(f"  Total credits needed: {estimate['total_credits']}")
            print(f"  Free tier covers: {estimate['credits_from_free_tier']} credits")
            print(f"  Paid credits: {estimate['paid_credits']}")
            print(f"  Estimated cost: ${estimate['estimated_cost_usd']:.2f}")
            return

        input_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*.png"

        result = await quick_batch(input_dir, output_dir, pattern)

        print(f"\n=== Batch Complete ===")
        print(f"Total: {result.total}")
        print(f"Successful: {result.successful}")
        print(f"Failed: {result.failed}")
        print(f"Skipped: {result.skipped}")
        print(f"Credits used: {result.total_credits}")
        print(f"Duration: {result.total_duration_seconds:.1f}s")
        print(f"Success rate: {result.success_rate:.1f}%")

    asyncio.run(main())

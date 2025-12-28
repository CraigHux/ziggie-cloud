"""
Meshy.ai API Client

Core API wrapper for Meshy.ai's Image-to-3D and Text-to-3D services.

API Reference:
- Image-to-3D: POST /v1/image-to-3d
- Text-to-3D: POST /v1/text-to-3d
- Task Status: GET /v1/image-to-3d/{task_id} or /v1/text-to-3d/{task_id}

Rate Limits (Free Tier):
- 200 credits/month
- ~10 requests/minute
"""

import asyncio
import aiohttp
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .config import MeshyConfig

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Meshy task status enum."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


@dataclass
class TaskResult:
    """Result of a Meshy API task."""
    task_id: str
    status: TaskStatus
    model_urls: Optional[Dict[str, str]] = None
    thumbnail_url: Optional[str] = None
    progress: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    credits_used: int = 0

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "TaskResult":
        """Create TaskResult from API response."""
        return cls(
            task_id=data.get("id", ""),
            status=TaskStatus(data.get("status", "PENDING")),
            model_urls=data.get("model_urls"),
            thumbnail_url=data.get("thumbnail_url"),
            progress=data.get("progress", 0),
            error_message=data.get("message") if data.get("status") == "FAILED" else None,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")) if data.get("created_at") else None,
            finished_at=datetime.fromisoformat(data["finished_at"].replace("Z", "+00:00")) if data.get("finished_at") else None,
            credits_used=data.get("credits_used", 0),
        )


class MeshyClient:
    """
    Asynchronous client for Meshy.ai API.

    Usage:
        config = MeshyConfig.from_aws_secrets()
        client = MeshyClient(config)

        # Image to 3D
        task = await client.create_image_to_3d("path/to/image.png")
        result = await client.wait_for_completion(task.task_id)

        # Download model
        await client.download_model(result, "output/model.glb")
    """

    def __init__(self, config: Optional[MeshyConfig] = None):
        """
        Initialize Meshy client.

        Args:
            config: MeshyConfig instance. If None, loads from AWS Secrets Manager.
        """
        self.config = config or MeshyConfig.from_aws_secrets()
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_tokens = self.config.requests_per_minute
        self._last_refill = time.time()

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_headers()
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    async def _rate_limit(self):
        """Simple token bucket rate limiter."""
        now = time.time()
        elapsed = now - self._last_refill

        # Refill tokens based on time elapsed
        tokens_to_add = elapsed * (self.config.requests_per_minute / 60)
        self._rate_limit_tokens = min(
            self.config.requests_per_minute,
            self._rate_limit_tokens + tokens_to_add
        )
        self._last_refill = now

        # Wait if no tokens available
        if self._rate_limit_tokens < 1:
            wait_time = (1 - self._rate_limit_tokens) * (60 / self.config.requests_per_minute)
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            self._rate_limit_tokens = 1

        self._rate_limit_tokens -= 1

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make API request with rate limiting and retries.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: JSON data to send
            files: Files to upload (for multipart)

        Returns:
            API response as dictionary
        """
        await self._ensure_session()
        await self._rate_limit()

        url = f"{self.config.base_url}{endpoint}"
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                if files:
                    # Multipart form data for file uploads
                    form = aiohttp.FormData()
                    for key, value in (data or {}).items():
                        form.add_field(key, str(value))
                    for key, (filename, content, content_type) in files.items():
                        form.add_field(key, content, filename=filename, content_type=content_type)

                    async with self._session.request(method, url, data=form) as response:
                        response_data = await response.json()
                        if response.status >= 400:
                            raise MeshyAPIError(
                                response.status,
                                response_data.get("message", "Unknown error")
                            )
                        return response_data
                else:
                    async with self._session.request(method, url, json=data) as response:
                        response_data = await response.json()
                        if response.status >= 400:
                            raise MeshyAPIError(
                                response.status,
                                response_data.get("message", "Unknown error")
                            )
                        return response_data

            except aiohttp.ClientError as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)

        raise MeshyAPIError(0, f"Request failed after {self.config.max_retries} retries: {last_error}")

    async def create_image_to_3d(
        self,
        image_path: str,
        mode: str = "preview",
        ai_model: str = "meshy-4",
        topology: str = "quad",
        target_polycount: int = 30000,
        enable_texture: Optional[bool] = None,
        enable_pbr: Optional[bool] = None,
    ) -> TaskResult:
        """
        Create an Image-to-3D task.

        Args:
            image_path: Path to input image (PNG, JPG, WEBP supported)
            mode: Generation mode - "preview" (fast, lower quality) or "refine" (slow, higher quality)
            ai_model: AI model to use - "meshy-4" (latest) or "meshy-3"
            topology: Mesh topology - "quad" or "triangle"
            target_polycount: Target polygon count (1000-200000)
            enable_texture: Override config texture setting
            enable_pbr: Override config PBR setting

        Returns:
            TaskResult with task_id for polling
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Read image content
        with open(path, "rb") as f:
            image_content = f.read()

        # Determine content type
        suffix = path.suffix.lower()
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        content_type = content_types.get(suffix, "image/png")

        data = {
            "mode": mode,
            "ai_model": ai_model,
            "topology": topology,
            "target_polycount": target_polycount,
            "should_remesh": True,
            "enable_texture": enable_texture if enable_texture is not None else self.config.enable_texture,
            "enable_pbr": enable_pbr if enable_pbr is not None else self.config.enable_pbr,
        }

        files = {
            "image_file": (path.name, image_content, content_type)
        }

        logger.info(f"Creating Image-to-3D task for: {path.name}")
        response = await self._request("POST", "/v1/image-to-3d", data=data, files=files)

        return TaskResult(
            task_id=response.get("result", response.get("id", "")),
            status=TaskStatus.PENDING,
            progress=0,
        )

    async def create_image_to_3d_from_url(
        self,
        image_url: str,
        mode: str = "preview",
        ai_model: str = "meshy-4",
        topology: str = "quad",
        target_polycount: int = 30000,
    ) -> TaskResult:
        """
        Create an Image-to-3D task from URL.

        Args:
            image_url: URL of the input image
            mode: Generation mode
            ai_model: AI model to use
            topology: Mesh topology
            target_polycount: Target polygon count

        Returns:
            TaskResult with task_id
        """
        data = {
            "image_url": image_url,
            "mode": mode,
            "ai_model": ai_model,
            "topology": topology,
            "target_polycount": target_polycount,
            "should_remesh": True,
            "enable_texture": self.config.enable_texture,
            "enable_pbr": self.config.enable_pbr,
        }

        logger.info(f"Creating Image-to-3D task from URL: {image_url[:50]}...")
        response = await self._request("POST", "/v1/image-to-3d", data=data)

        return TaskResult(
            task_id=response.get("result", response.get("id", "")),
            status=TaskStatus.PENDING,
            progress=0,
        )

    async def create_text_to_3d(
        self,
        prompt: str,
        mode: str = "preview",
        ai_model: str = "meshy-4",
        art_style: str = "realistic",
        negative_prompt: str = "",
        topology: str = "quad",
        target_polycount: int = 30000,
    ) -> TaskResult:
        """
        Create a Text-to-3D task.

        Args:
            prompt: Text description of desired 3D model
            mode: Generation mode - "preview" or "refine"
            ai_model: AI model to use
            art_style: Art style - "realistic", "sculpture", "pbr"
            negative_prompt: What to avoid in generation
            topology: Mesh topology
            target_polycount: Target polygon count

        Returns:
            TaskResult with task_id
        """
        data = {
            "prompt": prompt,
            "mode": mode,
            "ai_model": ai_model,
            "art_style": art_style,
            "negative_prompt": negative_prompt,
            "topology": topology,
            "target_polycount": target_polycount,
        }

        logger.info(f"Creating Text-to-3D task: {prompt[:50]}...")
        response = await self._request("POST", "/v1/text-to-3d", data=data)

        return TaskResult(
            task_id=response.get("result", response.get("id", "")),
            status=TaskStatus.PENDING,
            progress=0,
        )

    async def get_task_status(self, task_id: str, task_type: str = "image-to-3d") -> TaskResult:
        """
        Get status of a task.

        Args:
            task_id: Task ID from create_* methods
            task_type: Type of task - "image-to-3d" or "text-to-3d"

        Returns:
            TaskResult with current status
        """
        endpoint = f"/v1/{task_type}/{task_id}"
        response = await self._request("GET", endpoint)
        return TaskResult.from_api_response(response)

    async def wait_for_completion(
        self,
        task_id: str,
        task_type: str = "image-to-3d",
        poll_interval: float = 5.0,
        timeout: float = 600.0,
        progress_callback: Optional[callable] = None,
    ) -> TaskResult:
        """
        Wait for a task to complete.

        Args:
            task_id: Task ID to monitor
            task_type: Type of task
            poll_interval: Seconds between status checks
            timeout: Maximum wait time in seconds
            progress_callback: Optional callback(progress: int, status: str)

        Returns:
            Final TaskResult

        Raises:
            TimeoutError: If task doesn't complete within timeout
            MeshyAPIError: If task fails
        """
        start_time = time.time()

        while True:
            result = await self.get_task_status(task_id, task_type)

            if progress_callback:
                progress_callback(result.progress, result.status.value)

            if result.status == TaskStatus.SUCCEEDED:
                logger.info(f"Task {task_id} completed successfully")
                return result

            if result.status == TaskStatus.FAILED:
                raise MeshyAPIError(0, f"Task failed: {result.error_message}")

            if result.status == TaskStatus.EXPIRED:
                raise MeshyAPIError(0, "Task expired before completion")

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Task {task_id} timed out after {timeout}s")

            logger.debug(f"Task {task_id}: {result.progress}% - {result.status.value}")
            await asyncio.sleep(poll_interval)

    async def download_model(
        self,
        result: TaskResult,
        output_path: str,
        format: Optional[str] = None,
    ) -> str:
        """
        Download 3D model from completed task.

        Args:
            result: Completed TaskResult
            output_path: Path to save model (extension auto-detected)
            format: Output format (glb, fbx, obj, stl). If None, uses default from config.

        Returns:
            Path to downloaded file
        """
        if result.status != TaskStatus.SUCCEEDED:
            raise ValueError(f"Cannot download from non-completed task: {result.status}")

        if not result.model_urls:
            raise ValueError("No model URLs in task result")

        format = format or self.config.default_format
        model_url = result.model_urls.get(format)

        if not model_url:
            available = list(result.model_urls.keys())
            raise ValueError(f"Format '{format}' not available. Available: {available}")

        # Ensure output directory exists
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Download model
        await self._ensure_session()
        async with self._session.get(model_url) as response:
            if response.status != 200:
                raise MeshyAPIError(response.status, "Failed to download model")

            with open(output, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

        logger.info(f"Downloaded model to: {output}")
        return str(output)

    async def download_thumbnail(self, result: TaskResult, output_path: str) -> str:
        """Download thumbnail preview image."""
        if not result.thumbnail_url:
            raise ValueError("No thumbnail URL in task result")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        await self._ensure_session()
        async with self._session.get(result.thumbnail_url) as response:
            if response.status != 200:
                raise MeshyAPIError(response.status, "Failed to download thumbnail")

            with open(output, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

        logger.info(f"Downloaded thumbnail to: {output}")
        return str(output)

    async def list_tasks(
        self,
        task_type: str = "image-to-3d",
        page: int = 1,
        page_size: int = 20,
    ) -> List[TaskResult]:
        """
        List all tasks.

        Args:
            task_type: Type of tasks to list
            page: Page number (1-indexed)
            page_size: Results per page

        Returns:
            List of TaskResult objects
        """
        endpoint = f"/v1/{task_type}"
        params = f"?page={page}&page_size={page_size}"
        response = await self._request("GET", endpoint + params)

        tasks = response.get("tasks", response.get("results", []))
        return [TaskResult.from_api_response(task) for task in tasks]

    async def get_credits(self) -> Dict[str, Any]:
        """Get remaining credits information."""
        response = await self._request("GET", "/v1/credits")
        return response

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()


class MeshyAPIError(Exception):
    """Exception for Meshy API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Meshy API Error ({status_code}): {message}")


# Convenience function for synchronous usage
def create_client(config: Optional[MeshyConfig] = None) -> MeshyClient:
    """Create a Meshy client instance."""
    return MeshyClient(config or MeshyConfig.from_aws_secrets())


if __name__ == "__main__":
    # Quick test
    import sys

    async def test():
        config = MeshyConfig.from_env()
        if not config.api_key:
            print("Error: MESHY_API_KEY environment variable not set")
            sys.exit(1)

        async with MeshyClient(config) as client:
            credits = await client.get_credits()
            print(f"Available credits: {credits}")

    asyncio.run(test())

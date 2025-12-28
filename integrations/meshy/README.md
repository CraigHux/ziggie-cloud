# Meshy.ai Integration for Ziggie

Convert 2D concept art to 3D game models using Meshy.ai's Image-to-3D API.

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

#### Option A: AWS Secrets Manager (Recommended)

Store API key in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name ziggie/meshy-api-key \
    --secret-string '{"api_key": "YOUR_MESHY_API_KEY"}' \
    --region eu-north-1
```

The integration will automatically load from AWS:

```python
from integrations.meshy import MeshyConfig, MeshyClient

config = MeshyConfig.from_aws_secrets()
client = MeshyClient(config)
```

#### Option B: Environment Variable

```bash
export MESHY_API_KEY="your_api_key_here"
```

```python
config = MeshyConfig.from_env()
```

#### Option C: Config File

Edit `meshy-config.json` and add your API key:

```python
config = MeshyConfig.from_file("meshy-config.json")
```

### 3. Single Image Conversion

```python
import asyncio
from integrations.meshy import ImageTo3D

async def convert_single():
    async with ImageTo3D() as converter:
        result = await converter.convert(
            image_path="concept_art/cat_warrior.png",
            output_dir="models/units",
            mode="preview",  # or "refine" for higher quality
            format="glb",
        )

        if result.success:
            print(f"Model saved: {result.output_path}")
            print(f"Credits used: {result.credits_used}")
        else:
            print(f"Failed: {result.error_message}")

asyncio.run(convert_single())
```

### 4. Batch Processing

```python
import asyncio
from integrations.meshy import BatchProcessor

async def batch_convert():
    processor = BatchProcessor(max_concurrent=3)

    result = await processor.process_directory(
        input_dir="concept_art/units",
        output_dir="models/units",
        pattern="*.png",
        mode="preview",
        skip_existing=True,
    )

    print(f"Converted {result.successful}/{result.total} models")
    print(f"Total credits: {result.total_credits}")

    # Save report
    result.save_report("batch_report.json")

asyncio.run(batch_convert())
```

### 5. CLI Usage

```bash
# Single conversion
python -m integrations.meshy.image_to_3d concept_art/cat.png models/cat.glb

# Batch processing
python -m integrations.meshy.batch_processor ./concept_art ./3d_models "*.png"

# Cost estimation
python -m integrations.meshy.batch_processor --estimate 50 preview medium
```

## API Reference

### MeshyClient

Low-level API wrapper for Meshy.ai.

```python
from integrations.meshy import MeshyClient

async with MeshyClient() as client:
    # Create task
    task = await client.create_image_to_3d(
        image_path="image.png",
        mode="preview",
        ai_model="meshy-4",
        topology="quad",
        target_polycount=30000,
    )

    # Wait for completion
    result = await client.wait_for_completion(task.task_id)

    # Download model
    await client.download_model(result, "output.glb")

    # Check credits
    credits = await client.get_credits()
    print(f"Remaining: {credits['remaining']}")
```

### ImageTo3D

High-level conversion interface.

```python
from integrations.meshy import ImageTo3D

async with ImageTo3D() as converter:
    # Simple conversion
    result = await converter.convert("image.png")

    # With options
    result = await converter.convert(
        image_path="image.png",
        output_dir="models",
        output_name="my_model",
        mode="refine",
        format="fbx",
        progress_callback=lambda p, s: print(f"{p}% - {s}"),
    )

    # Two-stage refinement
    result = await converter.convert_with_refinement(
        image_path="image.png",
        output_dir="models",
    )
```

### BatchProcessor

Process multiple images efficiently.

```python
from integrations.meshy import BatchProcessor

processor = BatchProcessor(max_concurrent=3)

# From directory
result = await processor.process_directory(
    input_dir="concept_art",
    output_dir="models",
    pattern="*.png",
    recursive=True,
    skip_existing=True,
    checkpoint_path="checkpoint.json",  # Resume support
)

# From file list
result = await processor.process_files(
    files=["cat.png", "dog.png", "bird.png"],
    output_dir="models",
)

# From CSV
result = await processor.process_from_csv(
    csv_path="batch_jobs.csv",
    output_dir="models",
)
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `api_key` | "" | Meshy.ai API key |
| `base_url` | "https://api.meshy.ai" | API base URL |
| `default_format` | "glb" | Default output format |
| `quality_preset` | "medium" | Quality level (low/medium/high) |
| `timeout` | 300 | Request timeout in seconds |
| `max_retries` | 3 | Maximum retry attempts |
| `output_dir` | "C:/Ziggie/assets/3d_models" | Default output directory |
| `enable_texture` | true | Enable texture generation |
| `enable_pbr` | true | Enable PBR materials |
| `requests_per_minute` | 10 | Rate limit |
| `max_concurrent` | 3 | Max parallel conversions |

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| GLB | .glb | Universal, web-ready, includes textures |
| FBX | .fbx | Unity, Unreal Engine |
| OBJ | .obj | Universal, no textures embedded |
| STL | .stl | 3D printing |

## n8n Workflow Integration

Import `n8n-workflow-meshy.json` into n8n for automated pipeline:

1. Open n8n
2. Import workflow from file
3. Configure AWS credentials
4. Trigger via webhook:

```bash
curl -X POST http://localhost:5678/webhook/meshy-convert \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.png", "mode": "preview"}'
```

## Cost Estimation

| Mode | Quality | Credits/Model | Cost/Model* |
|------|---------|---------------|-------------|
| Preview | Low | 1 | $0.08 |
| Preview | Medium | 2 | $0.16 |
| Preview | High | 3 | $0.24 |
| Refine | Low | 3 | $0.24 |
| Refine | Medium | 5 | $0.40 |
| Refine | High | 8 | $0.64 |

*Approximate, varies by subscription plan

### Free Tier

- 200 credits/month
- Enough for ~100 preview models or ~40 refined models

### Cost Calculator

```python
from integrations.meshy import estimate_batch_cost

estimate = estimate_batch_cost(
    num_images=50,
    mode="preview",
    quality="medium",
)
print(f"Estimated cost: ${estimate['estimated_cost_usd']}")
```

## Troubleshooting

### "API key not configured"

Ensure your API key is set via one of:
- AWS Secrets Manager (ziggie/meshy-api-key)
- Environment variable (MESHY_API_KEY)
- Config file (meshy-config.json)

### "Rate limit exceeded"

The integration includes rate limiting. If you see this:
1. Reduce `max_concurrent` in config
2. Wait 60 seconds before retrying

### "Task timeout"

3D generation can take 30-120 seconds. Increase `timeout` in config if needed.

### "Invalid image format"

Supported formats: PNG, JPG, JPEG, WEBP
Maximum size: 4096x4096 pixels

## File Structure

```
C:\Ziggie\integrations\meshy\
    __init__.py          # Module exports
    config.py            # Configuration management
    meshy_client.py      # Core API wrapper
    image_to_3d.py       # High-level conversion
    batch_processor.py   # Batch processing
    meshy-config.json    # Config template
    requirements.txt     # Dependencies
    n8n-workflow-meshy.json  # n8n workflow
    README.md            # This file
```

## Security Notes

1. **Never commit API keys** - Use AWS Secrets Manager or environment variables
2. **Rotate keys regularly** - If exposed, regenerate immediately
3. **Use least privilege** - Only grant necessary AWS permissions

## License

Part of the Ziggie AI Game Development Ecosystem.

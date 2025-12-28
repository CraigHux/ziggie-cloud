# Ziggie n8n Workflows - Game Asset Generation

> **Purpose**: Automated game asset generation pipeline for MeowPing RTS
> **n8n Instance**: VPS port 5678
> **ComfyUI**: localhost:8188 (or MCP server)
> **S3 Bucket**: ziggie-assets-prod (eu-north-1)

---

## Workflow Overview

| Workflow | File | Endpoint | Purpose |
|----------|------|----------|---------|
| Asset Generation Pipeline | `asset-generation-pipeline.json` | `/generate-asset` | Single asset generation |
| Batch Generation | `batch-generation.json` | `/batch-generate` | Multiple asset processing |
| Quality Check | `quality-check.json` | `/quality-check` | Asset validation |

---

## 1. Asset Generation Pipeline

### Workflow Structure

```
Webhook Trigger (POST /generate-asset)
    │
    ▼
Validate Input
    │ - Validates asset_type, prompt, faction_color, output_format
    │ - Enhances prompt based on asset type
    │ - Generates unique asset ID
    ▼
Generate with ComfyUI (HTTP POST to :8188/prompt)
    │ - Sends SDXL workflow
    │ - Uses enhanced prompt with negative prompt
    ▼
Process ComfyUI Response
    │ - Extracts prompt_id
    │ - Prepares for polling
    ▼
Wait for Generation (5 seconds)
    │
    ▼
Check Generation Status (GET /history/{prompt_id})
    │
    ▼
Extract Output
    │ - Parses history response
    │ - Gets output image path
    ▼
Download Image (from ComfyUI)
    │
    ▼
Post-Process Image
    │ - Applies target dimensions per asset type
    │ - Prepares S3 metadata
    ▼
Upload to S3
    │ - Uploads to ziggie-assets-prod
    │ - Applies tags and metadata
    ▼
Build Response
    │ - Generates final asset URL
    │ - Compiles metadata
    ▼
┌─────────────────┐
│                 │
▼                 ▼
Discord Notify    Webhook Response
```

### API Request

**Endpoint**: `POST http://your-vps:5678/webhook/generate-asset`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "asset_type": "unit_sprite",
  "prompt": "Cat warrior archer with bow and quiver, medieval fantasy style",
  "faction_color": "blue",
  "output_format": "png",
  "width": 1024,
  "height": 1024,
  "negative_prompt": "blurry, low quality, distorted"
}
```

**Parameters**:

| Parameter | Type | Required | Default | Values |
|-----------|------|----------|---------|--------|
| `asset_type` | string | Yes | - | `unit_sprite`, `building`, `terrain_tile`, `hero`, `effect`, `prop` |
| `prompt` | string | Yes | - | Descriptive text for generation |
| `faction_color` | string | No | `neutral` | `red`, `blue`, `green`, `gold`, `neutral` |
| `output_format` | string | No | `png` | `png`, `webp`, `jpg` |
| `width` | number | No | 1024 | Image width in pixels |
| `height` | number | No | 1024 | Image height in pixels |
| `negative_prompt` | string | No | (default) | What to avoid in generation |

**Response**:
```json
{
  "success": true,
  "assetId": "unit_sprite_1703683200000_abc123def",
  "assetType": "unit_sprite",
  "factionColor": "blue",
  "assetUrl": "https://ziggie-assets-prod.s3.eu-north-1.amazonaws.com/game-assets/unit_sprite/blue/unit_sprite_1703683200000_abc123def.png",
  "s3Location": {
    "bucket": "ziggie-assets-prod",
    "key": "game-assets/unit_sprite/blue/unit_sprite_1703683200000_abc123def.png",
    "region": "eu-north-1"
  },
  "metadata": {
    "originalPrompt": "Cat warrior archer with bow and quiver, medieval fantasy style",
    "enhancedPrompt": "Cat warrior archer with bow and quiver, medieval fantasy style, isometric view, game sprite, transparent background, pixel perfect edges",
    "dimensions": {
      "original": { "width": 1024, "height": 1024 },
      "target": { "width": 128, "height": 128 }
    },
    "format": "png",
    "generatedAt": "2024-12-27T10:00:00.000Z",
    "completedAt": "2024-12-27T10:00:30.000Z"
  },
  "pipeline": {
    "comfyuiPromptId": "abc123-def456-ghi789",
    "processingTime": 30000
  }
}
```

### cURL Example

```bash
curl -X POST http://your-vps:5678/webhook/generate-asset \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "unit_sprite",
    "prompt": "Cat warrior archer with bow and quiver, medieval fantasy style",
    "faction_color": "blue",
    "output_format": "png"
  }'
```

---

## 2. Batch Generation Workflow

### Workflow Structure

```
Batch Webhook (POST /batch-generate)
    │
    ▼
Validate Batch
    │ - Validates assets array (max 50)
    │ - Generates batch ID
    ▼
Split Assets (SplitOut node)
    │ - Splits into individual items
    ▼
Prepare Asset (per item)
    │ - Enhances prompt
    │ - Generates asset ID
    ▼
Call Generation Pipeline (batched HTTP)
    │ - Calls /generate-asset for each
    │ - Batches: 3 concurrent, 5s interval
    ▼
Collect Result
    │
    ▼
Aggregate Results
    │ - Combines all results
    ▼
Build Summary
    │ - Calculates success rate
    │ - Lists successful/failed assets
    ▼
Should Notify?
    │
    ├─► Discord Batch Notification (if enabled)
    │
    ▼
Batch Response
```

### API Request

**Endpoint**: `POST http://your-vps:5678/webhook/batch-generate`

**Request Body**:
```json
{
  "assets": [
    {
      "asset_type": "unit_sprite",
      "prompt": "Cat warrior archer",
      "faction_color": "blue"
    },
    {
      "asset_type": "unit_sprite",
      "prompt": "Cat knight with sword",
      "faction_color": "red"
    },
    {
      "asset_type": "building",
      "prompt": "Medieval barracks",
      "faction_color": "neutral"
    }
  ],
  "priority": "normal",
  "notify_on_complete": true
}
```

**Response**:
```json
{
  "batchId": "batch_1703683200000_xyz789",
  "summary": {
    "total": 3,
    "successful": 3,
    "failed": 0,
    "successRate": "100.0%"
  },
  "successfulAssets": [
    {
      "assetId": "unit_sprite_1703683200001_abc",
      "assetType": "unit_sprite",
      "assetUrl": "https://..."
    }
  ],
  "failedAssets": [],
  "completedAt": "2024-12-27T10:05:00.000Z"
}
```

### cURL Example

```bash
curl -X POST http://your-vps:5678/webhook/batch-generate \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"asset_type": "unit_sprite", "prompt": "Cat archer", "faction_color": "blue"},
      {"asset_type": "unit_sprite", "prompt": "Cat knight", "faction_color": "red"}
    ],
    "notify_on_complete": true
  }'
```

---

## 3. Quality Check Workflow

### Workflow Structure

```
Quality Check Webhook (POST /quality-check)
    │
    ▼
Validate QC Input
    │ - Accepts asset_url or s3_key
    │ - Sets quality threshold
    ▼
Download Asset
    │
    ▼
Analyze Quality
    │ - Checks dimensions, file size, format
    │ - Checks transparency support
    │ - Calculates quality score
    ▼
Meets Threshold?
    │
    ├─► Build Pass Response (status: PASSED)
    │
    └─► Build Fail Response (status: FAILED, recommendations)
    │
    ▼
Merge Responses
    │
    ├─► QC Response
    │
    └─► Discord QC Notification
```

### API Request

**Endpoint**: `POST http://your-vps:5678/webhook/quality-check`

**Request Body**:
```json
{
  "asset_url": "https://ziggie-assets-prod.s3.eu-north-1.amazonaws.com/game-assets/unit_sprite/blue/asset123.png",
  "asset_type": "unit_sprite",
  "quality_threshold": "AA",
  "expected_dimensions": { "width": 128, "height": 128 },
  "check_transparency": true,
  "check_edges": true,
  "check_artifacts": true
}
```

**Or with S3 key**:
```json
{
  "s3_key": "game-assets/unit_sprite/blue/asset123.png",
  "s3_bucket": "ziggie-assets-prod",
  "asset_type": "unit_sprite",
  "quality_threshold": "AA"
}
```

**Response (PASSED)**:
```json
{
  "checkId": "qc_1703683200000_abc",
  "status": "PASSED",
  "assetUrl": "https://...",
  "assetType": "unit_sprite",
  "qualityRating": "AAA",
  "qualityScore": 100.0,
  "meetsThreshold": true,
  "threshold": "AA",
  "checks": {
    "dimensions": { "passed": true, "message": "..." },
    "fileSize": { "passed": true, "message": "..." },
    "format": { "passed": true, "message": "..." },
    "transparency": { "passed": true, "message": "..." }
  },
  "recommendation": "Asset is production-ready",
  "completedAt": "2024-12-27T10:00:00.000Z"
}
```

**Response (FAILED)**:
```json
{
  "checkId": "qc_1703683200000_xyz",
  "status": "FAILED",
  "qualityRating": "A",
  "qualityScore": 50.0,
  "meetsThreshold": false,
  "threshold": "AA",
  "failedChecks": [
    { "check": "transparency", "message": "JPEG does not support transparency" }
  ],
  "recommendations": [
    "Regenerate as PNG for transparency support"
  ]
}
```

---

## Import Instructions

### Step 1: Access n8n

1. Open browser: `http://your-vps:5678`
2. Login to n8n dashboard

### Step 2: Import Workflows

**Via UI**:
1. Click "Workflows" in sidebar
2. Click "Add workflow" > "Import from file"
3. Select each JSON file:
   - `asset-generation-pipeline.json`
   - `batch-generation.json`
   - `quality-check.json`

**Via n8n CLI** (if available):
```bash
n8n import:workflow --input=/path/to/asset-generation-pipeline.json
n8n import:workflow --input=/path/to/batch-generation.json
n8n import:workflow --input=/path/to/quality-check.json
```

### Step 3: Configure Credentials

**AWS S3 Credentials**:
1. Go to Settings > Credentials
2. Click "Add Credential" > "S3"
3. Configure:
   - Name: `Ziggie AWS S3`
   - Region: `eu-north-1`
   - Access Key ID: (from AWS Secrets Manager)
   - Secret Access Key: (from AWS Secrets Manager)

**Environment Variables**:
Add to n8n environment:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
```

### Step 4: Activate Workflows

1. Open each imported workflow
2. Click "Activate" toggle in top-right
3. Verify webhook URLs are registered

### Step 5: Test Workflows

```bash
# Test single generation
curl -X POST http://your-vps:5678/webhook/generate-asset \
  -H "Content-Type: application/json" \
  -d '{"asset_type": "unit_sprite", "prompt": "Test cat warrior"}'

# Test quality check
curl -X POST http://your-vps:5678/webhook/quality-check \
  -H "Content-Type: application/json" \
  -d '{"asset_url": "https://example.com/test.png", "quality_threshold": "A"}'
```

---

## Integration with MCP ComfyUI Server

The workflows are designed to work with the existing MCP ComfyUI server. The integration happens in two ways:

### Option 1: Direct HTTP (Current Implementation)

The workflows call ComfyUI directly via HTTP:
- **Endpoint**: `http://localhost:8188/prompt`
- **History**: `http://localhost:8188/history/{prompt_id}`
- **Images**: `http://localhost:8188/view?filename=...`

### Option 2: MCP Hub Integration (Alternative)

For MCP-aware integration, modify the ComfyUI node to use the hub:

```javascript
// Replace HTTP Request node with Code node calling MCP
const hubResponse = await fetch('http://mcp-gateway:8080/hub/route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    backend: 'comfyui',
    tool: 'comfyui_generate_sprite',
    arguments: {
      prompt: enhancedPrompt,
      width: width,
      height: height,
      negative_prompt: negativePrompt
    }
  })
});
```

### ComfyUI Workflow Customization

The default workflow uses SDXL base. To use custom workflows:

1. Save your ComfyUI workflow as API format (Save > Save (API Format))
2. Place in `C:\Ziggie\n8n-workflows\comfyui-templates\`
3. Modify the "Generate with ComfyUI" node to load template

---

## Quality Rating System

| Rating | Score | Production Use |
|--------|-------|----------------|
| **AAA** | 90-100% | Immediate production |
| **AA** | 75-89% | Production with minor work |
| **A** | 50-74% | Requires processing |
| **Poor** | <50% | Regenerate or reference only |

### Quality Checks Performed

| Check | Description | Weight |
|-------|-------------|--------|
| Dimensions | Matches expected size | 25% |
| File Size | 1KB < size < 10MB | 25% |
| Format | PNG/WebP/JPEG | 25% |
| Transparency | Alpha channel for sprites | 25% |

---

## Asset Type Target Sizes

| Asset Type | Target Dimensions | Use Case |
|------------|-------------------|----------|
| `unit_sprite` | 128x128 | Game units |
| `building` | 256x256 | Structures |
| `terrain_tile` | 64x64 | Tilemap cells |
| `hero` | 256x256 | Hero characters |
| `effect` | 128x128 | VFX sprites |
| `prop` | 128x128 | Environmental props |

---

## S3 Path Structure

```
ziggie-assets-prod/
└── game-assets/
    ├── unit_sprite/
    │   ├── red/
    │   ├── blue/
    │   ├── green/
    │   ├── gold/
    │   └── neutral/
    ├── building/
    │   └── [faction]/
    ├── terrain_tile/
    │   └── [faction]/
    ├── hero/
    │   └── [faction]/
    ├── effect/
    │   └── [faction]/
    └── prop/
        └── [faction]/
```

---

## Troubleshooting

### ComfyUI Connection Failed
```
Error: ECONNREFUSED 127.0.0.1:8188
```
**Solution**: Ensure ComfyUI is running on port 8188

### S3 Upload Failed
```
Error: Access Denied
```
**Solution**: Verify AWS credentials in n8n are correct and have s3:PutObject permission

### Generation Timeout
```
Error: Timeout waiting for generation
```
**Solution**: Increase wait time in "Wait for Generation" node (default: 5s may be too short for complex prompts)

### Discord Notification Failed
```
Error: 401 Unauthorized
```
**Solution**: Verify DISCORD_WEBHOOK_URL environment variable is set correctly

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-27 | Initial release with 3 workflows |

---

*Created by Ziggie Automation Agent*
*Part of the Ziggie AI Ecosystem*

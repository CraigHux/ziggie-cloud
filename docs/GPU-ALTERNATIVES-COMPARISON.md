# GPU Alternatives Comparison for ComfyUI

> **Created**: 2025-12-28 (Session M)
> **Context**: AWS GPU quota pending approval (24-48 hours)
> **Purpose**: Evaluate alternatives for immediate GPU access

---

## Quick Comparison Matrix

| Feature | RunPod.io | Google Colab (Free) | Meshy.ai API |
|---------|-----------|---------------------|--------------|
| **Best For** | Production workloads | Quick testing | Image-to-3D only |
| **GPU Access** | RTX 4090, A100, H100 | T4 (15GB VRAM) | Cloud (abstracted) |
| **Pricing** | $0.34-3.99/hr | Free (limited) | $20-120/mo credits |
| **ComfyUI Support** | Native templates | Manual setup | N/A (API only) |
| **Reliability** | High (99%+ uptime) | Variable | High |
| **API Access** | Yes (serverless) | No | Yes |
| **Idle Costs** | Per-second billing | Free | No idle costs |
| **Setup Time** | 5 minutes | 10-15 minutes | Immediate |

---

## 1. RunPod.io (RECOMMENDED)

### Pricing Tiers (2025)

| GPU | VRAM | Price/Hour | Use Case |
|-----|------|------------|----------|
| RTX 4090 | 24GB | $0.34-0.69 | SDXL, ComfyUI |
| RTX 3090 | 24GB | $0.50-0.69 | Testing, development |
| A100 | 40-80GB | $1.19-1.99 | Large models, training |
| H100 | 80GB | $1.99-3.99 | Maximum performance |

### Key Benefits
- **60-80% cheaper than AWS** for comparable GPUs
- **Per-second billing** - no wasted costs
- **No egress fees** - unlike AWS
- **50+ pre-built templates** including ComfyUI + Flux
- **Serverless option** - API that scales automatically

### ComfyUI Deployment
```bash
# One-click template in RunPod console
# Search: "ComfyUI with Flux"
# Recommended: RTX 4090 (24GB) for optimal performance
```

### Cost Estimate for Ziggie
| Usage Pattern | Monthly Cost |
|---------------|--------------|
| 2 hours/day | ~$20-40 |
| 4 hours/day | ~$40-80 |
| On-demand (50 images/week) | ~$5-15 |

**Source**: [RunPod Pricing](https://www.runpod.io/pricing)

---

## 2. Google Colab (Free Tier)

### Specifications
- **GPU**: Tesla T4 (15GB VRAM usable)
- **Performance**: ~7 years old, comparable to RTX 2070
- **Cost**: Free (with limitations)

### Limitations

| Limitation | Impact |
|------------|--------|
| 90-min idle timeout | Disconnects without interaction |
| 12-hour max runtime | Session dies, work lost |
| GPU not guaranteed | Sometimes K80 (slower) instead of T4 |
| Startup time | 5-10 minutes to load ComfyUI |
| No persistent storage | Files deleted on disconnect |

### When to Use
- Quick testing and prototyping
- Learning ComfyUI workflows
- When budget is $0
- Non-production use cases

### ComfyUI Setup
```python
# In Colab notebook
!git clone https://github.com/comfyanonymous/ComfyUI
%cd ComfyUI
!pip install -r requirements.txt
!python main.py --listen 0.0.0.0 --port 8188
```

### Keep-Alive Script (Browser Console)
```javascript
function ClickConnect() {
    document.querySelector("#top-toolbar > colab-connect-button")
        ?.shadowRoot?.querySelector("#connect")?.click();
}
setInterval(ClickConnect, 60000);
```

**Source**: [ComfyUI on Colab Guide](https://stable-diffusion-art.com/comfyui-colab/)

---

## 3. Meshy.ai API

### Pricing Tiers

| Tier | Price | Credits/Month | API Access |
|------|-------|---------------|------------|
| Free | $0 | 200 | No |
| Pro | $20/mo | 1,000 | Yes |
| Max | $120/mo | 4,000 | Yes |

### Key Features
- **Image-to-3D conversion** (primary use case)
- ~30 seconds per model generation
- 8 free retries for failed conversions
- Private asset storage (Max tier)

### API Usage
```python
import requests

# Image to 3D conversion
response = requests.post(
    "https://api.meshy.ai/v1/image-to-3d",
    headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
    files={"file": open("concept.png", "rb")}
)
task_id = response.json()["result"]

# Poll for completion
# Returns GLB/FBX/OBJ model
```

### Best For
- 2D concept art → 3D models pipeline
- Batch 3D asset generation
- When you don't need ComfyUI (just 3D conversion)

**Source**: [Meshy.ai Pricing](https://www.meshy.ai/pricing)

---

## Recommendation for Ziggie

### Immediate Actions (While AWS Quota Pending)

1. **For ComfyUI Image Generation**: Use **RunPod.io**
   - RTX 4090 template: $0.34-0.69/hr
   - One-click ComfyUI deployment
   - Pay only for what you use

2. **For Image-to-3D Pipeline**: Use **Meshy.ai**
   - Already integrated in n8n workflows
   - $20/mo Pro tier = 1,000 conversions
   - API-ready for automation

3. **For Testing/Learning**: Use **Google Colab**
   - Free T4 GPU
   - Good for workflow development
   - Not for production

### Cost Comparison (Monthly)

| Scenario | AWS (when approved) | RunPod | Meshy |
|----------|---------------------|--------|-------|
| 2 hrs/day ComfyUI | ~$40 (spot) | ~$25 | N/A |
| 100 3D conversions | N/A | N/A | $20 |
| Combined pipeline | ~$50-70 | ~$30-50 | $20 |

### Hybrid Strategy (Recommended)

```text
ComfyUI 2D Generation (RunPod)
         ↓
   Upload to S3
         ↓
  Meshy.ai API (3D)
         ↓
   Download GLB
         ↓
Blender 8-dir Render (VPS)
         ↓
   Game-Ready Sprites
```

---

## Quick Start Commands

### RunPod Setup
```bash
# 1. Create account at runpod.io
# 2. Add payment method
# 3. Deploy template: "ComfyUI with Flux"
# 4. Connect via web interface
```

### Meshy.ai Setup
```bash
# 1. Sign up at meshy.ai
# 2. Subscribe to Pro ($20/mo)
# 3. Get API key from dashboard
# 4. Store in AWS Secrets Manager:
aws secretsmanager create-secret \
  --name ziggie/meshy-api-key \
  --secret-string "your-api-key" \
  --region eu-north-1
```

### Google Colab Setup
```bash
# 1. Open: colab.research.google.com
# 2. Runtime → Change runtime type → GPU (T4)
# 3. Run ComfyUI setup cells
# 4. Use pinggy.io for public URL access
```

---

## Integration with Ziggie Ecosystem

### n8n Workflow Updates

```javascript
// Add to n8n workflow: Asset Generation
{
  "nodes": [
    {
      "name": "RunPod ComfyUI",
      "type": "HTTP Request",
      "url": "https://api.runpod.ai/v2/...",
      "method": "POST"
    },
    {
      "name": "Meshy 3D Conversion",
      "type": "HTTP Request",
      "url": "https://api.meshy.ai/v1/image-to-3d",
      "method": "POST"
    }
  ]
}
```

### When AWS Quota Approved

Once AWS GPU quota is approved (4 vCPUs for g4dn.xlarge):
1. AWS EC2 becomes primary for consistency
2. RunPod as backup/overflow
3. Meshy.ai continues for 3D conversion
4. Lambda auto-shutdown keeps costs low

---

**Document Status**: Complete
**Next Steps**:
1. Create RunPod account
2. Subscribe to Meshy Pro ($20/mo)
3. Test Colab notebook for development
4. Await AWS quota approval

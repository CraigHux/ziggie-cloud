# Pipeline Stages 1-3 Cloud Testing Guide

> **Created**: 2025-12-29 (Session M)
> **Purpose**: Manual testing of asset pipeline with cloud GPU services
> **Status**: Ready for execution when cloud services available

---

## Quick Reference

| Stage | Service | Cost | URL | Test Asset |
|-------|---------|------|-----|------------|
| 1 | RunPod ComfyUI | $0.34-0.69/hr | https://runpod.io | N/A (generation) |
| 2 | BRIA RMBG | Free | https://huggingface.co/spaces/briaai/BRIA-RMBG-2.0 | salvage_warrior_v2.jpg |
| 3 | Colab Real-ESRGAN | Free | See notebook below | salvage_warrior_v1_nobg.png |

---

## Test Assets Available

### Raw Concepts (with backgrounds) - Stage 2 Test Candidates

```
C:\Ziggie\assets\concepts\
├── salvage_warrior_v1.jpg          ← PRIMARY TEST ASSET
├── salvage_warrior_v2.jpg
├── sand_vanguard_warrior_v3.jpg
├── cinder_forger_warrior_v3.jpg
├── cryo_sentinal_warrior_v3.jpg
├── bio-hunters_warrior_v3.jpg
├── signal_hackers_warrior_v3.jpg
├── sand_vanguard_overclock_berserker_v3.jpg
├── cinder_forger_overclock_berserker_v3.jpg
├── cryo_sentinal_overclock_berserker_v3.jpg
├── bio-hunters_overclock_berserker_v3.jpg
├── signal_hackers_overclock_berserker_v3.jpg
└── Novasphereai_SAND_VANGUARD_*.jpg (3 upscaled variants)
```

### Processed Sprites (no background) - Stage 3 Test Candidates

```
C:\Ziggie\assets\concepts\
└── salvage_warrior_v1_nobg.png     ← STAGE 3 TEST ASSET
```

---

## Stage 1: 2D Generation with RunPod ComfyUI

### Setup (One-time, ~5 minutes)

1. **Create RunPod Account**
   - Go to: https://www.runpod.io/
   - Sign up with email
   - Add payment method ($10 minimum)

2. **Deploy ComfyUI Template**
   - Click "Templates" in dashboard
   - Search: "ComfyUI with Flux" or "ComfyUI SDXL"
   - Select GPU: RTX 4090 (24GB) - $0.34-0.69/hr
   - Click "Deploy"
   - Wait 2-3 minutes for startup

3. **Access ComfyUI**
   - Click "Connect" on your pod
   - Open the HTTP port (usually 8188)
   - ComfyUI interface loads in browser

### Test Prompt (MeowPing RTS Style)

```
Cat warrior archer, medieval fantasy style, wearing leather armor,
holding bow and arrow, isometric game sprite view, blue screen
background (#0000FF), high detail, stylized cartoon, game asset,
transparent background ready, 45-degree angle, full body shot
```

**Negative Prompt:**
```
blurry, low quality, text, watermark, realistic, photorealistic,
multiple characters, cropped, partial body
```

### Expected Results

| Metric | Target | Acceptable |
|--------|--------|------------|
| Generation Time | <15 seconds | <30 seconds |
| Resolution | 1024x1024 | 512x512+ |
| Style Match | MeowPing cartoon | Stylized |
| Background | Clean blue (#0000FF) | Solid color |

### Cost Estimate

| Usage | Time | Cost |
|-------|------|------|
| 10 test images | ~5 min | ~$0.06 |
| 50 production images | ~25 min | ~$0.30 |
| 1 hour session | 60 min | $0.34-0.69 |

---

## Stage 2: Background Removal with BRIA RMBG

### Setup (No account required)

1. **Open BRIA RMBG Space**
   - Go to: https://huggingface.co/spaces/briaai/BRIA-RMBG-2.0
   - No login required for basic use

### Test Procedure

1. **Upload Test Asset**
   - Click "Upload Image"
   - Select: `C:\Ziggie\assets\concepts\salvage_warrior_v2.jpg`

2. **Process**
   - Click "Remove Background"
   - Wait 5-15 seconds

3. **Download Result**
   - Right-click result → Save as PNG
   - Save to: `C:\Ziggie\assets\processed\salvage_warrior_v2_nobg.png`

### Expected Results

| Metric | Target | Acceptable |
|--------|--------|------------|
| Processing Time | <10 seconds | <30 seconds |
| Edge Quality | Clean, no artifacts | Minor aliasing |
| Character Complete | 100% preserved | 95%+ preserved |
| Transparency | Full alpha channel | Solid background removed |

### Alternative Services (if BRIA down)

| Service | URL | Quality |
|---------|-----|---------|
| Remove.bg | https://www.remove.bg/ | Excellent (50 free) |
| PhotoRoom | https://www.photoroom.com/background-remover | Good |
| Erase.bg | https://www.erase.bg/ | Good |

---

## Stage 3: Upscaling with Google Colab

### Setup (Google account required)

1. **Open Colab Notebook**
   - Go to: https://colab.research.google.com/
   - Sign in with Google account

2. **Create New Notebook**
   - File → New notebook
   - Runtime → Change runtime type → GPU (T4)

### Upscaling Code (Copy-paste into Colab)

```python
# Cell 1: Install Real-ESRGAN
!pip install realesrgan

# Cell 2: Import and setup
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from PIL import Image
import numpy as np

# Download model
!wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights/

# Initialize upscaler
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(
    scale=4,
    model_path='weights/RealESRGAN_x4plus.pth',
    model=model,
    tile=0,
    tile_pad=10,
    pre_pad=0,
    half=True
)

# Cell 3: Upload and process
from google.colab import files

# Upload your image
uploaded = files.upload()
input_path = list(uploaded.keys())[0]

# Read image
img = Image.open(input_path).convert('RGB')
img_np = np.array(img)

# Upscale
output, _ = upsampler.enhance(img_np, outscale=4)

# Save and download
output_img = Image.fromarray(output)
output_path = f"upscaled_{input_path}"
output_img.save(output_path)
files.download(output_path)

print(f"Upscaled from {img.size} to {output_img.size}")
```

### Test Procedure

1. **Run Cells 1-2** (one-time setup, ~2 min)
2. **Run Cell 3**
   - Upload: `salvage_warrior_v1_nobg.png`
   - Wait for processing (~10-30 seconds)
   - Download result automatically

### Expected Results

| Metric | Target | Acceptable |
|--------|--------|------------|
| Scale Factor | 4x | 2x+ |
| Processing Time | <30 seconds | <60 seconds |
| Detail Enhancement | Sharp edges | Visible improvement |
| Artifact-free | No hallucinations | Minimal artifacts |

### Keep-Alive Script (for long sessions)

Paste in browser console (F12 → Console):

```javascript
function ClickConnect() {
    console.log("Keeping session alive...");
    document.querySelector("#top-toolbar > colab-connect-button")
        ?.shadowRoot?.querySelector("#connect")?.click();
}
setInterval(ClickConnect, 60000);
```

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Google Chrome browser open
- [ ] Test assets copied to accessible location
- [ ] RunPod account created (optional - Stage 1)
- [ ] Google account signed in (Stage 3)

### Stage 1: 2D Generation (RunPod)
- [ ] Pod deployed with ComfyUI
- [ ] Workflow loaded (txt2img)
- [ ] Test prompt entered
- [ ] Image generated successfully
- [ ] Quality acceptable (AAA/AA rating)
- [ ] Pod stopped to avoid charges
- [ ] Screenshot saved

### Stage 2: Background Removal (BRIA)
- [ ] BRIA space loaded
- [ ] Test image uploaded (salvage_warrior_v2.jpg)
- [ ] Background removed successfully
- [ ] Edge quality checked
- [ ] Result downloaded as PNG
- [ ] Alpha channel verified

### Stage 3: Upscaling (Colab)
- [ ] Notebook created with GPU runtime
- [ ] Real-ESRGAN installed
- [ ] Model weights downloaded
- [ ] Test image uploaded (salvage_warrior_v1_nobg.png)
- [ ] 4x upscale completed
- [ ] Detail enhancement verified
- [ ] Result downloaded

### Post-Test
- [ ] All test results saved to `C:\Ziggie\assets\test-results\`
- [ ] Quality ratings assigned
- [ ] GAP-055 updated in tracking document
- [ ] Pipeline documentation updated

---

## Troubleshooting

### RunPod Issues

| Issue | Solution |
|-------|----------|
| Pod won't start | Check GPU availability, try different region |
| ComfyUI not loading | Wait 3-5 min, check logs in dashboard |
| Out of VRAM | Use smaller model or reduce batch size |
| High costs | Stop pod immediately after testing |

### BRIA Issues

| Issue | Solution |
|-------|----------|
| Space not loading | Wait 30 sec, refresh page |
| Queue too long | Try at off-peak hours (UTC morning) |
| Poor edge quality | Use Remove.bg as fallback |

### Colab Issues

| Issue | Solution |
|-------|----------|
| No GPU available | Wait 5 min, try again |
| Session disconnected | Run keep-alive script |
| CUDA out of memory | Restart runtime, reduce tile size |
| 12-hour limit | Save progress to Drive, restart |

---

## Success Criteria

### Stage 1 PASS
- [x] Generated at least 1 image
- [x] Resolution ≥ 512x512
- [x] Style matches MeowPing aesthetic
- [x] Cost ≤ $1 for test session

### Stage 2 PASS
- [x] Background removed cleanly
- [x] Character edges preserved
- [x] PNG with alpha channel
- [x] Processing time ≤ 30 seconds

### Stage 3 PASS
- [x] 4x upscale achieved
- [x] Details enhanced, not blurred
- [x] No visible artifacts
- [x] Processing time ≤ 60 seconds

---

## Next Steps After Testing

1. **If All Stages PASS**:
   - Update GAP-055 status to RESOLVED
   - Proceed to Stage 4 (2D-to-3D with Meshy.ai)
   - Begin batch processing of unit concepts

2. **If Stage Fails**:
   - Document failure reason
   - Try alternative service from backup list
   - Escalate if persistent failures

3. **Production Readiness**:
   - Calculate cost per 100 assets
   - Document optimal settings
   - Create batch processing scripts

---

## Cost Summary

| Stage | Service | Test Cost | 100 Assets |
|-------|---------|-----------|------------|
| 1 | RunPod (5 min) | ~$0.05 | ~$5 |
| 2 | BRIA | Free | Free |
| 3 | Colab | Free | Free |
| **Total** | | **~$0.05** | **~$5** |

---

**Document Status**: Ready for manual execution
**Created By**: Session M (2025-12-29)
**Related**: END-TO-END-ASSET-CREATION-PIPELINE.md, GPU-ALTERNATIVES-COMPARISON.md

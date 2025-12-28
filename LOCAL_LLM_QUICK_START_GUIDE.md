# LOCAL LLM QUICK START GUIDE
## Get Ollama Running in 15 Minutes

**Target Audience:** Ziggie Team
**Time Required:** 15-30 minutes
**Prerequisites:** Docker installed, 8GB+ RAM
**Cost:** $0

---

## STEP 1: Deploy Ollama (5 minutes)

### Option A: Docker (Recommended)

**With GPU (NVIDIA):**
```bash
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  --restart unless-stopped \
  ollama/ollama:latest
```

**Without GPU (CPU only, slower but works):**
```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  --restart unless-stopped \
  ollama/ollama:latest
```

### Option B: Windows Installer

1. Download: https://ollama.com/download
2. Run installer
3. Ollama will start automatically on port 11434

**Verify it's running:**
```bash
curl http://localhost:11434/api/tags
```

Expected output: `{"models":[]}`

---

## STEP 2: Pull Models (5-10 minutes)

**Essential models for Ziggie:**

```bash
# General purpose (FAST, 4.7GB download)
docker exec ollama ollama pull llama3.2

# Technical content (GOOD for code/workflows, 4.4GB)
docker exec ollama ollama pull qwen2.5:7b

# Ultra-fast (for simple tasks, 2.3GB)
docker exec ollama ollama pull phi3
```

**Download times:**
- Fast internet (100 Mbps): ~3-5 minutes per model
- Slow internet (10 Mbps): ~10-20 minutes per model

**Storage used:** ~11GB total for all three models

---

## STEP 3: Test Inference (2 minutes)

**Test 1: Simple generation**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Explain what ComfyUI is in one sentence."
}'
```

**Test 2: Chat mode**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "user", "content": "What is a diffusion model?"}
  ]
}'
```

**Test 3: Performance check**
```bash
time curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Count from 1 to 10."
}'
```

**Expected response time:**
- With GPU: 1-3 seconds
- Without GPU (CPU): 10-30 seconds

---

## STEP 4: Integrate with Ziggie (5-10 minutes)

### Update requirements.txt

**File:** `C:\Ziggie\control-center\backend\requirements.txt`

Add this line:
```
aiohttp==3.9.1
```

Install:
```bash
cd C:\Ziggie\control-center\backend
pip install -r requirements.txt
```

### Add LLM Service

**File:** `C:\Ziggie\control-center\backend\services\llm_service.py`

Copy the full LLM service code from the main strategy document, or use this minimal version:

```python
"""Simple Local LLM Service"""
import aiohttp

class LLMService:
    def __init__(self, url="http://localhost:11434"):
        self.url = url
        self.model = "llama3.2"

    async def generate(self, prompt: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            ) as response:
                result = await response.json()
                return {
                    "response": result["response"],
                    "model": self.model,
                    "cost": 0.0
                }

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/api/tags") as response:
                    return response.status == 200
        except:
            return False
```

### Test Integration

**File:** `C:\Ziggie\control-center\backend\test_local_llm.py`

```python
"""Test local LLM integration"""
import asyncio
import sys
sys.path.append('services')
from llm_service import LLMService

async def main():
    llm = LLMService()

    # Check health
    healthy = await llm.health_check()
    print(f"Ollama status: {'✅ Available' if healthy else '❌ Unavailable'}")

    if not healthy:
        print("Make sure Ollama is running: docker ps | grep ollama")
        return

    # Test generation
    print("\nTesting generation...")
    result = await llm.generate("What is 2+2? Answer in one sentence.")

    print(f"\nResponse: {result['response']}")
    print(f"Model: {result['model']}")
    print(f"Cost: ${result['cost']}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run test:
```bash
cd C:\Ziggie\control-center\backend
python test_local_llm.py
```

Expected output:
```
Ollama status: ✅ Available

Testing generation...

Response: 2+2 equals 4.
Model: llama3.2
Cost: $0.0
```

---

## STEP 5: Enable in Knowledge Base (Optional, 5 minutes)

**Quick modification to test local LLM for KB analysis:**

**File:** `C:\Ziggie\knowledge-base\src\ai_analyzer.py`

Add at the top of the `analyze_transcript` method:

```python
def analyze_transcript(self, video_data, transcript_text, creator_info):
    """Analyze a video transcript and extract insights."""

    # TEST: Use local LLM for one video
    TEST_LOCAL = True  # Set to False to disable

    if TEST_LOCAL:
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": self._build_analysis_prompt(video_data, transcript_text, creator_info),
                    "stream": False
                },
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                insights = self._parse_response(result["response"])

                if insights:
                    insights['model'] = 'llama3.2 (local)'
                    insights['cost_usd'] = 0.0
                    print("✅ Used LOCAL LLM (saved ~$0.09)")
                    return insights

        except Exception as e:
            print(f"Local LLM failed, using cloud: {e}")

    # Original cloud implementation continues here...
```

Test:
```bash
cd C:\Ziggie\knowledge-base
python test_pipeline.py
```

---

## TROUBLESHOOTING

### Issue: "Connection refused" error

**Problem:** Ollama not running
**Solution:**
```bash
# Check if running
docker ps | grep ollama

# If not, start it
docker start ollama

# Check logs
docker logs ollama
```

### Issue: "Model not found"

**Problem:** Model not pulled yet
**Solution:**
```bash
# List pulled models
docker exec ollama ollama list

# Pull missing model
docker exec ollama ollama pull llama3.2
```

### Issue: Very slow responses (30+ seconds)

**Problem:** No GPU detected or VRAM full
**Solution:**
```bash
# Check GPU access
docker exec ollama nvidia-smi

# If no GPU, use smaller model
docker exec ollama ollama pull phi3

# Update code to use phi3 instead of llama3.2
```

### Issue: Out of memory

**Problem:** Model too large for available VRAM
**Solution:**
```bash
# Use quantized (smaller) model
docker exec ollama ollama pull llama3.2:q4_0  # 4-bit quantization

# Or use smaller model
docker exec ollama ollama pull phi3  # Only 2.3GB
```

### Issue: Windows Firewall blocking

**Problem:** Port 11434 blocked
**Solution:**
1. Windows Security > Firewall > Advanced settings
2. Inbound Rules > New Rule
3. Port > TCP > 11434
4. Allow connection

---

## QUICK REFERENCE

### Useful Commands

```bash
# List models
docker exec ollama ollama list

# Pull a new model
docker exec ollama ollama pull <model-name>

# Remove a model
docker exec ollama ollama rm <model-name>

# View logs
docker logs ollama -f

# Restart Ollama
docker restart ollama

# Stop Ollama
docker stop ollama

# Start Ollama
docker start ollama

# Check disk usage
docker exec ollama du -sh /root/.ollama/models

# Interactive chat (for testing)
docker exec -it ollama ollama run llama3.2
```

### API Endpoints

```bash
# Generate completion
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello"
}'

# Chat completion
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Hello"}]
}'

# List models
curl http://localhost:11434/api/tags

# Show model info
curl http://localhost:11434/api/show -d '{
  "name": "llama3.2"
}'
```

---

## NEXT STEPS

Once basic integration is working:

1. **Week 1:** Complete Phase 1 from main strategy doc
   - Integrate KB analyzer
   - Integrate agent spawner
   - Add NL query endpoint

2. **Week 2:** Add usage tracking
   - Track local vs. cloud usage
   - Calculate cost savings
   - Generate reports

3. **Week 3:** Implement smart routing
   - Route based on task complexity
   - Automatic fallback on errors
   - Quality monitoring

4. **Month 2+:** Advanced features
   - Fine-tune models
   - RAG with Ziggie knowledge
   - Multi-agent workflows

---

## MODEL RECOMMENDATIONS

**For Ziggie use cases:**

| Task | Best Model | Reason |
|------|------------|--------|
| KB video analysis | `qwen2.5:7b` | Great for technical content |
| L3 agent tasks | `llama3.2` | Fast, accurate, general |
| Quick summaries | `phi3` | Ultra-fast, good enough |
| Complex reasoning | `llama3.1:70b` | Needs 48GB VRAM but excellent |
| Code generation | `qwen2.5-coder:7b` | Specialized for code |

**Download any model:**
```bash
docker exec ollama ollama pull <model-name>
```

Browse all models: https://ollama.com/library

---

## PERFORMANCE EXPECTATIONS

**With GPU (RTX 3090/4090):**
- Llama 3.2 8B: ~40 tokens/second
- Qwen 2.5 7B: ~45 tokens/second
- Phi-3 Mini: ~80 tokens/second
- Response time: 1-3 seconds for short prompts

**Without GPU (CPU only):**
- Llama 3.2 8B: ~5 tokens/second
- Qwen 2.5 7B: ~5 tokens/second
- Phi-3 Mini: ~10 tokens/second
- Response time: 10-30 seconds for short prompts

**Recommendation:** If no GPU, use `phi3` model for acceptable speed

---

## COST SAVINGS ESTIMATE

**Assumptions:**
- 50 KB video analyses/month
- 100 agent tasks/month
- 80% routed to local LLM

**Savings:**
- KB analyses: 40 x $0.09 = $3.60/month
- Agent tasks: 80 x $0.01 = $0.80/month
- **Total saved: $4.40/month**
- **Yearly: $52.80**

**At higher scale (500 videos/month, 1000 agents/month):**
- Monthly savings: $44
- Yearly savings: $528
- **2-year savings: $1,056** (covers GPU cost!)

---

## SUCCESS CHECKLIST

- [ ] Ollama running and accessible on port 11434
- [ ] At least one model pulled (llama3.2 recommended)
- [ ] Test inference working (curl test passes)
- [ ] Python integration working (test_local_llm.py passes)
- [ ] Response time acceptable (<5 seconds with GPU, <30 seconds without)
- [ ] Quality acceptable (compare output to cloud API)
- [ ] Team understands how to use it

**Once all checked, you're ready for Phase 1 full integration!**

---

## RESOURCES

- **Ollama Docs:** https://ollama.com/docs
- **Model Library:** https://ollama.com/library
- **Discord Community:** https://discord.gg/ollama
- **GitHub:** https://github.com/ollama/ollama

**Questions?** Ask L1 Resource Manager in Ziggie Control Center

---

**HAPPY LOCAL LLM-ING!** 🚀

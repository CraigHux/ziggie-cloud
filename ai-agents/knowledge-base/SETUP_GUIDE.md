# KNOWLEDGE BASE PIPELINE - SETUP GUIDE

**Version:** 1.0 (Phase 2 Implementation)
**Created:** 2025-11-08
**Status:** Ready for Testing

---

## QUICK START (5 Minutes)

```bash
# 1. Install Python dependencies
cd C:\meowping-rts\ai-agents\knowledge-base
pip install -r requirements.txt

# 2. Configure API keys
copy .env.example .env
# Edit .env with your API keys (see below)

# 3. Test with a single video
python test_pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

---

## DETAILED SETUP

### Step 1: Install Dependencies

**Requirements:**
- Python 3.8+ (recommended: 3.11)
- pip (Python package manager)

**Install packages:**
```bash
cd C:\meowping-rts\ai-agents\knowledge-base
pip install -r requirements.txt
```

**What gets installed:**
- `yt-dlp` - YouTube video/transcript download
- `youtube-transcript-api` - Direct transcript extraction
- `anthropic` - Claude API client
- `google-api-python-client` - YouTube Data API (for video scanning)
- `python-dotenv` - Environment variable management
- And more... (see requirements.txt)

**Estimated install time:** 2-3 minutes

---

### Step 2: Get API Keys

You need **2 API keys** (1 critical, 1 optional):

#### ✅ CRITICAL: Anthropic Claude API

**Why:** Extracts insights from transcripts (core functionality)
**Cost:** ~$0.01 per video analysis (~$5/month for 50+ creators)

**How to get:**
1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

**Add to .env:**
```
ANTHROPIC_API_KEY=[REDACTED-ANTHROPIC-KEY]
```

---

#### ⚠️ OPTIONAL: YouTube Data API v3

**Why:** Automatic video discovery from channels (optional for testing)
**Cost:** FREE (10,000 requests/day quota)

**How to get:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create API Key
5. Copy the API key

**Add to .env:**
```
YOUTUBE_API_KEY=[REDACTED-GOOGLE-KEY]...your-key-here
```

**Note:** For testing with direct video URLs, this is optional. Only needed for automated channel scanning.

---

#### 🔧 OPTIONAL: OpenAI API (Whisper)

**Why:** Fallback transcription for videos without captions
**Cost:** ~$0.06 per hour of audio
**When needed:** Rarely (most YouTube videos have auto-captions)

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Add to .env: `OPENAI_API_KEY=sk-...`

---

### Step 3: Configure Environment

**Copy the template:**
```bash
copy .env.example .env
```

**Edit .env file:**
```ini
# Required
ANTHROPIC_API_KEY=[REDACTED-ANTHROPIC-KEY]

# Optional (for automated scanning)
YOUTUBE_API_KEY=[REDACTED-GOOGLE-KEY]...your-key-here

# Optional (for fallback transcription)
OPENAI_API_KEY=sk-...your-key-here

# Paths (default values should work)
KB_PATH=C:\meowping-rts\ai-agents\knowledge-base
LOG_PATH=C:\meowping-rts\ai-agents\knowledge-base\logs

# Settings (defaults are good for testing)
CONFIDENCE_THRESHOLD=80
MAX_VIDEOS_PER_SCAN=10
TEST_MODE=false
```

**Save and close .env**

---

### Step 4: Test the Pipeline

**Test with a single video:**

```bash
python test_pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**What it does:**
1. ✅ Validates configuration
2. ✅ Extracts transcript from video
3. ✅ Analyzes with Claude API
4. ✅ Extracts actionable insights
5. ✅ Saves results to temp/

**Expected output:**
```
============================================================
  KNOWLEDGE PIPELINE TEST
============================================================
Testing with video: https://www.youtube.com/watch?v=...

============================================================
Step 1: Configuration Check
============================================================
✓ Configuration valid

============================================================
Step 2: Extract Transcript
============================================================
✓ Transcript extracted using: youtube_auto
  Language: en
  Length: 12453 characters
  Preview: In this video, I'll show you...

============================================================
Step 3: AI Analysis (Claude API)
============================================================
✓ Insights extracted successfully

{
  "primary_topic": "ComfyUI Workflows",
  "key_insights": [
    "IP-Adapter locks both face and colors above 0.70",
    "For equipment changes, reduce to 0.40",
    ...
  ],
  "confidence_score": 92,
  ...
}

============================================================
PIPELINE TEST SUMMARY
============================================================
✓ All steps completed successfully!

Primary Topic: ComfyUI Workflows
Confidence: 92% (approved)
Target Agents: L1.2-character-pipeline, L2.2.1-workflow-optimizer...

✓ Results saved to: temp/test_results_VIDEO_ID.json

============================================================
NEXT STEPS
============================================================
1. Review the extracted insights above
2. If satisfied, the full pipeline can process 50+ creators
3. Run automated weekly scans
```

---

## TESTING RECOMMENDATIONS

### Test Videos by Creator:

**InstaSD (ComfyUI specialist):**
```bash
# Find a recent InstaSD video about ComfyUI
python test_pipeline.py "https://www.youtube.com/watch?v=INSTASD_VIDEO"
```

**Automation Avenue (n8n/DevOps):**
```bash
# Find a recent n8n automation tutorial
python test_pipeline.py "https://www.youtube.com/watch?v=AUTOMATION_VIDEO"
```

**Matthew Berman (AI news):**
```bash
# Find a recent AI news video
python test_pipeline.py "https://www.youtube.com/watch?v=MATTHEW_VIDEO"
```

---

## TROUBLESHOOTING

### Problem: "ANTHROPIC_API_KEY is required"

**Solution:**
```bash
1. Check .env file exists
2. Verify API key is correct (starts with sk-ant-)
3. No quotes around the key in .env
4. File is named .env (not .env.txt)
```

---

### Problem: "Failed to extract transcript"

**Possible causes:**
1. Video has no captions/transcript
2. Video is private or age-restricted
3. Invalid video URL

**Solutions:**
- Try a different video
- Verify video URL is correct
- Check if video has captions (CC button on YouTube)

---

### Problem: "YouTube API error"

**If you see YouTube API errors but have the key:**
- Check API quota (10,000/day limit)
- Verify YouTube Data API v3 is enabled in Google Cloud Console
- API key restrictions might be blocking it

**Workaround:**
- Test with direct video URLs (doesn't need YouTube API)
- Only automated scanning needs YouTube API

---

### Problem: "Claude API error" or "Rate limit"

**Solutions:**
- Check Anthropic API key is valid
- Verify you have API credits/billing set up
- Rate limit: Wait a few seconds and retry
- Script has automatic retry with exponential backoff

---

### Problem: "ImportError: No module named..."

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or install specific missing module
pip install MODULE_NAME
```

---

## WHAT'S NEXT?

### After Successful Test:

**1. Process More Videos** (Manual Testing)
```bash
# Test 3-5 videos from different creators
python test_pipeline.py "URL1"
python test_pipeline.py "URL2"
python test_pipeline.py "URL3"

# Review results in temp/ folder
# Verify insights are accurate and useful
```

**2. Test Video Scanner** (If you have YouTube API key)
```python
# Create test_scanner.py
from src.video_scanner import VideoScanner

scanner = VideoScanner()
videos = scanner.scan_creator("instasd")
print(f"Found {len(videos)} recent videos")
```

**3. Review Extracted Knowledge**
```bash
# Check temp/test_results_*.json files
# Verify:
# - Insights are accurate
# - Confidence scores reasonable
# - Target agents correct
# - Technical details captured
```

**4. Deploy Automated Scanning** (Phase 3)
```bash
# Not implemented yet, but coming:
python pipeline.py --schedule weekly
# This will scan all 50+ creators automatically
```

---

## COST ESTIMATES

### Per Video:
- Transcript extraction: FREE (YouTube auto-captions)
- Claude analysis: ~$0.01 per video
- **Total: ~$0.01 per video**

### Monthly (50 creators, 10 videos each):
- 500 videos × $0.01 = **$5/month**

### ROI:
- Manual research time saved: 16+ hours/month
- Value (at $100/hr): $1,600/month
- **ROI: 32,000%** 🚀

---

## CONFIGURATION OPTIONS

See `.env.example` for all options. Key settings:

```ini
# Quality Control
CONFIDENCE_THRESHOLD=80          # Auto-approve above this
HUMAN_REVIEW_THRESHOLD=60       # Manual review below this
AUTO_REJECT_THRESHOLD=40        # Auto-reject below this

# Performance
MAX_VIDEOS_PER_SCAN=10          # Limit per creator
MAX_TRANSCRIPT_LENGTH=50000     # Character limit

# Analysis
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_TEMPERATURE=0.3          # Lower = more consistent
CLAUDE_MAX_TOKENS=4096

# Testing
TEST_MODE=false                 # true = process only 1 video
DRY_RUN=false                   # true = don't save results
VERBOSE=false                   # true = detailed logs
```

---

## LOGS AND DEBUGGING

**Log files:** `logs/pipeline_YYYYMMDD.log`

**View recent logs:**
```bash
# Windows
type logs\pipeline_20251108.log

# View last 50 lines
powershell "Get-Content logs\pipeline_20251108.log -Tail 50"
```

**Enable verbose logging:**
```ini
# In .env
LOG_LEVEL=DEBUG
VERBOSE=true
```

---

## SUPPORT

**Issues?**
1. Check logs in `logs/` folder
2. Review troubleshooting section above
3. Verify API keys are correct
4. Test with a known good video

**Common Test Videos:**
- Any recent InstaSD ComfyUI tutorial
- Automation Avenue n8n workflow video
- Matthew Berman AI news update

---

## SYSTEM STATUS

**✅ IMPLEMENTED:**
- Configuration system
- Transcript extraction (YouTube auto-captions + API)
- AI analysis (Claude API)
- Validation and confidence scoring
- Test script for single videos

**🔄 IN PROGRESS:**
- Knowledge routing to agents
- KB file writing
- Multi-source validation

**📅 COMING SOON:**
- Automated scheduler
- Full 50+ creator scanning
- Agent integration
- Dashboard

---

## QUICK REFERENCE

```bash
# Install
pip install -r requirements.txt

# Configure
copy .env.example .env
# Edit .env with API keys

# Test single video
python test_pipeline.py "YOUTUBE_URL"

# Check logs
type logs\pipeline_20251108.log

# View results
type temp\test_results_VIDEO_ID.json
```

---

**Ready to extract knowledge from YouTube experts!** 🚀

**Status:** Phase 2 Complete ✅
**Next:** Test with real videos, then deploy automated scanning

🐱 **Cats rule. AI falls! (With expert knowledge!)** 🤖

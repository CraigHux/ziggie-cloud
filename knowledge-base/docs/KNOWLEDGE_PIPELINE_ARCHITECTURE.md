# KNOWLEDGE EXTRACTION PIPELINE ARCHITECTURE

**Version:** 1.0
**Created:** 2025-11-08
**Status:** Active Development

---

## OVERVIEW

The Knowledge Extraction Pipeline automatically scans 50+ YouTube creators, extracts insights from their content, and distributes knowledge to the 584 AI agents (8 L1 + 64 L2 + 512 L3) working on Meow Ping RTS.

**Goal:** Keep agents current with latest AI/game dev techniques without manual research.

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

[1] VIDEO SCANNING → [2] CONTENT EXTRACTION → [3] AI ANALYSIS
        ↓                      ↓                      ↓
   YouTube API        Transcript Fetch         Claude API
   (50+ creators)     (yt-dlp/YouTube)        (Insight Extraction)
        ↓                      ↓                      ↓
    Video URLs          Text Transcripts        Structured Knowledge
                                                       ↓
[4] KNOWLEDGE ROUTING → [5] AGENT UPDATES → [6] VALIDATION
        ↓                      ↓                   ↓
  Agent Mapping         KB File Updates      Confidence Check
  (JSON rules)          (Markdown files)     (Score >80%)
        ↓                      ↓                   ↓
  Target Agents         584 Agents           Applied/Flagged
```

---

## COMPONENT BREAKDOWN

### 1. VIDEO SCANNING (Scheduler)

**Purpose:** Discover new content from creators

**Technology:**
- Python scheduler (APScheduler)
- YouTube Data API v3

**Process:**
```python
def scan_creators():
    for creator in creator_database:
        if should_scan(creator.priority, creator.last_scan):
            videos = fetch_latest_videos(
                channel_id=creator.handle,
                max_results=creator.scan_last_n_videos
            )
            queue_for_processing(videos)
```

**Scan Frequency:**
- Critical: Every 3 days
- High: Weekly (Sunday 2 AM)
- Medium: Bi-weekly
- Low: Monthly

**Output:** List of video URLs to process

---

### 2. CONTENT EXTRACTION (Transcription)

**Purpose:** Extract text content from videos

**Technology:**
- yt-dlp (YouTube download tool)
- YouTube automatic captions API
- Whisper API (fallback for videos without captions)

**Process:**
```python
def extract_content(video_url):
    # Try 1: YouTube auto-captions
    transcript = get_youtube_transcript(video_url)

    if not transcript:
        # Try 2: Manual captions
        transcript = get_manual_captions(video_url)

    if not transcript:
        # Try 3: Whisper transcription (audio → text)
        audio = download_audio(video_url)
        transcript = whisper_transcribe(audio)

    # Also extract metadata
    metadata = {
        "title": video.title,
        "description": video.description,
        "upload_date": video.upload_date,
        "duration": video.duration,
        "views": video.views
    }

    return {
        "transcript": transcript,
        "metadata": metadata
    }
```

**Output:** Text transcripts + metadata

---

### 3. AI ANALYSIS (Insight Extraction)

**Purpose:** Extract actionable insights from transcripts

**Technology:**
- Claude API (Anthropic)
- Structured prompts for consistency

**Process:**
```python
def analyze_transcript(transcript, video_metadata, creator_info):
    prompt = f"""
    Analyze this YouTube video transcript and extract actionable insights
    for AI game development agents.

    Creator: {creator_info.name} (Focus: {creator_info.focus})
    Video: {video_metadata.title}
    Duration: {video_metadata.duration}

    Transcript:
    {transcript}

    Extract:
    1. Primary topic (1-2 words)
    2. Key insights (3-5 bullet points)
    3. Technical settings/parameters (if any)
    4. Code snippets or workflow steps (if any)
    5. Target AI agents (which agents would benefit?)
    6. Knowledge category (e.g., "comfyui-workflows", "n8n-automation")
    7. Confidence score (0-100)

    Output as JSON.
    """

    response = claude_api.complete(prompt)
    insights = parse_json(response)

    return insights
```

**Example Output:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "creator": "instasd",
  "title": "ComfyUI IP-Adapter Deep Dive",
  "primary_topic": "IP-Adapter Settings",
  "key_insights": [
    "IP-Adapter weight >0.70 locks BOTH face AND colors",
    "For color changes, reduce IP weight to 0.40",
    "Combine with denoise 0.40 for best results",
    "Use negative prompts to exclude old colors"
  ],
  "technical_settings": {
    "ip_adapter_weight": 0.40,
    "denoise": 0.40,
    "controlnet_strength": 0.60
  },
  "code_snippets": [],
  "target_agents": [
    "L1.2-character-pipeline",
    "L2.2.1-workflow-optimizer",
    "L2.2.4-ip-adapter-specialist",
    "L3.2.1.2-ip-adapter-weight-optimizer"
  ],
  "knowledge_category": "comfyui-workflows",
  "confidence_score": 95,
  "timestamp_references": [
    {"time": "2:30", "topic": "IP-Adapter color locking"},
    {"time": "5:15", "topic": "Parameter balancing"}
  ]
}
```

---

### 4. KNOWLEDGE ROUTING (Agent Mapping)

**Purpose:** Route insights to correct agents

**Technology:**
- JSON-based mapping rules
- Multi-agent routing (one insight → many agents)

**Routing Rules:**
```json
{
  "comfyui-workflows": {
    "primary": ["L1.2-character-pipeline"],
    "sub": ["L2.2.1-workflow-optimizer", "L2.2.2-prompt-engineer"],
    "micro": ["L3.2.1.1-denoise-tuner", "L3.2.1.2-ip-adapter-optimizer"]
  },
  "n8n-automation": {
    "primary": ["L1.7-integration"],
    "sub": ["L2.7.4-cicd-pipeline"],
    "micro": []
  },
  "game-design": {
    "primary": ["L1.6-content-designer"],
    "sub": ["L2.6.2-mission-designer", "L2.6.5-difficulty-curve"],
    "micro": []
  }
}
```

**Process:**
```python
def route_knowledge(insights):
    category = insights['knowledge_category']
    routing_rules = load_routing_rules()

    targets = routing_rules[category]

    for agent_id in targets['primary'] + targets['sub'] + targets['micro']:
        queue_update(agent_id, insights)
```

---

### 5. AGENT UPDATES (Knowledge Base Files)

**Purpose:** Write insights to agent knowledge bases

**Storage:** Markdown files per creator per agent

**File Structure:**
```
knowledge-base/
├── L1-character-pipeline/
│   ├── comfyui-workflows/
│   │   ├── instasd-insights.md
│   │   ├── stefan-3d-techniques.md
│   │   └── _synthesized-best-practices.md
│   └── ip-adapter-knowledge/
│       └── color-locking-behavior.md
```

**Update Process:**
```python
def update_agent_kb(agent_id, insights):
    kb_path = get_kb_path(agent_id, insights['creator'])

    # Append new entry
    entry = f"""
## {insights['title']} ({insights['date']})
**Source:** {insights['creator']} - [{insights['video_id']}]
**Confidence:** {insights['confidence_score']}%

### Key Insights:
{format_insights(insights['key_insights'])}

### Technical Settings:
{format_settings(insights['technical_settings'])}

### Timestamp References:
{format_timestamps(insights['timestamp_references'])}

### Applied To:
- Updated workflow guide: equipment_variations.json
- Notified: {insights['target_agents']}

---
"""

    append_to_file(kb_path, entry)

    # Also update synthesized best practices
    update_synthesized_kb(agent_id, insights)
```

---

### 6. VALIDATION (Confidence & Conflict Check)

**Purpose:** Ensure quality before applying

**Validation Checks:**

**Check 1: Confidence Threshold**
```python
if insights['confidence_score'] < 80:
    flag_for_human_review(insights)
    status = "pending_review"
else:
    status = "approved"
```

**Check 2: Conflict Detection**
```python
existing_knowledge = load_agent_kb(agent_id)

conflicts = detect_conflicts(insights, existing_knowledge)

if conflicts:
    flag_conflict(insights, conflicts)
    status = "conflicting"
```

**Check 3: Source Validation**
```python
# Multiple sources agree?
similar_insights = find_similar(insights)

if len(similar_insights) >= 2:
    confidence_boost = +10
    status = "validated_by_multiple_sources"
```

**Validation Outcomes:**
- ✅ **Approved** (confidence >80%, no conflicts) → Auto-apply
- ⚠️ **Pending Review** (confidence 60-80%) → Human review queue
- ❌ **Rejected** (confidence <60%) → Discard
- 🔀 **Conflicting** (contradicts existing) → Human decision

---

## KNOWLEDGE SYNTHESIS

**Purpose:** Combine insights from multiple creators

When 2+ creators cover the same topic:

```python
def synthesize_knowledge(topic, insights_list):
    """
    Example: n8n Automation

    Sources:
    - Automation Avenue: DevOps workflows
    - Lead Gen Jay: Business automation
    - Eric Tech: Full-stack integration

    Synthesized Output:
    - Common patterns (validated by 3 sources)
    - Unique insights per use case
    - Recommended approach per scenario
    """

    common_patterns = find_common(insights_list)
    unique_insights = find_unique(insights_list)

    synthesized = {
        "topic": topic,
        "validated_by": len(insights_list),
        "common_best_practices": common_patterns,
        "use_case_specific": unique_insights,
        "confidence": calculate_confidence(insights_list)
    }

    # Save to cross-agent knowledge
    save_synthesized(synthesized)
```

**Output File:** `cross-agent-knowledge/synthesized-{topic}.md`

---

## AGENT INVOCATION WITH KNOWLEDGE

When an agent is invoked, it automatically loads relevant knowledge:

```python
# Agent startup sequence
class CharacterPipelineAgent:
    def __init__(self):
        self.knowledge_base = load_knowledge_base([
            "L1-character-pipeline/comfyui-workflows/",
            "L1-character-pipeline/ip-adapter-knowledge/",
            "cross-agent-knowledge/ai-tools-updates/"
        ])

    def generate_character(self, request):
        # Apply latest knowledge
        settings = self.workflow_optimizer.get_optimal_settings(
            use_case=request.use_case,
            knowledge_base=self.knowledge_base
        )

        # Generate with informed settings
        result = comfyui.generate(settings)

        # Cite sources
        sources = self.get_knowledge_sources(settings)
        result['source_citations'] = sources

        return result
```

**Agent Response with Citations:**
```
Character Pipeline Agent:
"I'll generate Meow Ping Tier 2 with equipment changes.

Settings selected:
- Denoise: 0.40 ✅
- IP-Adapter: 0.40 ✅ (per InstaSD tutorial, 2025-11-05)
- ControlNet: 0.60 ✅

Knowledge sources applied:
✅ InstaSD: IP-Adapter color locking behavior (confidence: 95%)
✅ Stefan 3D AI Lab: Color theory for 3D assets (confidence: 88%)
✅ Our testing: Validated 91% success rate

[Generates image]

Result: Success! Applied latest ComfyUI techniques from 3 sources."
```

---

## IMPLEMENTATION PHASES

### Phase 1: Core Infrastructure (Week 1) ✅
- [x] Create knowledge base folder structure
- [x] Build creator database (50+ channels)
- [x] Design pipeline architecture
- [ ] Set up Python environment

### Phase 2: Extraction Pipeline (Week 2)
- [ ] Implement video scanner (YouTube API)
- [ ] Build transcript extractor (yt-dlp)
- [ ] Create AI analyzer (Claude API)
- [ ] Test with InstaSD videos

### Phase 3: Knowledge Routing (Week 3)
- [ ] Build agent mapping system
- [ ] Create knowledge file writers
- [ ] Implement validation checks
- [ ] Test end-to-end with 5 creators

### Phase 4: Synthesis & Automation (Week 4)
- [ ] Build knowledge synthesis system
- [ ] Create automated scheduler
- [ ] Implement conflict detection
- [ ] Deploy weekly automation

### Phase 5: Agent Integration (Week 5)
- [ ] Update agent prompts to load KB
- [ ] Test agent invocations with KB
- [ ] Add source citations
- [ ] Validate improvements

---

## TECHNICAL STACK

**Languages:**
- Python 3.11+ (pipeline automation)
- Bash (system integration)

**Libraries:**
- `yt-dlp` - YouTube video/transcript download
- `youtube-transcript-api` - Transcript extraction
- `anthropic` - Claude API for analysis
- `apscheduler` - Scheduled scanning
- `pyyaml` - Configuration files
- `requests` - API calls

**APIs:**
- YouTube Data API v3 (video metadata)
- Anthropic Claude API (insight extraction)
- OpenAI Whisper API (fallback transcription)

**Storage:**
- JSON (creator database, metadata)
- Markdown (knowledge base files)
- SQLite (processing queue, logs)

---

## CONFIGURATION

**Environment Variables:**
```bash
# .env
YOUTUBE_API_KEY=your_youtube_api_key
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_key (optional, for Whisper)

KB_PATH=C:\meowping-rts\ai-agents\knowledge-base
LOG_PATH=C:\meowping-rts\ai-agents\knowledge-base\logs

SCAN_SCHEDULE_CRITICAL=every_3_days
SCAN_SCHEDULE_HIGH=weekly
SCAN_SCHEDULE_MEDIUM=biweekly
SCAN_SCHEDULE_LOW=monthly

CONFIDENCE_THRESHOLD=80
MAX_VIDEOS_PER_SCAN=10
```

**Pipeline Config:** `config/pipeline-config.yaml`
```yaml
extraction:
  transcript_sources:
    - youtube_auto_captions
    - manual_captions
    - whisper_api

  max_transcript_length: 50000  # characters

analysis:
  model: claude-3-5-sonnet-20241022
  temperature: 0.3  # Lower = more consistent
  max_tokens: 4096

routing:
  rules_file: config/routing-rules.json
  allow_multi_agent: true

validation:
  confidence_threshold: 80
  require_human_review_below: 60
  auto_reject_below: 40

storage:
  format: markdown
  include_timestamps: true
  include_citations: true
```

---

## MONITORING & LOGGING

**Logs:**
```
knowledge-base/logs/
├── scan-log.txt          # Video scanning activity
├── extraction-log.txt    # Transcript extraction
├── analysis-log.txt      # AI analysis results
├── routing-log.txt       # Knowledge routing
├── validation-log.txt    # Validation outcomes
└── errors.txt            # Pipeline errors
```

**Metrics Tracked:**
```json
{
  "pipeline_metrics": {
    "videos_scanned": 127,
    "transcripts_extracted": 124,
    "insights_generated": 118,
    "insights_applied": 102,
    "insights_pending_review": 12,
    "insights_rejected": 4,
    "agents_updated": 87,
    "average_confidence": 86.5,
    "last_run": "2025-11-08T02:00:00Z"
  }
}
```

**Dashboard:** `knowledge-base/dashboard.html`
- Real-time pipeline status
- Recent insights by creator
- Agent knowledge freshness
- Confidence score trends

---

## USAGE EXAMPLES

### Manual Trigger
```bash
# Scan specific creator
python pipeline.py scan --creator instasd

# Process specific video
python pipeline.py process --url https://youtube.com/watch?v=abc123

# Update specific agent
python pipeline.py update-agent --agent L1.2 --source instasd
```

### Automated (Scheduled)
```bash
# Start pipeline daemon
python pipeline.py start-daemon

# Check status
python pipeline.py status

# Stop daemon
python pipeline.py stop-daemon
```

### Agent Query
```python
# Inside agent code
kb = agent.load_knowledge_base()

# Get latest on topic
insights = kb.query(topic="ip-adapter", min_confidence=85)

# Get by creator
instasd_tips = kb.query(creator="instasd", limit=5)

# Get synthesized knowledge
best_practices = kb.get_synthesized("comfyui-workflows")
```

---

## BENEFITS

✅ **Agents stay current** - Weekly updates from 50+ experts
✅ **No manual research** - Fully automated pipeline
✅ **Multi-source validation** - Higher confidence from agreement
✅ **Transparent decisions** - Source citations for every recommendation
✅ **Continuous learning** - System improves with feedback
✅ **Specialized knowledge** - Right insights → right agents

---

## ROADMAP

**v1.0 (Current):** Core infrastructure, manual testing
**v1.1:** Automated weekly scans, 5 critical creators
**v1.2:** All 50+ creators, synthesis engine
**v1.3:** Real-time scanning (webhooks for new uploads)
**v1.4:** Agent feedback loop (track which insights help most)
**v2.0:** AI-powered insight ranking, predictive relevance

---

## GETTING STARTED

See: [KNOWLEDGE_PIPELINE_SETUP_GUIDE.md](KNOWLEDGE_PIPELINE_SETUP_GUIDE.md)

Quick start:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 3. Test with one video
python pipeline.py test --url https://youtube.com/watch?v=abc123

# 4. Start automated scanning
python pipeline.py start-daemon
```

---

**Status:** Architecture Complete ✅
**Next:** Implementation Phase 2 (Extraction Pipeline)
**Maintained by:** Integration Agent (L1.7)

🚀 **Automated learning from 50+ experts, 24/7!**

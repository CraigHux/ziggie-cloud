"""
AI Analyzer - Uses Claude API to extract insights from transcripts
"""

import json
import time
from anthropic import Anthropic, APIError

from config import Config
from logger import logger


class AIAnalyzer:
    """Analyzes video transcripts using Claude API to extract actionable insights"""

    def __init__(self):
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.CLAUDE_MODEL
        self.temperature = Config.CLAUDE_TEMPERATURE
        self.max_tokens = Config.CLAUDE_MAX_TOKENS

    def analyze_transcript(self, video_data, transcript_text, creator_info):
        """
        Analyze a video transcript and extract insights

        Args:
            video_data: Dict with video metadata (title, description, etc.)
            transcript_text: Full transcript text
            creator_info: Dict with creator metadata

        Returns:
            Dict with extracted insights or None if failed
        """

        prompt = self._build_analysis_prompt(video_data, transcript_text, creator_info)

        retry_count = 0
        while retry_count < Config.ANALYSIS_RETRY_COUNT:
            try:
                logger.info(f"Analyzing video: {video_data.get('title', 'Unknown')}")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                # Extract JSON from response
                response_text = response.content[0].text
                insights = self._parse_response(response_text)

                if insights:
                    # Add metadata
                    insights['video_id'] = video_data.get('video_id')
                    insights['creator_id'] = creator_info.get('id')
                    insights['analyzed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    insights['model'] = self.model

                    logger.info(f"Successfully analyzed video (confidence: {insights.get('confidence_score', 'N/A')}%)")
                    return insights

                logger.warning("Failed to parse insights from response")
                retry_count += 1

            except APIError as e:
                logger.error(f"Claude API error: {e}")
                retry_count += 1
                if retry_count < Config.ANALYSIS_RETRY_COUNT:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error during analysis: {e}")
                break

        logger.error(f"Failed to analyze video after {Config.ANALYSIS_RETRY_COUNT} attempts")
        return None

    def _build_analysis_prompt(self, video_data, transcript_text, creator_info):
        """Build the analysis prompt for Claude"""

        prompt = f"""Analyze this YouTube video transcript and extract actionable insights for AI game development agents.

**Creator Information:**
- Name: {creator_info.get('name')}
- Focus: {creator_info.get('focus')}
- Priority: {creator_info.get('priority')}

**Video Metadata:**
- Title: {video_data.get('title')}
- Duration: {video_data.get('duration_seconds', 0)} seconds
- Published: {video_data.get('published_at')}
- Description: {video_data.get('description', '')[:500]}

**Transcript:**
{transcript_text[:40000]}  # Limit to ~40k chars to fit in context

---

**Your Task:**
Extract actionable insights that would help AI agents working on game development (specifically an RTS game using ComfyUI for assets, Unity for game engine, n8n for automation, etc.).

**Output Format (JSON):**
```json
{{
  "primary_topic": "One or two word topic (e.g., 'ComfyUI Workflows', 'n8n Automation')",
  "key_insights": [
    "First key insight that's actionable",
    "Second key insight",
    "Third key insight"
  ],
  "technical_settings": {{
    "setting_name": "value",
    "another_setting": "value"
  }},
  "code_snippets": [
    {{
      "language": "python",
      "description": "What this code does",
      "code": "actual code here"
    }}
  ],
  "workflow_steps": [
    "Step 1: Do this",
    "Step 2: Then do this"
  ],
  "target_agents": [
    "L1.2-character-pipeline",
    "L2.2.1-workflow-optimizer"
  ],
  "knowledge_category": "comfyui-workflows",
  "confidence_score": 85,
  "timestamp_references": [
    {{
      "time": "2:30",
      "topic": "IP-Adapter color locking behavior"
    }}
  ],
  "tools_mentioned": ["ComfyUI", "SDXL Turbo", "IP-Adapter"],
  "key_takeaways": [
    "Main takeaway 1",
    "Main takeaway 2"
  ]
}}
```

**Important Guidelines:**
1. **Be specific and actionable** - Agents need concrete steps, not vague advice
2. **Extract technical details** - Settings, parameters, exact values when mentioned
3. **Identify applicable agents** - Which L1/L2/L3 agents would benefit?
4. **Rate confidence** - How confident are you in this information (0-100)?
5. **Note timestamps** - When specific topics are discussed (if identifiable)
6. **Focus on practical value** - What can agents actually DO with this information?

**Knowledge Categories:**
comfyui-workflows, workflow-optimization, prompt-engineering, ip-adapter-knowledge, controlnet-techniques, 3d-asset-generation, blender-3d, unreal-engine, environment-art, vfx-techniques, n8n-automation, make-automation, devops, cloud-aws, docker, game-design, game-mechanics, unity, ai-agents, fullstack-dev, ui-ux-design, conversational-ai, database, ai-news, ai-tools, ai-coding-tools, seo, marketing, testing, performance-optimization

**Target Agents:**
L1.1-art-director, L1.2-character-pipeline, L1.3-environment-pipeline, L1.4-game-systems, L1.5-ui-ux, L1.6-content-designer, L1.7-integration, L1.8-qa-testing

Output ONLY the JSON, no additional text."""

        return prompt

    def _parse_response(self, response_text):
        """Parse Claude's response to extract JSON"""
        try:
            # Try to extract JSON from markdown code block
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                json_str = response_text.strip()

            insights = json.loads(json_str)
            return insights

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return None

    def validate_insights(self, insights):
        """Validate extracted insights"""
        required_fields = ['primary_topic', 'key_insights', 'knowledge_category', 'confidence_score', 'target_agents']

        for field in required_fields:
            if field not in insights:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate confidence score
        confidence = insights.get('confidence_score', 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
            logger.warning(f"Invalid confidence score: {confidence}")
            return False

        # Validate key insights
        if not insights.get('key_insights') or len(insights['key_insights']) == 0:
            logger.warning("No key insights extracted")
            return False

        return True

    def get_approval_status(self, confidence_score):
        """Determine approval status based on confidence"""
        if confidence_score >= Config.CONFIDENCE_THRESHOLD:
            return "approved", "Auto-approved (high confidence)"
        elif confidence_score >= Config.HUMAN_REVIEW_THRESHOLD:
            return "pending_review", "Pending human review (medium confidence)"
        elif confidence_score >= Config.AUTO_REJECT_THRESHOLD:
            return "flagged", "Flagged for review (low confidence)"
        else:
            return "rejected", "Auto-rejected (very low confidence)"


# Test function
if __name__ == "__main__":
    from logger import log_section

    log_section("AI Analyzer Test")

    if not Config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set. Cannot test AI analyzer.")
        exit(1)

    analyzer = AIAnalyzer()

    # Test data
    test_video = {
        'video_id': 'test123',
        'title': 'ComfyUI IP-Adapter Tutorial',
        'description': 'Learn how to use IP-Adapter with ControlNet',
        'duration_seconds': 900,
        'published_at': '2025-11-05'
    }

    test_creator = {
        'id': 'instasd',
        'name': 'InstaSD',
        'focus': 'ComfyUI workflows',
        'priority': 'critical'
    }

    test_transcript = """
    In this tutorial, I'll show you how IP-Adapter works with ComfyUI.
    An important thing to understand is that IP-Adapter locks both the face AND the colors.
    When you set the IP-Adapter weight above 0.70, you're locking everything.
    For equipment changes, you want to reduce it to 0.40.
    Also set your denoise to 0.40 and ControlNet to 0.60.
    This gives you the best balance for changing colors while keeping the face similar.
    """

    logger.info("Analyzing test transcript...")
    insights = analyzer.analyze_transcript(test_video, test_transcript, test_creator)

    if insights:
        logger.info("\nExtracted Insights:")
        logger.info(json.dumps(insights, indent=2))

        valid = analyzer.validate_insights(insights)
        logger.info(f"\nValidation: {valid}")

        status, message = analyzer.get_approval_status(insights['confidence_score'])
        logger.info(f"Status: {status} - {message}")
    else:
        logger.error("Failed to extract insights")

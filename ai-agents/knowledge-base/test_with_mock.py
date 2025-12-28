#!/usr/bin/env python3
"""
Test pipeline with mock transcript data
This tests the AI analysis without needing YouTube API
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from logger import logger, log_section
from ai_analyzer import AIAnalyzer

# Mock transcript about ComfyUI (simulating an InstaSD tutorial)
MOCK_TRANSCRIPT = """
In this video, I'm going to show you an important discovery about IP-Adapter and ControlNet in ComfyUI.

Many people don't realize that IP-Adapter doesn't just lock the face - it also locks the colors.
At weights above 0.70, you'll get perfect face consistency, but you won't be able to change equipment colors at all.

So here's what I've found works best for equipment variations:
- Set your Denoise to 0.40
- Reduce IP-Adapter weight to 0.40
- Keep ControlNet strength at 0.60

With these settings, you maintain the pose from ControlNet, but you free up the colors so you can
change equipment, armor, or clothing colors while keeping the character's face recognizable.

This is huge for game asset pipelines where you need the same character in different equipment tiers.

The key insight is that ControlNet handles the pose locking, so you don't need IP-Adapter at full strength.
By reducing it to 0.40, you get the best of both worlds - face similarity without color constraints.

I've tested this with dozens of variations and it works consistently. Give it a try and let me know your results!
"""

MOCK_VIDEO_DATA = {
    "video_id": "MOCK_TEST",
    "title": "ComfyUI IP-Adapter + ControlNet for Equipment Variations",
    "creator": "InstaSD",
    "url": "https://www.youtube.com/watch?v=MOCK_TEST"
}

def test_with_mock():
    """Test AI analysis with mock transcript"""

    log_section("KNOWLEDGE PIPELINE - MOCK TEST")

    logger.info("Testing with mock InstaSD transcript")
    logger.info("")

    # Step 1: Configuration
    logger.info("="*60)
    logger.info("Step 1: Configuration Check")
    logger.info("="*60)

    try:
        Config.validate()
        logger.info("[OK] Configuration valid")
    except ValueError as e:
        logger.error(f"[X] Configuration error: {e}")
        return False

    # Step 2: Mock Transcript (skip extraction)
    logger.info("")
    logger.info("="*60)
    logger.info("Step 2: Mock Transcript")
    logger.info("="*60)
    logger.info(f"[OK] Using mock transcript ({len(MOCK_TRANSCRIPT)} characters)")
    logger.info(f"  Preview: {MOCK_TRANSCRIPT[:100]}...")

    # Step 3: AI Analysis
    logger.info("")
    logger.info("="*60)
    logger.info("Step 3: AI Analysis (Claude API)")
    logger.info("="*60)
    logger.info("Analyzing mock transcript with Claude...")

    analyzer = AIAnalyzer()

    creator_info = {
        "name": "InstaSD",
        "focus": "ComfyUI workflows",
        "priority": "critical"
    }

    try:
        insights = analyzer.analyze_transcript(
            video_data=MOCK_VIDEO_DATA,
            transcript_text=MOCK_TRANSCRIPT,
            creator_info=creator_info
        )

        if not insights:
            logger.error("[X] Failed to extract insights")
            return False

        logger.info("[OK] Insights extracted successfully")
        logger.info("")

        # Show results
        logger.info("="*60)
        logger.info("EXTRACTED INSIGHTS")
        logger.info("="*60)
        logger.info("")
        print(json.dumps(insights, indent=2))
        logger.info("")

        # Validation
        logger.info("="*60)
        logger.info("Validation")
        logger.info("="*60)
        confidence = insights.get("confidence_score", 0)
        logger.info(f"Confidence Score: {confidence}%")
        logger.info(f"Threshold: {Config.CONFIDENCE_THRESHOLD}%")

        if confidence >= Config.CONFIDENCE_THRESHOLD:
            logger.info(f"[OK] Above threshold - APPROVED")
            status = "approved"
        elif confidence >= Config.HUMAN_REVIEW_THRESHOLD:
            logger.info(f"[!] Needs human review")
            status = "review"
        else:
            logger.info(f"[X] Below threshold - REJECTED")
            status = "rejected"

        logger.info("")

        # Save results
        output_file = Config.TEMP_PATH / f"mock_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Config.TEMP_PATH.mkdir(parents=True, exist_ok=True)

        results = {
            "video_data": MOCK_VIDEO_DATA,
            "transcript_preview": MOCK_TRANSCRIPT[:500],
            "insights": insights,
            "validation_status": status,
            "tested_at": datetime.now().isoformat()
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("="*60)
        logger.info("MOCK TEST SUMMARY")
        logger.info("="*60)
        logger.info("")
        logger.info(f"[OK] AI analysis working!")
        logger.info(f"Primary Topic: {insights.get('primary_topic', 'N/A')}")
        logger.info(f"Confidence: {confidence}%")
        logger.info(f"Status: {status}")
        logger.info(f"Target Agents: {', '.join(insights.get('target_agents', []))}")
        logger.info("")
        logger.info(f"[OK] Results saved to: {output_file}")
        logger.info("")

        logger.info("="*60)
        logger.info("NEXT STEP")
        logger.info("="*60)
        logger.info("")
        logger.info("The AI analysis pipeline is working!")
        logger.info("The issue is with YouTube transcript extraction.")
        logger.info("")
        logger.info("Possible solutions:")
        logger.info("1. Try different videos (some may have captions blocked)")
        logger.info("2. Install ffmpeg for Whisper fallback")
        logger.info("3. Use YouTube Data API + manual download")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"[X] Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_mock()

    print("")
    print("="*60)
    if success:
        print("[OK] MOCK TEST SUCCESSFUL!")
        print("="*60)
        print("")
        print("AI analysis is working. Ready to test with real transcripts.")
    else:
        print("[X] MOCK TEST FAILED")
        print("="*60)
        print("")
        print("Check logs for details")

    sys.exit(0 if success else 1)

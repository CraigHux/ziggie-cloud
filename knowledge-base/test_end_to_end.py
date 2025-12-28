#!/usr/bin/env python3
"""
End-to-End Knowledge Pipeline Test
Tests: Mock transcript -> AI Analysis -> Knowledge Writing -> Agent KB
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
from knowledge_writer import KnowledgeWriter

# Mock transcript about ComfyUI
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
    "video_id": "E2E_TEST_001",
    "title": "ComfyUI IP-Adapter + ControlNet for Equipment Variations",
    "creator": "InstaSD",
    "url": "https://www.youtube.com/watch?v=E2E_TEST_001"
}

MOCK_CREATOR_INFO = {
    "name": "InstaSD",
    "focus": "ComfyUI workflows",
    "priority": "critical"
}


def test_end_to_end():
    """Test complete pipeline: Analysis -> Writing -> Agent KB"""

    log_section("END-TO-END PIPELINE TEST")

    logger.info("Testing complete pipeline with mock data")
    logger.info("")

    # Step 1: Configuration
    logger.info("="*60)
    logger.info("Step 1: Configuration")
    logger.info("="*60)

    try:
        Config.validate()
        logger.info("[OK] Configuration valid")
    except ValueError as e:
        logger.error(f"[X] Configuration error: {e}")
        return False

    # Step 2: Mock Transcript
    logger.info("")
    logger.info("="*60)
    logger.info("Step 2: Mock Transcript")
    logger.info("="*60)
    logger.info(f"[OK] Using mock transcript ({len(MOCK_TRANSCRIPT)} characters)")

    # Step 3: AI Analysis
    logger.info("")
    logger.info("="*60)
    logger.info("Step 3: AI Analysis")
    logger.info("="*60)
    logger.info("Analyzing with Claude API...")

    analyzer = AIAnalyzer()

    try:
        insights = analyzer.analyze_transcript(
            video_data=MOCK_VIDEO_DATA,
            transcript_text=MOCK_TRANSCRIPT,
            creator_info=MOCK_CREATOR_INFO
        )

        if not insights:
            logger.error("[X] Analysis failed")
            return False

        logger.info(f"[OK] Analysis complete (confidence: {insights.get('confidence_score')}%)")

    except Exception as e:
        logger.error(f"[X] Analysis error: {e}")
        return False

    # Step 4: Knowledge Writing
    logger.info("")
    logger.info("="*60)
    logger.info("Step 4: Knowledge Writing")
    logger.info("="*60)
    logger.info("Writing insights to agent KB files...")

    writer = KnowledgeWriter()

    try:
        written_files = writer.write_insights(
            insights=insights,
            video_data=MOCK_VIDEO_DATA,
            creator_info=MOCK_CREATOR_INFO
        )

        if not written_files:
            logger.error("[X] No files written")
            return False

        logger.info(f"[OK] Written to {len(written_files)} agent(s)")

    except Exception as e:
        logger.error(f"[X] Writing error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Verification
    logger.info("")
    logger.info("="*60)
    logger.info("Step 5: Verification")
    logger.info("="*60)

    for file_path in written_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            logger.info(f"[OK] {Path(file_path).name} ({size} bytes)")
        else:
            logger.error(f"[X] File not found: {file_path}")
            return False

    # Summary
    logger.info("")
    logger.info("="*60)
    logger.info("END-TO-END TEST SUMMARY")
    logger.info("="*60)
    logger.info("")
    logger.info("[OK] Complete pipeline working!")
    logger.info("")
    logger.info(f"Primary Topic: {insights.get('primary_topic')}")
    logger.info(f"Confidence: {insights.get('confidence_score')}%")
    logger.info(f"Target Agents: {', '.join(insights.get('target_agents', []))}")
    logger.info(f"Files Written: {len(written_files)}")
    logger.info("")

    logger.info("Knowledge written to:")
    for file_path in written_files:
        rel_path = Path(file_path).relative_to(Path.cwd().parent.parent)
        logger.info(f"  -> {rel_path}")

    logger.info("")
    logger.info("="*60)
    logger.info("AGENT KB FILES UPDATED")
    logger.info("="*60)
    logger.info("")
    logger.info("Agents can now access this knowledge:")
    logger.info("")

    for agent_id in insights.get('target_agents', []):
        logger.info(f"  {agent_id}")
        logger.info(f"    - Has access to ComfyUI workflow knowledge")
        logger.info(f"    - IP-Adapter settings: 0.40")
        logger.info(f"    - ControlNet settings: 0.60")
        logger.info(f"    - Denoise settings: 0.40")
        logger.info("")

    # Save summary
    summary_file = Config.TEMP_PATH / f"e2e_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Config.TEMP_PATH.mkdir(parents=True, exist_ok=True)

    summary = {
        "test_type": "end_to_end",
        "timestamp": datetime.now().isoformat(),
        "video_data": MOCK_VIDEO_DATA,
        "creator_info": MOCK_CREATOR_INFO,
        "insights": insights,
        "files_written": written_files,
        "status": "success"
    }

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"[OK] Summary saved: {summary_file}")
    logger.info("")

    return True


if __name__ == "__main__":
    success = test_end_to_end()

    print("")
    print("="*60)
    if success:
        print("[OK] END-TO-END TEST SUCCESSFUL!")
        print("="*60)
        print("")
        print("Complete pipeline validated:")
        print("  1. AI Analysis (Claude API)")
        print("  2. Knowledge Extraction")
        print("  3. Agent KB Writing")
        print("  4. File Verification")
        print("")
        print("Agents now have access to the extracted knowledge!")
        print("")
        print("Next: Test with real YouTube videos (after ffmpeg install)")
    else:
        print("[X] END-TO-END TEST FAILED")
        print("="*60)
        print("")
        print("Check logs for details")

    sys.exit(0 if success else 1)

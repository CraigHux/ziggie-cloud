"""
Knowledge Pipeline Test Script
Test the complete pipeline with a single YouTube video
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from logger import logger, log_section
from transcript_extractor import TranscriptExtractor
from ai_analyzer import AIAnalyzer


def test_single_video(video_url):
    """Test the complete pipeline with a single video"""

    log_section("KNOWLEDGE PIPELINE TEST")

    logger.info(f"Testing with video: {video_url}")

    # Step 1: Configuration
    logger.info("\n" + "="*60)
    logger.info("Step 1: Configuration Check")
    logger.info("="*60)

    try:
        Config.validate()
        logger.info("[OK] Configuration valid")
        print(Config.summary())
    except ValueError as e:
        logger.error(f"[X] Configuration error: {e}")
        logger.error("\nPlease create a .env file with your API keys:")
        logger.error("  cp .env.example .env")
        logger.error("  # Edit .env with your API keys")
        return False

    # Step 2: Extract Transcript
    logger.info("\n" + "="*60)
    logger.info("Step 2: Extract Transcript")
    logger.info("="*60)

    extractor = TranscriptExtractor()
    transcript_result = extractor.get_transcript(video_url)

    if not transcript_result:
        logger.error("[X] Failed to extract transcript")
        logger.error("\nPossible reasons:")
        logger.error("  - Video has no captions/transcript")
        logger.error("  - Video ID is invalid")
        logger.error("  - API quota exceeded")
        return False

    logger.info(f"[OK] Transcript extracted using: {transcript_result['method']}")
    logger.info(f"  Language: {transcript_result['language']}")
    logger.info(f"  Length: {len(transcript_result['text'])} characters")
    logger.info(f"  Preview: {transcript_result['text'][:200]}...")

    # Validate
    valid, message = extractor.validate_transcript(transcript_result)
    if not valid:
        logger.error(f"[X] Transcript validation failed: {message}")
        return False

    logger.info(f"[OK] Transcript validation passed: {message}")

    # Step 3: Analyze with Claude
    logger.info("\n" + "="*60)
    logger.info("Step 3: AI Analysis (Claude API)")
    logger.info("="*60)

    # Mock video and creator data for testing
    video_data = {
        'video_id': extractor.extract_video_id(video_url),
        'title': 'Test Video',  # Would come from video_scanner in full pipeline
        'description': 'Testing knowledge extraction',
        'duration_seconds': 600,
        'published_at': '2025-11-08',
        'url': video_url
    }

    creator_info = {
        'id': 'test-creator',
        'name': 'Test Creator',
        'focus': 'ComfyUI and AI workflows',
        'priority': 'high'
    }

    analyzer = AIAnalyzer()
    insights = analyzer.analyze_transcript(video_data, transcript_result['text'], creator_info)

    if not insights:
        logger.error("[X] Failed to extract insights from transcript")
        return False

    logger.info(f"[OK] Insights extracted successfully")
    logger.info(f"\n{json.dumps(insights, indent=2)}")

    # Step 4: Validate Insights
    logger.info("\n" + "="*60)
    logger.info("Step 4: Validate Insights")
    logger.info("="*60)

    valid = analyzer.validate_insights(insights)
    if not valid:
        logger.error("[X] Insights validation failed")
        return False

    logger.info("[OK] Insights validation passed")

    # Check approval status
    status, message = analyzer.get_approval_status(insights['confidence_score'])
    logger.info(f"\nApproval Status: {status}")
    logger.info(f"Message: {message}")
    logger.info(f"Confidence Score: {insights['confidence_score']}%")

    # Step 5: Summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE TEST SUMMARY")
    logger.info("="*60)

    logger.info(f"\n[OK] All steps completed successfully!\n")
    logger.info(f"Primary Topic: {insights.get('primary_topic')}")
    logger.info(f"Knowledge Category: {insights.get('knowledge_category')}")
    logger.info(f"Target Agents: {', '.join(insights.get('target_agents', [])[:3])}...")
    logger.info(f"Key Insights: {len(insights.get('key_insights', []))} insights extracted")
    logger.info(f"Confidence: {insights['confidence_score']}% ({status})")

    # Save results
    output_file = Config.TEMP_PATH / f"test_results_{video_data['video_id']}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'video': video_data,
            'transcript': {
                'method': transcript_result['method'],
                'language': transcript_result['language'],
                'length': len(transcript_result['text'])
            },
            'insights': insights
        }, f, indent=2)

    logger.info(f"\n[OK] Results saved to: {output_file}")

    logger.info("\n" + "="*60)
    logger.info("NEXT STEPS")
    logger.info("="*60)
    logger.info("\n1. Review the extracted insights above")
    logger.info("2. Check if insights are accurate and useful")
    logger.info("3. If satisfied, the full pipeline can:")
    logger.info("   - Scan 50+ YouTube creators automatically")
    logger.info("   - Extract insights from hundreds of videos")
    logger.info("   - Update 584 AI agents weekly")
    logger.info("\n4. To process more videos, run:")
    logger.info("   python test_pipeline.py <youtube_url>")
    logger.info("\n5. To deploy full automation:")
    logger.info("   python pipeline.py --schedule weekly")

    return True


if __name__ == "__main__":
    # Test with provided URL or use example
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        # Example: Use a video URL
        # User should replace this with actual video URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        logger.warning(f"\nNo URL provided, using example: {test_url}")
        logger.warning("Usage: python test_pipeline.py <youtube_url>\n")

    success = test_single_video(test_url)

    if success:
        print("\n" + "="*60)
        print("[OK] PIPELINE TEST SUCCESSFUL!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("[X] PIPELINE TEST FAILED")
        print("="*60)
        print("\nCheck the logs above for error details")
        sys.exit(1)

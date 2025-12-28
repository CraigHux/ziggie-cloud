#!/usr/bin/env python3
"""
Knowledge Base Pipeline Manager
Central command for all pipeline operations
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from logger import logger, log_section


def cmd_test_single(args):
    """Test with a single video URL"""
    from test_pipeline import test_single_video

    logger.info(f"Testing with video: {args.url}")
    success = test_single_video(args.url)

    sys.exit(0 if success else 1)


def cmd_test_mock(args):
    """Test with mock transcript"""
    from test_end_to_end import test_end_to_end

    logger.info("Running end-to-end test with mock data...")
    success = test_end_to_end()

    sys.exit(0 if success else 1)


def cmd_scan_creator(args):
    """Scan a specific creator"""
    from src.scheduler import KnowledgePipelineScheduler
    import json

    scheduler = KnowledgePipelineScheduler()

    # Find creator in database
    creator = None
    for c in scheduler.creators:
        if c.get('id') == args.creator_id or c.get('name').lower() == args.creator_id.lower():
            creator = c
            break

    if not creator:
        logger.error(f"Creator not found: {args.creator_id}")
        logger.info("\nAvailable creators:")
        for c in scheduler.creators[:10]:
            logger.info(f"  - {c.get('id')} ({c.get('name')})")
        sys.exit(1)

    processed = scheduler.scan_creator(creator)
    logger.info(f"\n✓ Processed {processed} videos")

    sys.exit(0)


def cmd_scan_all(args):
    """Scan all creators"""
    from src.scheduler import manual_scan

    logger.info(f"Scanning all creators (priority: {args.priority or 'all'})...")
    manual_scan(priority=args.priority)

    sys.exit(0)


def cmd_schedule(args):
    """Start automated scheduler"""
    from src.scheduler import KnowledgePipelineScheduler

    logger.info("Starting automated scheduler...")
    logger.info("The system will scan creators based on their priority:")
    logger.info("  - Critical: Every 3 days")
    logger.info("  - High: Weekly (Mondays)")
    logger.info("  - Medium: Biweekly (1st & 15th)")
    logger.info("  - Low: Monthly (1st)")
    logger.info("\nPress Ctrl+C to stop\n")

    scheduler = KnowledgePipelineScheduler()
    scheduler.start()


def cmd_status(args):
    """Show pipeline status"""

    log_section("KNOWLEDGE BASE PIPELINE STATUS")

    # Configuration
    logger.info("\n📋 Configuration:")
    try:
        Config.validate()
        logger.info("  ✓ Configuration valid")
        logger.info(f"  Model: {Config.CLAUDE_MODEL}")
        logger.info(f"  Confidence threshold: {Config.CONFIDENCE_THRESHOLD}%")
        logger.info(f"  Max videos per scan: {Config.MAX_VIDEOS_PER_SCAN}")
    except Exception as e:
        logger.error(f"  ✗ Configuration error: {e}")

    # Creator database
    logger.info("\n📚 Creator Database:")
    creator_db_path = Config.METADATA_PATH / "creator-database.json"
    if creator_db_path.exists():
        import json
        with open(creator_db_path) as f:
            data = json.load(f)
            creators = data.get('creators', [])

        priority_counts = {}
        for c in creators:
            priority = c.get('priority', 'unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        logger.info(f"  Total creators: {len(creators)}")
        for priority, count in sorted(priority_counts.items()):
            logger.info(f"  {priority.capitalize()}: {count}")
    else:
        logger.warning("  Creator database not found")

    # Knowledge base files
    logger.info("\n📁 Knowledge Base:")
    kb_root = Config.KB_PATH.parent / "ai-agents"
    if kb_root.exists():
        from collections import defaultdict

        kb_stats = defaultdict(int)
        total_files = 0

        for agent_dir in kb_root.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
                for cat_dir in agent_dir.iterdir():
                    if cat_dir.is_dir():
                        kb_files = list(cat_dir.glob("*.md"))
                        if kb_files:
                            kb_stats[agent_dir.name] += len(kb_files)
                            total_files += len(kb_files)

        logger.info(f"  Total KB files: {total_files}")
        if kb_stats:
            logger.info("  By agent:")
            for agent, count in sorted(kb_stats.items())[:10]:
                logger.info(f"    {agent}: {count} files")
    else:
        logger.warning("  Knowledge base directory not found")

    # Recent activity
    logger.info("\n📊 Recent Activity:")
    log_dir = Config.LOG_PATH
    if log_dir.exists():
        log_files = list(log_dir.glob("pipeline_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"  Latest log: {latest_log.name}")
            logger.info(f"  Size: {latest_log.stat().st_size / 1024:.1f} KB")
        else:
            logger.info("  No log files found")
    else:
        logger.warning("  Log directory not found")

    logger.info("\n✓ Status check complete")


def cmd_list_creators(args):
    """List all creators in database"""
    import json

    creator_db_path = Config.METADATA_PATH / "creator-database.json"

    if not creator_db_path.exists():
        logger.error("Creator database not found")
        sys.exit(1)

    with open(creator_db_path) as f:
        data = json.load(f)
        creators = data.get('creators', [])

    logger.info(f"\n📚 Knowledge Base Creators ({len(creators)} total)\n")

    # Group by priority
    by_priority = {}
    for c in creators:
        priority = c.get('priority', 'unknown')
        by_priority.setdefault(priority, []).append(c)

    for priority in ['critical', 'high', 'medium', 'low']:
        if priority in by_priority:
            logger.info(f"\n{priority.upper()} Priority ({len(by_priority[priority])}):")
            for c in by_priority[priority]:
                logger.info(f"  • {c.get('name')} ({c.get('id')})")
                logger.info(f"    Focus: {c.get('focus', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Base Pipeline Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with mock data
  python manage.py test-mock

  # Test with a specific video
  python manage.py test "https://www.youtube.com/watch?v=VIDEO_ID"

  # Scan a specific creator
  python manage.py scan-creator instasd

  # Scan all critical priority creators
  python manage.py scan-all --priority critical

  # Start automated scheduler
  python manage.py schedule

  # Show status
  python manage.py status

  # List all creators
  python manage.py list-creators
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # test command
    test_parser = subparsers.add_parser('test', help='Test with a single video')
    test_parser.add_argument('url', help='YouTube video URL')
    test_parser.set_defaults(func=cmd_test_single)

    # test-mock command
    test_mock_parser = subparsers.add_parser('test-mock', help='Test with mock data')
    test_mock_parser.set_defaults(func=cmd_test_mock)

    # scan-creator command
    scan_creator_parser = subparsers.add_parser('scan-creator', help='Scan a specific creator')
    scan_creator_parser.add_argument('creator_id', help='Creator ID or name')
    scan_creator_parser.set_defaults(func=cmd_scan_creator)

    # scan-all command
    scan_all_parser = subparsers.add_parser('scan-all', help='Scan all creators')
    scan_all_parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'],
                                 help='Filter by priority')
    scan_all_parser.set_defaults(func=cmd_scan_all)

    # schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Start automated scheduler')
    schedule_parser.set_defaults(func=cmd_schedule)

    # status command
    status_parser = subparsers.add_parser('status', help='Show pipeline status')
    status_parser.set_defaults(func=cmd_status)

    # list-creators command
    list_parser = subparsers.add_parser('list-creators', help='List all creators')
    list_parser.set_defaults(func=cmd_list_creators)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()

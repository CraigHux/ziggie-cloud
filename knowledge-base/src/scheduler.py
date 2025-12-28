"""
Automated Scheduler - Weekly scans of all creators
Phase 4 implementation
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
from pathlib import Path

from config import Config
from logger import logger, log_section
from video_scanner import VideoScanner
from transcript_extractor import TranscriptExtractor
from ai_analyzer import AIAnalyzer
from knowledge_writer import KnowledgeWriter


class KnowledgePipelineScheduler:
    """Automated scheduling for knowledge extraction"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.scanner = VideoScanner()
        self.extractor = TranscriptExtractor()
        self.analyzer = AIAnalyzer()
        self.writer = KnowledgeWriter()

        self.creator_db_path = Config.METADATA_PATH / "creator-database.json"
        self.load_creators()

    def load_creators(self):
        """Load creator database"""
        if self.creator_db_path.exists():
            with open(self.creator_db_path, 'r') as f:
                data = json.load(f)
                self.creators = data.get('creators', [])
        else:
            logger.warning(f"Creator database not found: {self.creator_db_path}")
            self.creators = []

    def scan_creator(self, creator_info):
        """Scan and process videos from a single creator"""

        creator_name = creator_info.get('name', 'Unknown')
        priority = creator_info.get('priority', 'medium')
        max_videos = creator_info.get('scan_last_n_videos', Config.MAX_VIDEOS_PER_SCAN)

        log_section(f"Scanning: {creator_name}")
        logger.info(f"Priority: {priority}")
        logger.info(f"Max videos: {max_videos}")

        try:
            # Find recent videos
            videos = self.scanner.scan_creator(creator_info)

            if not videos:
                logger.warning(f"No videos found for {creator_name}")
                return 0

            logger.info(f"Found {len(videos)} recent videos")

            processed_count = 0

            for video_data in videos[:max_videos]:
                try:
                    video_id = video_data.get('video_id')
                    title = video_data.get('title', 'Untitled')

                    logger.info(f"\nProcessing: {title} ({video_id})")

                    # Extract transcript
                    transcript_result = self.extractor.get_transcript(video_id)

                    if not transcript_result:
                        logger.warning(f"  Skipped: No transcript available")
                        continue

                    logger.info(f"  Transcript: {len(transcript_result['text'])} chars")

                    # Analyze with Claude
                    insights = self.analyzer.analyze_transcript(
                        video_data=video_data,
                        transcript_text=transcript_result['text'],
                        creator_info=creator_info
                    )

                    if not insights:
                        logger.warning(f"  Skipped: Analysis failed")
                        continue

                    confidence = insights.get('confidence_score', 0)
                    logger.info(f"  Confidence: {confidence}%")

                    # Validate confidence
                    if confidence < Config.CONFIDENCE_THRESHOLD:
                        logger.warning(f"  Skipped: Below threshold ({Config.CONFIDENCE_THRESHOLD}%)")
                        continue

                    # Write to agent KBs
                    written_files = self.writer.write_insights(
                        insights=insights,
                        video_data=video_data,
                        creator_info=creator_info
                    )

                    logger.info(f"  Written to {len(written_files)} agent(s)")
                    processed_count += 1

                except Exception as e:
                    logger.error(f"  Error processing video: {e}")
                    continue

            logger.info(f"\nCompleted: {creator_name}")
            logger.info(f"Processed: {processed_count}/{len(videos)} videos")

            return processed_count

        except Exception as e:
            logger.error(f"Error scanning {creator_name}: {e}")
            return 0

    def scan_all_creators(self, priority_filter=None):
        """Scan all creators (optionally filtered by priority)"""

        log_section("AUTOMATED KNOWLEDGE SCAN")

        logger.info(f"Total creators: {len(self.creators)}")
        if priority_filter:
            logger.info(f"Priority filter: {priority_filter}")

        total_processed = 0
        total_creators = 0

        for creator in self.creators:
            priority = creator.get('priority', 'medium')

            # Filter by priority if specified
            if priority_filter and priority != priority_filter:
                continue

            total_creators += 1
            processed = self.scan_creator(creator)
            total_processed += processed

        log_section("SCAN COMPLETE")
        logger.info(f"Creators scanned: {total_creators}")
        logger.info(f"Videos processed: {total_processed}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return total_processed

    def schedule_scans(self):
        """Set up automated scanning schedules"""

        log_section("SCHEDULING AUTOMATED SCANS")

        # Critical creators: Every 3 days
        self.scheduler.add_job(
            func=lambda: self.scan_all_creators('critical'),
            trigger=CronTrigger(day='*/3', hour=9, minute=0),
            id='scan_critical',
            name='Scan Critical Creators',
            replace_existing=True
        )
        logger.info("Scheduled: Critical creators (every 3 days at 9 AM)")

        # High priority: Weekly (Monday 9 AM)
        self.scheduler.add_job(
            func=lambda: self.scan_all_creators('high'),
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='scan_high',
            name='Scan High Priority Creators',
            replace_existing=True
        )
        logger.info("Scheduled: High priority (Mondays at 9 AM)")

        # Medium priority: Biweekly (1st & 15th at 10 AM)
        self.scheduler.add_job(
            func=lambda: self.scan_all_creators('medium'),
            trigger=CronTrigger(day='1,15', hour=10, minute=0),
            id='scan_medium',
            name='Scan Medium Priority Creators',
            replace_existing=True
        )
        logger.info("Scheduled: Medium priority (1st & 15th at 10 AM)")

        # Low priority: Monthly (1st of month at 11 AM)
        self.scheduler.add_job(
            func=lambda: self.scan_all_creators('low'),
            trigger=CronTrigger(day=1, hour=11, minute=0),
            id='scan_low',
            name='Scan Low Priority Creators',
            replace_existing=True
        )
        logger.info("Scheduled: Low priority (1st of month at 11 AM)")

        logger.info("\nScheduler configured successfully!")
        logger.info("The system will now run automated scans based on creator priority.")

    def start(self):
        """Start the scheduler"""

        self.schedule_scans()

        logger.info("\nStarting scheduler...")
        logger.info("Press Ctrl+C to stop\n")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\nScheduler stopped by user")
            self.scheduler.shutdown()


def manual_scan(priority=None):
    """Run a manual scan immediately"""

    scheduler = KnowledgePipelineScheduler()
    scheduler.scan_all_creators(priority_filter=priority)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Manual scan mode
        if sys.argv[1] == "--manual":
            priority = sys.argv[2] if len(sys.argv) > 2 else None
            logger.info(f"Running manual scan (priority: {priority or 'all'})")
            manual_scan(priority)
        elif sys.argv[1] == "--help":
            print("""
Knowledge Pipeline Scheduler

Usage:
  python scheduler.py                    # Start automated scheduler
  python scheduler.py --manual           # Run manual scan (all creators)
  python scheduler.py --manual critical  # Run manual scan (critical only)
  python scheduler.py --manual high      # Run manual scan (high priority only)
  python scheduler.py --help             # Show this help

Scheduled scans:
  Critical: Every 3 days at 9 AM
  High:     Mondays at 9 AM
  Medium:   1st & 15th at 10 AM
  Low:      1st of month at 11 AM
            """)
    else:
        # Start automated scheduler
        scheduler = KnowledgePipelineScheduler()
        scheduler.start()

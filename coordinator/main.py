"""
Agent Deployment Coordinator
Main entry point for the coordinator service
"""

import sys
import signal
import logging
from pathlib import Path
from datetime import datetime
from .watcher import DeploymentWatcher


def setup_logging(log_dir: Path):
    """Configure logging"""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log file with timestamp
    log_file = log_dir / f"coordinator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def main():
    """Main entry point"""
    # Deployment directory
    deployment_dir = Path(__file__).parent.parent / "agent-deployment"
    log_dir = deployment_dir / "logs"

    # Setup logging
    logger = setup_logging(log_dir)

    logger.info("=" * 60)
    logger.info("ZIGGIE Agent Deployment Coordinator")
    logger.info("File-Based MVP v1.0")
    logger.info("=" * 60)
    logger.info(f"Deployment Directory: {deployment_dir}")
    logger.info(f"Log Directory: {log_dir}")

    # Create watcher
    watcher = DeploymentWatcher(
        deployment_dir=deployment_dir,
        log_callback=logger.info
    )

    # Handle shutdown signals
    def signal_handler(sig, frame):
        logger.info("\n" + "=" * 60)
        logger.info("Shutdown signal received")
        logger.info("=" * 60)
        watcher.stop()
        logger.info("Coordinator stopped successfully")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start coordinator
    try:
        logger.info("Starting coordinator service...")
        watcher.run()
    except Exception as e:
        logger.error(f"Coordinator error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

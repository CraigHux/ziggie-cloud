"""
Logging configuration for Knowledge Base Pipeline
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

from config import Config


def setup_logger(name="knowledge_pipeline"):
    """Set up logger with console and file handlers"""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Remove existing handlers
    logger.handlers = []

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if Config.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if Config.LOG_TO_FILE:
        log_file = Config.LOG_PATH / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=Config.MAX_LOG_FILE_SIZE,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()


def log_section(title):
    """Log a section header"""
    logger.info("=" * 60)
    logger.info(f"  {title}")
    logger.info("=" * 60)

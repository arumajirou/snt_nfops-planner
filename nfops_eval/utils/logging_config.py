"""logging_config.py - ÉçÉOê›íË"""
from pathlib import Path
from loguru import logger
import sys


def setup_logging(log_dir: Path = Path("logs"), level: str = "INFO"):
    """ÉçÉOê›íË"""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level=level, format="^<green^>{time:HH:mm:ss}^</green^> ^| ^<level^>{level}^</level^> ^| {message}")
    logger.add(log_dir / "eval_{time:YYYYMMDD}.log", rotation="1 day")

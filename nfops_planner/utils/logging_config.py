"""logging_config.py - ログ設宁E""
from pathlib import Path
from loguru import logger
import sys


def setup_logging(log_dir: Path = Path("logs"), level: str = "INFO"):
    """ログ設宁E""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level=level)
    logger.add(log_dir / "planner_{time}.log", rotation="1 day")
    logger.info("Logging configured")

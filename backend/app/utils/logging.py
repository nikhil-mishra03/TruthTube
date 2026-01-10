"""
Logging configuration for TruthTube.
Provides structured logging with appropriate verbosity levels.
"""
import logging
import sys
from typing import Optional

from app.config import get_settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configure application logging.
    
    Args:
        log_level: Override log level (uses settings if not provided)
    
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Create formatter - concise but informative
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    return logging.getLogger("truthtube")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"truthtube.{name}")

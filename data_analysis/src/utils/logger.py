"""
Logger utility for the AI thesis analysis.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import LOG_DIR, LOG_LEVEL, LOG_FORMAT


class LoggerSetup:
    """Sets up logging for the application."""
    
    def __init__(self, log_dir: str = LOG_DIR):
        """
        Initialize logger setup.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
    def get_logger(self, 
                   name: str, 
                   log_file: Optional[str] = None,
                   level: str = LOG_LEVEL) -> logging.Logger:
        """
        Get a configured logger with both file and console handlers.
        
        Args:
            name: Name of the logger
            log_file: Specific log file name (if None, uses name)
            level: Logging level
            
        Returns:
            Configured logger
        """
        # Convert string level to logging constant
        log_level = getattr(logging, level.upper())
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # Create formatters
        file_formatter = logging.Formatter(LOG_FORMAT)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Create file handler if log_file specified or generated
        if log_file is None:
            log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(
            self.log_dir / log_file,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


# Singleton instance for easy access
logger_setup = LoggerSetup()

def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name
        log_file: Optional log file name
        
    Returns:
        Configured logger
    """
    return logger_setup.get_logger(name, log_file)
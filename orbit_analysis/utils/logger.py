import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoggerSetup:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        
    def setup_logger(self, 
                    logger_name: str, 
                    log_file: Optional[str] = None,
                    level: int = logging.INFO) -> logging.Logger:
        """
        Set up a logger with both file and console handlers.
        
        Args:
            logger_name (str): Name of the logger
            log_file (str, optional): Specific log file name. If None, uses logger_name
            level (int): Logging level
            
        Returns:
            logging.Logger: Configured logger
        """
        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = []
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        
        # Create file handler
        if log_file is None:
            log_file = f"{logger_name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(
            self.log_dir / log_file,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
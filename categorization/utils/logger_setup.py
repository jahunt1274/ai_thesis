import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LoggerSetup:
    """Handles the setup and configuration of loggers."""
    
    def __init__(self, log_dir):
        """
        Initialize the logger setup.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
    
    def setup_logger(self, name, log_file=None, level=logging.INFO):
        """
        Set up a logger with both console and file handlers.
        
        Args:
            name: Name of the logger
            log_file: Optional filename for the log file
            level: Logging level
            
        Returns:
            logging.Logger: Configured logger
        """
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # If a log file is specified, create a file handler
        if log_file:
            # If log_file doesn't have a full path, add the log directory
            if not os.path.isabs(log_file):
                log_file = os.path.join(self.log_dir, log_file)
                
            # Create rotating file handler (10 MB max size, keep 5 backups)
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def get_timestamp():
        """Get a formatted timestamp for filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
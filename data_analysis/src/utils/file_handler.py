"""
File handling utilities for the AI thesis analysis.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.utils.logger import get_logger

logger = get_logger("file_handler")


class FileHandler:
    """Handles file operations for the analysis system."""
    
    @staticmethod
    def load_json(filepath: str) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Loaded JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        logger.info(f"Loading JSON from {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded JSON from {filepath}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filepath: Path to save the file
            indent: JSON indentation level
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving JSON to {filepath}")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"Successfully saved JSON to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def generate_filename(
            output_dir: str, 
            prefix: Optional[str] = None, 
            suffix: Optional[str] = None, 
            extension: str = "json") -> str:
        """
        Generate a timestamped filename.
        
        Args:
            output_dir: Directory for the file
            prefix: Optional prefix for the filename
            suffix: Optional suffix for the filename
            extension: File extension (default: json)
            
        Returns:
            Full filepath with timestamp
        """
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Build filename
        filename_parts = []
        if prefix:
            filename_parts.append(prefix)
        
        filename_parts.append(timestamp)
        
        if suffix:
            filename_parts.append(suffix)
        
        filename = "_".join(filename_parts) + f".{extension}"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        return os.path.join(output_dir, filename)
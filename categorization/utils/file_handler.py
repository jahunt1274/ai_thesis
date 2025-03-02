import json
import os
from datetime import datetime, timedelta, timezone

class FileHandler:
    """Handles all file operations for the categorization process."""
    
    @staticmethod
    def load_json(filepath):
        """Load data from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Error loading JSON file {filepath}: {e}")

    @staticmethod
    def save_json(data, filepath, indent=2):
        """Save data to a JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=indent)
            return True
        except Exception as e:
            raise IOError(f"Error saving JSON file {filepath}: {e}")
    
    @staticmethod
    def generate_filename(output_dir, prefix=None, suffix=None, extension="json"):
        """
        Generate a dynamic filename with optional prefix/suffix.
        
        Args:
            output_dir: Directory where file will be saved
            prefix: Optional prefix to add before the timestamp
            suffix: Optional suffix to add after the timestamp
            extension: File extension (default: json)
            
        Returns:
            str: The generated full filepath
        """
        # Use EST timezone for consistency
        offset_hours = -5
        est = timezone(timedelta(hours=offset_hours))
        local_time = datetime.now(est)
        timestamp = local_time.strftime("%Y%m%d_%H%M")
        
        # Build filename parts
        filename_parts = []
        if prefix:
            filename_parts.append(prefix)
        filename_parts.append(timestamp)
        if suffix:
            filename_parts.append(suffix)
        
        # Join parts with underscores and add extension
        filename = "_".join(filename_parts) + f".{extension}"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        return os.path.join(output_dir, filename)
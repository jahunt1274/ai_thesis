"""
File handling utilities for the AI thesis analysis.
"""

import json
import os
import csv
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, List, Optional

from src.utils.logger import get_logger

logger = get_logger("file_handler")


class FileHandler:
    """Handles file operations for the analysis system."""

    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize the file handler.

        Args:
            encoding: Default encoding for file operations
        """
        self.encoding = encoding

    def load_json(self, filepath: str) -> Any:
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
        self.ensure_file_exists(filepath)

        try:
            with open(filepath, "r", encoding=self.encoding) as f:
                data = json.load(f)

            logger.info(f"Successfully loaded JSON from {filepath}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {str(e)}")
            raise

    def save_json(self, data: Any, filepath: str, indent: int = 2) -> bool:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            filepath: Path to save the file
            indent: JSON indentation level

        Returns:
            True if successful, False otherwise
        """
        self.ensure_directory_exists(os.path.dirname(filepath))

        try:
            with open(filepath, "w", encoding=self.encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            logger.info(f"Successfully saved JSON to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {str(e)}")
            return False

    def load_csv(self, filepath: str, as_dict: bool = True, **kwargs) -> List:
        """
        Load data from a CSV file with standardized error handling.

        Args:
            filepath: Path to the CSV file
            as_dict: Whether to return data as list of dictionaries (True) or list of lists (False)
            **kwargs: Additional parameters for csv.reader/DictReader

        Returns:
            List of records from the CSV file

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.ensure_file_exists(filepath)

        try:
            with open(filepath, "r", encoding=self.encoding, newline="") as f:
                if as_dict:
                    reader = csv.DictReader(f, **kwargs)
                else:
                    reader = csv.reader(f, **kwargs)
                data = list(reader)

            logger.info(f"Successfully loaded CSV from {filepath}")
            return data

        except Exception as e:
            logger.error(f"Error loading CSV from {filepath}: {str(e)}")
            raise

    def save_csv(
        self,
        data: List,
        filepath: str,
        fieldnames: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        Save data to a CSV file with standardized error handling.

        Args:
            data: List of records to save
            filepath: Path to save the file
            fieldnames: List of field names for the CSV header
            **kwargs: Additional parameters for csv.writer/DictWriter

        Returns:
            True if successful, False otherwise
        """
        self.ensure_directory_exists(os.path.dirname(filepath))

        try:
            with open(filepath, "w", encoding=self.encoding, newline="") as f:
                if isinstance(data[0] if data else {}, dict) and fieldnames is None:
                    # Infer fieldnames from the first record if not provided
                    fieldnames = list(data[0].keys())

                if fieldnames:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, **kwargs)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    writer = csv.writer(f, **kwargs)
                    writer.writerows(data)

            logger.info(f"Successfully saved CSV to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving CSV to {filepath}: {str(e)}")
            return False

    def load_yaml(self, filepath: str) -> Any:
        """
        Load data from a YAML file with standardized error handling.

        Args:
            filepath: Path to the YAML file

        Returns:
            Loaded YAML data

        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the file contains invalid YAML
        """
        self.ensure_file_exists(filepath)

        try:
            with open(filepath, "r", encoding=self.encoding) as f:
                data = yaml.safe_load(f)

            logger.info(f"Successfully loaded YAML from {filepath}")
            return data

        except ImportError:
            logger.error(
                "PyYAML is not installed. Please install it with 'pip install pyyaml'."
            )
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {filepath}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading YAML from {filepath}: {str(e)}")
            raise

    def save_yaml(self, data: Any, filepath: str, **kwargs) -> bool:
        """
        Save data to a YAML file with standardized error handling.

        Args:
            data: Data to save
            filepath: Path to save the file
            **kwargs: Additional parameters for yaml.dump

        Returns:
            True if successful, False otherwise
        """
        self.ensure_directory_exists(os.path.dirname(filepath))

        try:
            with open(filepath, "w", encoding=self.encoding) as f:
                yaml.dump(data, f, **kwargs)

            logger.info(f"Successfully saved YAML to {filepath}")
            return True

        except ImportError:
            logger.error(
                "PyYAML is not installed. Please install it with 'pip install pyyaml'."
            )
            return False
        except Exception as e:
            logger.error(f"Error saving YAML to {filepath}: {str(e)}")
            return False

    def load_text(self, filepath: str) -> str:
        """
        Load text from a file with standardized error handling.

        Args:
            filepath: Path to the text file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.ensure_file_exists(filepath)

        try:
            with open(filepath, "r", encoding=self.encoding) as f:
                data = f.read()

            logger.info(f"Successfully loaded text from {filepath}")
            return data

        except Exception as e:
            logger.error(f"Error loading text from {filepath}: {str(e)}")
            raise

    def save_text(self, text: str, filepath: str) -> bool:
        """
        Save text to a file with standardized error handling.

        Args:
            text: Text to save
            filepath: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        self.ensure_directory_exists(os.path.dirname(filepath))

        try:
            with open(filepath, "w", encoding=self.encoding) as f:
                f.write(text)

            logger.info(f"Successfully saved text to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving text to {filepath}: {str(e)}")
            return False

    def generate_filename(
        self,
        output_dir: str,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        extension: str = "json",
        add_timestamp: bool = True,
    ) -> str:
        """
        Generate a timestamped filename.

        Args:
            output_dir: Directory for the file
            prefix: Optional prefix for the filename
            suffix: Optional suffix for the filename
            extension: File extension (default: json)
            add_timestamp: Whether to add a timestamp to the filename

        Returns:
            Full filepath with timestamp
        """
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if add_timestamp else ""

        # Build filename
        filename_parts = []
        if prefix:
            filename_parts.append(prefix)

        if add_timestamp:
            filename_parts.append(timestamp)

        if suffix:
            filename_parts.append(suffix)

        filename = "_".join(filename_parts) + f".{extension}"

        # Ensure output directory exists
        self.ensure_directory_exists(output_dir)

        return os.path.join(output_dir, filename)

    def list_files(
        self, directory: str, pattern: Optional[str] = None, recursive: bool = False
    ) -> List[str]:
        """
        List files in a directory.

        Args:
            directory: Directory path
            pattern: Optional glob pattern for filtering files
            recursive: Whether to search recursively

        Returns:
            List of file paths
        """
        self.ensure_directory_exists(directory)

        path = Path(directory)

        if pattern:
            if recursive:
                files = list(path.glob(f"**/{pattern}"))
            else:
                files = list(path.glob(pattern))
        else:
            if recursive:
                files = [f for f in path.rglob("*") if f.is_file()]
            else:
                files = [f for f in path.glob("*") if f.is_file()]

        return [str(f) for f in files]

    def get_latest_file(
        self, directory: str, pattern: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the most recently modified file in a directory.

        Args:
            directory: Directory path
            pattern: Optional glob pattern for filtering files

        Returns:
            Path to the latest file, or None if no files found
        """
        files = self.list_files(directory, pattern)

        if not files:
            return None

        # Sort by modification time (newest first)
        return max(files, key=os.path.getmtime)

    def ensure_file_exists(self, filepath: str) -> None:
        """
        Ensure a file exists.

        Args:
            filepath: Path to the file

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.isfile(filepath):
            error_msg = f"File not found: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    def ensure_directory_exists(self, directory: str) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path
        """
        if directory:
            os.makedirs(directory, exist_ok=True)

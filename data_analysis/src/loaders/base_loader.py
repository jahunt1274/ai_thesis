"""
Data loaders for the AI thesis analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generic
from src.constants.data_constants import T
from src.utils import FileHandler, get_logger

logger = get_logger("data_loader")


class BaseLoader(Generic[T], ABC):
    """Abstract base class for all data loaders with common functionality."""

    def __init__(self, file_path: str):
        """
        Initialize the base loader.

        Args:
            file_path: Path to the data file
        """
        self.file_path = file_path
        self.file_handler = FileHandler()
        self.raw_data = None
        self.processed_data = None
        self.logger = get_logger(self.__class__.__name__.lower())

    def load(self) -> List[T]:
        """
        Load data from the file.

        Returns:
            List of data records
        """
        self.logger.info(f"Loading data from {self.file_path}")
        self.raw_data = self.file_handler.load_json(self.file_path)

        # Check data format
        if not isinstance(self.raw_data, list):
            raise ValueError(
                f"{self.__class__.__name__} data must be a list of objects"
            )

        self.logger.info(f"Loaded {len(self.raw_data)} records")
        return self.raw_data

    def process(self) -> List[T]:
        """
        Process raw data into a standardized format.

        Returns:
            List of processed records
        """
        if self.raw_data is None:
            self.load()

        self.logger.info(f"Processing {len(self.raw_data)} records")
        self.processed_data = []

        for item in self.raw_data:
            processed_item = self._process_item(item)
            if processed_item:
                self.processed_data.append(processed_item)

        self.logger.info(f"Processed {len(self.processed_data)} records")
        return self.processed_data

    @abstractmethod
    def _process_item(self, item: Dict[str, Any]) -> Optional[T]:
        """
        Process a single data record.

        Args:
            item: Raw data record

        Returns:
            Processed data record, or None if invalid
        """
        pass

    @staticmethod
    def _extract_id(id_value: Any) -> str:
        """
        Extract ID from various formats.

        Args:
            id_value: ID value in various possible formats

        Returns:
            Standardized ID string
        """
        if isinstance(id_value, dict) and "$oid" in id_value:
            return id_value["$oid"]
        return str(id_value)

    @staticmethod
    def _extract_timestamp(timestamp: Any) -> Optional[str]:
        """
        Extract timestamp from various formats.

        Args:
            timestamp: Timestamp in various possible formats

        Returns:
            Standardized timestamp string
        """
        if not timestamp:
            return None

        if isinstance(timestamp, dict) and "$date" in timestamp:
            return timestamp["$date"]

        return str(timestamp)

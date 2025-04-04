"""
Date utility functions for data analysis.
"""

import ast
from datetime import datetime, timezone
from typing import Optional, Any, List, Dict


class DateUtils:
    """Utility class for date-related operations."""

    @staticmethod
    def parse_date(date_string: str) -> Optional[datetime]:
        """
        Parse a date string in various formats.

        Args:
            date_string: Date string to parse

        Returns:
            Parsed datetime object, or None if parsing fails
        """
        if not date_string:
            return None

        # Try various date formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with milliseconds
            "%Y-%m-%dT%H:%M:%SZ",  # ISO format without milliseconds
            "%Y-%m-%d",  # Simple date format
            "%Y/%m/%d",  # Alternative date format
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def extract_timestamp(timestamp: Any) -> Optional[str]:
        """
        Extract timestamp from various formats.

        Args:
            timestamp: Timestamp in various possible formats

        Returns:
            Standardized timestamp string or None if extraction fails
        """
        if not timestamp:
            return None

        # Handle dict with $date key
        if isinstance(timestamp, dict) and "$date" in timestamp:
            return timestamp["$date"]

        # Handle other formats by converting to string
        return str(timestamp)

    @staticmethod
    def get_days_since(
        date_value: Any, end_date: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Calculate days between a date and the end date (default: now).

        Args:
            date_value: Date value in various possible formats
            end_date: End date for calculation (default: now)

        Returns:
            Number of days between dates, or None if calculation fails
        """
        if not date_value:
            return None

        # Set default end date to now if not provided
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        try:
            # Case 1 & 2: Integer or string representing epoch time
            if isinstance(date_value, (int, float)) or (
                isinstance(date_value, str) and date_value.isdigit()
            ):
                epoch_time = float(date_value)
                # Check if the number needs to be divided by 1000 (milliseconds to seconds)
                if epoch_time > 1e11:  # Large values likely represent milliseconds
                    epoch_time /= 1000
                # Use fromtimestamp with timezone to get aware datetime
                start_date = datetime.fromtimestamp(epoch_time, tz=timezone.utc)

            # Case 3: Dict with $numberLong key
            elif isinstance(date_value, dict) and "$numberLong" in date_value:
                epoch_time = float(date_value["$numberLong"])
                # Check if the number needs to be divided by 1000 (milliseconds to seconds)
                if epoch_time > 1e11:  # Large values likely represent milliseconds
                    epoch_time /= 1000
                start_date = datetime.fromtimestamp(epoch_time, tz=timezone.utc)

            # Case 4: Dict with $date key containing ISO format string
            elif isinstance(date_value, dict) and "$date" in date_value:
                date_str = date_value["$date"]
                start_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # Case where date_value is a string but not a numeric string
            elif isinstance(date_value, str):
                # Check if it's an ISO format string
                if "T" in date_value:
                    start_date = datetime.fromisoformat(
                        date_value.replace("Z", "+00:00")
                    )
                # Case where date_value is a string of dict with key '$numberLong"
                elif "$numberLong" in date_value:
                    date_dict = ast.literal_eval(date_value)
                    epoch_time = float(date_dict["$numberLong"])
                    if epoch_time > 1e11:  # Large values likely represent milliseconds
                        epoch_time /= 1000
                    start_date = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
                else:
                    # For date-only formats, create a naive datetime then make it aware
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]:
                        try:
                            naive_date = datetime.strptime(date_value, fmt)
                            start_date = naive_date.replace(tzinfo=timezone.utc)
                            break
                        except ValueError:
                            continue
                    else:
                        return None  # Could not parse with any format

            else:
                return None  # Unrecognized format

            # Calculate days since login
            days_since = (end_date - start_date).days
            return days_since

        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def group_by_month(date_list: List[datetime]) -> Dict[str, List[datetime]]:
        """
        Group dates by month.

        Args:
            date_list: List of datetime objects

        Returns:
            Dictionary mapping month strings (YYYY-MM) to lists of dates
        """
        result = {}
        for date in date_list:
            if date:
                month_key = date.strftime("%Y-%m")
                if month_key not in result:
                    result[month_key] = []
                result[month_key].append(date)
        return result

    @staticmethod
    def month_sort_key(month_str: str) -> tuple:
        """
        Generate a sortable key for month strings (YYYY-MM).

        Args:
            month_str: Month string in YYYY-MM format

        Returns:
            Tuple of (year, month) for sorting
        """
        try:
            year, month = month_str.split("-")
            return int(year), int(month)
        except (ValueError, IndexError):
            return 0, 0

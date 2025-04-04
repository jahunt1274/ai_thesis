"""
Data grouping utility functions for data analysis.
"""

from collections import defaultdict
from typing import List, Dict, Any, Callable, Tuple, TypeVar

T = TypeVar("T")  # Generic type for the data items


class DataGroupingUtils:
    """Utility class for data grouping operations."""

    @staticmethod
    def group_by_key(
        data: List[Dict[str, Any]], key: str
    ) -> Dict[Any, List[Dict[str, Any]]]:
        """
        Group data items by a specific key.

        Args:
            data: List of dictionaries to group
            key: Key to group by

        Returns:
            Dictionary mapping key values to lists of data items
        """
        grouped = defaultdict(list)

        for item in data:
            key_value = item.get(key)
            if key_value is not None:
                grouped[key_value].append(item)

        return dict(grouped)

    @staticmethod
    def group_by_func(
        data: List[T], key_func: Callable[[T], Any]
    ) -> Dict[Any, List[T]]:
        """
        Group data items by a function of each item.

        Args:
            data: List of items to group
            key_func: Function that takes an item and returns a key value

        Returns:
            Dictionary mapping key values to lists of data items
        """
        grouped = defaultdict(list)

        for item in data:
            key_value = key_func(item)
            if key_value is not None:
                grouped[key_value].append(item)

        return dict(grouped)

    @staticmethod
    def group_values_by_range(
        values: List[float], ranges: List[Tuple[float, float]]
    ) -> Dict[str, List[float]]:
        """
        Group values into predefined ranges.

        Args:
            values: List of values to group
            ranges: List of (min, max) tuples defining the ranges

        Returns:
            Dictionary mapping range descriptions to lists of values
        """
        grouped = defaultdict(list)

        for value in values:
            for min_val, max_val in ranges:
                if min_val <= value < max_val:
                    range_desc = f"{min_val}-{max_val}"
                    grouped[range_desc].append(value)
                    break
            else:
                # If no range matched, put in "other"
                grouped["other"].append(value)

        return dict(grouped)

    @staticmethod
    def count_by_key(data: List[Dict[str, Any]], key: str) -> Dict[Any, int]:
        """
        Count occurrences of each unique value for a specific key.

        Args:
            data: List of dictionaries to analyze
            key: Key to count by

        Returns:
            Dictionary mapping key values to counts
        """
        counts = defaultdict(int)

        for item in data:
            key_value = item.get(key)
            if key_value is not None:
                counts[key_value] += 1

        return dict(counts)

    @staticmethod
    def count_by_func(data: List[T], key_func: Callable[[T], Any]) -> Dict[Any, int]:
        """
        Count occurrences by a function of each item.

        Args:
            data: List of items to analyze
            key_func: Function that takes an item and returns a key value

        Returns:
            Dictionary mapping key values to counts
        """
        counts = defaultdict(int)

        for item in data:
            key_value = key_func(item)
            if key_value is not None:
                counts[key_value] += 1

        return dict(counts)

    @staticmethod
    def nested_grouping(
        data: List[Dict[str, Any]], primary_key: str, secondary_key: str
    ) -> Dict[Any, Dict[Any, List[Dict[str, Any]]]]:
        """
        Perform nested grouping on two levels.

        Args:
            data: List of dictionaries to group
            primary_key: First level grouping key
            secondary_key: Second level grouping key

        Returns:
            Nested dictionary with two levels of grouping
        """
        result = defaultdict(lambda: defaultdict(list))

        for item in data:
            primary = item.get(primary_key)
            secondary = item.get(secondary_key)

            if primary is not None and secondary is not None:
                result[primary][secondary].append(item)

        # Convert defaultdicts to regular dicts
        return {k: dict(v) for k, v in result.items()}

    @staticmethod
    def find_relationships(
        primary_data: List[Dict[str, Any]],
        secondary_data: List[Dict[str, Any]],
        primary_key: str,
        secondary_key: str,
    ) -> Dict[Any, List[Dict[str, Any]]]:
        """
        Find relationships between two datasets using keys.

        Args:
            primary_data: Primary dataset
            secondary_data: Secondary dataset
            primary_key: Key in primary dataset
            secondary_key: Key in secondary dataset

        Returns:
            Dictionary mapping primary key values to matching secondary items
        """
        relationships = defaultdict(list)

        # Create lookup dictionary for faster matching
        secondary_lookup = {}
        for item in secondary_data:
            key_value = item.get(secondary_key)
            if key_value is not None:
                if key_value not in secondary_lookup:
                    secondary_lookup[key_value] = []
                secondary_lookup[key_value].append(item)

        # Find relationships
        for primary_item in primary_data:
            key_value = primary_item.get(primary_key)
            if key_value is not None and key_value in secondary_lookup:
                relationships[key_value].extend(secondary_lookup[key_value])

        return dict(relationships)

    @staticmethod
    def group_into_categories(
        items: List[Dict[str, Any]], key: str, category_map: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group items into categories based on a mapping.

        Args:
            items: List of items to categorize
            key: The key in each item to check against categories
            category_map: Dictionary mapping category names to lists of key values

        Returns:
            Dictionary mapping category names to lists of matching items
        """
        # Create reverse mapping for efficient lookup
        value_to_category = {}
        for category, values in category_map.items():
            for value in values:
                value_to_category[value] = category

        # Group items by category
        categorized = defaultdict(list)
        uncategorized = []

        for item in items:
            key_value = item.get(key)
            if key_value in value_to_category:
                category = value_to_category[key_value]
                categorized[category].append(item)
            else:
                uncategorized.append(item)

        # Add uncategorized items if any
        if uncategorized:
            categorized["uncategorized"] = uncategorized

        return dict(categorized)

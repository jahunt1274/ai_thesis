"""
Category merger for the AI thesis analysis.
"""

from typing import Dict, List, Any, Optional

from src.utils import get_logger, FileHandler

logger = get_logger("category_merger")


class CategoryMerger:
    """Merges pre-categorized ideas with the main idea dataset."""

    def __init__(self, ideas: List[Dict[str, Any]]):
        """
        Initialize the category merger.

        Args:
            ideas: List of idea records to merge categories into
        """
        self.ideas = ideas
        self.file_handler = FileHandler()

    def load_and_merge_categories(self, categorized_file: str) -> List[Dict[str, Any]]:
        """
        Load categorized ideas from a file and merge with main idea dataset.

        Args:
            categorized_file: Path to the categorized ideas JSON file

        Returns:
            List of ideas with categories merged in
        """
        logger.info(f"Loading pre-categorized ideas from {categorized_file}")

        try:
            # Load categorized ideas
            categorized_ideas = self.file_handler.load_json(categorized_file)

            if not isinstance(categorized_ideas, list):
                logger.error("Categorized ideas file must contain a list of objects")
                return self.ideas

            logger.info(f"Loaded {len(categorized_ideas)} pre-categorized ideas")

            # Create lookup map of categorized ideas by ID
            category_map = {}

            for cat_idea in categorized_ideas:
                # Extract ID from different possible formats
                idea_id = self._extract_id(cat_idea.get("_id"))
                category = cat_idea.get("category")

                if idea_id and category:
                    category_map[idea_id] = category

            logger.info(f"Found {len(category_map)} valid categorized ideas")

            # Merge categories into main idea dataset
            merged_ideas = []
            matched_count = 0

            for idea in self.ideas:
                # Extract ID from different possible formats
                idea_id = self._extract_id(idea.get("id"))

                # If a category exists for this ID, add it to the idea
                if idea_id in category_map:
                    idea["category"] = category_map[idea_id]
                    matched_count += 1

                merged_ideas.append(idea)

            logger.info(
                f"Merged categories into {matched_count} out of {len(self.ideas)} ideas"
            )

            return merged_ideas

        except Exception as e:
            logger.error(f"Error merging categories: {str(e)}")
            return self.ideas

    @staticmethod
    def _extract_id(id_value: Any) -> Optional[str]:
        """Extract ID from different possible formats."""
        if id_value is None:
            return None

        # Handle dict format with $oid
        if isinstance(id_value, dict) and "$oid" in id_value:
            return id_value["$oid"]

        # Handle string format
        if isinstance(id_value, str):
            return id_value

        # Handle other formats by converting to string
        return str(id_value)

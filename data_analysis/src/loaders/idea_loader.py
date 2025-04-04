"""
Idea loader for the AI thesis analysis.
"""

from typing import Dict, List, Any, Optional

from config import IDEA_DATA_FILE
from src.constants.data_constants import IdeaDataType
from src.loaders.base_loader import BaseLoader
from src.utils import get_logger

logger = get_logger("idea_loader")


class IdeaLoader(BaseLoader[IdeaDataType]):
    """Loads and processes idea data."""

    def __init__(self, file_path: str = IDEA_DATA_FILE):
        """
        Initialize the idea loader.

        Args:
            file_path: Path to the idea data file
        """
        super().__init__(file_path)

    def _process_item(self, idea: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single idea record.

        Args:
            idea: Raw idea record

        Returns:
            Processed idea record, or None if invalid
        """
        try:
            # Basic validation
            if not idea:
                self.logger.warning("Empty idea record")
                return None

            # Extract fields
            idea_id = self._extract_id(idea.get("_id"))

            # Extract and process title and description
            raw_title = idea.get("title", "").strip()
            raw_description = idea.get("description", "").strip()

            # Handle the different scenarios for title and description
            if raw_title and raw_description:
                # Both title and description are non-empty, join with a colon
                title = f"{raw_title}: {raw_description}"
                description = raw_description
            elif raw_title and not raw_description:
                # Only title is non-empty
                title = raw_title
                description = raw_description
            elif not raw_title and raw_description:
                # Only description is non-empty, use it for both
                title = raw_description
                description = raw_description
            else:
                # Both are empty, skip idea
                self.logger.warning(f"Idea {idea_id} has no content, skipping")
                return None

            # Extract timestamps
            created_date = self._extract_timestamp(idea.get("created"))

            # Create processed idea
            processed_idea = {
                "id": idea_id,
                "title": title,
                "description": description,
                "created_date": created_date,
                "owner": idea.get("owner"),
                "ranking": idea.get("ranking", 0),
                "total_progress": idea.get("total_progress", 0),
                "de_progress": self._extract_progress(
                    idea, "disciplined-entrepreneurship"
                ),
                "st_progress": self._extract_progress(idea, "startup-tactics"),
                "language": idea.get("language", "en"),
                "frameworks": self._determine_frameworks(idea),
                "steps_completed": self._count_completed_steps(idea),
            }

            return processed_idea

        except Exception as e:
            self.logger.error(
                f"Error processing idea {idea.get('_id', 'unknown')}: {str(e)}"
            )
            return None

    @staticmethod
    def _extract_progress(idea: Dict[str, Any], framework: str) -> float:
        """Extract progress for a specific framework."""
        if "progress" not in idea or not idea["progress"]:
            return 0.0

        if framework in idea["progress"]:
            progress = idea["progress"][framework]
            if isinstance(progress, (int, float)):
                return float(progress)

        # Check alternative formats
        if framework == "disciplined-entrepreneurship" and "DE_progress" in idea:
            return float(idea["DE_progress"]) if idea["DE_progress"] else 0.0

        if framework == "startup-tactics" and "ST_progress" in idea:
            return float(idea["ST_progress"]) if idea["ST_progress"] else 0.0

        return 0.0

    @staticmethod
    def _determine_frameworks(idea: Dict[str, Any]) -> List[str]:
        """Determine which frameworks are used by this idea."""
        frameworks = []

        # Check progress fields
        if "progress" in idea and idea["progress"]:
            for framework in idea["progress"]:
                if idea["progress"][framework] > 0:
                    frameworks.append(framework)

        # Check framework-specific progress
        if "DE_progress" in idea and idea["DE_progress"]:
            frameworks.append("disciplined-entrepreneurship")

        if "ST_progress" in idea and idea["ST_progress"]:
            frameworks.append("startup-tactics")

        # Check from_tactics flag
        if "from_tactics" in idea and idea["from_tactics"]:
            frameworks.append("startup-tactics")

        return list(set(frameworks))  # Remove duplicates

    @staticmethod
    def _count_completed_steps(idea: Dict[str, Any]) -> int:
        """Count the number of completed steps for this idea."""
        completed_steps = 0

        for key in idea:
            # Count fields with content that match step patterns
            if (
                key.startswith("market-")
                or key.startswith("beachhead-")
                or key.startswith("define-")
                or key.startswith("chart-")
                or key.startswith("map-")
                or key.startswith("design-")
            ):

                if (
                    idea[key]
                    and isinstance(idea[key], str)
                    and len(idea[key].strip()) > 0
                ):
                    completed_steps += 1

            # Count selected steps which represent user choices
            if (
                key.startswith("selected-")
                and idea[key]
                and isinstance(idea[key], str)
                and len(idea[key].strip()) > 0
            ):
                completed_steps += 1

        return completed_steps

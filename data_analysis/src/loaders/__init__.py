"""
Data loaders for the AI thesis analysis.
"""

from typing import List, Optional, Tuple

from src.constants.data_constants import UserDataType, IdeaDataType, StepDataType
from src.loaders.course_eval_loader import CourseEvaluationLoader
from src.loaders.step_loader import StepLoader
from src.loaders.idea_loader import IdeaLoader
from src.loaders.user_loader import UserLoader
from src.utils import get_logger

logger = get_logger("data_loader")


class DataLoader:
    """Centralized data loader that handles all data types."""

    def __init__(
        self,
        user_file: Optional[str] = None,
        idea_file: Optional[str] = None,
        step_file: Optional[str] = None,
        eval_dir: Optional[str] = None,
    ):
        """
        Initialize the data loader.

        Args:
            user_file: Path to the user data file (optional)
            idea_file: Path to the idea data file (optional)
            step_file: Path to the step data file (optional)
            eval_dir: Directory containing course evaluation files (optional)
        """
        self.user_loader = UserLoader(user_file) if user_file else UserLoader()
        self.idea_loader = IdeaLoader(idea_file) if idea_file else IdeaLoader()
        self.step_loader = StepLoader(step_file) if step_file else StepLoader()
        self.course_eval_loader = (
            CourseEvaluationLoader(eval_dir) if eval_dir else CourseEvaluationLoader()
        )

        self.users = None
        self.ideas = None
        self.steps = None
        self.evaluations = None

        self.logger = get_logger("data_loader")

    def load_and_process_all(
        self,
        on_load_complete=None
    ) -> Tuple[List[UserDataType], List[IdeaDataType], List[StepDataType]]:
        """
        Load and process all data types.

        Returns:
            Tuple of (users, ideas, steps)
        """
        self.logger.info("Loading and processing all data")

        # Process data in parallel would be more efficient,
        # but keeping it sequential for simplicity and because
        # the amount of data is not large
        self.users = self.load_and_process_users()
        self.ideas = self.load_and_process_ideas()
        self.steps = self.load_and_process_steps()
        self.evaluations = self.load_and_process_evaluations()

        self.logger.info(
            f"Loaded {len(self.users)} users, {len(self.ideas)} ideas, {len(self.steps)} steps, {len(self.evaluations)} evaluations"
        )

        if on_load_complete:
            on_load_complete()

        return self.users, self.ideas, self.steps, self.evaluations

    def load_and_process_users(self) -> List[UserDataType]:
        """
        Load and process users.

        Returns:
            List of processed users
        """
        self.logger.info("Loading and processing users")
        self.users = self.user_loader.process()
        return self.users

    def load_and_process_ideas(self) -> List[IdeaDataType]:
        """
        Load and process ideas.

        Returns:
            List of processed ideas
        """
        self.logger.info("Loading and processing ideas")
        self.ideas = self.idea_loader.process()
        return self.ideas

    def load_and_process_steps(self) -> List[StepDataType]:
        """
        Load and process steps.

        Returns:
            List of processed steps
        """
        self.logger.info("Loading and processing steps")
        self.steps = self.step_loader.process()
        return self.steps

    def load_and_process_evaluations(self) -> List[dict]:
        """
        Load and process course evaluations.

        Returns:
            List of processed course evaluations
        """
        self.logger.info("Loading and processing course evaluations")
        self.evaluations = self.course_eval_loader.process()
        return self.evaluations

    def get_data(
        self,
    ) -> Tuple[List[UserDataType], List[IdeaDataType], List[StepDataType]]:
        """
        Get all loaded data or load it if not already loaded.

        Returns:
            Tuple of (users, ideas, steps)
        """
        if (
            self.users is None
            or self.ideas is None
            or self.steps is None
            or self.evaluations is None
        ):
            return self.load_and_process_all()
        return self.users, self.ideas, self.steps, self.evaluations

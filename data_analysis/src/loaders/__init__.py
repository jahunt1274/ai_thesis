"""
Data loaders for the AI thesis analysis.
"""

from typing import Dict, List, Any
from src.loaders.user_loader import UserLoader
from src.loaders.idea_loader import IdeaLoader
from src.loaders.step_loader import StepLoader
from src.loaders.course_eval_loader import CourseEvaluationLoader


class DataLoader:
    """Centralized data loader that handles all data types."""
    
    def __init__(self, 
                 user_file: str = None, 
                 idea_file: str = None, 
                 step_file: str = None):
        """
        Initialize the data loader.
        
        Args:
            user_file: Path to the user data file (optional)
            idea_file: Path to the idea data file (optional)
            step_file: Path to the step data file (optional)
        """
        self.user_loader = UserLoader(user_file) if user_file else UserLoader()
        self.idea_loader = IdeaLoader(idea_file) if idea_file else IdeaLoader()
        self.step_loader = StepLoader(step_file) if step_file else StepLoader()
        
        self.users = None
        self.ideas = None
        self.steps = None
        
    def load_and_process_all(self):
        """
        Load and process all data types.
        
        Returns:
            Tuple of (users, ideas, steps)
        """
        self.users = self.load_and_process_users()
        self.ideas = self.load_and_process_ideas()
        self.steps = self.load_and_process_steps()
        
        return self.users, self.ideas, self.steps
    
    def load_and_process_users(self) -> List[Dict[str, Any]]:
        """
        Load and process users.
        
        Returns:
            List of users
        """
        self.users = self.user_loader.process()
    
    def load_and_process_ideas(self) -> List[Dict[str, Any]]:
        """
        Load and process ideas.
        
        Returns:
            List of ideas
        """
        self.ideas = self.idea_loader.process()
    
    def load_and_process_steps(self) -> List[Dict[str, Any]]:
        """
        Load and process steps.
        
        Returns:
            List of steps
        """
        self.steps = self.step_loader.process()
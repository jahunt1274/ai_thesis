"""
Data loaders for the AI thesis analysis.
"""

from src.loaders.user_loader import UserLoader
from src.loaders.idea_loader import IdeaLoader
from src.loaders.step_loader import StepLoader


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
        self.users = self.user_loader.process()
        self.ideas = self.idea_loader.process()
        self.steps = self.step_loader.process()
        
        return self.users, self.ideas, self.steps
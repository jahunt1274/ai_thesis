from typing import List
from constants import IDEA_CATEGORIES

class PromptHandler:
    def __init__(self, logger = None):
        self.logger = logger

    def create_idea_categorization_prompt(self, categories: List = None, batch_content: List = []) -> str:
        """
        Create a prompt for idea categorization based on categories and batch contents.
        
        Args:
            categories: List of available categories
            batch_content: List of ideas in the batch 
            
        Returns:
            String prompt for API client
        """
        prompt_categories = categories if categories else IDEA_CATEGORIES
        
        base_prompt =  (
            "You are an expert startup idea categorizer. "
            "Categorize each of the following ideas into one of the given categories.\n\n"
            f"Categories: {prompt_categories}\n\n"
            "Do not create additional categories outside of the given list. "
            "For each idea, return an object with the original '_id', and an additional field 'category' indicating the chosen category. "
            "Return your answer as a JSON array of objects with the following structure:\n"
            '{ "_id": original id, "category": chosen category }\n\n'
            "Here are the ideas:\n"
            f"{batch_content}"
        )

        return base_prompt
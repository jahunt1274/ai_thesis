import json
from typing import Dict, List, Any, Optional
from collections import Counter
from config import LOG_DIR
from utils.logger import LoggerSetup

class CategoryProcessor:
    """
    Processor class for analyzing ideas and categories data.
    """
    
    def __init__(
            self, 
            ideas_with_categories_filepath,
            categories_filepath,
            output_filepath,
            logger=None
        ):
        """
        Initialize the CategoryProcessor.
        
        Args:
            logger: Optional logger instance for logging
        """
        
        self.ideas_with_categories_filepath = ideas_with_categories_filepath
        self.categories_filepath = categories_filepath
        self.output_filepath = output_filepath

        self.ideas_data = []
        self.categories_data = []

        # Set up logger
        if not logger:
            logger_setup = LoggerSetup(LOG_DIR)
            self.logger = logger_setup.setup_logger('idea_categorizer')
        else:
            self.logger = logger
        
    def load_data(self, ideas_file: str, categories_file: str) -> bool:
        """
        Load ideas and categories data from JSON files.
        
        Args:
            ideas_file: Path to ideas JSON file
            categories_file: Path to categories JSON file
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            # Load ideas data
            with open(ideas_file, 'r', encoding='utf-8') as f:
                self.ideas_data = json.load(f)
            
            # Load categories data
            with open(categories_file, 'r', encoding='utf-8') as f:
                self.categories_data = json.load(f)
                
            if self.logger:
                self.logger.info(f"Loaded {len(self.ideas_data)} ideas and {len(self.categories_data)} categories")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def create_category_map(self) -> Dict[str, str]:
        """
        Create a mapping of idea IDs to their categories.
        
        Returns:
            Dict[str, str]: Mapping of idea ID (oid string) to category name
        """
        # Create a mapping of idea ID to category
        category_map = {}
        
        for item in self.categories_data:
            # # Check if _id and category fields exist
            # if "_id" in item and "category" in item:
            #     # Handle the case where _id is a dictionary with $oid key
            #     if isinstance(item["_id"], dict) and "$oid" in item["_id"]:
            #         idea_id = item["_id"]["$oid"]
            #     else:
            #         idea_id = item["_id"]
                
            #     category_map[idea_id] = item["category"]
            category_map[item] = 0
        
        if self.logger:
            self.logger.info(f"Created category map with {len(category_map)} entries")
            
        return category_map
    
    def count_categories(self) -> Dict[str, int]:
        """
        Count the occurrences of each category.
        
        Returns:
            Dict[str, int]: Mapping of category name to count
        """
        # Get the category for each idea
        category_map = self.create_category_map()
        
        # Extract just the categories
        # categories = list(category_map.values())
        categories = self.categories_data
        
        # Count the occurrences of each category
        # category_counts = Counter(categories)
        category_counts = 0
        for idea in self.ideas_data:
            if idea["category"] != "Uncategorized":
                if category_map.get(idea["category"]) is not None:
                    category_map[idea["category"]] += 1
                else:
                    category_map[idea["category"]] = 1
                    self.logger.info(f"Added new category {idea['category']} to list")
                category_counts += 1
        
        if self.logger:
            self.logger.info(f"Counted {category_counts} unique categories")
            
        return dict(category_map)
    
    def save_category_counts(self, output_file: str) -> bool:
        """
        Count categories and save the results to a JSON file.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Count categories
            category_counts = self.count_categories()
            
            # Add total count
            result = {
                "categories": category_counts,
                "total": sum(category_counts.values())
            }
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
            if self.logger:
                self.logger.info(f"Saved category counts to {output_file}")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving category counts: {str(e)}")
            return False
    
    # def get_ideas_by_category(self, category: str) -> List[Dict[str, Any]]:
    def get_ideas_by_category(self, category: str):
        """
        Get all ideas that belong to a specific category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List[Dict[str, Any]]: List of ideas in the specified category
        """
        # Get the category map
        # category_map = self.create_category_map()
        
        # Create a set of idea IDs that belong to the specified category
        # category_idea_ids = {
        #     idea_id for idea_id, cat in category_map.items() 
        #     if cat.lower() == category.lower()
        # }
        
        # Filter ideas by category
        try:
            category_ideas = []
            for idea in self.ideas_data:
                # if "_id" in idea:
                #     # Handle the case where _id is a dictionary with $oid key
                #     if isinstance(idea["_id"], dict) and "$oid" in idea["_id"]:
                #         idea_id = idea["_id"]["$oid"]
                #     else:
                #         idea_id = idea["_id"]
                        
                if idea["category"].lower() ==  category.lower():
                    formatted_idea = {
                        "_id": idea["_id"],
                        "title": idea["title"]
                    }
                    category_ideas.append(formatted_idea)
            
            if self.logger:
                self.logger.info(f"Found {len(category_ideas)} ideas in category '{category}'")
                
            with open(self.output_filepath, 'w', encoding='utf-8') as f:
                    json.dump(category_ideas, f, indent=2)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting ideas for category {category.lower()}: {str(e)}")
        
        # return category_ideas
    
    # Example usage
    def run(self):
        # Load data

        success = self.load_data(self.ideas_with_categories_filepath, self.categories_filepath)
        if not success:
            print("Failed to load data")
            return
        
        # self.get_ideas_by_category("Uncategorized")
        # Save category counts
        self.save_category_counts(self.output_filepath)
        
        # Print counts
        category_counts = self.count_categories()
        print("\nCategory Counts:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{category}: {count}")

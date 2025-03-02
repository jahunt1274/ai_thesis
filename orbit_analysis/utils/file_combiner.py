import json
from typing import Dict
from utils.logger import LoggerSetup
from config import LOG_DIR
from data.idea_categories import IDEA_CATEGORIES

class FileCombiner:
    """
    Combine two JSON files based on ID matching.
    Used initially for matching categorized ideas from LLM API with idea file from Orbit
        The files are combined on the matching idea IDs

    Args:
        categories_file (str): Path to the categories JSON file  (response from the LLM API)
        ideas_file (str): Path to the ideas JSON file            (Orbit generated ideas file)
        output_file (str): Path to save the combined JSON
    """
    def __init__(self, categories_file, ideas_file, output_file):
        self.categories_file = categories_file
        self.ideas_file = ideas_file
        self.output_file = output_file

        # Set up logger
        logger_setup = LoggerSetup(LOG_DIR)
        self.logger = logger_setup.setup_logger('file_combiner')
    
    def create_original_category_lookup(self) -> Dict[str, bool]:
        lookup = {}
        for category in IDEA_CATEGORIES:
            lookup[category] = True
        return lookup
    
    def combine_json_files(self):
        # Load categories data
        with open(self.categories_file, 'r') as f:
            categories_data = json.load(f)
        
        new_categories = {}
        new_category_count = 0
        # Create a lookup of original categories
        original_categories = self.create_original_category_lookup()
        
        # Create a dictionary for quick lookup of categories by ID
        categories_dict = {}
        for item in categories_data:
            item_cat = item["category"]
            if type(item["_id"]) is dict:
                categories_dict[item["_id"]["$oid"]] = item_cat
            else:
                categories_dict[item["_id"]] = item_cat
            if not original_categories.get(item_cat) and not new_categories.get(item_cat):
                new_categories[item_cat] = True
                new_category_count += 1

        # Load ideas data
        with open(self.ideas_file, 'r') as f:
            ideas_data = json.load(f)
        
        # Combine the data
        combined_data = []
        uncategorized_count = 0

        for idea in ideas_data:
            # Extract the $oid value from the idea
            oid_value = idea["_id"]["$oid"]
            
            # Create a new combined object
            combined_obj = {
                "_id": idea["_id"],
                "title": idea["title"]
            }
            
            # Add category if available
            if oid_value in categories_dict:
                combined_obj["category"] = categories_dict[oid_value]
            else:
                # Optional: add a default category or log missing matches
                combined_obj["category"] = "No Category Detected"
                uncategorized_count += 1
                self.logger.debug(f"No category found for idea with ID: {oid_value}")
            
            combined_data.append(combined_obj)
        
        # Save the combined data
        with open(self.output_file, 'w') as f:
            json.dump(combined_data, f, indent=2)
        
        self.logger.info(f"Combined data saved to {self.output_file}")
        self.logger.info(f"Total ideas: {len(ideas_data)}")
        self.logger.info(f"Total categories: {len(categories_data)}")
        self.logger.info(f"Total combined objects: {len(combined_data)}")
        
        if new_category_count > 0:
            self.logger.info(f"{new_category_count} new categories created: {new_categories.keys()}")

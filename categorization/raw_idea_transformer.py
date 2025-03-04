import json
import os
from typing import Any
from config import DATA_DIR, OUTPUT_DIR

class RawIdeaTransformer:
    """
    Transform ideas from the Orbit data into trhe input for LLM idea categorization
    """
    def __init__(self, input_file_path: str, output_file_path: str):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    @staticmethod
    def load_json(filepath: str) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Loaded JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        print(f"Loading JSON from {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Successfully loaded JSON from {filepath}")
            return data
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in {filepath}: {str(e)}")
            raise
        except Exception as e:
            print(f"Error loading JSON from {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filepath: Path to save the file
            indent: JSON indentation level
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Saving JSON to {filepath}")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            print(f"Successfully saved JSON to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving JSON to {filepath}: {str(e)}")
            return False
    
    def get_transformed_ideas(self, ideas):
        transformed_ideas = []
        
        for idea in ideas:
            # Extract fields
            idea_id = idea["_id"]["$oid"]
            raw_title = idea["title"]
            raw_description = idea["description"]

            title = ""
            
            # Handle the different scenarios for title and description
            if raw_title and raw_description:
                # Both title and description are non-empty, join with a colon
                title = f"{raw_title}: {raw_description}"
            elif raw_title and not raw_description:
                # Only title is non-empty
                title = raw_title
            elif not raw_title and raw_description:
                # Only description is non-empty, use it for both
                title = raw_description
            else:
                # Both are empty, skip idea
                print(f"Idea {idea_id} has no content, skipping")
                continue

            transformed_idea = {
                "_id": {
                "$oid": idea_id
                },
                "title": title
            }

            transformed_ideas.append(transformed_idea)
        
        return transformed_ideas
    
    def run(self):
        # Load ideas
        print("Loading ideas")
        ideas = self.load_json(self.input_file_path)

        # Transform ideas
        print("Transforming ideas")
        transformed_ideas = self.get_transformed_ideas(ideas)

        # Save data
        print("Saving data")
        self.save_json(transformed_ideas, self.output_file_path)

def main():
    input_file_path = f"{DATA_DIR}/raw_ideas.json"
    output_file_path = f"{OUTPUT_DIR}/transformed_ideas.json"

    transformer = RawIdeaTransformer(
        input_file_path,
        output_file_path
    )

    transformer.run()

if __name__ == "__main__":
    main()

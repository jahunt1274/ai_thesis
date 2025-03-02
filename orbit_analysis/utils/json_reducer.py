import json
import logging
from typing import List, Dict, Any
from utils.logger import LoggerSetup
from utils.json_validator import JSONValidator
from config import LOG_DIR

class JSONReducer:
    def __init__(self, input_file_location: str, output_file_location: str, auto_fix: bool = True):
        self.input_file_location = input_file_location
        self.output_file_location = output_file_location
        self.auto_fix = auto_fix

        # Set up logger
        logger_setup = LoggerSetup(LOG_DIR)
        self.logger = logger_setup.setup_logger('json_reducer')

        # Set up validator
        self.validator = JSONValidator(self.logger)

    def _should_keep_object(self, obj: Dict[str, Any]) -> bool:
        """
        Check if an object should be kept based on its title field.
        
        Args:
            obj (Dict[str, Any]): The object to check
            
        Returns:
            bool: True if object should be kept, False if it should be filtered out
        """
        result = 'title' not in obj or (isinstance(obj['title'], str) and obj['title'].strip())
        if not result:
            self.logger.debug(f"Filtering out object: {obj.get('_id', 'unknown id')}")
        return result
    
    def _validate_input(self) -> bool:
        """
        Validate the input JSON file before processing.
        
        Returns:
            bool: True if valid, False otherwise
        """
        self.logger.info(f"Validating input file: {self.input_file_location}")
        is_valid, error_message = self.validator.validate_file(self.input_file_location)
        
        if not is_valid:
            self.logger.error(f"JSON validation failed:\n{error_message}")
        else:
            self.logger.info("JSON validation successful")
            
        return is_valid
    
    def reduce_json_fields(self, fields_to_keep: List[str]) -> None:
        """
        Reduces JSON objects to only include specified fields.
        
        Args:
            input_file (str): Path to input JSON file
            output_file (str): Path to output JSON file
            fields_to_keep (List[str]): List of field names to keep in the output
            
        Example:
            reduce_json_fields(
                'input.json',
                'output.json',
                ['_id', 'title']
            )
        """
        try:
            # Validate and potentially fix the input
            is_valid, error_message, content = self.validator.validate_and_fix_file(
                self.input_file_location,
                self.auto_fix
            )
            
            if not is_valid:
                self.logger.error(f"Cannot proceed with invalid JSON input: {error_message}")
                return
            
            self.logger.info(f"Starting JSON reduction with fields: {fields_to_keep}")
            
            # Parse the validated/fixed JSON content
            data = json.loads(content)
            
            self.logger.debug(f"Loaded {len(data)} objects from input file")
            
            # Verify input is a list of objects
            if not isinstance(data, list):
                self.logger.error("Input JSON must be an array of objects")
                raise ValueError("Input JSON must be an array of objects")
                
            # Filter and reduce objects
            reduced_data = []
            filtered_count = 0
            
            for obj in data:
                if self._should_keep_object(obj):
                    reduced_obj = {
                        field: obj[field]
                        for field in fields_to_keep
                        if field in obj
                    }
                    reduced_data.append(reduced_obj)
                else:
                    filtered_count += 1
            
            self.logger.info(f"Processed {len(reduced_data)} objects")
            self.logger.info(f"Filtered out {filtered_count} objects with empty titles")

            # Write reduced data to output file
            with open(self.output_file_location, 'w', encoding='utf-8') as f:
                json.dump(reduced_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Output saved to: {self.output_file_location}")
                
            print(f"Successfully processed {len(reduced_data)} objects")
            print(f"Filtered out {filtered_count} objects with empty titles")
            print(f"Output saved to: {self.output_file_location}")
                
        except FileNotFoundError:
            self.logger.error(f"Input file '{self.input_file_location}' not found")
            print(f"Error: Input file '{self.input_file_location}' not found")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in input file")
            print("Error: Invalid JSON format in input file")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            print(f"Error: {str(e)}")

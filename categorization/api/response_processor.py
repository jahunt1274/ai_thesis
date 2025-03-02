import json
import re

class ResponseProcessor:
    """Processes and cleans API responses."""
    
    def __init__(self, logger=None):
        """
        Initialize the response processor.
        
        Args:
            logger: Logger object
        """
        self.logger = logger
    
    def clean_response(self, response_text, batch_number=None):
        """
        Clean an API response by removing markdown and other formatting.
        
        Args:
            response_text: Raw response text from API
            batch_number: Optional batch number for logging
            
        Returns:
            str: Cleaned response text
        """
        try:
            # Remove leading/trailing whitespace
            response_text = response_text.strip()
            
            # Remove markdown code fences if present
            if response_text.startswith("```"):
                # Remove the first line if it starts with ```
                response_text = re.sub(r"^```(?:json)?\n", "", response_text)
                
                # Remove the ending code fence
                response_text = re.sub(r"\n```$", "", response_text)
                
            return response_text
            
        except Exception as e:
            if self.logger:
                batch_info = f"batch {batch_number}" if batch_number is not None else "response"
                self.logger.error(f"Error cleaning {batch_info}: {e}")
            raise
    
    def parse_json_response(self, response_text, batch_number=None):
        """
        Parse a JSON response and handle errors.
        
        Args:
            response_text: Text response to parse
            batch_number: Optional batch number for logging
            
        Returns:
            dict or list: Parsed JSON data
        """
        try:
            # Clean the response first
            cleaned_text = self.clean_response(response_text, batch_number)
            
            # Parse the JSON
            parsed_data = json.loads(cleaned_text)
            return parsed_data
            
        except json.JSONDecodeError as e:
            if self.logger:
                batch_info = f"batch {batch_number}" if batch_number is not None else "response"
                self.logger.error(f"Error parsing JSON for {batch_info}: {e}")
                self.logger.error(f"Raw response: {response_text}")
            raise
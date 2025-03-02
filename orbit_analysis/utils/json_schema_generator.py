import json
from collections import defaultdict
from utils.logger import LoggerSetup
from config import LOG_DIR

class JSONSchemaGenerator:
    def __init__(self, input_filepath, output_filepath, logger = None):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath

        # Set up logging
        if not logger:
            logger_setup = LoggerSetup(LOG_DIR)
            self.logger = logger_setup.setup_logger('json_schema_generator')
        else:
            self.logger = logger

    def extract_schema(self, data_array):
        """Recursively extract schema from an array of objects"""
        try:
            if not isinstance(data_array, list) or not data_array:
                return {}
            
            schema = defaultdict(lambda: defaultdict(set))
            
            # Process each object in the array
            for obj in data_array:
                if not isinstance(obj, dict):
                    continue
                    
                # Extract field names and their types
                for field_name, value in obj.items():
                    # Handle the value based on its type
                    if value is None:
                        schema[field_name]['types'].add("null")
                    elif isinstance(value, dict):
                        # Recursively process nested objects
                        schema[field_name]['types'].add("object")
                        nested_schema = self.extract_schema_from_object(value)
                        if 'properties' not in schema[field_name]:
                            schema[field_name]['properties'] = nested_schema
                        else:
                            # Merge with existing properties
                            self.merge_schemas(schema[field_name]['properties'], nested_schema)
                    elif isinstance(value, list):
                        schema[field_name]['types'].add("array")
                        # Process array items if the array is not empty
                        if value:
                            schema[field_name]['items'] = self.extract_array_items_schema(value)
                    else:
                        schema[field_name]['types'].add(type(value).__name__)
        except Exception as e:
            self.logger.error(f"Error extracting schema from json object array: {e}")
        
        return dict(schema)

    def extract_schema_from_object(self, obj):
        """Extract schema from a single object"""
        try:
            if not isinstance(obj, dict):
                return {}
            
            schema = defaultdict(lambda: defaultdict(set))
            
            for field_name, value in obj.items():
                if value is None:
                    schema[field_name]['types'].add("null")
                elif isinstance(value, dict):
                    schema[field_name]['types'].add("object")
                    schema[field_name]['properties'] = self.extract_schema_from_object(value)
                elif isinstance(value, list):
                    schema[field_name]['types'].add("array")
                    if value:
                        schema[field_name]['items'] = self.extract_array_items_schema(value)
                else:
                    schema[field_name]['types'].add(type(value).__name__)
        except Exception as e:
            self.logger.error(f"Error extracting schema from a single json onject: \nObject: {obj}\nError: {e}")
            return
        
        return dict(schema)

    def extract_array_items_schema(self, array):
        """Extract schema from array items"""
        try:
            if not array:
                return {}
            
            # Check if array contains objects
            if all(isinstance(item, dict) for item in array):
                return self.extract_schema(array)
            
            # For arrays of primitive types or mixed types
            types = set()
            for item in array:
                if item is None:
                    types.add("null")
                elif isinstance(item, dict):
                    types.add("object")
                elif isinstance(item, list):
                    types.add("array")
                else:
                    types.add(type(item).__name__)
        except Exception as e:
            self.logger.error(f"Error extracting schema from array of items: \nItems: {array}\nError: {e}")
            return
        
        return {'types': types}

    def merge_schemas(self, schema1, schema2):
        """
        Merge two schemas together.
        
        Args:
            schema1 (dict): First schema (will be modified in place)
            schema2 (dict): Second schema to merge in
        """
        try:
            for field, info in schema2.items():
                if field not in schema1:
                    schema1[field] = info
                else:
                    # Merge types (always sets in intermediate processing)
                    for type_name in info['types']:
                        schema1[field]['types'].add(type_name)
                    
                    # Merge properties if both have them
                    if 'properties' in info and 'properties' in schema1[field]:
                        self.merge_schemas(schema1[field]['properties'], info['properties'])
                    elif 'properties' in info:
                        schema1[field]['properties'] = info['properties']
                    
                    # Merge items if both have them
                    if 'items' in info and 'items' in schema1[field]:
                        if 'types' in info['items'] and 'types' in schema1[field]['items']:
                            for type_name in info['items']['types']:
                                schema1[field]['items']['types'].add(type_name)
                    elif 'items' in info:
                        schema1[field]['items'] = info['items']
        except Exception as e:
            self.logger.error(f"Error merging schemas together: {e}")
            return

    def sets_to_lists(self, schema):
        """
        Convert all sets in the schema to lists for the final output.
        This is a recursive function that processes nested objects.
        
        Args:
            schema (dict): Schema with sets
            
        Returns:
            dict: Schema with all sets converted to lists
        """
        result = {}
        
        for field, info in schema.items():
            result[field] = {}
            
            for key, value in info.items():
                if key == 'types' and isinstance(value, set):
                    result[field][key] = list(value)
                elif key == 'properties' and isinstance(value, dict):
                    result[field][key] = self.sets_to_lists(value)
                elif key == 'items' and isinstance(value, dict):
                    if 'types' in value and isinstance(value['types'], set):
                        result[field][key] = {'types': list(value['types'])}
                    else:
                        result[field][key] = self.sets_to_lists(value)
                else:
                    result[field][key] = value
                    
        return result
    
    def generate_schema_from_json(self):
        # Read the JSON file
        try:
            self.logger.info(f"Reading input json data from {self.input_filepath}")
            with open(self.input_filepath, 'r') as file:
                data = json.load(file)
            
            # Ensure the data is an array
            if not isinstance(data, list):
                raise ValueError("JSON file must contain an array of objects")
        except Exception as e:
            self.logger.error(f"Error loading input data: {e}")
            return
        
        # Process the array and extract schema
        schema = self.extract_schema(data)
        
        # Convert sets to lists for the final output
        return self.sets_to_lists(schema)

    def run(self):
        self.logger.info(f"Running json schema generator")
        try:
            json_schema = self.generate_schema_from_json()

            # Save the combined data
            self.logger.info(f"Saving data to {self.output_filepath}")
            with open(self.output_filepath, 'w') as f:
                json.dump(json_schema, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error occured while running json schema generator: {e}")

"""
Step data loader for the AI thesis analysis.
"""

from typing import Dict, List, Any, Optional

from config import STEP_DATA_FILE
from src.utils import FileHandler, get_logger

logger = get_logger("step_loader")


class StepLoader:
    """Loads and processes step data."""
    
    def __init__(self, file_path: str = STEP_DATA_FILE):
        """
        Initialize the step loader.
        
        Args:
            file_path: Path to the step data file
        """
        self.file_path = file_path
        self.file_handler = FileHandler()
        self.raw_steps = None
        self.processed_steps = None
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Load step data from the file.
        
        Returns:
            List of step records
        """
        logger.info(f"Loading step data from {self.file_path}")
        self.raw_steps = self.file_handler.load_json(self.file_path)
        
        # Check data format
        if not isinstance(self.raw_steps, list):
            raise ValueError("Step data must be a list of objects")
        
        logger.info(f"Loaded {len(self.raw_steps)} step records")
        return self.raw_steps
    
    def process(self) -> List[Dict[str, Any]]:
        """
        Process raw step data into a standardized format.
        
        Returns:
            List of processed step records
        """
        if self.raw_steps is None:
            self.load()
        
        logger.info("Processing step data")
        self.processed_steps = []
        
        for step in self.raw_steps:
            processed_step = self._process_step(step)
            if processed_step:
                self.processed_steps.append(processed_step)
        
        logger.info(f"Processed {len(self.processed_steps)} step records")
        return self.processed_steps
    
    def _process_step(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single step record.
        
        Args:
            step: Raw step record
            
        Returns:
            Processed step record, or None if invalid
        """
        try:
            # Basic validation
            if not step:
                logger.warning("Empty step record")
                return None
            
            # Skip incomplete steps
            if 'content' not in step or not step['content'] or not step['content'].strip():
                logger.debug(f"Step {step.get('_id', 'unknown')} has empty content, skipping")
                return None
                
            if 'step' not in step or not step['step']:
                logger.debug(f"Step {step.get('_id', 'unknown')} missing step name, skipping")
                return None
                
            if 'idea_id' not in step or not step['idea_id']:
                logger.debug(f"Step {step.get('_id', 'unknown')} missing idea ID, skipping")
                return None
            
            # Extract fields
            step_id = self._extract_id(step.get('_id'))
            idea_id = self._extract_id(step.get('idea_id'))
            
            # Extract created timestamp
            created_at = self._extract_timestamp(step.get('created_at'))
            
            # Create processed step
            processed_step = {
                'id': step_id,
                'idea_id': idea_id,
                'owner': step.get('owner'),
                'framework': step.get('framework'),
                'step_name': step.get('step'),
                'content': step.get('content'),
                'created_at': created_at,
                'active': step.get('active', False),
                'name': step.get('name', ''),
                'message': step.get('message', ''),
                'content_word_count': len(step.get('content', '').split()),
                'content_sections': self._count_sections(step.get('content', ''))
            }
            
            return processed_step
            
        except Exception as e:
            logger.error(f"Error processing step {step.get('_id', 'unknown')}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_id(id_value: Any) -> str:
        """Extract ID from various formats."""
        if isinstance(id_value, dict) and '$oid' in id_value:
            return id_value['$oid']
        return str(id_value)
    
    @staticmethod
    def _extract_timestamp(timestamp: Any) -> Optional[str]:
        """Extract timestamp from various formats."""
        if not timestamp:
            return None
            
        if isinstance(timestamp, dict) and '$date' in timestamp:
            return timestamp['$date']
        
        return str(timestamp)
    
    @staticmethod
    def _count_sections(content: str) -> int:
        """
        Count the number of sections in the content (marked by headings).
        
        Args:
            content: The content to analyze
            
        Returns:
            Number of sections
        """
        import re
        # Count markdown headings (# Heading)
        headings = re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE)
        return len(headings)
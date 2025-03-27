"""
Step loader for the AI thesis analysis.
"""

from typing import Dict, Any, Optional

from config import STEP_DATA_FILE
from src.constants.data_constants import StepDataType
from src.loaders.base_loader import BaseLoader
from src.utils import get_logger

logger = get_logger("step_loader")

class StepLoader(BaseLoader[StepDataType]):
    """Loads and processes step data."""
    
    def __init__(self, file_path: str = STEP_DATA_FILE):
        """
        Initialize the step loader.
        
        Args:
            file_path: Path to the step data file
        """
        super().__init__(file_path)
    
    def _process_item(self, step: Dict[str, Any]) -> Optional[StepDataType]:
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
                self.logger.warning("Empty step record")
                return None
            
            # Skip incomplete steps
            if 'content' not in step or not step['content'] or not step['content'].strip():
                self.logger.debug(f"Step {step.get('_id', 'unknown')} has empty content, skipping")
                return None
                
            if 'step' not in step or not step['step']:
                self.logger.debug(f"Step {step.get('_id', 'unknown')} missing step name, skipping")
                return None
                
            if 'idea_id' not in step or not step['idea_id']:
                self.logger.debug(f"Step {step.get('_id', 'unknown')} missing idea ID, skipping")
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
            self.logger.error(f"Error processing step {step.get('_id', 'unknown')}: {str(e)}")
            return None
    
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
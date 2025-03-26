"""
Course evaluation data loader for the AI thesis analysis.
"""

import os
import json
from typing import Dict, List, Any, Optional
from jsonschema import validate

from config import COURSE_EVAL_DIR, COURSE_EVAL_SCHEMA
from src.utils import FileHandler, get_logger

logger = get_logger("course_eval_loader")


class CourseEvaluationLoader:
    """Loads and processes course evaluation data."""
    
    def __init__(self, eval_dir: str = COURSE_EVAL_DIR):
        """
        Initialize the course evaluation loader.
        
        Args:
            eval_dir: Directory containing course evaluation JSON files
        """
        self.eval_dir = eval_dir
        self.file_handler = FileHandler()
        self.raw_evaluations = None
        self.processed_evaluations = None
        
        # Load schema
        self.schema = None
        if os.path.exists(COURSE_EVAL_SCHEMA):
            try:
                self.schema = self.file_handler.load_json(COURSE_EVAL_SCHEMA)
                logger.info(f"Loaded course evaluation schema from {COURSE_EVAL_SCHEMA}")
            except Exception as e:
                logger.warning(f"Failed to load schema: {str(e)}")
    
    def load_all(self) -> List[Dict[str, Any]]:
        """
        Load all course evaluation files from the directory.
        
        Returns:
            List of course evaluation records
        """
        logger.info(f"Loading course evaluation data from {self.eval_dir}")
        
        if not os.path.exists(self.eval_dir):
            logger.error(f"Course evaluation directory not found: {self.eval_dir}")
            return []
        
        evaluations = []
        
        for filename in os.listdir(self.eval_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.eval_dir, filename)
                try:
                    eval_data = self.file_handler.load_json(file_path)
                    
                    for eval in eval_data:
                        # Validate against schema if available
                        if self.schema:
                            try:
                                validate(instance=eval, schema=self.schema)
                            except Exception as e:
                                logger.warning(f"Validation failed for {filename}: {str(e)}")
                                continue
                        
                        evaluations.append(eval)
                    logger.info(f"Loaded evaluation data from {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {str(e)}")
        
        self.raw_evaluations = evaluations
        logger.info(f"Loaded {len(evaluations)} course evaluation records")
        return evaluations
    
    def process(self) -> List[Dict[str, Any]]:
        """
        Process raw evaluation data into a standardized format.
        
        Returns:
            List of processed evaluation records
        """
        if self.raw_evaluations is None:
            self.load_all()
        
        logger.info("Processing course evaluation data")
        self.processed_evaluations = []
        
        for eval_data in self.raw_evaluations:
            processed_eval = self._process_evaluation(eval_data)
            if processed_eval:
                self.processed_evaluations.append(processed_eval)
        
        logger.info(f"Processed {len(self.processed_evaluations)} evaluation records")
        return self.processed_evaluations
    
    def _process_evaluation(self, eval_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single evaluation record.
        
        Args:
            eval_data: Raw evaluation record
            
        Returns:
            Processed evaluation record, or None if invalid
        """
        try:
            # Basic validation
            if not eval_data:
                logger.warning("Empty evaluation record")
                return None
            
            # Check for required fields
            for field in ['course_id', 'semester', 'evaluation_metrics']:
                if field not in eval_data:
                    logger.warning(f"Evaluation missing required field: {field}")
                    return None
            
            # Extract and standardize fields
            semester = eval_data.get('semester', {})
            term = semester.get('term', '').lower()
            year = semester.get('year')
            
            # Get or infer the order field
            order = semester.get('order')
            if order is None:
                # If no order is specified, infer it based on term (Spring=1, Fall=2)
                order = 1 if term == 'spring' else 2
            
            # Create a semester code for easier sorting and comparison
            semester_code = f"{year}_{term}"
            
            # Format the display name
            display_name = f"{term.capitalize()} {year}"
            
            # Get tool version information
            tool_version = eval_data.get('tool_version')
            
            # Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics(eval_data.get('evaluation_metrics', []))
            
            # Create processed evaluation
            processed_eval = {
                'course_id': eval_data.get('course_id'),
                'semester': {
                    'term': term,
                    'year': year,
                    'code': semester_code,
                    'display_name': display_name,
                    'order': order
                },
                'tool_version': tool_version,
                'evaluation_metrics': eval_data.get('evaluation_metrics', []),
                'overall_metrics': overall_metrics
            }
            
            return processed_eval
            
        except Exception as e:
            logger.error(f"Error processing evaluation for {eval_data.get('course_id', 'unknown')}: {str(e)}")
            return None
    
    def _calculate_overall_metrics(self, evaluation_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall metrics across all evaluation sections.
        
        Args:
            evaluation_metrics: List of evaluation metric sections
            
        Returns:
            Dictionary of overall metrics
        """
        all_questions = []
        section_averages = {}
        
        # Collect questions from all sections
        for section in evaluation_metrics:
            section_name = section.get('section')
            questions = section.get('questions', [])
            
            # Calculate section average
            valid_scores = [q.get('avg') for q in questions if q.get('avg') is not None]
            if valid_scores:
                section_averages[section_name] = sum(valid_scores) / len(valid_scores)
            
            all_questions.extend(questions)
        
        # Calculate overall average
        valid_scores = [q.get('avg') for q in all_questions if q.get('avg') is not None]
        overall_avg = sum(valid_scores) / len(valid_scores) if valid_scores else None
        
        return {
            'overall_avg': overall_avg,
            'section_averages': section_averages,
            'total_questions': len(all_questions),
            'valid_scores': len(valid_scores)
        }
"""
Base analyzer for data analysis.
"""

from typing import Dict, Any, Optional

from src.utils import get_logger


class BaseAnalyzer:
    """Base class for all analyzers with common functionality."""
    
    def __init__(self, logger_name: Optional[str] = None):
        """
        Initialize the base analyzer.
        
        Args:
            logger_name: Optional logger name (defaults to class name)
        """
        self.logger = get_logger(logger_name or self.__class__.__name__.lower())
    
    def analyze(self) -> Dict[str, Any]:
        """
        Template method for analysis process.
        
        Returns:
            Dictionary of analysis results
        """
        self.logger.info(f"Starting analysis with {self.__class__.__name__}")
        
        # Validate data
        self.validate_data()
        
        # Preprocess data if needed
        self.preprocess()
        
        # Perform the actual analysis
        results = self.perform_analysis()
        
        # Format results
        formatted_results = self.format_results(results)
        
        self.logger.info(f"Analysis completed for {self.__class__.__name__}")
        return formatted_results
    
    def validate_data(self) -> None:
        """
        Validate input data.
        Override this method to add specific validations.
        """
        pass
    
    def preprocess(self) -> None:
        """
        Preprocess data before analysis.
        Override this method to add specific preprocessing steps.
        """
        pass
    
    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform the actual analysis.
        This method must be implemented by subclasses.
        
        Returns:
            Dictionary of analysis results
        """
        raise NotImplementedError("Subclasses must implement perform_analysis")
    
    def format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results.
        
        Args:
            results: Raw analysis results
            
        Returns:
            Formatted analysis results
        """
        return results
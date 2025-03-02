"""
Base visualization module for the AI thesis analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseVisualizer(ABC):
    """Abstract base class for all visualizers."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = output_dir
    
    @abstractmethod
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations from data.
        
        Args:
            data: Data to visualize
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        pass
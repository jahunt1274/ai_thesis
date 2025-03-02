from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """Abstract base class for all processors."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
    
    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """Process the data and return results."""
        pass
from typing import Dict, Any, List
import re
from datetime import datetime
from .base_processor import BaseProcessor

class StepProcessor(BaseProcessor):
    def process(self) -> Dict[str, Any]:
        """Process step content data."""
        return {
            "content_analysis": self._analyze_content(),
            "step_progression": self._analyze_step_progression(),
            "framework_usage": self._analyze_framework_usage()
        }
    
    def _analyze_content(self) -> Dict[str, Any]:
        """Analyze the content of steps."""
        content_metrics = []
        for step in self.data:
            content = step.get('content', '')
            metrics = {
                'step': step['step'],
                'framework': step['framework'],
                'word_count': len(content.split()),
                'sections': self._count_sections(content),
                'creation_date': step['created_at']['$date']
            }
            content_metrics.append(metrics)
        return content_metrics
    
    def _count_sections(self, content: str) -> int:
        """Count number of sections in content (marked by ###)."""
        return len(re.findall(r'###\s+', content))
    
    def _analyze_step_progression(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze how users progress through steps."""
        user_progression = {}
        for step in self.data:
            owner = step['owner']
            if owner not in user_progression:
                user_progression[owner] = []
            user_progression[owner].append({
                'step': step['step'],
                'date': step['created_at']['$date'],
                'framework': step['framework']
            })
        return user_progression
    
    def _analyze_framework_usage(self) -> Dict[str, int]:
        """Analyze which frameworks are most commonly used."""
        framework_counts = {}
        for step in self.data:
            framework = step['framework']
            framework_counts[framework] = framework_counts.get(framework, 0) + 1
        return framework_counts
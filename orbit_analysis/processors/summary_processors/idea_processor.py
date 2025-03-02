from typing import Dict, Any, List
from .base_processor import BaseProcessor
from datetime import datetime

class IdeaProcessor(BaseProcessor):
    def process(self) -> Dict[str, Any]:
        """Process idea-related data."""
        return {
            "idea_rankings": self._analyze_rankings(),
            "idea_creation_timeline": self._analyze_creation_timeline(),
            "ideas_per_user": self._analyze_ideas_per_user()
        }
    
    def _analyze_rankings(self) -> Dict[str, int]:
        """Analyze distribution of idea rankings."""
        ranking_counts = {}
        for idea in self.data:
            ranking = idea.get('ranking', 0)
            ranking_counts[ranking] = ranking_counts.get(ranking, 0) + 1
        return ranking_counts
    
    def _analyze_creation_timeline(self) -> List[Dict[str, Any]]:
        """Analyze idea creation patterns over time."""
        timeline = []
        try:
            # First, let's print a sample idea to debug
            if self.data and len(self.data) > 0:
                print("Sample idea structure:", self.data[0])
            
            for idea in self.data:
                # Extract creation date safely
                created_date = idea.get('created', {})
                if isinstance(created_date, dict):
                    date_str = created_date.get('$date')
                else:
                    continue  # Skip if creation date not in expected format

                timeline.append({
                    'date': date_str,
                    'title': idea.get('title', 'Untitled'),
                    'owner': idea.get('owner', 'Unknown'),
                    'ranking': idea.get('ranking', 0)
                })
            
            # Sort timeline by date
            timeline.sort(key=lambda x: x['date'] if x['date'] else '')
            
        except Exception as e:
            print(f"Error in _analyze_creation_timeline: {str(e)}")
            print("Data sample:", self.data[:1])
        
        return timeline
    
    def _analyze_ideas_per_user(self) -> Dict[str, int]:
        """Count number of ideas per user."""
        user_counts = {}
        for idea in self.data:
            owner = idea.get('owner', 'unknown')
            user_counts[owner] = user_counts.get(owner, 0) + 1
        return user_counts
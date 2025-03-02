from typing import Dict, Any, List
from .base_processor import BaseProcessor

class ProfileProcessor(BaseProcessor):
    def process(self) -> Dict[str, Any]:
        """Process user profile data."""
        profiles = self._get_profile_summaries()
        interest_stats = self._get_interest_statistics()
        
        return {
            "profile_summaries": profiles,
            "interest_statistics": interest_stats
        }
    
    def _get_profile_summaries(self) -> List[Dict[str, Any]]:
        """Generate summaries of user profiles."""
        summaries = []
        for profile in self.data:
            summary = {
                'name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip(),
                'email': profile.get('email'),
                'type': profile.get('type'),
                'title': profile.get('title'),
                'departments': [
                    dept['name'] 
                    for affiliation in profile.get('affiliations', [])
                    for dept in affiliation.get('departments', [])
                ],
                'interests': profile.get('orbitProfile', {}).get('interest', [])
            }
            summaries.append(summary)
        return summaries
    
    def _get_interest_statistics(self) -> Dict[str, int]:
        """Calculate statistics about user interests."""
        interest_counts = {}
        for profile in self.data:
            if 'orbitProfile' in profile and 'interest' in profile['orbitProfile']:
                for interest in profile['orbitProfile']['interest']:
                    interest_counts[interest] = interest_counts.get(interest, 0) + 1
        return interest_counts
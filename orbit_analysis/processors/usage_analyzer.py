from typing import Dict, Any, List
from collections import defaultdict

class UsageAnalyzer:
    def __init__(self, users_data: List[Dict[str, Any]], ideas_data: List[Dict[str, Any]]):
        self.users = users_data
        self.ideas = ideas_data

    def analyze_user_engagement(self) -> Dict[str, Any]:
        """Analyze user engagement levels."""
        user_idea_counts = defaultdict(int)
        for idea in self.ideas:
            user_idea_counts[idea['owner']] += 1

        engagement_levels = {
            'high': 0,  # >5 ideas
            'medium': 0,  # 2-5 ideas
            'low': 0,  # 1 idea
            'none': 0  # 0 ideas
        }

        for count in user_idea_counts.values():
            if count > 5:
                engagement_levels['high'] += 1
            elif count >= 2:
                engagement_levels['medium'] += 1
            elif count == 1:
                engagement_levels['low'] += 1

        engagement_levels['none'] = len(self.users) - sum(engagement_levels.values())
        return engagement_levels

    def analyze_idea_rankings(self) -> Dict[str, Any]:
        """Analyze idea rankings and iterations."""
        ranking_distribution = defaultdict(int)
        user_idea_iterations = defaultdict(lambda: defaultdict(int))

        for idea in self.ideas:
            ranking = idea.get('ranking', 0)
            ranking_distribution[ranking] += 1
            user_idea_iterations[idea['owner']][idea['title']] += 1

        return {
            'ranking_distribution': dict(ranking_distribution),
            'user_iterations': {
                user: dict(ideas)
                for user, ideas in user_idea_iterations.items()
            }
        }
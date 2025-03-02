from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime

class EngagementAnalyzer:
    def __init__(self, users_data: List[Dict[str, Any]], 
                 ideas_data: List[Dict[str, Any]], 
                 steps_data: List[Dict[str, Any]]):
        self.users = users_data
        self.ideas = ideas_data
        self.steps = steps_data

    def analyze_process_completion(self) -> Dict[str, Any]:
        """Analyze how users progress through the idea development process."""
        user_progress = defaultdict(lambda: defaultdict(int))
        
        for step in self.steps:
            user_progress[step['owner']][step['step']] += 1

        completion_stats = {
            'complete_process': 0,
            'partial_process': 0,
            'single_step': 0,
            'step_distribution': defaultdict(int)
        }

        for user_steps in user_progress.values():
            step_count = len(user_steps)
            if step_count > 1:
                completion_stats['partial_process'] += 1
            elif step_count == 1:
                completion_stats['single_step'] += 1
            
            for step in user_steps:
                completion_stats['step_distribution'][step] += 1

        return {
            'completion_stats': dict(completion_stats),
            'step_distribution': dict(completion_stats['step_distribution'])
        }

    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze usage patterns over time."""
        time_patterns = {
            'daily': defaultdict(int),
            'weekly': defaultdict(int),
            'monthly': defaultdict(int)
        }

        for step in self.steps:
            if 'created_at' in step:
                date_str = step['created_at'].get('$date', '')
                if date_str:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    time_patterns['daily'][date.strftime('%Y-%m-%d')] += 1
                    time_patterns['weekly'][date.strftime('%Y-%W')] += 1
                    time_patterns['monthly'][date.strftime('%Y-%m')] += 1

        return {
            'daily_usage': dict(time_patterns['daily']),
            'weekly_usage': dict(time_patterns['weekly']),
            'monthly_usage': dict(time_patterns['monthly'])
        }
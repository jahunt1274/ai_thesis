import json
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class SummaryAnalyzer:
    def __init__(self, results_file: str):
        """Initialize with path to results JSON file."""
        self.results = self._load_results(results_file)
        
    def _load_results(self, file_path: str) -> Dict[str, Any]:
        """Load and validate results file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        report = []
        report.append("=== Entrepreneurship Platform Analysis Summary ===\n")
        
        # User Base Summary
        report.append("User Base Overview:")
        user_types = self.results['journeys']['completion_rates']
        for user_type, stats in user_types.items():
            report.append(f"- {user_type.title()} Users:")
            report.append(f"  * Total: {stats['total']}")
            report.append(f"  * Active: {stats['active']}")
            if 'participation_rate' in stats:
                rate = stats['participation_rate'] * 100
                report.append(f"  * Participation Rate: {rate:.1f}%")
        
        # Engagement Metrics
        report.append("\nEngagement Metrics:")
        engagement = self.results['journeys']['user_engagement']
        active_users = engagement['active_users']
        report.append(f"- Total Users: {active_users['total_users']}")
        report.append(f"- Active Last 30 Days: {active_users['active_last_30_days']}")
        report.append(f"- Users with Enrollments: {active_users['with_enrollments']}")
        report.append(f"- Complete Profiles: {active_users['with_complete_profile']}")
        
        # Course Analysis
        report.append("\nTop Courses:")
        enrollment_stats = engagement['enrollment_stats']
        for course, count in enrollment_stats['most_popular_courses'][:5]:
            report.append(f"- {course}: {count} enrollments")
        
        # Ideas Analysis
        report.append("\nIdeas Overview:")
        ideas = self.results['ideas']
        report.append(f"- Total Ideas: {len(ideas['idea_creation_timeline'])}")
        
        # Compute average ranking
        rankings = ideas['idea_rankings']
        total_ideas = sum(rankings.values())
        avg_ranking = sum(int(k) * v for k, v in rankings.items()) / total_ideas
        report.append(f"- Average Idea Ranking: {avg_ranking:.2f}")
        
        return "\n".join(report)
    
    def get_key_metrics(self) -> Dict[str, Any]:
        """Extract key performance metrics."""
        engagement = self.results['journeys']['user_engagement']
        active_users = engagement['active_users']
        
        return {
            'total_users': active_users['total_users'],
            'active_users_30d': active_users['active_last_30_days'],
            'active_rate': active_users['active_last_30_days'] / active_users['total_users'],
            'total_enrollments': engagement['enrollment_stats']['total_enrollments'],
            'avg_enrollments_per_user': engagement['enrollment_stats']['avg_enrollments_per_user'],
            'total_ideas': len(self.results['ideas']['idea_creation_timeline']),
            'profile_completion_rate': active_users['with_complete_profile'] / active_users['total_users']
        }
    
    def get_enrollment_trends(self) -> List[Dict[str, Any]]:
        """Analyze course enrollment trends."""
        engagement = self.results['journeys']['user_engagement']
        course_data = engagement['enrollment_stats']['most_popular_courses']
        
        return [
            {
                'course': course,
                'enrollments': count,
                'percentage': (count / engagement['enrollment_stats']['total_enrollments']) * 100
            }
            for course, count in course_data
        ]
    
    def get_user_activity_timeline(self) -> List[Dict[str, Any]]:
        """Generate timeline of user activity."""
        timeline = []
        for journey in self.results['journeys']['journey_timelines']:
            for event in journey['events']:
                if 'date' in event:
                    timeline.append({
                        'date': event['date'],
                        'type': event['type'],
                        'user_type': journey['user_type']
                    })
        
        # Sort by date
        timeline.sort(key=lambda x: x['date'])
        return timeline
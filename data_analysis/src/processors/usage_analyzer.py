"""
Usage analyzer for the AI thesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils import get_logger

logger = get_logger("usage_analyzer")


class UsageAnalyzer:
    """Analyzes usage patterns of the Orbit tool."""
    
    def __init__(self, users: List[Dict[str, Any]], ideas: List[Dict[str, Any]]):
        """
        Initialize the usage analyzer.
        
        Args:
            users: List of processed user records
            ideas: List of processed idea records
        """
        self.users = users
        self.ideas = ideas
        
        # Create lookup map of ideas by owner for efficiency
        self.ideas_by_owner = self._group_ideas_by_owner()
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive usage analysis.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info("Performing usage analysis")
        
        results = {
            'idea_generation': self._analyze_idea_generation(),
            'engagement_levels': self._analyze_engagement_levels(),
            'idea_characterization': self._analyze_idea_characterization(),
            'framework_usage': self._analyze_framework_usage(),
            'timeline': self._analyze_usage_timeline()
        }
        
        return results
    
    def _analyze_idea_generation(self) -> Dict[str, Any]:
        """Analyze idea generation patterns."""
        idea_counts = {
            'total_ideas': len(self.ideas),
            'unique_owners': len(self.ideas_by_owner),
            'avg_ideas_per_owner': 0,
            'max_ideas_per_owner': 0,
            'ideas_by_ranking': defaultdict(int)
        }
        
        # Count ideas by ranking
        for idea in self.ideas:
            ranking = idea.get('ranking', 0)
            idea_counts['ideas_by_ranking'][ranking] += 1
        
        # Calculate averages
        if idea_counts['unique_owners'] > 0:
            idea_counts['avg_ideas_per_owner'] = (
                idea_counts['total_ideas'] / idea_counts['unique_owners']
            )
        
        # Find maximum ideas per owner
        for owner, ideas in self.ideas_by_owner.items():
            idea_counts['max_ideas_per_owner'] = max(
                idea_counts['max_ideas_per_owner'],
                len(ideas)
            )
        
        # Convert defaultdict to regular dict
        idea_counts['ideas_by_ranking'] = dict(idea_counts['ideas_by_ranking'])
        
        return idea_counts
    
    def _analyze_engagement_levels(self) -> Dict[str, Any]:
        """Analyze user engagement levels."""
        # Define engagement level thresholds
        engagement_levels = {
            'high': 0,     # >5 ideas
            'medium': 0,   # 2-5 ideas
            'low': 0,      # 1 idea
            'none': 0      # 0 ideas
        }
        
        # Count users by engagement level
        for owner, ideas in self.ideas_by_owner.items():
            if len(ideas) > 5:
                engagement_levels['high'] += 1
            elif len(ideas) >= 2:
                engagement_levels['medium'] += 1
            elif len(ideas) == 1:
                engagement_levels['low'] += 1
        
        # Count users with no ideas
        engagement_levels['none'] = len(self.users) - sum(engagement_levels.values())
        
        # Calculate engagement by framework usage
        framework_engagement = self._analyze_framework_engagement()
        
        # Calculate engagement over time
        temporal_engagement = self._analyze_temporal_engagement()
        
        return {
            'engagement_levels': engagement_levels,
            'framework_engagement': framework_engagement,
            'temporal_engagement': temporal_engagement
        }
    
    def _analyze_idea_characterization(self) -> Dict[str, Any]:
        """Analyze characteristics of ideas."""
        # Analyze idea iteration patterns
        iteration_patterns = self._analyze_iteration_patterns()
        
        # Analyze idea progress
        progress_stats = self._analyze_progress_stats()
        
        return {
            'iteration_patterns': iteration_patterns,
            'progress_stats': progress_stats
        }
    
    def _analyze_framework_usage(self) -> Dict[str, Any]:
        """Analyze usage of different frameworks."""
        framework_counts = defaultdict(int)
        
        for idea in self.ideas:
            for framework in idea.get('frameworks', []):
                framework_counts[framework] += 1
        
        # Calculate framework completion rates
        de_completion = self._calculate_completion_rate('Disciplined Entrepreneurship')
        st_completion = self._calculate_completion_rate('Startup Tactics')
        
        return {
            'framework_counts': dict(framework_counts),
            'de_completion': de_completion,
            'st_completion': st_completion
        }
    
    def _analyze_usage_timeline(self) -> Dict[str, Any]:
        """Analyze usage patterns over time."""
        # Group ideas by creation date
        ideas_by_date = defaultdict(list)
        
        for idea in self.ideas:
            created_date = idea.get('created_date')
            if created_date:
                # Extract date part only (YYYY-MM-DD)
                if 'T' in created_date:
                    date_part = created_date.split('T')[0]
                else:
                    date_part = created_date
                
                ideas_by_date[date_part].append(idea)
        
        # Count ideas by date and calculate daily statistics
        daily_counts = {}
        for date, ideas in ideas_by_date.items():
            daily_counts[date] = {
                'count': len(ideas),
                'avg_progress': sum(idea.get('total_progress', 0) for idea in ideas) / len(ideas) if ideas else 0
            }
        
        # Group by month for monthly analysis
        monthly_counts = defaultdict(list)
        for date, stats in daily_counts.items():
            month = date[:7]  # Extract YYYY-MM
            monthly_counts[month].append(stats['count'])
        
        # Calculate monthly statistics
        monthly_stats = {}
        for month, counts in monthly_counts.items():
            monthly_stats[month] = {
                'total_ideas': sum(counts),
                'avg_ideas_per_day': sum(counts) / len(counts) if counts else 0
            }
        
        return {
            'daily_counts': daily_counts,
            'monthly_stats': monthly_stats
        }
    
    def _group_ideas_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group ideas by owner for efficient access."""
        ideas_by_owner = defaultdict(list)
        
        for idea in self.ideas:
            owner = idea.get('owner')
            if owner:
                ideas_by_owner[owner].append(idea)
        
        return ideas_by_owner
    
    def _analyze_framework_engagement(self) -> Dict[str, Any]:
        """Analyze engagement by framework usage."""
        framework_users = {
            'Disciplined Entrepreneurship': set(),
            'Startup Tactics': set(),
            'both_frameworks': set(),
            'no_framework': set()
        }
        
        # Track users by framework
        for idea in self.ideas:
            owner = idea.get('owner')
            frameworks = idea.get('frameworks', [])
            
            if 'Disciplined Entrepreneurship' in frameworks:
                framework_users['Disciplined Entrepreneurship'].add(owner)
            
            if 'Startup Tactics' in frameworks:
                framework_users['Startup Tactics'].add(owner)
        
        # Identify users using both frameworks
        framework_users['both_frameworks'] = (
            framework_users['Disciplined Entrepreneurship'] & 
            framework_users['Startup Tactics']
        )
        
        # Identify users using no framework
        all_idea_owners = set(self.ideas_by_owner.keys())
        framework_users['no_framework'] = all_idea_owners - (
            framework_users['Disciplined Entrepreneurship'] | 
            framework_users['Startup Tactics']
        )
        
        # Convert sets to counts
        return {
            framework: len(users)
            for framework, users in framework_users.items()
        }
    
    def _analyze_temporal_engagement(self) -> Dict[str, Any]:
        """Analyze engagement patterns over time."""
        # Track active users by month
        monthly_active_users = defaultdict(set)
        
        for idea in self.ideas:
            created_date = idea.get('created_date')
            owner = idea.get('owner')
            
            if created_date and owner:
                # Extract month (YYYY-MM)
                if 'T' in created_date:
                    month = created_date.split('T')[0][:7]
                else:
                    month = created_date[:7]
                
                monthly_active_users[month].add(owner)
        
        # Convert sets to counts
        monthly_users = {
            month: len(users)
            for month, users in monthly_active_users.items()
        }
        
        return {
            'monthly_active_users': monthly_users
        }
    
    def _analyze_iteration_patterns(self) -> Dict[str, Any]:
        """Analyze idea iteration patterns."""
        # Count users by number of iterations (ranking)
        users_by_iterations = defaultdict(int)
        
        for owner, ideas in self.ideas_by_owner.items():
            # Count iterations by tracking rankings
            rankings = set(idea.get('ranking', 0) for idea in ideas)
            max_iteration = max(rankings) if rankings else 0
            
            users_by_iterations[max_iteration] += 1
        
        # Count similar ideas (potential iterations)
        return {
            'users_by_max_iteration': dict(users_by_iterations)
        }
    
    def _analyze_progress_stats(self) -> Dict[str, Any]:
        """Analyze idea progress statistics."""
        progress_data = {
            'total_ideas': len(self.ideas),
            'avg_progress': 0,
            'progress_distribution': defaultdict(int),
            'framework_progress': {
                'Disciplined Entrepreneurship': {
                    'avg_progress': 0,
                    'total_ideas': 0
                },
                'Startup Tactics': {
                    'avg_progress': 0,
                    'total_ideas': 0
                }
            }
        }
        
        # Track progress metrics
        total_progress = 0
        de_total = 0
        de_count = 0
        st_total = 0
        st_count = 0
        
        for idea in self.ideas:
            progress = idea.get('total_progress', 0)
            total_progress += progress
            
            # Track by 10% increments
            progress_bucket = int(progress / 10) * 10
            progress_data['progress_distribution'][progress_bucket] += 1
            
            # Track by framework
            if 'Disciplined Entrepreneurship' in idea.get('frameworks', []):
                de_total += idea.get('de_progress', 0)
                de_count += 1
            
            if 'Startup Tactics' in idea.get('frameworks', []):
                st_total += idea.get('st_progress', 0)
                st_count += 1
        
        # Calculate averages
        if len(self.ideas) > 0:
            progress_data['avg_progress'] = total_progress / len(self.ideas)
        
        if de_count > 0:
            progress_data['framework_progress']['Disciplined Entrepreneurship']['avg_progress'] = de_total / de_count
            progress_data['framework_progress']['Disciplined Entrepreneurship']['total_ideas'] = de_count
        
        if st_count > 0:
            progress_data['framework_progress']['Startup Tactics']['avg_progress'] = st_total / st_count
            progress_data['framework_progress']['Startup Tactics']['total_ideas'] = st_count
        
        # Convert defaultdict to regular dict
        progress_data['progress_distribution'] = dict(progress_data['progress_distribution'])
        
        return progress_data
    
    def _calculate_completion_rate(self, framework: str) -> Dict[str, Any]:
        """
        Calculate completion rate for a specific framework.
        
        Args:
            framework: Framework name
            
        Returns:
            Dictionary of completion statistics
        """
        completion_stats = {
            'total_ideas': 0,
            'completed_ideas': 0,
            'completion_rate': 0,
            'avg_progress': 0
        }
        
        # Track progress for this framework
        total_progress = 0
        framework_ideas = []
        
        for idea in self.ideas:
            if framework in idea.get('frameworks', []):
                framework_ideas.append(idea)
                
                # Get framework-specific progress
                if framework == 'Disciplined Entrepreneurship':
                    progress = idea.get('de_progress', 0)
                elif framework == 'Startup Tactics':
                    progress = idea.get('st_progress', 0)
                else:
                    progress = 0
                
                total_progress += progress
                
                # Count as completed if progress is at least 80%
                if progress >= 80:
                    completion_stats['completed_ideas'] += 1
        
        # Update statistics
        completion_stats['total_ideas'] = len(framework_ideas)
        
        if completion_stats['total_ideas'] > 0:
            completion_stats['completion_rate'] = (
                completion_stats['completed_ideas'] / completion_stats['total_ideas']
            )
            completion_stats['avg_progress'] = total_progress / completion_stats['total_ideas']
        
        return completion_stats
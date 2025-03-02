"""
Engagement analyzer for the AI thesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils import get_logger

logger = get_logger("engagement_analyzer")


class EngagementAnalyzer:
    """Analyzes user engagement and process progression."""
    
    def __init__(self, users: List[Dict[str, Any]], ideas: List[Dict[str, Any]], steps: List[Dict[str, Any]]):
        """
        Initialize the engagement analyzer.
        
        Args:
            users: List of processed user records
            ideas: List of processed idea records
            steps: List of processed step records
        """
        self.users = users
        self.ideas = ideas
        self.steps = steps
        
        # Create lookup maps for efficient access
        self.ideas_by_id = {idea.get('id'): idea for idea in ideas}
        self.steps_by_idea = self._group_steps_by_idea()
        self.steps_by_owner = self._group_steps_by_owner()
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive engagement analysis.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info("Performing engagement analysis")
        
        results = {
            'process_completion': self._analyze_process_completion(),
            'dropout_points': self._analyze_dropout_points(),
            'time_based_engagement': self._analyze_time_based_engagement(),
            'cohort_comparison': self._analyze_cohort_comparison()
        }
        
        return results
    
    def _analyze_process_completion(self) -> Dict[str, Any]:
        """Analyze how users progress through the idea development process."""
        completion_stats = {
            'total_ideas': len(self.ideas),
            'ideas_with_steps': 0,
            'avg_steps_per_idea': 0,
            'max_steps_per_idea': 0,
            'step_distribution': defaultdict(int),
            'completion_by_framework': {
                'Disciplined Entrepreneurship': {
                    'avg_completion': 0,
                    'total_ideas': 0
                },
                'Startup Tactics': {
                    'avg_completion': 0,
                    'total_ideas': 0
                }
            }
        }
        
        # Track step counts
        total_steps = 0
        ideas_with_steps = 0
        max_steps = 0
        
        de_completion_total = 0
        de_ideas_count = 0
        st_completion_total = 0
        st_ideas_count = 0
        
        # Calculate step counts by idea
        for idea_id, steps in self.steps_by_idea.items():
            if not steps:
                continue
                
            # Count ideas with steps
            ideas_with_steps += 1
            
            # Count steps for this idea
            step_count = len(steps)
            total_steps += step_count
            max_steps = max(max_steps, step_count)
            
            # Track steps per idea distribution
            completion_stats['step_distribution'][step_count] += 1
            
            # Track framework-specific completion
            framework_counts = self._count_frameworks_for_idea(steps)
            
            for framework, count in framework_counts.items():
                if framework == 'Disciplined Entrepreneurship':
                    de_completion_total += count
                    de_ideas_count += 1
                elif framework == 'Startup Tactics':
                    st_completion_total += count
                    st_ideas_count += 1
        
        # Calculate averages
        completion_stats['ideas_with_steps'] = ideas_with_steps
        
        if ideas_with_steps > 0:
            completion_stats['avg_steps_per_idea'] = total_steps / ideas_with_steps
        
        completion_stats['max_steps_per_idea'] = max_steps
        
        # Calculate framework-specific averages
        if de_ideas_count > 0:
            completion_stats['completion_by_framework']['Disciplined Entrepreneurship']['avg_completion'] = (
                de_completion_total / de_ideas_count
            )
            completion_stats['completion_by_framework']['Disciplined Entrepreneurship']['total_ideas'] = de_ideas_count
        
        if st_ideas_count > 0:
            completion_stats['completion_by_framework']['Startup Tactics']['avg_completion'] = (
                st_completion_total / st_ideas_count
            )
            completion_stats['completion_by_framework']['Startup Tactics']['total_ideas'] = st_ideas_count
        
        # Convert defaultdict to regular dict
        completion_stats['step_distribution'] = dict(completion_stats['step_distribution'])
        
        return completion_stats
    
    def _analyze_dropout_points(self) -> Dict[str, Any]:
        """Analyze where users stop in the process."""
        # Track step progression to identify common dropout points
        step_progression = defaultdict(int)
        final_steps = defaultdict(int)
        
        # Group steps by idea
        for idea_id, steps in self.steps_by_idea.items():
            if not steps:
                continue
            
            # Sort steps by creation date
            sorted_steps = sorted(
                steps,
                key=lambda s: s.get('created_at', ''),
                reverse=True
            )
            
            # Track all steps in the progression
            for step in sorted_steps:
                step_name = step.get('step_name', '')
                step_progression[step_name] += 1
            
            # The last step is the most recent one
            last_step = sorted_steps[0]
            last_step_name = last_step.get('step_name', '')
            
            # Track final steps
            final_steps[last_step_name] += 1
        
        # Calculate progression rates
        step_completion_rates = {}
        total_ideas_with_steps = len(self.steps_by_idea)
        
        if total_ideas_with_steps > 0:
            for step, count in step_progression.items():
                step_completion_rates[step] = count / total_ideas_with_steps
        
        # Calculate dropout rates for each step
        dropout_rates = {}
        
        for step, count in final_steps.items():
            if step in step_progression:
                # Dropout rate is the percentage of ideas that end at this step
                dropout_rates[step] = count / step_progression[step]
            else:
                dropout_rates[step] = 0
        
        return {
            'step_progression': dict(step_progression),
            'final_steps': dict(final_steps),
            'step_completion_rates': step_completion_rates,
            'dropout_rates': dropout_rates
        }
    
    def _analyze_time_based_engagement(self) -> Dict[str, Any]:
        """Analyze time-based engagement patterns."""
        # Group steps by creation date
        steps_by_date = defaultdict(list)
        
        for step in self.steps:
            created_at = step.get('created_at')
            if created_at:
                # Extract date part only (YYYY-MM-DD)
                if 'T' in created_at:
                    date_part = created_at.split('T')[0]
                else:
                    date_part = created_at
                
                steps_by_date[date_part].append(step)
        
        # Calculate daily activity
        daily_activity = {}
        for date, steps in steps_by_date.items():
            daily_activity[date] = {
                'steps_count': len(steps),
                'unique_ideas': len(set(step.get('idea_id') for step in steps if step.get('idea_id'))),
                'unique_users': len(set(step.get('owner') for step in steps if step.get('owner')))
            }
        
        # Group by month for monthly analysis
        monthly_activity = defaultdict(lambda: {'steps': 0, 'ideas': set(), 'users': set()})
        
        for date, steps in steps_by_date.items():
            month = date[:7]  # Extract YYYY-MM
            
            monthly_activity[month]['steps'] += len(steps)
            monthly_activity[month]['ideas'].update(
                step.get('idea_id') for step in steps if step.get('idea_id')
            )
            monthly_activity[month]['users'].update(
                step.get('owner') for step in steps if step.get('owner')
            )
        
        # Convert sets to counts for monthly activity
        monthly_stats = {}
        for month, data in monthly_activity.items():
            monthly_stats[month] = {
                'steps_count': data['steps'],
                'unique_ideas': len(data['ideas']),
                'unique_users': len(data['users'])
            }
        
        # Check for seasonal patterns and peak usage periods
        seasonal_patterns = self._identify_seasonal_patterns(monthly_stats)
        
        # Calculate time between steps
        step_intervals = self._calculate_step_intervals()
        
        return {
            'daily_activity': daily_activity,
            'monthly_activity': monthly_stats,
            'seasonal_patterns': seasonal_patterns,
            'step_intervals': step_intervals
        }
    
    def _analyze_cohort_comparison(self) -> Dict[str, Any]:
        """Compare engagement across different user cohorts."""
        # Define cohorts based on user types
        cohorts = {
            'by_user_type': self._analyze_user_type_cohorts(),
            'by_institution': self._analyze_institution_cohorts(),
            'by_enrollment': self._analyze_enrollment_cohorts()
        }
        
        return cohorts
    
    def _group_steps_by_idea(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group steps by idea ID for efficient access."""
        steps_by_idea = defaultdict(list)
        
        for step in self.steps:
            idea_id = step.get('idea_id')
            if idea_id:
                steps_by_idea[idea_id].append(step)
        
        return steps_by_idea
    
    def _group_steps_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group steps by owner for efficient access."""
        steps_by_owner = defaultdict(list)
        
        for step in self.steps:
            owner = step.get('owner')
            if owner:
                steps_by_owner[owner].append(step)
        
        return steps_by_owner
    
    def _count_frameworks_for_idea(self, steps: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count steps by framework for an idea.
        
        Args:
            steps: List of steps for an idea
            
        Returns:
            Dictionary of framework counts
        """
        framework_counts = defaultdict(int)
        
        for step in steps:
            framework = step.get('framework')
            if framework:
                framework_counts[framework] += 1
        
        return dict(framework_counts)
    
    def _identify_seasonal_patterns(self, monthly_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify seasonal patterns in engagement.
        
        Args:
            monthly_stats: Monthly activity statistics
            
        Returns:
            Dictionary of seasonal patterns
        """
        # Extract months and years
        month_activity = defaultdict(list)  # Month number -> activity levels
        year_activity = defaultdict(list)   # Year -> activity levels
        
        for month_str, stats in monthly_stats.items():
            try:
                year, month = month_str.split('-')
                month_activity[int(month)].append(stats['steps_count'])
                year_activity[year].append(stats['steps_count'])
            except (ValueError, IndexError):
                continue
        
        # Calculate average activity by month
        avg_monthly_activity = {}
        for month, activities in month_activity.items():
            if activities:
                avg_monthly_activity[month] = sum(activities) / len(activities)
        
        # Find peak months
        peak_months = []
        if avg_monthly_activity:
            max_activity = max(avg_monthly_activity.values())
            peak_months = [
                month for month, activity in avg_monthly_activity.items()
                if activity >= 0.8 * max_activity  # Consider months with at least 80% of max activity
            ]
        
        # Identify trends in academic calendar
        academic_patterns = {
            'semester_start': False,  # Jan/Feb and Aug/Sep
            'semester_end': False,    # May and Dec
            'summer_slump': False     # Jun/Jul
        }
        
        if avg_monthly_activity:
            # Check for semester start peaks
            if any(m in peak_months for m in [1, 2, 8, 9]):
                academic_patterns['semester_start'] = True
            
            # Check for semester end peaks
            if any(m in peak_months for m in [5, 12]):
                academic_patterns['semester_end'] = True
            
            # Check for summer slump
            summer_activity = [avg_monthly_activity.get(6, 0), avg_monthly_activity.get(7, 0)]
            non_summer_activity = [
                activity for month, activity in avg_monthly_activity.items()
                if month not in [6, 7]
            ]
            
            if summer_activity and non_summer_activity:
                avg_summer = sum(summer_activity) / len(summer_activity)
                avg_non_summer = sum(non_summer_activity) / len(non_summer_activity)
                
                if avg_summer < 0.7 * avg_non_summer:  # 30% drop in summer
                    academic_patterns['summer_slump'] = True
        
        return {
            'monthly_averages': avg_monthly_activity,
            'peak_months': peak_months,
            'academic_patterns': academic_patterns
        }
    
    def _calculate_step_intervals(self) -> Dict[str, Any]:
        """
        Calculate time intervals between steps.
        
        Returns:
            Dictionary of step interval statistics
        """
        intervals_by_idea = {}
        
        for idea_id, steps in self.steps_by_idea.items():
            if len(steps) < 2:
                continue
            
            # Sort steps by creation date
            sorted_steps = sorted(
                steps,
                key=lambda s: s.get('created_at', ''),
                reverse=False
            )
            
            # Calculate intervals between steps
            intervals = []
            for i in range(1, len(sorted_steps)):
                prev_step = sorted_steps[i-1]
                curr_step = sorted_steps[i]
                
                prev_date = self._parse_date(prev_step.get('created_at', ''))
                curr_date = self._parse_date(curr_step.get('created_at', ''))
                
                if prev_date and curr_date:
                    # Calculate days between steps
                    days_between = (curr_date - prev_date).days
                    intervals.append(days_between)
            
            if intervals:
                intervals_by_idea[idea_id] = intervals
        
        # Calculate average intervals
        all_intervals = [
            interval
            for idea_intervals in intervals_by_idea.values()
            for interval in idea_intervals
        ]
        
        avg_interval = 0
        if all_intervals:
            avg_interval = sum(all_intervals) / len(all_intervals)
        
        return {
            'intervals_by_idea': intervals_by_idea,
            'avg_interval_days': avg_interval,
            'max_interval_days': max(all_intervals) if all_intervals else 0,
            'min_interval_days': min(all_intervals) if all_intervals else 0
        }
    
    def _analyze_user_type_cohorts(self) -> Dict[str, Any]:
        """
        Compare engagement across user type cohorts.
        
        Returns:
            Dictionary of cohort comparisons
        """
        # Group users by type
        users_by_type = defaultdict(list)
        
        for user in self.users:
            user_type = user.get('type', 'unknown')
            users_by_type[user_type].append(user)
        
        # Calculate engagement metrics for each cohort
        cohort_metrics = {}
        
        for user_type, users in users_by_type.items():
            # Skip small cohorts
            if len(users) < 5:
                continue
            
            user_ids = [user.get('id') for user in users]
            user_emails = [user.get('email') for user in users]
            
            # Count ideas and steps
            ideas_count = 0
            steps_count = 0
            active_users = 0
            
            for email in user_emails:
                if not email:
                    continue
                
                # Count ideas by this user
                user_ideas = [
                    idea for idea in self.ideas
                    if idea.get('owner') == email
                ]
                
                if user_ideas:
                    active_users += 1
                    ideas_count += len(user_ideas)
                
                # Count steps by this user
                user_steps = self.steps_by_owner.get(email, [])
                steps_count += len(user_steps)
            
            # Calculate metrics
            cohort_size = len(users)
            active_rate = active_users / cohort_size if cohort_size > 0 else 0
            ideas_per_active_user = ideas_count / active_users if active_users > 0 else 0
            steps_per_idea = steps_count / ideas_count if ideas_count > 0 else 0
            
            cohort_metrics[user_type] = {
                'cohort_size': cohort_size,
                'active_users': active_users,
                'active_rate': active_rate,
                'ideas_count': ideas_count,
                'steps_count': steps_count,
                'ideas_per_active_user': ideas_per_active_user,
                'steps_per_idea': steps_per_idea
            }
        
        return cohort_metrics
    
    def _analyze_institution_cohorts(self) -> Dict[str, Any]:
        """
        Compare engagement across institution cohorts.
        
        Returns:
            Dictionary of cohort comparisons
        """
        # Group users by institution
        users_by_institution = defaultdict(list)
        
        for user in self.users:
            institution = user.get('institution', {})
            if institution:
                institution_name = institution.get('name', 'unknown')
                users_by_institution[institution_name].append(user)
        
        # Calculate engagement metrics for each cohort
        cohort_metrics = {}
        
        for institution, users in users_by_institution.items():
            # Skip small cohorts or unknown institution
            if len(users) < 5 or institution == 'unknown':
                continue
            
            user_emails = [user.get('email') for user in users]
            
            # Calculate metrics similar to user type cohorts
            ideas_count = 0
            steps_count = 0
            active_users = 0
            
            for email in user_emails:
                if not email:
                    continue
                
                # Count ideas by this user
                user_ideas = [
                    idea for idea in self.ideas
                    if idea.get('owner') == email
                ]
                
                if user_ideas:
                    active_users += 1
                    ideas_count += len(user_ideas)
                
                # Count steps by this user
                user_steps = self.steps_by_owner.get(email, [])
                steps_count += len(user_steps)
            
            # Calculate metrics
            cohort_size = len(users)
            active_rate = active_users / cohort_size if cohort_size > 0 else 0
            ideas_per_active_user = ideas_count / active_users if active_users > 0 else 0
            steps_per_idea = steps_count / ideas_count if ideas_count > 0 else 0
            
            cohort_metrics[institution] = {
                'cohort_size': cohort_size,
                'active_users': active_users,
                'active_rate': active_rate,
                'ideas_count': ideas_count,
                'steps_count': steps_count,
                'ideas_per_active_user': ideas_per_active_user,
                'steps_per_idea': steps_per_idea
            }
        
        return cohort_metrics
    
    def _analyze_enrollment_cohorts(self) -> Dict[str, Any]:
        """
        Compare engagement across enrollment cohorts.
        
        Returns:
            Dictionary of cohort comparisons
        """
        # Group users by enrollment
        users_by_enrollment = defaultdict(list)
        
        for user in self.users:
            enrollments = user.get('enrollments', [])
            
            if enrollments:
                for enrollment in enrollments:
                    users_by_enrollment[enrollment].append(user)
            else:
                users_by_enrollment['no_enrollment'].append(user)
        
        # Calculate engagement metrics for each cohort
        cohort_metrics = {}
        
        for enrollment, users in users_by_enrollment.items():
            # Skip small cohorts
            if len(users) < 5:
                continue
            
            user_emails = [user.get('email') for user in users]
            
            # Calculate metrics similar to other cohorts
            ideas_count = 0
            steps_count = 0
            active_users = 0
            
            for email in user_emails:
                if not email:
                    continue
                
                # Count ideas by this user
                user_ideas = [
                    idea for idea in self.ideas
                    if idea.get('owner') == email
                ]
                
                if user_ideas:
                    active_users += 1
                    ideas_count += len(user_ideas)
                
                # Count steps by this user
                user_steps = self.steps_by_owner.get(email, [])
                steps_count += len(user_steps)
            
            # Calculate metrics
            cohort_size = len(users)
            active_rate = active_users / cohort_size if cohort_size > 0 else 0
            ideas_per_active_user = ideas_count / active_users if active_users > 0 else 0
            steps_per_idea = steps_count / ideas_count if ideas_count > 0 else 0
            
            cohort_metrics[enrollment] = {
                'cohort_size': cohort_size,
                'active_users': active_users,
                'active_rate': active_rate,
                'ideas_count': ideas_count,
                'steps_count': steps_count,
                'ideas_per_active_user': ideas_per_active_user,
                'steps_per_idea': steps_per_idea
            }
        
        return cohort_metrics
    
    @staticmethod
    def _parse_date(date_string: str) -> Optional[datetime]:
        """Parse a date string in various formats."""
        if not date_string:
            return None
        
        # Try various date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with milliseconds
            '%Y-%m-%dT%H:%M:%SZ',     # ISO format without milliseconds
            '%Y-%m-%d',               # Simple date format
            '%Y/%m/%d',               # Alternative date format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        return None
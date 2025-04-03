"""
User analyzer for data analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.processors.base_analyzer import BaseAnalyzer
from src.utils import DataGroupingUtils, DateUtils, StatsUtils


class UserAnalyzer(BaseAnalyzer):
    """Analyzes user demographics, cohorts, and other user attributes."""
    
    def __init__(self, users: List[Dict[str, Any]], ideas: Optional[List[Dict[str, Any]]] = None, 
                steps: Optional[List[Dict[str, Any]]] = None, end_date: Optional[datetime] = None):
        """
        Initialize the user analyzer.
        
        Args:
            users: List of processed user records
            ideas: Optional list of processed idea records
            steps: Optional list of processed step records
            end_date: Optional reference date for time-based calculations (default: now)
        """
        super().__init__("user_analyzer")
        self.users = users
        self.ideas = ideas or []
        self.steps = steps or []
        
        # Set reference date for time-based calculations
        self.end_date = end_date or datetime(2025, 2, 4, tzinfo=timezone.utc)  # Default from original code
    
    def validate_data(self) -> None:
        """Validate input user data."""
        if not self.users:
            self.logger.warning("No user data provided")
    
    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive user analysis.
        
        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Performing user analysis")
        
        # Create user lookup by email for faster reference
        self.user_by_email = {user.get('email'): user for user in self.users if user.get('email')}
        
        # Analyze different aspects of user data
        results = {
            'user_counts': self._analyze_user_counts(),
            'demographics': self._analyze_demographics(),
            'cohorts': self._analyze_cohorts(),
            'affiliations': self._analyze_affiliations(),
            'institutions': self._analyze_institutions(),
            'enrollment': self._analyze_enrollments()
        }
        
        # Only run activity summary if ideas are provided
        if self.ideas:
            results['activity_summary'] = self._analyze_activity_summary()
        
        return results
    
    def _analyze_user_counts(self) -> Dict[str, int]:
        """Analyze basic user count metrics."""
        counts = {
            'total_users': len(self.users),
            'active_users': 0,
            'inactive_users': 0,
            'with_profile_image': 0,
            'with_complete_profile': 0,
        }
        
        for user in self.users:
            # Count active users (those with recent login)
            if self._is_active_user(user):
                counts['active_users'] += 1
            else:
                counts['inactive_users'] += 1
            
            # Count users with profile images
            if user.get('orbit_profile', {}).get('has_image'):
                counts['with_profile_image'] += 1
            
            # Count users with complete profiles (name, email)
            if (user.get('first_name') and 
                user.get('last_name') and 
                user.get('email')):
                counts['with_complete_profile'] += 1
        
        return counts
    
    def _analyze_demographics(self) -> Dict[str, Any]:
        """Analyze user demographic distributions."""
        # Group users by type
        user_types = DataGroupingUtils.count_by_key(self.users, 'type')
        
        # Extract and count user personas from orbit profiles
        persona_counts = defaultdict(int)
        interest_counts = defaultdict(int)
        
        for user in self.users:
            orbit_profile = user.get('orbit_profile', {})
            
            # Count personas
            for persona in orbit_profile.get('persona', []):
                if persona:
                    persona_counts[persona] += 1
            
            # Count interests
            for interest in orbit_profile.get('interests', []):
                if interest:
                    interest_counts[interest] += 1
        
        # Calculate gender distribution if data is available
        gender_counts = DataGroupingUtils.count_by_key(self.users, 'gender')
        
        return {
            'user_types': user_types,
            'personas': dict(persona_counts),
            'interests': dict(interest_counts),
            'top_interests': StatsUtils.find_top_n(interest_counts, 10),
            'gender': gender_counts
        }
    
    def _analyze_cohorts(self) -> Dict[str, Any]:
        """Analyze user cohorts by various criteria."""
        # Time-based cohorts
        # User join date cohort (by year-month)
        creation_cohorts = defaultdict(int)
        
        for user in self.users:
            # Creation date cohort (by year-month)
            created_date = user.get('created_date')
            if created_date:
                try:
                    # Extract year-month
                    if 'T' in created_date:
                        # ISO format
                        year_month = created_date.split('T')[0][:7]  # YYYY-MM
                    else:
                        # Other format
                        date_obj = datetime.strptime(created_date, "%Y-%m-%d")
                        year_month = date_obj.strftime("%Y-%m")
                    
                    creation_cohorts[year_month] += 1
                except (ValueError, IndexError):
                    pass
        
        # Last login cohort (30, 60, 90, 180, 365 days)
        activity_cohorts = {
            'active_last_30d': 0,
            'active_31d_90d': 0,
            'active_91d_180d': 0, 
            'active_181d_365d': 0,
            'inactive_over_365d': 0
        }
        
        for user in self.users:
            days_since_login = DateUtils.get_days_since(user.get('last_login'), self.end_date)
            
            if days_since_login is None:
                activity_cohorts['inactive_over_365d'] += 1
            elif days_since_login <= 30:
                activity_cohorts['active_last_30d'] += 1
            elif days_since_login <= 90:
                activity_cohorts['active_31d_90d'] += 1
            elif days_since_login <= 180:
                activity_cohorts['active_91d_180d'] += 1
            elif days_since_login <= 365:
                activity_cohorts['active_181d_365d'] += 1
            else:
                activity_cohorts['inactive_over_365d'] += 1
        
        # Create user types cohort
        user_types = DataGroupingUtils.count_by_key(self.users, 'type')
        
        return {
            'user_types': user_types,
            'creation_dates': dict(creation_cohorts),
            'activity': activity_cohorts
        }
    
    def _analyze_affiliations(self) -> Dict[str, Any]:
        """Analyze user affiliations and departments."""
        # Track affiliation types
        affiliation_counts = defaultdict(int)
        department_counts = defaultdict(int)
        
        for user in self.users:
            # Check user type as primary affiliation
            user_type = user.get('type')
            if user_type:
                affiliation_counts[user_type] += 1
            
            # Check detailed affiliations
            for affiliation in user.get('affiliations', []):
                aff_type = affiliation.get('type')
                if aff_type:
                    affiliation_counts[f"{aff_type} (detailed)"] += 1
                
                # Count department affiliations
                for dept in affiliation.get('departments', []):
                    dept_name = dept.get('name')
                    if dept_name:
                        department_counts[dept_name] += 1
        
        # Get top departments
        top_departments = StatsUtils.find_top_n(department_counts, 10)
        
        return {
            'affiliation_counts': dict(affiliation_counts),
            'department_counts': dict(department_counts),
            'top_departments': top_departments
        }
    
    def _analyze_institutions(self) -> Dict[str, Any]:
        """Analyze institutions associated with users."""
        institution_counts = defaultdict(int)
        
        for user in self.users:
            institution = user.get('institution', {})
            if institution:
                institution_name = institution.get('name', 'Unknown')
                institution_counts[institution_name] += 1
        
        # Get top institutions
        top_institutions = StatsUtils.find_top_n(institution_counts, 10)
        
        # Calculate percentage distribution
        total_users = len(self.users)
        percentages = {
            k: (v / total_users) * 100 if total_users > 0 else 0
            for k, v in institution_counts.items()
        }
        
        return {
            'institution_counts': dict(institution_counts),
            'top_institutions': top_institutions,
            'percentages': percentages
        }
    
    def _analyze_enrollments(self) -> Dict[str, Any]:
        """Analyze enrollment patterns."""
        enrollment_counts = defaultdict(int)
        users_with_enrollments = 0
        total_enrollments = 0
        
        for user in self.users:
            enrollments = user.get('enrollments', [])
            if enrollments:
                users_with_enrollments += 1
                total_enrollments += len(enrollments)
                
                for enrollment in enrollments:
                    enrollment_counts[enrollment] += 1
        
        # Calculate average enrollments per user
        avg_enrollments = 0
        if users_with_enrollments > 0:
            avg_enrollments = total_enrollments / users_with_enrollments
        
        # Get top courses
        top_courses = StatsUtils.find_top_n(enrollment_counts, 10)
        
        return {
            'course_popularity': dict(enrollment_counts),
            'users_with_enrollments': users_with_enrollments,
            'total_enrollments': total_enrollments,
            'avg_enrollments_per_user': avg_enrollments,
            'top_courses': top_courses
        }
    
    def _analyze_activity_summary(self) -> Dict[str, Any]:
        """Analyze basic activity metrics for users."""
        if not self.ideas:
            return {}
            
        # Count ideas by owner
        ideas_by_owner = DataGroupingUtils.group_by_key(self.ideas, 'owner')
        
        # Create activity counts
        user_count = len(self.users)
        users_with_ideas = len(ideas_by_owner)
        active_rate = users_with_ideas / user_count if user_count > 0 else 0
        
        # Calculate ideas per user stats
        ideas_per_user = {}
        for email, user_ideas in ideas_by_owner.items():
            ideas_per_user[email] = len(user_ideas)
        
        # Get idea count distribution
        distribution = defaultdict(int)
        for count in ideas_per_user.values():
            bucket = min(count, 10)  # Cap at 10+
            if count >= 10:
                bucket = '10+'
            distribution[bucket] += 1
            
        # Add users with no ideas
        distribution[0] = user_count - users_with_ideas
        
        # Calculate average ideas per active user
        avg_ideas = 0
        if users_with_ideas > 0:
            avg_ideas = len(self.ideas) / users_with_ideas
            
        return {
            'users_with_ideas': users_with_ideas,
            'active_rate': active_rate,
            'avg_ideas_per_active_user': avg_ideas,
            'idea_count_distribution': dict(distribution),
            'total_ideas': len(self.ideas)
        }
    
    def _is_active_user(self, user: Dict[str, Any]) -> bool:
        """
        Check if a user is considered active (recent login).
        
        Args:
            user: User record
            
        Returns:
            True if active, False otherwise
        """
        # Consider active if logged in within the last 90 days
        days_since_login = DateUtils.get_days_since(user.get('last_login'), self.end_date)
        return days_since_login is not None and days_since_login <= 90
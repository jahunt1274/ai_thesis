"""
Demographic analyzer for the AI thesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils import get_logger

logger = get_logger("demographic_analyzer")


class DemographicAnalyzer:
    """Analyzes user demographics and distributions."""
    
    def __init__(self, users: List[Dict[str, Any]]):
        """
        Initialize the demographic analyzer.
        
        Args:
            users: List of processed user records
        """
        self.users = users
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive demographic analysis.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info("Performing demographic analysis")
        
        results = {
            'user_counts': self._analyze_user_counts(),
            'affiliations': self._analyze_affiliations(),
            'cohorts': self._analyze_cohorts(),
            'enrollments': self._analyze_enrollments(),
            'interests': self._analyze_interests(),
            'institutions': self._analyze_institutions()
        }
        
        return results
    
    def _analyze_user_counts(self) -> Dict[str, int]:
        """Analyze basic user counts."""
        counts = {
            'total_users': len(self.users),
            'active_users': 0,
            'inactive_users': 0,
            'with_profile_image': 0,
            'with_complete_profile': 0
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
    
    def _analyze_affiliations(self) -> Dict[str, int]:
        """Analyze user affiliations."""
        # Track affiliation types
        affiliation_counts = defaultdict(int)
        
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
                        affiliation_counts[f"Department: {dept_name}"] += 1
        
        return dict(affiliation_counts)
    
    def _analyze_cohorts(self) -> Dict[str, Any]:
        """Analyze user cohorts by various criteria."""
        # Time-based cohorts
        time_cohorts = defaultdict(int)
        
        # Create user types cohort
        user_types = defaultdict(int)
        
        # User join date cohort (by year-month)
        creation_cohorts = defaultdict(int)
        
        for user in self.users:
            # User type cohort
            user_type = user.get('type', 'unknown')
            user_types[user_type] += 1
            
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
            days_since_login = self._get_days_since_login(user)
            
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
        
        return {
            'user_types': dict(user_types),
            'creation_dates': dict(creation_cohorts),
            'activity': activity_cohorts
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
        
        return {
            'course_popularity': dict(enrollment_counts),
            'users_with_enrollments': users_with_enrollments,
            'total_enrollments': total_enrollments,
            'avg_enrollments_per_user': avg_enrollments,
            'top_courses': sorted(
                enrollment_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 most popular courses
        }
    
    def _analyze_interests(self) -> Dict[str, int]:
        """Analyze user interests from Orbit profiles."""
        interest_counts = defaultdict(int)
        persona_counts = defaultdict(int)
        
        for user in self.users:
            orbit_profile = user.get('orbit_profile', {})
            
            # Count interests
            for interest in orbit_profile.get('interests', []):
                if interest:
                    interest_counts[interest] += 1
            
            # Count personas
            for persona in orbit_profile.get('persona', []):
                if persona:
                    persona_counts[persona] += 1
        
        return {
            'interests': dict(interest_counts),
            'personas': dict(persona_counts)
        }
    
    def _analyze_institutions(self) -> Dict[str, int]:
        """Analyze institutions associated with users."""
        institution_counts = defaultdict(int)
        
        for user in self.users:
            institution = user.get('institution', {})
            if institution:
                institution_name = institution.get('name', 'Unknown')
                institution_counts[institution_name] += 1
        
        return dict(institution_counts)
    
    @staticmethod
    def _is_active_user(user: Dict[str, Any]) -> bool:
        """
        Check if a user is considered active (recent login).
        
        Args:
            user: User record
            
        Returns:
            True if active, False otherwise
        """
        # Consider active if logged in within the last 90 days
        days_since_login = DemographicAnalyzer._get_days_since_login(user)
        return days_since_login is not None and days_since_login <= 90
    
    @staticmethod
    def _get_days_since_login(user: Dict[str, Any]) -> Optional[int]:
        """
        Calculate days since last login.
        
        Args:
            user: User record
            
        Returns:
            Number of days since last login, or None if unavailable
        """
        last_login = user.get('last_login')
        if not last_login:
            return None
        
        try:
            # Parse last login date
            if 'T' in last_login:
                # ISO format
                login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            else:
                # Try to parse with various formats
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        login_date = datetime.strptime(last_login, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return None  # Could not parse date
            
            # Calculate days since login
            days_since = (datetime.now() - login_date).days
            return days_since
        
        except (ValueError, TypeError):
            return None
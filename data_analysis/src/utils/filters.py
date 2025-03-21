"""
Filtering utilities for the AI thesis analysis.
"""

from typing import List, Dict, Any, Callable, Optional, Set

class DataFilter:
    """Provides filtering capabilities for users, ideas, and steps data."""

    @staticmethod
    def filter_by_course(users: List[Dict[str, Any]], 
                         ideas: List[Dict[str, Any]], 
                         steps: List[Dict[str, Any]],
                         course_code: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter data to include only users enrolled in a specific course and their related ideas and steps.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            course_code: Course code to filter by (e.g., "15.390")
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        # Identify users enrolled in the target course
        enrolled_user_emails = set()
        
        for user in users:
            enrollments = user.get('enrollments', [])
            if any(str(enrollment).startswith(course_code) for enrollment in enrollments):
                if user.get('email'):
                    enrolled_user_emails.add(user.get('email'))
        
        # Apply the filters
        return DataFilter._apply_user_filter(users, ideas, steps, enrolled_user_emails)
    
    @staticmethod
    def filter_by_user_type(users: List[Dict[str, Any]], 
                           ideas: List[Dict[str, Any]], 
                           steps: List[Dict[str, Any]],
                           user_type: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter data to include only users of a specific type and their related ideas and steps.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            user_type: User type to filter by
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        # Identify users of the target type
        filtered_user_emails = set()
        
        for user in users:
            if user.get('type') == user_type and user.get('email'):
                filtered_user_emails.add(user.get('email'))
        
        # Apply the filters
        return DataFilter._apply_user_filter(users, ideas, steps, filtered_user_emails)
    
    @staticmethod
    def filter_by_activity(users: List[Dict[str, Any]], 
                          ideas: List[Dict[str, Any]], 
                          steps: List[Dict[str, Any]],
                          min_ideas: int = 0,
                          min_steps: int = 0) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter data to include only users with a minimum level of activity.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            min_ideas: Minimum number of ideas a user must have
            min_steps: Minimum number of steps a user must have
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        # Count ideas and steps per user
        ideas_by_user = {}
        steps_by_user = {}
        
        for idea in ideas:
            owner = idea.get('owner')
            if owner:
                ideas_by_user[owner] = ideas_by_user.get(owner, 0) + 1
        
        for step in steps:
            owner = step.get('owner')
            if owner:
                steps_by_user[owner] = steps_by_user.get(owner, 0) + 1
        
        # Identify users meeting the activity criteria
        active_user_emails = set()
        
        for user in users:
            email = user.get('email')
            if not email:
                continue
                
            if (ideas_by_user.get(email, 0) >= min_ideas and
                steps_by_user.get(email, 0) >= min_steps):
                active_user_emails.add(email)
        
        # Apply the filters
        return DataFilter._apply_user_filter(users, ideas, steps, active_user_emails)
    
    @staticmethod
    def filter_by_time_period(users: List[Dict[str, Any]], 
                             ideas: List[Dict[str, Any]], 
                             steps: List[Dict[str, Any]],
                             start_date: str,
                             end_date: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter data to include only users, ideas, and steps created within a time period.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        from datetime import datetime
        
        # Parse date strings to datetime objects
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Helper function to check if date is in range
        def is_in_range(date_str: Optional[str]) -> bool:
            if not date_str:
                return False
                
            try:
                # Handle different date formats
                if 'T' in date_str:
                    date = datetime.fromisoformat(date_str.split('T')[0])
                else:
                    date = datetime.fromisoformat(date_str)
                    
                return start <= date <= end
            except ValueError:
                return False
        
        # Filter users by creation date
        filtered_users = [user for user in users if is_in_range(user.get('created_date'))]
        
        # Filter ideas by creation date
        filtered_ideas = [idea for idea in ideas if is_in_range(idea.get('created_date'))]
        
        # Filter steps by creation date
        filtered_steps = [step for step in steps if is_in_range(step.get('created_at'))]
        
        return filtered_users, filtered_ideas, filtered_steps
    
    @staticmethod
    def _apply_user_filter(users: List[Dict[str, Any]], 
                          ideas: List[Dict[str, Any]], 
                          steps: List[Dict[str, Any]],
                          user_emails: Set[str]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Apply filtering based on a set of user emails.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            user_emails: Set of user emails to include
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        # Filter users
        filtered_users = [user for user in users if user.get('email') in user_emails]
        
        # Filter ideas
        filtered_ideas = [idea for idea in ideas if idea.get('owner') in user_emails]
        
        # Get IDs of filtered ideas for step filtering
        filtered_idea_ids = [idea.get('id') for idea in filtered_ideas if idea.get('id')]
        
        # Filter steps - either by owner or by idea_id
        filtered_steps = []
        for step in steps:
            # Include if owner is in filtered users
            if step.get('owner') in user_emails:
                filtered_steps.append(step)
            # OR include if idea_id is in filtered ideas
            elif step.get('idea_id') in filtered_idea_ids:
                filtered_steps.append(step)
        
        return filtered_users, filtered_ideas, filtered_steps
    
    @staticmethod
    def compose_filters(users: List[Dict[str, Any]], 
                       ideas: List[Dict[str, Any]], 
                       steps: List[Dict[str, Any]],
                       filters: List[Callable]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Apply multiple filters in sequence.
        
        Args:
            users: List of user records
            ideas: List of idea records
            steps: List of step records
            filters: List of filter functions to apply
            
        Returns:
            Tuple of (filtered_users, filtered_ideas, filtered_steps)
        """
        filtered_users, filtered_ideas, filtered_steps = users, ideas, steps
        
        for filter_func in filters:
            filtered_users, filtered_ideas, filtered_steps = filter_func(
                filtered_users, filtered_ideas, filtered_steps
            )
        
        return filtered_users, filtered_ideas, filtered_steps
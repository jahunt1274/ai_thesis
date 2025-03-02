from typing import Dict, Any, List
from datetime import datetime
from .base_processor import BaseProcessor

class UserJourneyProcessor(BaseProcessor):
    def process(self) -> Dict[str, Any]:
        """Process user journey data by combining user, idea, and step information."""
        if self.data and len(self.data) > 0:
            print("Sample user structure:", self.data[0])
            
        return {
            "journey_timelines": self._create_journey_timelines(),
            "completion_rates": self._analyze_completion_rates(),
            "user_engagement": self._analyze_user_engagement()
        }
    
    def _process_timestamp(self, timestamp_value: Any) -> str:
        """Safely process a timestamp value that could be in various formats."""
        try:
            if isinstance(timestamp_value, dict):
                # Handle case where timestamp is a dictionary with $date
                if '$date' in timestamp_value:
                    return timestamp_value['$date']
            elif isinstance(timestamp_value, (int, float)):
                # Handle case where timestamp is a number (milliseconds since epoch)
                return datetime.fromtimestamp(timestamp_value / 1000).isoformat()
            elif isinstance(timestamp_value, str):
                # Handle case where timestamp is already a string
                return timestamp_value
            return None
        except Exception as e:
            print(f"Error processing timestamp {timestamp_value}: {str(e)}")
            return None
    
    def _create_journey_timelines(self) -> List[Dict[str, Any]]:
        """Create timeline of user interactions with ideas and steps."""
        timelines = []
        for user in self.data:
            try:
                user_timeline = {
                    'user_id': user.get('kerberos') or user.get('owner'),
                    'user_email': user.get('email'),
                    'user_type': user.get('type'),
                    'events': []
                }
                
                # Add profile creation
                if 'created' in user:
                    created_date = self._process_timestamp(user['created'])
                    if created_date:
                        user_timeline['events'].append({
                            'type': 'profile_created',
                            'date': created_date,
                            'details': 'User profile created'
                        })
                
                # Add last login if available
                if 'last_login' in user:
                    last_login_date = self._process_timestamp(user['last_login'])
                    if last_login_date:
                        user_timeline['events'].append({
                            'type': 'last_login',
                            'date': last_login_date,
                            'details': 'User last login'
                        })
                
                # Add enrollment information if available
                if 'enrollments' in user:
                    user_timeline['events'].append({
                        'type': 'enrollments',
                        'count': len(user['enrollments']),
                        'details': user['enrollments']
                    })
                
                timelines.append(user_timeline)
            except Exception as e:
                print(f"Error processing user {user.get('kerberos', 'unknown')}: {str(e)}")
                continue
                
        return timelines
    
    def _analyze_completion_rates(self) -> Dict[str, float]:
        """Analyze participation rates by user type."""
        completion_rates = {
            'student': {'total': 0, 'active': 0},
            'professional': {'total': 0, 'active': 0},
            'staff': {'total': 0, 'active': 0},
            'MIT': {'total': 0, 'active': 0}  # Added MIT type
        }
        
        for user in self.data:
            user_type = user.get('type', 'unknown').lower()
            if user_type in completion_rates:
                completion_rates[user_type]['total'] += 1
                # Consider user active if they have enrollments or recent login
                if user.get('enrollments') or user.get('last_login'):
                    completion_rates[user_type]['active'] += 1
        
        # Calculate rates
        for user_type in completion_rates:
            total = completion_rates[user_type]['total']
            if total > 0:
                completion_rates[user_type]['participation_rate'] = (
                    completion_rates[user_type]['active'] / total
                )
            else:
                completion_rates[user_type]['participation_rate'] = 0
                
        return completion_rates
    
    def _analyze_user_engagement(self) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        engagement_metrics = {
            'enrollment_stats': self._get_enrollment_stats(),
            'user_type_distribution': self._get_user_type_distribution(),
            'active_users': self._get_active_users_count()
        }
        return engagement_metrics
    
    def _get_enrollment_stats(self) -> Dict[str, Any]:
        """Calculate statistics about enrollments."""
        total_enrollments = 0
        users_with_enrollments = 0
        course_popularity = {}
        
        for user in self.data:
            enrollments = user.get('enrollments', [])
            if enrollments:
                total_enrollments += len(enrollments)
                users_with_enrollments += 1
                # Track course popularity
                for course in enrollments:
                    course_popularity[course] = course_popularity.get(course, 0) + 1
                
        return {
            'total_enrollments': total_enrollments,
            'users_with_enrollments': users_with_enrollments,
            'avg_enrollments_per_user': (
                total_enrollments / users_with_enrollments 
                if users_with_enrollments > 0 else 0
            ),
            'most_popular_courses': sorted(
                course_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 most popular courses
        }
    
    def _get_user_type_distribution(self) -> Dict[str, int]:
        """Get distribution of user types."""
        type_counts = {}
        for user in self.data:
            user_type = user.get('type', 'unknown')
            type_counts[user_type] = type_counts.get(user_type, 0) + 1
        return type_counts
    
    def _get_active_users_count(self) -> Dict[str, int]:
        """Get detailed active user statistics."""
        stats = {
            'total_users': len(self.data),
            'active_last_30_days': 0,
            'active_last_90_days': 0,
            'with_enrollments': 0,
            'with_complete_profile': 0
        }
        
        current_time = datetime.now().timestamp() * 1000
        thirty_days_ms = 30 * 24 * 60 * 60 * 1000
        ninety_days_ms = 90 * 24 * 60 * 60 * 1000
        
        for user in self.data:
            # Check last login
            last_login = user.get('last_login')
            if isinstance(last_login, (int, float)):
                if (current_time - last_login) < thirty_days_ms:
                    stats['active_last_30_days'] += 1
                if (current_time - last_login) < ninety_days_ms:
                    stats['active_last_90_days'] += 1
            
            # Check enrollments
            if user.get('enrollments'):
                stats['with_enrollments'] += 1
            
            # Check profile completeness
            if user.get('first_name') and user.get('last_name') and user.get('email'):
                stats['with_complete_profile'] += 1
                
        return stats
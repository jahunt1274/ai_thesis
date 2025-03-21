from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils import get_logger

logger = get_logger("cohort_analyzer")


class CohortAnalyzer:
    """Analyzes user cohorts based on enrollment period and tool usage metrics."""
    
    def __init__(self, users: List[Dict[str, Any]], ideas: List[Dict[str, Any]], steps: List[Dict[str, Any]]):
        """
        Initialize the cohort analyzer.
        
        Args:
            users: List of processed user records
            ideas: List of processed idea records
            steps: List of processed step records
        """
        self.users = users
        self.ideas = ideas
        self.steps = steps
        
        # Create lookup maps for efficient access
        self.ideas_by_owner = self._group_ideas_by_owner()
        self.steps_by_idea = self._group_steps_by_idea()
        self.steps_by_owner = self._group_steps_by_owner()
        
        # Define time-based cohorts based on thesis plan
        self.time_cohorts = {
            "fall_2023": {  # No Jetpack (Control)
                "start_date": "2023-09-01", 
                "end_date": "2023-12-31",
                "tool_version": "none",
                "sections": 2
            },
            "spring_2024": {  # Jetpack v1
                "start_date": "2024-01-01", 
                "end_date": "2024-05-31",
                "tool_version": "v1",
                "sections": 2
            },
            "fall_2024": {  # Jetpack v2
                "start_date": "2024-09-01", 
                "end_date": "2024-12-31",
                "tool_version": "v2",
                "sections": 1
            },
            # Spring 2025 excluded as it's upcoming and no data available yet
        }
        
        # Define usage level thresholds
        self.usage_thresholds = {
            "steps": {
                "low": 1,     # At least 1 step
                "medium": 5,  # At least 5 steps
                "high": 15    # At least 15 steps
            },
            "ideas": {
                "low": 1,     # At least 1 idea
                "medium": 2,  # At least 2 ideas
                "high": 5     # At least 5 ideas
            },
            "completion": {
                "low": 0.2,    # At least 20% complete
                "medium": 0.5, # At least 50% complete
                "high": 0.8    # At least 80% complete
            },
            "interactions": {
                "low": 3,      # At least 3 interactions
                "medium": 10,  # At least 10 interactions
                "high": 20     # At least 20 interactions
            }
        }
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive cohort analysis.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info("Performing cohort analysis")
        
        results = {
            'time_cohorts': self._analyze_time_cohorts(),
            'usage_cohorts': self._analyze_usage_cohorts(),
            'enrollment_cohorts': self._analyze_enrollment_cohorts(),
            'tool_adoption': self._analyze_tool_adoption(),
            'learning_metrics': self._analyze_learning_metrics(),
            'cohort_comparison': self._analyze_cohort_comparison()
        }
        
        return results
    
    def _analyze_time_cohorts(self) -> Dict[str, Any]:
        """Analyze user distribution across time-based cohorts."""
        logger.info("Analyzing time-based cohorts")
        
        cohort_stats = {}
        
        # Group users by cohort based on their creation date
        for cohort_name, cohort_info in self.time_cohorts.items():
            cohort_start = self._parse_date(cohort_info["start_date"])
            cohort_end = self._parse_date(cohort_info["end_date"])
            
            # Find users in this cohort's date range
            cohort_users = []
            for user in self.users:
                created_date = self._parse_date(user.get('created_date'))
                if created_date and cohort_start <= created_date <= cohort_end:
                    cohort_users.append(user)
            
            # Skip if no users found
            if not cohort_users:
                continue
            
            # Get user emails for filtering ideas and steps
            user_emails = [user.get('email') for user in cohort_users if user.get('email')]
            
            # Count ideas and steps for this cohort
            cohort_ideas = [idea for idea in self.ideas if idea.get('owner') in user_emails]
            
            # Count steps in two ways: by idea relationship and by owner (for steps without idea ID)
            cohort_steps = []
            for step in self.steps:
                # Include step if the idea belongs to the cohort
                idea_id = step.get('idea_id')
                if idea_id:
                    idea_owners = [idea.get('owner') for idea in cohort_ideas if idea.get('id') == idea_id]
                    if any(owner in user_emails for owner in idea_owners):
                        cohort_steps.append(step)
                        continue
                
                # Include step if the owner is directly in the cohort
                owner = step.get('owner')
                if owner in user_emails:
                    cohort_steps.append(step)
            
            # Calculate metrics for this cohort
            active_users = len(set(idea.get('owner') for idea in cohort_ideas if idea.get('owner')))
            active_rate = active_users / len(cohort_users) if cohort_users else 0
            
            steps_per_idea = len(cohort_steps) / len(cohort_ideas) if cohort_ideas else 0
            ideas_per_active_user = len(cohort_ideas) / active_users if active_users else 0
            
            # Store cohort statistics
            cohort_stats[cohort_name] = {
                'tool_version': cohort_info['tool_version'],
                'sections': cohort_info['sections'],
                'total_users': len(cohort_users),
                'active_users': active_users,
                'active_rate': active_rate,
                'total_ideas': len(cohort_ideas),
                'total_steps': len(cohort_steps),
                'ideas_per_active_user': ideas_per_active_user,
                'steps_per_idea': steps_per_idea,
                'user_distribution': self._analyze_user_distribution(cohort_users)
            }
        
        return cohort_stats
    
    def _analyze_usage_cohorts(self) -> Dict[str, Any]:
        """Categorize users based on their tool usage levels."""
        logger.info("Analyzing usage-based cohorts")
        
        # First, calculate usage metrics for each user
        user_metrics = {}
        
        for user in self.users:
            email = user.get('email')
            if not email:
                continue
            
            # Count ideas by this user
            user_ideas = [idea for idea in self.ideas if idea.get('owner') == email]
            ideas_count = len(user_ideas)
            
            # Count steps by this user (directly and via their ideas)
            user_steps = self.steps_by_owner.get(email, [])
            steps_count = len(user_steps)
            
            # Also count steps for ideas they own
            for idea in user_ideas:
                idea_id = idea.get('id')
                if idea_id in self.steps_by_idea:
                    steps_count += len(self.steps_by_idea[idea_id])
            
            # Determine usage levels using different methods
            usage_level = self._determine_usage_level(ideas_count, steps_count)
            usage_by_ideas = self._determine_usage_by_ideas(ideas_count)
            usage_by_steps = self._determine_usage_by_steps(steps_count)
            usage_by_completion = self._determine_usage_by_completion(user_ideas)
            usage_by_interactions = self._determine_usage_by_interactions(steps_count, ideas_count)
            
            # Store metrics for this user
            user_metrics[email] = {
                'ideas_count': ideas_count,
                'steps_count': steps_count,
                'user_id': user.get('id'),
                'user_type': user.get('type'),
                'usage_level': usage_level,                   # Combined metric (default)
                'usage_by_ideas': usage_by_ideas,             # Based only on idea count
                'usage_by_steps': usage_by_steps,             # Based only on step count
                'usage_by_completion': usage_by_completion,   # Based on framework completion
                'usage_by_interactions': usage_by_interactions # Based on total interactions
            }
        
        # Group users by different usage categorization methods
        categorization_methods = [
            'usage_level',          # Combined metric (default)
            'usage_by_ideas',       # Based only on idea count
            'usage_by_steps',       # Based only on step count
            'usage_by_completion',  # Based on framework completion
            'usage_by_interactions' # Based on total interactions
        ]
        
        # Create cohort dictionaries for each method
        usage_cohorts = {}
        for method in categorization_methods:
            usage_cohorts[method] = {
                'high': [],
                'medium': [],
                'low': [],
                'none': []
            }
        
        # Group users by each categorization method
        for email, metrics in user_metrics.items():
            for method in categorization_methods:
                usage_level = metrics[method]
                usage_cohorts[method][usage_level].append(email)
        
        # Calculate statistics for each usage cohort by each method
        usage_stats = {}
        for method in categorization_methods:
            usage_stats[method] = {}
            
            for level, users in usage_cohorts[method].items():
                if not users:
                    continue
                
                # Count ideas and steps for this cohort
                cohort_ideas = [idea for idea in self.ideas if idea.get('owner') in users]
                
                cohort_steps = []
                for step in self.steps:
                    idea_id = step.get('idea_id')
                    if idea_id:
                        idea_owners = [idea.get('owner') for idea in cohort_ideas if idea.get('id') == idea_id]
                        if any(owner in users for owner in idea_owners):
                            cohort_steps.append(step)
                    
                    owner = step.get('owner')
                    if owner in users:
                        cohort_steps.append(step)
                
                # Calculate metrics for this usage cohort
                usage_stats[method][level] = {
                    'user_count': len(users),
                    'ideas_count': len(cohort_ideas),
                    'steps_count': len(cohort_steps),
                    'ideas_per_user': len(cohort_ideas) / len(users) if users else 0,
                    'steps_per_idea': len(cohort_steps) / len(cohort_ideas) if cohort_ideas else 0,
                    'avg_steps_per_user': len(cohort_steps) / len(users) if users else 0
                }
        
        # Cross-analyze usage levels by time cohort using all categorization methods
        usage_by_time_cohort = {}
        
        for cohort_name, cohort_info in self.time_cohorts.items():
            cohort_start = self._parse_date(cohort_info["start_date"])
            cohort_end = self._parse_date(cohort_info["end_date"])
            
            # Track usage by each method
            categorization_results = {}
            for method in categorization_methods:
                categorization_results[method] = {
                    'counts': {
                        'high': 0,
                        'medium': 0,
                        'low': 0,
                        'none': 0
                    },
                    'percentages': {}
                }
            
            # Count users in this cohort by their usage levels across all methods
            for user in self.users:
                email = user.get('email')
                if not email or email not in user_metrics:
                    continue
                
                created_date = self._parse_date(user.get('created_date'))
                if created_date and cohort_start <= created_date <= cohort_end:
                    # Count for each categorization method
                    for method in categorization_methods:
                        usage_level = user_metrics[email][method]
                        categorization_results[method]['counts'][usage_level] += 1
            
            # Calculate percentages for each method
            total_users = 0
            # Use the default method to determine total users
            for level, count in categorization_results['usage_level']['counts'].items():
                total_users += count
            
            # Calculate percentages for all methods
            for method in categorization_methods:
                if total_users > 0:
                    for level, count in categorization_results[method]['counts'].items():
                        categorization_results[method]['percentages'][level] = count / total_users
            
            # Store results for this cohort
            usage_by_time_cohort[cohort_name] = {
                'total_users': total_users,
                'tool_version': cohort_info.get('tool_version', 'unknown'),
                'categories': categorization_results
            }
        
        # Add summary of categorization methods comparison
        method_comparison = self._compare_categorization_methods(user_metrics, categorization_methods)
        
        return {
            'user_metrics': user_metrics,
            'usage_stats': usage_stats,
            'usage_by_time_cohort': usage_by_time_cohort,
            'categorization_methods': categorization_methods,
            'method_comparison': method_comparison
        }
    
    def _analyze_enrollment_cohorts(self) -> Dict[str, Any]:
        """Analyze users based on their course enrollments."""
        logger.info("Analyzing enrollment-based cohorts")
        
        # Group users by enrollment
        enrollments = defaultdict(list)
        
        for user in self.users:
            user_enrollments = user.get('enrollments', [])
            if not user_enrollments:
                enrollments['no_enrollment'].append(user)
                continue
            
            for enrollment in user_enrollments:
                if enrollment:
                    enrollments[enrollment].append(user)
        
        # Focus on course enrollments from the thesis plan
        target_courses = [
            "15.390",  # The main course mentioned in thesis
            # "15.S08",  # An alternate course code possibility
        ]
        
        # Find all course-like enrollments
        course_enrollments = {}
        other_enrollments = {}
        
        for enrollment, users in enrollments.items():
            enrollment_str = str(enrollment)
            
            # Check if this might be a course
            is_target = any(course in enrollment_str for course in target_courses)
            is_course = any(c.isdigit() for c in enrollment_str) or '.' in enrollment_str
            
            if is_target or is_course:
                course_enrollments[enrollment_str] = users
            else:
                other_enrollments[enrollment_str] = users
        
        # Calculate metrics for each course enrollment
        course_metrics = {}
        
        for course, users in course_enrollments.items():
            # Skip small cohorts
            if len(users) < 3:
                continue
            
            # Get user emails
            user_emails = [user.get('email') for user in users if user.get('email')]
            
            # Count ideas and steps by these users
            course_ideas = [idea for idea in self.ideas if idea.get('owner') in user_emails]
            
            course_steps = []
            for step in self.steps:
                idea_id = step.get('idea_id')
                if idea_id:
                    idea_owners = [idea.get('owner') for idea in course_ideas if idea.get('id') == idea_id]
                    if any(owner in user_emails for owner in idea_owners):
                        course_steps.append(step)
                
                owner = step.get('owner')
                if owner in user_emails:
                    course_steps.append(step)
            
            # Calculate active users
            active_users = len(set(idea.get('owner') for idea in course_ideas if idea.get('owner')))
            
            # Store course metrics
            course_metrics[course] = {
                'user_count': len(users),
                'active_users': active_users,
                'active_rate': active_users / len(users) if users else 0,
                'ideas_count': len(course_ideas),
                'steps_count': len(course_steps),
                'ideas_per_active_user': len(course_ideas) / active_users if active_users else 0,
                'steps_per_idea': len(course_steps) / len(course_ideas) if course_ideas else 0
            }
        
        return {
            'course_enrollments': course_metrics,
            'enrollment_counts': {k: len(v) for k, v in enrollments.items()},
            'top_enrollments': sorted(
                [(enroll, len(users)) for enroll, users in enrollments.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 enrollments by count
        }
    
    def _analyze_tool_adoption(self) -> Dict[str, Any]:
        """Analyze tool adoption patterns across cohorts."""
        logger.info("Analyzing tool adoption patterns")
        
        # Track tool adoption by time cohort
        adoption_by_cohort = {}
        
        for cohort_name, cohort_info in self.time_cohorts.items():
            cohort_start = self._parse_date(cohort_info["start_date"])
            cohort_end = self._parse_date(cohort_info["end_date"])
            
            # Find users in this cohort's date range
            cohort_users = []
            for user in self.users:
                created_date = self._parse_date(user.get('created_date'))
                if created_date and cohort_start <= created_date <= cohort_end:
                    cohort_users.append(user)
            
            # Skip if no users found
            if not cohort_users:
                continue
            
            # Get user emails for filtering ideas and steps
            user_emails = [user.get('email') for user in cohort_users if user.get('email')]
            
            # Track first-time usage
            first_engagement = {}
            for email in user_emails:
                # Find the first idea or step by this user
                user_ideas = [idea for idea in self.ideas if idea.get('owner') == email]
                user_steps = self.steps_by_owner.get(email, [])
                
                idea_dates = [self._parse_date(idea.get('created_date')) for idea in user_ideas 
                             if idea.get('created_date')]
                step_dates = [self._parse_date(step.get('created_at')) for step in user_steps 
                             if step.get('created_at')]
                
                all_dates = [d for d in idea_dates + step_dates if d]
                
                if all_dates:
                    first_date = min(all_dates)
                    first_engagement[email] = first_date
            
            # Calculate adoption rate over time
            adoption_timeline = self._calculate_adoption_timeline(
                first_engagement, cohort_start, cohort_end
            )
            
            # Calculate framework distribution
            framework_counts = defaultdict(int)
            for email in user_emails:
                user_ideas = [idea for idea in self.ideas if idea.get('owner') == email]
                for idea in user_ideas:
                    for framework in idea.get('frameworks', []):
                        framework_counts[framework] += 1
            
            # Store cohort adoption metrics
            adoption_by_cohort[cohort_name] = {
                'total_users': len(cohort_users),
                'engaged_users': len(first_engagement),
                'adoption_rate': len(first_engagement) / len(cohort_users) if cohort_users else 0,
                'adoption_timeline': adoption_timeline,
                'framework_distribution': dict(framework_counts)
            }
        
        return {
            'adoption_by_cohort': adoption_by_cohort
        }
    
    def _analyze_learning_metrics(self) -> Dict[str, Any]:
        """
        Analyze learning metrics across cohorts.
        
        Note: This is a placeholder for integrating with actual learning outcome data.
        In a real implementation, this would connect with course grades, assessments,
        or other learning outcome measures.
        """
        logger.info("Analyzing learning metrics (placeholder)")
        
        # This is a placeholder for actual learning metrics
        # In a real implementation, we would integrate with:
        # - Course grades
        # - Learning assessments
        # - Project outcomes
        # - Student surveys
        
        # For now, we'll use proxy metrics like:
        # - Framework completion rates
        # - Content volume and quality (e.g., word count in steps)
        # - Iteration frequency
        
        # Calculate framework completion by cohort
        framework_completion = {}
        
        for cohort_name, cohort_info in self.time_cohorts.items():
            cohort_start = self._parse_date(cohort_info["start_date"])
            cohort_end = self._parse_date(cohort_info["end_date"])
            
            # Find users in this cohort's date range
            cohort_users = []
            for user in self.users:
                created_date = self._parse_date(user.get('created_date'))
                if created_date and cohort_start <= created_date <= cohort_end:
                    cohort_users.append(user)
            
            # Skip if no users found
            if not cohort_users:
                continue
            
            # Get user emails for filtering ideas
            user_emails = [user.get('email') for user in cohort_users if user.get('email')]
            
            # Track framework completion
            de_completion = []
            st_completion = []
            
            for email in user_emails:
                user_ideas = [idea for idea in self.ideas if idea.get('owner') == email]
                
                for idea in user_ideas:
                    # Check Disciplined Entrepreneurship progress
                    if 'DE_progress' in idea:
                        de_completion.append(idea.get('DE_progress', 0))
                    
                    # Check Startup Tactics progress
                    if 'ST_progress' in idea:
                        st_completion.append(idea.get('ST_progress', 0))
            
            # Calculate average completion rates
            avg_de = sum(de_completion) / len(de_completion) if de_completion else 0
            avg_st = sum(st_completion) / len(st_completion) if st_completion else 0
            
            # Store metrics
            framework_completion[cohort_name] = {
                'avg_de_completion': avg_de,
                'avg_st_completion': avg_st,
                'de_ideas_count': len(de_completion),
                'st_ideas_count': len(st_completion)
            }
        
        # Calculate content metrics (average word count in steps)
        content_metrics = {}
        
        for cohort_name, cohort_info in self.time_cohorts.items():
            cohort_start = self._parse_date(cohort_info["start_date"])
            cohort_end = self._parse_date(cohort_info["end_date"])
            
            # Find users in this cohort's date range
            cohort_users = []
            for user in self.users:
                created_date = self._parse_date(user.get('created_date'))
                if created_date and cohort_start <= created_date <= cohort_end:
                    cohort_users.append(user)
            
            # Skip if no users found
            if not cohort_users:
                continue
            
            # Get user emails for filtering steps
            user_emails = [user.get('email') for user in cohort_users if user.get('email')]
            
            # Track word counts in steps
            word_counts = []
            for email in user_emails:
                user_steps = self.steps_by_owner.get(email, [])
                
                for step in user_steps:
                    content_word_count = step.get('content_word_count', 0)
                    if content_word_count:
                        word_counts.append(content_word_count)
            
            # Calculate average word count
            avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
            
            # Store metrics
            content_metrics[cohort_name] = {
                'avg_word_count': avg_word_count,
                'total_word_count': sum(word_counts),
                'steps_with_content': len(word_counts)
            }
        
        return {
            'framework_completion': framework_completion,
            'content_metrics': content_metrics
        }
    
    def _analyze_cohort_comparison(self) -> Dict[str, Any]:
        """Compare key metrics across all cohorts for direct comparison."""
        logger.info("Analyzing cohort comparisons")
        
        # Define key metrics to compare
        key_metrics = {
            'active_rate': {},
            'ideas_per_active_user': {},
            'steps_per_idea': {},
            'avg_de_completion': {},
            'avg_st_completion': {},
            'avg_word_count': {}
        }
        
        # Extract metrics from time cohorts
        time_cohort_data = self._analyze_time_cohorts()
        for cohort_name, cohort_data in time_cohort_data.items():
            key_metrics['active_rate'][cohort_name] = cohort_data.get('active_rate', 0)
            key_metrics['ideas_per_active_user'][cohort_name] = cohort_data.get('ideas_per_active_user', 0)
            key_metrics['steps_per_idea'][cohort_name] = cohort_data.get('steps_per_idea', 0)
        
        # Extract metrics from learning metrics
        learning_data = self._analyze_learning_metrics()
        
        if 'framework_completion' in learning_data:
            for cohort_name, framework_data in learning_data['framework_completion'].items():
                key_metrics['avg_de_completion'][cohort_name] = framework_data.get('avg_de_completion', 0)
                key_metrics['avg_st_completion'][cohort_name] = framework_data.get('avg_st_completion', 0)
        
        if 'content_metrics' in learning_data:
            for cohort_name, content_data in learning_data['content_metrics'].items():
                key_metrics['avg_word_count'][cohort_name] = content_data.get('avg_word_count', 0)
        
        # Calculate statistical significance
        # Note: This is a placeholder for actual significance tests
        # In a real implementation, we would use t-tests or other appropriate tests
        comparison_pairs = []
        cohort_names = list(time_cohort_data.keys())
        
        for i in range(len(cohort_names)):
            for j in range(i+1, len(cohort_names)):
                cohort1 = cohort_names[i]
                cohort2 = cohort_names[j]
                
                comparison_pairs.append({
                    'cohort1': cohort1,
                    'cohort2': cohort2,
                    'tool_versions': {
                        cohort1: self.time_cohorts[cohort1]['tool_version'],
                        cohort2: self.time_cohorts[cohort2]['tool_version']
                    },
                    'metric_differences': {
                        metric: key_metrics[metric].get(cohort2, 0) - key_metrics[metric].get(cohort1, 0)
                        for metric in key_metrics
                    }
                })
        
        return {
            'key_metrics': key_metrics,
            'comparison_pairs': comparison_pairs
        }
    
    def _group_ideas_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group ideas by owner for efficient access."""
        ideas_by_owner = defaultdict(list)
        
        for idea in self.ideas:
            owner = idea.get('owner')
            if owner:
                ideas_by_owner[owner].append(idea)
        
        return ideas_by_owner
    
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
    
    def _analyze_user_distribution(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user distribution by type and affiliation.
        
        Args:
            users: List of users in a cohort
            
        Returns:
            Dictionary of user distribution statistics
        """
        # Count users by type
        user_types = defaultdict(int)
        institutions = defaultdict(int)
        
        for user in users:
            # Count by user type
            user_type = user.get('type', 'unknown')
            user_types[user_type] += 1
            
            # Count by institution
            institution = user.get('institution', {})
            if institution:
                institution_name = institution.get('name', 'unknown')
                institutions[institution_name] += 1
        
        return {
            'by_type': dict(user_types),
            'by_institution': dict(institutions)
        }
    
    def _determine_usage_level(self, ideas_count: int, steps_count: int) -> str:
        """
        Determine a user's usage level based on ideas and steps counts.
        This is the default method that considers both ideas and steps.
        
        Args:
            ideas_count: Number of ideas created by the user
            steps_count: Number of steps created by the user
            
        Returns:
            Usage level: 'high', 'medium', 'low', or 'none'
        """
        if ideas_count >= self.usage_thresholds['ideas']['high'] or steps_count >= self.usage_thresholds['steps']['high']:
            return 'high'
        elif ideas_count >= self.usage_thresholds['ideas']['medium'] or steps_count >= self.usage_thresholds['steps']['medium']:
            return 'medium'
        elif ideas_count >= self.usage_thresholds['ideas']['low'] or steps_count >= self.usage_thresholds['steps']['low']:
            return 'low'
        else:
            return 'none'
    
    def _determine_usage_by_ideas(self, ideas_count: int) -> str:
        """
        Determine a user's usage level based solely on number of ideas.
        
        Args:
            ideas_count: Number of ideas created by the user
            
        Returns:
            Usage level: 'high', 'medium', 'low', or 'none'
        """
        if ideas_count >= self.usage_thresholds['ideas']['high']:
            return 'high'
        elif ideas_count >= self.usage_thresholds['ideas']['medium']:
            return 'medium'
        elif ideas_count >= self.usage_thresholds['ideas']['low']:
            return 'low'
        else:
            return 'none'
    
    def _determine_usage_by_steps(self, steps_count: int) -> str:
        """
        Determine a user's usage level based solely on number of steps.
        
        Args:
            steps_count: Number of steps created by the user
            
        Returns:
            Usage level: 'high', 'medium', 'low', or 'none'
        """
        if steps_count >= self.usage_thresholds['steps']['high']:
            return 'high'
        elif steps_count >= self.usage_thresholds['steps']['medium']:
            return 'medium'
        elif steps_count >= self.usage_thresholds['steps']['low']:
            return 'low'
        else:
            return 'none'
    
    def _determine_usage_by_completion(self, user_ideas: List[Dict[str, Any]]) -> str:
        """
        Determine a user's usage level based on framework completion rate.
        Uses the maximum completion rate across all ideas owned by the user.
        
        Args:
            user_ideas: List of ideas created by the user
            
        Returns:
            Usage level: 'high', 'medium', 'low', or 'none'
        """
        if not user_ideas:
            return 'none'
        
        # Calculate max completion rate from all frameworks
        max_completion = 0
        for idea in user_ideas:
            # Check DE progress
            de_progress = idea.get('DE_progress', 0)
            max_completion = max(max_completion, de_progress)
            
            # Check ST progress
            st_progress = idea.get('DE_progress', 0)
            max_completion = max(max_completion, st_progress)
            
            # Check total progress as fallback
            total_progress = idea.get('total_progress', 0)
            max_completion = max(max_completion, total_progress)
        
        # Normalize to 0-1 scale if needed
        if max_completion > 1:
            max_completion = max_completion / 100
        
        # Determine level based on completion thresholds
        if max_completion >= self.usage_thresholds['completion']['high']:
            return 'high'
        elif max_completion >= self.usage_thresholds['completion']['medium']:
            return 'medium'
        elif max_completion >= self.usage_thresholds['completion']['low']:
            return 'low'
        else:
            return 'none'
    
    def _determine_usage_by_interactions(self, steps_count: int, ideas_count: int) -> str:
        """
        Determine a user's usage level based on total interactions.
        Interactions are defined as the sum of ideas and steps.
        
        Args:
            steps_count: Number of steps created by the user
            ideas_count: Number of ideas created by the user
            
        Returns:
            Usage level: 'high', 'medium', 'low', or 'none'
        """
        # Calculate total interactions (ideas + steps)
        interactions = ideas_count + steps_count
        
        if interactions >= self.usage_thresholds['interactions']['high']:
            return 'high'
        elif interactions >= self.usage_thresholds['interactions']['medium']:
            return 'medium'
        elif interactions >= self.usage_thresholds['interactions']['low']:
            return 'low'
        else:
            return 'none'
    
    def _calculate_adoption_timeline(self, first_engagement: Dict[str, datetime], 
                                   cohort_start: datetime, cohort_end: datetime) -> Dict[str, int]:
        """
        Calculate adoption timeline based on first engagement dates.
        
        Args:
            first_engagement: Dictionary mapping user emails to their first engagement date
            cohort_start: Start date of the cohort
            cohort_end: End date of the cohort
            
        Returns:
            Dictionary of cumulative adoption by month
        """
        if not first_engagement or not cohort_start or not cohort_end:
            return {}
        
        # Initialize timeline with zeroes for each month in the cohort period
        timeline = {}
        current_date = datetime(cohort_start.year, cohort_start.month, 1)
        
        while current_date <= cohort_end:
            month_key = current_date.strftime('%Y-%m')
            timeline[month_key] = 0
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Count adoptions by month
        for email, date in first_engagement.items():
            month_key = date.strftime('%Y-%m')
            if month_key in timeline:
                timeline[month_key] += 1
        
        # Convert to cumulative
        cumulative = {}
        running_total = 0
        
        for month in sorted(timeline.keys()):
            running_total += timeline[month]
            cumulative[month] = running_total
        
        return cumulative
    
    def _compare_categorization_methods(self, user_metrics: Dict[str, Dict[str, Any]], 
                                 categorization_methods: List[str]) -> Dict[str, Any]:
        """
        Compare how different categorization methods align with each other.
        
        Args:
            user_metrics: Dictionary of user metrics
            categorization_methods: List of categorization method names
            
        Returns:
            Comparison statistics
        """
        # Initialize confusion matrices between methods
        confusion_matrices = {}
        agreement_rates = {}
        
        # Compare each pair of methods
        for i, method1 in enumerate(categorization_methods):
            for j, method2 in enumerate(categorization_methods):
                if i >= j:  # Skip self-comparisons and repetitions
                    continue
                
                # Create key for this method pair
                key = f"{method1}_vs_{method2}"
                
                # Initialize confusion matrix
                confusion_matrices[key] = {
                    'high': {'high': 0, 'medium': 0, 'low': 0, 'none': 0},
                    'medium': {'high': 0, 'medium': 0, 'low': 0, 'none': 0},
                    'low': {'high': 0, 'medium': 0, 'low': 0, 'none': 0},
                    'none': {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
                }
                
                # Count agreements and disagreements
                agreement_count = 0
                total_count = 0
                
                for email, metrics in user_metrics.items():
                    level1 = metrics[method1]
                    level2 = metrics[method2]
                    
                    # Update confusion matrix
                    confusion_matrices[key][level1][level2] += 1
                    
                    # Count agreement
                    if level1 == level2:
                        agreement_count += 1
                    
                    total_count += 1
                
                # Calculate agreement rate
                agreement_rate = agreement_count / total_count if total_count > 0 else 0
                agreement_rates[key] = agreement_rate
        
        # Calculate overall distribution for each method
        method_distributions = {}
        
        for method in categorization_methods:
            distribution = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
            
            for _, metrics in user_metrics.items():
                level = metrics[method]
                distribution[level] += 1
            
            # Convert to percentages
            total = sum(distribution.values())
            if total > 0:
                for level in distribution:
                    distribution[level] = distribution[level] / total
            
            method_distributions[method] = distribution
        
        return {
            'confusion_matrices': confusion_matrices,
            'agreement_rates': agreement_rates,
            'method_distributions': method_distributions
        }
    
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
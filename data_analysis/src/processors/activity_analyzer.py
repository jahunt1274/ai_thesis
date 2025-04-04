"""
Activity analyzer for data analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.processors.base_analyzer import BaseAnalyzer
from src.utils import DataGroupingUtils


class ActivityAnalyzer(BaseAnalyzer):
    """Analyzes usage patterns and user engagement."""

    def __init__(
        self,
        users: List[Dict[str, Any]],
        ideas: List[Dict[str, Any]],
        steps: List[Dict[str, Any]],
        end_date: Optional[datetime] = None,
    ):
        """
        Initialize the activity analyzer.

        Args:
            users: List of processed user records
            ideas: List of processed idea records
            steps: List of processed step records
            end_date: Optional reference date for time-based calculations (default: now)
        """
        super().__init__("activity_analyzer")
        self.users = users
        self.ideas = ideas
        self.steps = steps

        # Set reference date for time-based calculations
        self.end_date = end_date or datetime(
            2025, 2, 4, tzinfo=timezone.utc
        )  # Default from original code

        # Create lookup maps for efficient access
        self.ideas_by_id = {idea.get("id"): idea for idea in ideas if idea.get("id")}
        self.ideas_by_owner = self._group_ideas_by_owner()
        self.steps_by_idea = self._group_steps_by_idea()
        self.steps_by_owner = self._group_steps_by_owner()

    def validate_data(self) -> None:
        """Validate input data."""
        if not self.ideas:
            self.logger.warning("No idea data provided")
        if not self.steps:
            self.logger.warning("No step data provided")

    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive activity analysis.

        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Performing activity analysis")

        results = {
            "idea_generation": self._analyze_idea_generation(),
            "engagement_levels": self._analyze_engagement_levels(),
            "process_completion": self._analyze_process_completion(),
            "dropout_points": self._analyze_dropout_points(),
            "framework_usage": self._analyze_framework_usage(),
            "timeline": self._analyze_usage_timeline(),
        }

        return results

    def _analyze_idea_generation(self) -> Dict[str, Any]:
        """Analyze idea generation patterns."""
        idea_counts = {
            "total_ideas": len(self.ideas),
            "unique_owners": len(self.ideas_by_owner),
            "avg_ideas_per_owner": 0,
            "max_ideas_per_owner": 0,
            "ideas_by_ranking": defaultdict(int),
        }

        # Count ideas by ranking
        for idea in self.ideas:
            ranking = idea.get("ranking", 0)
            idea_counts["ideas_by_ranking"][ranking] += 1

        if idea_counts["unique_owners"] > 0:
            idea_counts["avg_ideas_per_owner"] = (
                idea_counts["total_ideas"] / idea_counts["unique_owners"]
            )

        # Find maximum ideas per owner
        for owner, ideas in self.ideas_by_owner.items():
            idea_counts["max_ideas_per_owner"] = max(
                idea_counts["max_ideas_per_owner"], len(ideas)
            )

        # Convert defaultdict to regular dict
        idea_counts["ideas_by_ranking"] = dict(idea_counts["ideas_by_ranking"])

        return idea_counts

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
            framework = step.get("framework")
            if framework:
                framework_counts[framework] += 1

        return dict(framework_counts)

    def _group_ideas_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group ideas by owner for efficient access."""
        return DataGroupingUtils.group_by_key(self.ideas, "owner")

    def _group_steps_by_idea(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group steps by idea ID for efficient access."""
        return DataGroupingUtils.group_by_key(self.steps, "idea_id")

    def _group_steps_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group steps by owner for efficient access."""
        return DataGroupingUtils.group_by_key(self.steps, "owner")

    def _analyze_engagement_levels(self) -> Dict[str, Any]:
        """Analyze user engagement levels."""
        # Define engagement level thresholds
        engagement_levels = {
            "high": 0,  # >5 ideas
            "medium": 0,  # 2-5 ideas
            "low": 0,  # 1 idea
            "none": 0,  # 0 ideas
        }

        # Count users by engagement level
        for owner, ideas in self.ideas_by_owner.items():
            if len(ideas) > 5:
                engagement_levels["high"] += 1
            elif len(ideas) >= 2:
                engagement_levels["medium"] += 1
            elif len(ideas) == 1:
                engagement_levels["low"] += 1

        # Count users with no ideas
        engagement_levels["none"] = len(self.users) - sum(engagement_levels.values())

        # Calculate engagement by framework usage
        framework_engagement = self._analyze_framework_engagement()

        # Calculate engagement over time
        temporal_engagement = self._analyze_temporal_engagement()

        # Calculate idea characteristics
        idea_characterization = self._analyze_idea_characterization()

        return {
            "engagement_levels": engagement_levels,
            "framework_engagement": framework_engagement,
            "temporal_engagement": temporal_engagement,
            "idea_characterization": idea_characterization,
        }

    def _analyze_process_completion(self) -> Dict[str, Any]:
        """Analyze how users progress through the idea development process."""
        self.logger.info("Analyzing process completion")

        completion_stats = {
            "total_ideas": len(self.ideas),
            "ideas_with_steps": 0,
            "avg_steps_per_idea": 0,
            "max_steps_per_idea": 0,
            "step_distribution": defaultdict(int),
            "completion_by_framework": {
                "disciplined-entrepreneurship": {"avg_completion": 0, "total_ideas": 0},
                "startup-tactics": {"avg_completion": 0, "total_ideas": 0},
            },
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
            completion_stats["step_distribution"][step_count] += 1

            # Track framework-specific completion
            framework_counts = self._count_frameworks_for_idea(steps)

            for framework, count in framework_counts.items():
                if framework == "disciplined-entrepreneurship":
                    de_completion_total += count
                    de_ideas_count += 1
                elif framework == "startup-tactics":
                    st_completion_total += count
                    st_ideas_count += 1

        # Calculate averages
        completion_stats["ideas_with_steps"] = ideas_with_steps

        if ideas_with_steps > 0:
            completion_stats["avg_steps_per_idea"] = total_steps / ideas_with_steps

        completion_stats["max_steps_per_idea"] = max_steps

        # Calculate framework-specific averages
        if de_ideas_count > 0:
            completion_stats["completion_by_framework"]["disciplined-entrepreneurship"][
                "avg_completion"
            ] = (de_completion_total / de_ideas_count)
            completion_stats["completion_by_framework"]["disciplined-entrepreneurship"][
                "total_ideas"
            ] = de_ideas_count

        if st_ideas_count > 0:
            completion_stats["completion_by_framework"]["startup-tactics"][
                "avg_completion"
            ] = (st_completion_total / st_ideas_count)
            completion_stats["completion_by_framework"]["startup-tactics"][
                "total_ideas"
            ] = st_ideas_count

        # Convert defaultdict to regular dict
        completion_stats["step_distribution"] = dict(
            completion_stats["step_distribution"]
        )

        return completion_stats

    def _analyze_dropout_points(self) -> Dict[str, Any]:
        """Analyze where users stop in the process."""
        self.logger.info("Analyzing dropout points")

        # Track step progression to identify common dropout points
        step_progression = defaultdict(int)
        final_steps = defaultdict(int)

        # Group steps by idea
        for idea_id, steps in self.steps_by_idea.items():
            if not steps:
                continue

            # Sort steps by creation date
            sorted_steps = sorted(
                steps, key=lambda s: s.get("created_at", ""), reverse=True
            )

            # Track all steps in the progression
            for step in sorted_steps:
                step_name = step.get("step_name", "")
                step_progression[step_name] += 1

            # The last step is the most recent one
            last_step = sorted_steps[0]
            last_step_name = last_step.get("step_name", "")

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
            "step_progression": dict(step_progression),
            "final_steps": dict(final_steps),
            "step_completion_rates": step_completion_rates,
            "dropout_rates": dropout_rates,
        }

    def _analyze_framework_usage(self) -> Dict[str, Any]:
        """Analyze usage of different frameworks."""
        framework_counts = defaultdict(int)

        for idea in self.ideas:
            for framework in idea.get("frameworks", []):
                framework_counts[framework] += 1

        # Calculate framework completion rates
        de_completion = self._calculate_completion_rate("disciplined-entrepreneurship")
        st_completion = self._calculate_completion_rate("startup-tactics")

        return {
            "framework_counts": dict(framework_counts),
            "de_completion": de_completion,
            "st_completion": st_completion,
        }

    def _analyze_usage_timeline(self) -> Dict[str, Any]:
        """Analyze usage patterns over time."""
        # Group ideas by creation date
        ideas_by_date = defaultdict(list)

        for idea in self.ideas:
            created_date = idea.get("created_date")
            if created_date:
                # Extract date part only (YYYY-MM-DD)
                if "T" in created_date:
                    date_part = created_date.split("T")[0]
                else:
                    date_part = created_date

                ideas_by_date[date_part].append(idea)

        # Count ideas by date and calculate daily statistics
        daily_counts = {}
        for date, ideas in ideas_by_date.items():
            daily_counts[date] = {
                "count": len(ideas),
                "avg_progress": (
                    sum(idea.get("total_progress", 0) for idea in ideas) / len(ideas)
                    if ideas
                    else 0
                ),
            }

        # Group by month for monthly analysis
        monthly_counts = defaultdict(list)
        for date, stats in daily_counts.items():
            month = date[:7]  # Extract YYYY-MM
            monthly_counts[month].append(stats["count"])

        # Calculate monthly statistics
        monthly_stats = {}
        for month, counts in monthly_counts.items():
            monthly_stats[month] = {
                "total_ideas": sum(counts),
                "avg_ideas_per_day": sum(counts) / len(counts) if counts else 0,
            }

        return {"daily_counts": daily_counts, "monthly_stats": monthly_stats}

    def _analyze_idea_characterization(self) -> Dict[str, Any]:
        """Analyze characteristics of ideas."""
        # Analyze idea iteration patterns
        iteration_patterns = self._analyze_iteration_patterns()

        # Analyze idea progress
        progress_stats = self._analyze_progress_stats()

        return {
            "iteration_patterns": iteration_patterns,
            "progress_stats": progress_stats,
        }

    def _analyze_framework_engagement(self) -> Dict[str, Any]:
        """Analyze engagement by framework usage."""
        framework_users = {
            "disciplined-entrepreneurship": set(),
            "startup-tactics": set(),
            "both_frameworks": set(),
            "no_framework": set(),
        }

        # Track users by framework
        for idea in self.ideas:
            owner = idea.get("owner")
            frameworks = idea.get("frameworks", [])

            if "disciplined-entrepreneurship" in frameworks:
                framework_users["disciplined-entrepreneurship"].add(owner)

            if "startup-tactics" in frameworks:
                framework_users["startup-tactics"].add(owner)

        # Identify users using both frameworks
        framework_users["both_frameworks"] = (
            framework_users["disciplined-entrepreneurship"]
            & framework_users["startup-tactics"]
        )

        # Identify users using no framework
        all_idea_owners = set(self.ideas_by_owner.keys())
        framework_users["no_framework"] = all_idea_owners - (
            framework_users["disciplined-entrepreneurship"]
            | framework_users["startup-tactics"]
        )

        # Convert sets to counts
        return {framework: len(users) for framework, users in framework_users.items()}

    def _analyze_temporal_engagement(self) -> Dict[str, Any]:
        """Analyze engagement patterns over time."""
        # Track active users by month
        monthly_active_users = defaultdict(set)

        for idea in self.ideas:
            created_date = idea.get("created_date")
            owner = idea.get("owner")

            if created_date and owner:
                # Extract month (YYYY-MM)
                if "T" in created_date:
                    month = created_date.split("T")[0][:7]
                else:
                    month = created_date[:7]

                monthly_active_users[month].add(owner)

        # Convert sets to counts
        monthly_users = {
            month: len(users) for month, users in monthly_active_users.items()
        }

        return {"monthly_active_users": monthly_users}

    def _analyze_iteration_patterns(self) -> Dict[str, Any]:
        """Analyze idea iteration patterns."""
        # Count users by number of iterations (ranking)
        users_by_iterations = defaultdict(int)

        for owner, ideas in self.ideas_by_owner.items():
            # Count iterations by tracking rankings
            rankings = set(idea.get("ranking", 0) for idea in ideas)
            max_iteration = max(rankings) if rankings else 0

            users_by_iterations[max_iteration] += 1

        # Count similar ideas (potential iterations)
        return {"users_by_max_iteration": dict(users_by_iterations)}

    def _analyze_progress_stats(self) -> Dict[str, Any]:
        """Analyze idea progress statistics."""
        progress_data = {
            "total_ideas": len(self.ideas),
            "avg_progress": 0,
            "progress_distribution": defaultdict(int),
            "framework_progress": {
                "disciplined-entrepreneurship": {"avg_progress": 0, "total_ideas": 0},
                "startup-tactics": {"avg_progress": 0, "total_ideas": 0},
            },
        }

        # Track progress metrics
        total_progress = 0
        de_total = 0
        de_count = 0
        st_total = 0
        st_count = 0

        for idea in self.ideas:
            progress = idea.get("total_progress", 0)
            total_progress += progress

            # Track by 10% increments
            progress_bucket = int(progress / 10) * 10
            progress_data["progress_distribution"][progress_bucket] += 1

            # Track by framework
            if "disciplined-entrepreneurship" in idea.get("frameworks", []):
                de_total += idea.get("de_progress", 0)
                de_count += 1

            if "startup-tactics" in idea.get("frameworks", []):
                st_total += idea.get("st_progress", 0)
                st_count += 1

        # Calculate averages
        if len(self.ideas) > 0:
            progress_data["avg_progress"] = total_progress / len(self.ideas)

        if de_count > 0:
            progress_data["framework_progress"]["disciplined-entrepreneurship"][
                "avg_progress"
            ] = (de_total / de_count)
            progress_data["framework_progress"]["disciplined-entrepreneurship"][
                "total_ideas"
            ] = de_count

        if st_count > 0:
            progress_data["framework_progress"]["startup-tactics"]["avg_progress"] = (
                st_total / st_count
            )
            progress_data["framework_progress"]["startup-tactics"][
                "total_ideas"
            ] = st_count

        # Convert defaultdict to regular dict
        progress_data["progress_distribution"] = dict(
            progress_data["progress_distribution"]
        )

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
            "total_ideas": 0,
            "completed_ideas": 0,
            "completion_rate": 0,
            "avg_progress": 0,
        }

        # Track progress for this framework
        total_progress = 0
        framework_ideas = []

        for idea in self.ideas:
            if framework in idea.get("frameworks", []):
                framework_ideas.append(idea)

                # Get framework-specific progress
                if framework == "disciplined-entrepreneurship":
                    progress = idea.get("de_progress", 0)
                elif framework == "startup-tactics":
                    progress = idea.get("st_progress", 0)
                else:
                    progress = 0

                total_progress += progress

                # Count as completed if progress is at least 80%
                if progress >= 80:
                    completion_stats["completed_ideas"] += 1

        # Update statistics
        completion_stats["total_ideas"] = len(framework_ideas)

        if completion_stats["total_ideas"] > 0:
            completion_stats["completion_rate"] = (
                completion_stats["completed_ideas"] / completion_stats["total_ideas"]
            )
            completion_stats["avg_progress"] = (
                total_progress / completion_stats["total_ideas"]
            )

        return completion_stats

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

        idea_generation = self._analyze_idea_generation()
        engagement_levels = self._analyze_engagement_levels()
        process_completion = self._analyze_process_completion()
        dropout_points = self._analyze_dropout_points()
        framework_usage = self._analyze_framework_usage()
        timeline = self._analyze_usage_timeline()
        view_action_correlation = self._analyze_view_action_correlation()
        process_flow = self._analyze_process_flow(view_action_correlation)

        results = {
            "idea_generation": idea_generation,
            "engagement_levels": engagement_levels,
            "process_completion": process_completion,
            "dropout_points": dropout_points,
            "framework_usage": framework_usage,
            "timeline": timeline,
            "view_action_correlation": view_action_correlation,
            "process_flow": process_flow,
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

    def _analyze_view_action_correlation(self) -> Dict[str, Any]:
        """
        Analyze the temporal correlation between user views and actions (idea/step creation).

        Returns:
            Dictionary with view-to-action correlation analysis
        """
        self.logger.info("Analyzing view to action correlation")

        # TODO Set values as constant/enum
        # Initialize result structure
        correlation_data = {
            "view_to_idea_intervals": [],  # Time between view and idea creation
            "view_to_step_intervals": [],  # Time between view and step creation
            "user_patterns": {},  # Per-user patterns
            "interval_distribution": {},  # Distribution of time intervals
            "action_after_view_rate": 0,  # % of views followed by action within threshold
            "immediate_action_threshold": 300,  # 5 minutes in seconds
            # "immediate_action_threshold": 1800,  # 30 minutes in seconds
            # "session_threshold": 1800,  # 30 minutes in seconds
            "session_threshold": 3600,  # 1 hour in seconds
            # "session_threshold": 43200,  # 12 hours in seconds
            "sessions": [],  # List of session data
            "users_analyzed": 0,  # Count of users with view data
            "users_with_correlated_actions": 0,  # Users with views followed by actions
        }

        # Define time thresholds for analysis (in seconds)
        immediate_threshold = correlation_data["immediate_action_threshold"]
        session_threshold = correlation_data["session_threshold"]

        # Track users with view data
        users_with_views = 0
        users_with_correlated_actions = 0

        # Process each user
        for user in self.users:
            user_email = user.get("email")
            if not user_email:
                continue

            # Get views for this user
            views = user.get("views", [])
            if not views:
                continue

            # Increment users with views count
            users_with_views += 1

            # Convert view timestamps to seconds and sort
            view_timestamps = []
            for view in views:
                # Convert string eopch time to int
                view = int(view)
                # Handle different timestamp formats
                if isinstance(view, (int, float)):
                    # Check if timestamp needs to be divided by 1000 (milliseconds vs seconds)
                    if view > 1e11:  # Large values likely represent milliseconds
                        timestamp = view / 1000
                    else:
                        timestamp = view
                    view_timestamps.append(timestamp)

            # Skip if no valid timestamps
            if not view_timestamps:
                continue

            # Sort timestamps chronologically
            view_timestamps.sort()

            # Get ideas for this user
            user_ideas = self.ideas_by_owner.get(user_email, [])

            # Process each idea created by this user
            idea_timestamps = []
            for idea in user_ideas:
                created_date = idea.get("created_date")
                idea_id = idea.get("id")

                if not created_date or not idea_id:
                    continue

                # Convert ISO timestamp to seconds
                try:
                    if "T" in created_date:
                        # Extract timestamp from ISO format
                        from datetime import datetime

                        dt = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                        idea_timestamp = dt.timestamp()

                        # Add to list with idea info
                        idea_timestamps.append(
                            {
                                "timestamp": idea_timestamp,
                                "idea_id": idea_id,
                                "type": "idea",
                            }
                        )
                except (ValueError, TypeError):
                    continue

            # Get steps for this user
            user_steps = self.steps_by_owner.get(user_email, [])

            # Process each step created by this user
            step_timestamps = []
            for step in user_steps:
                created_at = step.get("created_at")
                step_id = step.get("id")
                idea_id = step.get("idea_id")

                if not created_at or not step_id:
                    continue

                # Convert ISO timestamp to seconds
                try:
                    if "T" in created_at:
                        # Extract timestamp from ISO format
                        from datetime import datetime

                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        step_timestamp = dt.timestamp()

                        # Add to list with step info
                        step_timestamps.append(
                            {
                                "timestamp": step_timestamp,
                                "step_id": step_id,
                                "idea_id": idea_id,
                                "type": "step",
                            }
                        )
                except (ValueError, TypeError):
                    continue

            # Combine all actions (ideas and steps) and sort by timestamp
            all_actions = idea_timestamps + step_timestamps
            all_actions.sort(key=lambda x: x["timestamp"])

            # Skip if no actions
            if not all_actions:
                continue

            # Find the closest view before each action
            has_correlated_actions = False

            for action in all_actions:
                action_time = action["timestamp"]
                action_type = action["type"]

                # Find the closest view before this action
                closest_view_time = None
                for view_time in view_timestamps:
                    if view_time <= action_time:
                        closest_view_time = view_time
                    else:
                        break

                # Skip if no view before action
                if closest_view_time is None:
                    continue

                # Calculate time interval (in seconds)
                time_interval = action_time - closest_view_time

                # Record the interval
                if action_type == "idea":
                    correlation_data["view_to_idea_intervals"].append(time_interval)
                else:  # step
                    correlation_data["view_to_step_intervals"].append(time_interval)

                # Record if this was an immediate action
                if time_interval <= immediate_threshold:
                    has_correlated_actions = True

            if has_correlated_actions:
                users_with_correlated_actions += 1

            # Session analysis for this user
            sessions = self._identify_sessions(
                view_timestamps, all_actions, session_threshold
            )

            # Store user-specific patterns
            correlation_data["user_patterns"][user_email] = {
                "view_count": len(view_timestamps),
                "idea_count": len(idea_timestamps),
                "step_count": len(step_timestamps),
                "session_count": len(sessions),
                "avg_actions_per_session": (
                    sum(s["action_count"] for s in sessions) / len(sessions)
                    if sessions
                    else 0
                ),
            }

            # Add sessions to global list
            correlation_data["sessions"].extend(sessions)

        # Calculate action after view rate
        correlation_data["users_analyzed"] = users_with_views
        correlation_data["users_with_correlated_actions"] = (
            users_with_correlated_actions
        )

        if users_with_views > 0:
            correlation_data["action_after_view_rate"] = (
                users_with_correlated_actions / users_with_views
            )

        # Create interval distribution
        intervals = (
            correlation_data["view_to_idea_intervals"]
            + correlation_data["view_to_step_intervals"]
        )

        if intervals:
            # Define buckets for distribution (in seconds)
            buckets = [
                (0, 60, "< 1 min"),
                (60, 300, "1-5 min"),
                (300, 900, "5-15 min"),
                (900, 1800, "15-30 min"),
                (1800, 3600, "30-60 min"),
                (3600, 7200, "1-2 hours"),
                (7200, 86400, "2-24 hours"),
                (86400, float("inf"), "> 24 hours"),
            ]

            # Count intervals in each bucket
            interval_distribution = defaultdict(int)

            for interval in intervals:
                for start, end, label in buckets:
                    if start <= interval < end:
                        interval_distribution[label] += 1
                        break

            correlation_data["interval_distribution"] = dict(interval_distribution)

            # Calculate basic statistics
            correlation_data["interval_stats"] = {
                "min": min(intervals),
                "max": max(intervals),
                "mean": sum(intervals) / len(intervals),
                "median": sorted(intervals)[len(intervals) // 2],
                "immediate_action_count": sum(
                    1 for i in intervals if i <= immediate_threshold
                ),
                "immediate_action_percentage": (
                    sum(1 for i in intervals if i <= immediate_threshold)
                    / len(intervals)
                    * 100
                ),
            }

        # Calculate session statistics
        if correlation_data["sessions"]:
            sessions = correlation_data["sessions"]
            correlation_data["session_stats"] = {
                "total_sessions": len(sessions),
                "avg_session_duration": sum(s["duration"] for s in sessions)
                / len(sessions),
                "avg_views_per_session": sum(s["view_count"] for s in sessions)
                / len(sessions),
                "avg_actions_per_session": sum(s["action_count"] for s in sessions)
                / len(sessions),
                "sessions_with_actions": sum(
                    1 for s in sessions if s["action_count"] > 0
                ),
                "action_session_percentage": (
                    sum(1 for s in sessions if s["action_count"] > 0)
                    / len(sessions)
                    * 100
                ),
            }

        self.logger.info(
            f"Completed view-action correlation analysis for {users_with_views} users"
        )

        return correlation_data

    def _identify_sessions(
        self,
        view_timestamps: List[float],
        actions: List[Dict[str, Any]],
        session_threshold: float,
    ) -> List[Dict[str, Any]]:
        """
        Identify user sessions based on view and action timestamps.

        Args:
            view_timestamps: Sorted list of view timestamps
            actions: List of actions with timestamps
            session_threshold: Time threshold for session boundary (in seconds)

        Returns:
            List of session data dictionaries
        """
        if not view_timestamps:
            return []

        # Combine views and actions into a single timeline
        timeline = []

        # Add views to timeline
        for timestamp in view_timestamps:
            timeline.append({"timestamp": timestamp, "type": "view"})

        # Add actions to timeline
        for action in actions:
            timeline.append(
                {
                    "timestamp": action["timestamp"],
                    "type": action["type"],
                    "id": action.get("idea_id") or action.get("step_id"),
                }
            )

        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        # Identify sessions
        sessions = []
        current_session = {
            "start_time": timeline[0]["timestamp"],
            "end_time": timeline[0]["timestamp"],
            "events": [timeline[0]],
            "view_count": 1 if timeline[0]["type"] == "view" else 0,
            "idea_count": 1 if timeline[0]["type"] == "idea" else 0,
            "step_count": 1 if timeline[0]["type"] == "step" else 0,
        }

        for i in range(1, len(timeline)):
            event = timeline[i]
            time_since_last = event["timestamp"] - timeline[i - 1]["timestamp"]

            # Check if this event belongs to the current session
            if time_since_last <= session_threshold:
                # Add to current session
                current_session["events"].append(event)
                current_session["end_time"] = event["timestamp"]

                # Update counts
                if event["type"] == "view":
                    current_session["view_count"] += 1
                elif event["type"] == "idea":
                    current_session["idea_count"] += 1
                else:  # step
                    current_session["step_count"] += 1
            else:
                # Calculate session statistics
                current_session["duration"] = (
                    current_session["end_time"] - current_session["start_time"]
                )
                current_session["action_count"] = (
                    current_session["idea_count"] + current_session["step_count"]
                )

                # Store the session
                sessions.append(current_session)

                # Start a new session
                current_session = {
                    "start_time": event["timestamp"],
                    "end_time": event["timestamp"],
                    "events": [event],
                    "view_count": 1 if event["type"] == "view" else 0,
                    "idea_count": 1 if event["type"] == "idea" else 0,
                    "step_count": 1 if event["type"] == "step" else 0,
                }

        # Don't forget the last session
        current_session["duration"] = (
            current_session["end_time"] - current_session["start_time"]
        )
        current_session["action_count"] = (
            current_session["idea_count"] + current_session["step_count"]
        )
        sessions.append(current_session)

        return sessions

    def _analyze_process_flow(
        self, view_action_correlation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze process flow patterns based on user action sequences.

        Args:
            view_action_correlation: View-action correlation analysis results

        Returns:
            Dictionary with process flow analysis results
        """
        self.logger.info("Analyzing process flow patterns")

        process_flow = {
            "global_transition_matrix": defaultdict(lambda: defaultdict(float)),
            "common_sequences": defaultdict(int),
            "most_frequent_starting_actions": defaultdict(int),
            "most_frequent_ending_actions": defaultdict(int),
            "average_sequence_length": 0,
            "path_completion_rates": {},
            "user_sequence_patterns": {},
        }

        # Get sessions from correlation analysis
        sessions = view_action_correlation.get("sessions", [])

        # Skip if no sessions
        if not sessions:
            self.logger.warning("No sessions available for process flow analysis")
            return process_flow

        # Process each session
        all_event_sequences = []

        for session in sessions:
            events = session.get("events", [])
            if len(events) < 2:
                continue

            # Extract sequences from this session
            sequence_results = self._extract_action_sequences(events)

            # Add to global results
            for seq, count in sequence_results["sequence_frequencies"].items():
                process_flow["common_sequences"][seq] += count

            # Update global transition matrix
            for from_type, to_types in sequence_results["transition_matrix"].items():
                for to_type, prob in to_types.items():
                    process_flow["global_transition_matrix"][from_type][to_type] += prob

            # Track first and last actions in sessions
            if events:
                first_action = events[0]["type"]
                last_action = events[-1]["type"]
                process_flow["most_frequent_starting_actions"][first_action] += 1
                process_flow["most_frequent_ending_actions"][last_action] += 1

            # Add sequence to all event sequences
            event_types = [e["type"] for e in events]
            all_event_sequences.append(event_types)

        # Normalize global transition matrix
        num_sessions = len(sessions)
        if num_sessions > 0:
            # Average the probabilities across all sessions
            for from_type in process_flow["global_transition_matrix"]:
                for to_type in process_flow["global_transition_matrix"][from_type]:
                    process_flow["global_transition_matrix"][from_type][
                        to_type
                    ] /= num_sessions

        # Convert defaultdicts to regular dicts for JSON serialization
        process_flow["global_transition_matrix"] = {
            from_type: dict(to_types)
            for from_type, to_types in process_flow["global_transition_matrix"].items()
        }
        process_flow["common_sequences"] = dict(process_flow["common_sequences"])
        process_flow["most_frequent_starting_actions"] = dict(
            process_flow["most_frequent_starting_actions"]
        )
        process_flow["most_frequent_ending_actions"] = dict(
            process_flow["most_frequent_ending_actions"]
        )

        # Calculate average sequence length
        if all_event_sequences:
            total_length = sum(len(seq) for seq in all_event_sequences)
            process_flow["average_sequence_length"] = total_length / len(
                all_event_sequences
            )

        # Find most common full paths (view to last action)
        view_to_end_paths = defaultdict(int)

        for seq in all_event_sequences:
            if seq and seq[0] == "view":
                path_key = " → ".join(seq)
                view_to_end_paths[path_key] += 1

        # Get top 10 full paths
        top_paths = sorted(view_to_end_paths.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        process_flow["most_common_full_paths"] = dict(top_paths)

        # Calculate path completion rate (% of view->idea->step vs. view->idea only)
        if (
            "view -> idea -> step" in process_flow["common_sequences"]
            and "view -> idea" in process_flow["common_sequences"]
        ):
            view_idea_step = process_flow["common_sequences"]["view -> idea -> step"]
            view_idea = process_flow["common_sequences"]["view -> idea"]
            if view_idea > 0:
                process_flow["path_completion_rates"]["view_idea_to_step"] = (
                    view_idea_step / view_idea * 100
                )

        self.logger.info("Process flow analysis completed")
        return process_flow

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

    @staticmethod
    def _extract_action_sequences(timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and analyze action sequences from a user's timeline.

        Args:
            timeline: Chronologically sorted list of user events (views and actions)

        Returns:
            Dictionary with sequence analysis results
        """
        sequence_results = {
            "common_sequences": [],
            "sequence_frequencies": {},
            "transition_matrix": {},
            "typical_paths": [],
        }

        # Skip if timeline is too short
        if len(timeline) < 2:
            return sequence_results

        # Extract action sequences (n-grams of actions)
        sequences = []
        current_sequence = []

        for event in timeline:
            event_type = event["type"]
            current_sequence.append(event_type)

            # Keep sequences manageable (up to 5 events)
            if len(current_sequence) > 5:
                current_sequence.pop(0)

            # Save all sequences of length 2 or more
            if len(current_sequence) >= 2:
                sequences.append(tuple(current_sequence.copy()))

        # Count sequence frequencies
        sequence_counts = defaultdict(int)
        for seq in sequences:
            sequence_counts[seq] += 1

        # Sort by frequency and convert to list of (sequence, count)
        sorted_sequences = sorted(
            sequence_counts.items(), key=lambda x: x[1], reverse=True
        )
        sequence_results["common_sequences"] = sorted_sequences[:10]  # Top 10 sequences
        sequence_results["sequence_frequencies"] = dict(sequence_counts)

        # Calculate transition probabilities
        transitions = defaultdict(lambda: defaultdict(int))

        # Count transitions between event types
        for i in range(len(timeline) - 1):
            from_type = timeline[i]["type"]
            to_type = timeline[i + 1]["type"]
            transitions[from_type][to_type] += 1

        # Convert counts to probabilities
        transition_matrix = {}
        for from_type, to_types in transitions.items():
            total = sum(to_types.values())
            transition_matrix[from_type] = {
                to_type: count / total for to_type, count in to_types.items()
            }

        sequence_results["transition_matrix"] = transition_matrix

        # Identify typical paths (most common sequences starting with a view)
        view_sequences = [seq for seq in sorted_sequences if seq[0][0] == "view"]
        sequence_results["typical_paths"] = view_sequences[
            :5
        ]  # Top 5 view-initiated sequences

        return sequence_results

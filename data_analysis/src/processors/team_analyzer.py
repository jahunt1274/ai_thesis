"""
Team analyzer for data analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.processors.base_analyzer import BaseAnalyzer
from src.loaders.relationship_loader import RelationshipLoader
from src.utils import StatsUtils, DataGroupingUtils


class TeamAnalyzer(BaseAnalyzer):
    """Analyzes team-based metrics and patterns."""

    def __init__(
        self,
        users: List[Dict[str, Any]],
        ideas: List[Dict[str, Any]],
        steps: List[Dict[str, Any]],
        relationship_loader: RelationshipLoader,
        end_date: Optional[datetime] = None,
    ):
        """
        Initialize the team analyzer.

        Args:
            users: List of processed user records
            ideas: List of processed idea records
            steps: List of processed step records
            relationship_loader: Loader for relationship data
            end_date: Optional reference date for time-based calculations (default: now)
        """
        super().__init__("team_analyzer")
        self.users = users
        self.ideas = ideas
        self.steps = steps
        self.relationships = relationship_loader
        
        # Set reference date for time-based calculations
        self.end_date = end_date or datetime(2025, 2, 4, tzinfo=timezone.utc)

        # Create lookup maps for efficient access
        self.ideas_by_owner = {
            user.get("email"): [] for user in users if user.get("email")
        }
        self.steps_by_owner = {
            user.get("email"): [] for user in users if user.get("email")
        }
        
        # Populate lookup maps
        for idea in self.ideas:
            owner = idea.get("owner")
            if owner and owner in self.ideas_by_owner:
                self.ideas_by_owner[owner].append(idea)
                
        for step in self.steps:
            owner = step.get("owner")
            if owner and owner in self.steps_by_owner:
                self.steps_by_owner[owner].append(step)

    def validate_data(self) -> None:
        """Validate input data and relationships."""
        if not self.users:
            self.logger.warning("No user data provided")
        if not self.ideas:
            self.logger.warning("No idea data provided")
        if not self.steps:
            self.logger.warning("No step data provided")
            
        # Check if relationship data is loaded
        if not self.relationships.team_student_map:
            self.logger.warning("No team-student mapping data available")
        if not self.relationships.term_section_map:
            self.logger.warning("No term-section mapping data available")

    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive team-based analysis.

        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Performing team analysis")

        results = {
            "team_engagement": self._analyze_team_engagement(),
            "team_activity": self._analyze_team_activity(),
            "section_comparison": self._analyze_section_comparison(),
            "semester_comparison": self._analyze_semester_comparison(),
            "team_size_impact": self._analyze_team_size_impact(),
            "work_distribution": self._analyze_work_distribution(),
            "tool_version_impact": self._analyze_tool_version_impact(),
        }

        return results

    def _analyze_team_engagement(self) -> Dict[str, Any]:
        """
        Analyze engagement metrics for all teams.

        Returns:
            Dictionary with team engagement metrics
        """
        self.logger.info("Analyzing team engagement")
        
        team_metrics = {}
        
        # Process each team
        for team_id, student_emails in self.relationships.team_student_map.items():
            if not student_emails:
                continue
                
            # Get team metadata
            team_metadata = self.relationships.get_team_metadata(int(team_id))
            
            # Calculate team metrics
            ideas_count = 0
            steps_count = 0
            avg_idea_progress = 0
            total_progress_values = []
            unique_framework_users = {"disciplined-entrepreneurship": set(), "startup-tactics": set()}
            framework_counts = {"disciplined-entrepreneurship": 0, "startup-tactics": 0}
            
            # Collect metrics for each team member
            for email in student_emails:
                # Count ideas and extract progress values
                user_ideas = self.ideas_by_owner.get(email, [])
                ideas_count += len(user_ideas)
                
                for idea in user_ideas:
                    # Track progress values
                    progress = idea.get("total_progress", 0)
                    total_progress_values.append(progress)
                    
                    # Track framework usage
                    for framework in idea.get("frameworks", []):
                        if framework in unique_framework_users:
                            unique_framework_users[framework].add(email)
                            framework_counts[framework] += 1
                
                # Count steps
                steps_count += len(self.steps_by_owner.get(email, []))
            
            # Calculate averages
            avg_ideas_per_member = ideas_count / len(student_emails) if student_emails else 0
            avg_steps_per_member = steps_count / len(student_emails) if student_emails else 0
            if total_progress_values:
                avg_idea_progress = sum(total_progress_values) / len(total_progress_values)
            
            # Determine preferred framework
            preferred_framework = None
            if framework_counts["disciplined-entrepreneurship"] > framework_counts["startup-tactics"]:
                preferred_framework = "disciplined-entrepreneurship"
            elif framework_counts["startup-tactics"] > framework_counts["disciplined-entrepreneurship"]:
                preferred_framework = "startup-tactics"
            elif framework_counts["disciplined-entrepreneurship"] > 0:  # Equal non-zero counts
                preferred_framework = "both"
            
            # Store team metrics
            team_metrics[team_id] = {
                "name": team_metadata.get("name", f"Team {team_id}"),
                "term": team_metadata.get("term"),
                "year": team_metadata.get("year"),
                "member_count": len(student_emails),
                "total_ideas": ideas_count,
                "total_steps": steps_count,
                "avg_ideas_per_member": avg_ideas_per_member,
                "avg_steps_per_member": avg_steps_per_member,
                "avg_idea_progress": avg_idea_progress,
                "framework_counts": framework_counts,
                "framework_users": {
                    k: len(v) for k, v in unique_framework_users.items()
                },
                "preferred_framework": preferred_framework,
            }
        
        # Calculate overall statistics
        if team_metrics:
            overall_stats = {
                "total_teams": len(team_metrics),
                "avg_team_size": sum(tm["member_count"] for tm in team_metrics.values()) / len(team_metrics),
                "avg_ideas_per_team": sum(tm["total_ideas"] for tm in team_metrics.values()) / len(team_metrics),
                "avg_steps_per_team": sum(tm["total_steps"] for tm in team_metrics.values()) / len(team_metrics),
                "framework_preference_counts": {
                    "disciplined-entrepreneurship": sum(1 for tm in team_metrics.values() if tm["preferred_framework"] == "disciplined-entrepreneurship"),
                    "startup-tactics": sum(1 for tm in team_metrics.values() if tm["preferred_framework"] == "startup-tactics"),
                    "both": sum(1 for tm in team_metrics.values() if tm["preferred_framework"] == "both"),
                    "none": sum(1 for tm in team_metrics.values() if tm["preferred_framework"] is None),
                }
            }
        else:
            overall_stats = {
                "total_teams": 0,
                "avg_team_size": 0,
                "avg_ideas_per_team": 0,
                "avg_steps_per_team": 0,
                "framework_preference_counts": {
                    "disciplined-entrepreneurship": 0,
                    "startup-tactics": 0,
                    "both": 0,
                    "none": 0,
                }
            }
            
        return {
            "team_metrics": team_metrics,
            "overall_stats": overall_stats
        }

    def _analyze_team_activity(self) -> Dict[str, Any]:
        """
        Analyze activity patterns within teams.

        Returns:
            Dictionary with team activity metrics
        """
        self.logger.info("Analyzing team activity patterns")
        
        team_activity = {}
        
        # Process each team
        for team_id, student_emails in self.relationships.team_student_map.items():
            if not student_emails:
                continue
                
            # Get team metadata
            team_metadata = self.relationships.get_team_metadata(int(team_id))
            
            # Track activity timeline
            activity_dates = []
            
            # Track activity by user
            member_activity = {}
            
            for email in student_emails:
                # Track this member's activity
                user_ideas = self.ideas_by_owner.get(email, [])
                user_steps = self.steps_by_owner.get(email, [])
                
                # Extract dates from ideas
                idea_dates = []
                for idea in user_ideas:
                    created_date = idea.get("created_date")
                    if created_date:
                        if "T" in created_date:
                            date_str = created_date.split("T")[0]  # YYYY-MM-DD
                            idea_dates.append(date_str)
                            activity_dates.append(date_str)
                
                # Extract dates from steps
                step_dates = []
                for step in user_steps:
                    created_at = step.get("created_at")
                    if created_at:
                        if "T" in created_at:
                            date_str = created_at.split("T")[0]  # YYYY-MM-DD
                            step_dates.append(date_str)
                            activity_dates.append(date_str)
                
                # Store this member's activity
                member_activity[email] = {
                    "idea_count": len(user_ideas),
                    "step_count": len(user_steps),
                    "idea_dates": idea_dates,
                    "step_dates": step_dates,
                    "active_dates": sorted(set(idea_dates + step_dates)),
                    "total_activity": len(user_ideas) + len(user_steps)
                }
            
            # Calculate team-level timeline
            if activity_dates:
                unique_activity_dates = sorted(set(activity_dates))
                first_activity = unique_activity_dates[0] if unique_activity_dates else None
                last_activity = unique_activity_dates[-1] if unique_activity_dates else None
                
                # Count activity per day
                daily_activity = defaultdict(int)
                for date in activity_dates:
                    daily_activity[date] += 1
                
                # Find peak activity
                peak_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else (None, 0)
            else:
                unique_activity_dates = []
                first_activity = None
                last_activity = None
                daily_activity = {}
                peak_day = (None, 0)
            
            # Calculate activity spread across team
            if member_activity:
                member_contributions = [data["total_activity"] for email, data in member_activity.items()]
                activity_distribution = {
                    "min": min(member_contributions) if member_contributions else 0,
                    "max": max(member_contributions) if member_contributions else 0,
                    "mean": sum(member_contributions) / len(member_contributions) if member_contributions else 0,
                    "std_dev": StatsUtils.calculate_standard_deviation(member_contributions) if len(member_contributions) > 1 else 0,
                    "gini_coefficient": StatsUtils.calculate_gini_coefficient(member_contributions) if len(member_contributions) > 1 else 0
                }
                
                # Identify most and least active members
                most_active = max(member_activity.items(), key=lambda x: x[1]["total_activity"]) if member_activity else (None, {})
                least_active = min(member_activity.items(), key=lambda x: x[1]["total_activity"]) if member_activity else (None, {})
            else:
                activity_distribution = {
                    "min": 0,
                    "max": 0,
                    "mean": 0,
                    "std_dev": 0,
                    "gini_coefficient": 0
                }
                most_active = (None, {})
                least_active = (None, {})
            
            # Store team activity data
            team_activity[team_id] = {
                "name": team_metadata.get("name", f"Team {team_id}"),
                "term": team_metadata.get("term"),
                "year": team_metadata.get("year"),
                "member_count": len(student_emails),
                "activity_timeline": {
                    "first_activity": first_activity,
                    "last_activity": last_activity,
                    "unique_activity_days": len(unique_activity_dates),
                    "peak_day": peak_day[0],
                    "peak_activity_count": peak_day[1],
                    "daily_activity": dict(daily_activity)
                },
                "member_activity": member_activity,
                "activity_distribution": activity_distribution,
                "most_active_member": {
                    "email": most_active[0],
                    "activity_count": most_active[1].get("total_activity", 0) if most_active[1] else 0
                },
                "least_active_member": {
                    "email": least_active[0],
                    "activity_count": least_active[1].get("total_activity", 0) if least_active[1] else 0
                }
            }
        
        # Calculate collaborative metrics
        for team_id, activity in team_activity.items():
            # Skip teams with insufficient data
            if activity["member_count"] <= 1:
                continue
                
            # Calculate collaboration score based on distribution of work
            gini = activity["activity_distribution"]["gini_coefficient"]
            # Convert Gini to collaboration score (1 - Gini, so 1 is perfect equality)
            activity["collaboration_score"] = 1 - gini
            
            # Classify collaboration pattern
            if gini < 0.2:
                activity["collaboration_pattern"] = "Highly collaborative"
            elif gini < 0.4:
                activity["collaboration_pattern"] = "Collaborative"
            elif gini < 0.6:
                activity["collaboration_pattern"] = "Moderately collaborative"
            else:
                activity["collaboration_pattern"] = "Dominated by few members"
        
        return team_activity

    def _analyze_section_comparison(self) -> Dict[str, Any]:
        """
        Compare team performance across different sections.

        Returns:
            Dictionary with section comparison metrics
        """
        self.logger.info("Analyzing section comparisons")
        
        section_data = {}
        
        # Extract terms with multiple sections
        terms_with_sections = {}
        for term_key, term_info in self.relationships.term_section_map.items():
            sections = term_info.get("sections", [])
            if len(sections) > 1:
                terms_with_sections[term_key] = sections
        
        # For each term with multiple sections, compare the sections
        for term_key, sections in terms_with_sections.items():
            term_parts = term_key.split("_")
            if len(term_parts) < 2:
                continue
                
            term = term_parts[0]
            try:
                year = int(term_parts[1])
            except ValueError:
                continue
                
            # Get tool version information
            tool_version = self.relationships.get_tool_version(term, year)
                
            # Initialize section comparison data
            section_comparison = {
                "term": term,
                "year": year,
                "tool_version": tool_version,
                "sections": {}
            }
            
            # For each section, aggregate team metrics
            for section in sections:
                section_id = f"{term}_{year}_{section}"
                team_ids = self.relationships.section_team_map.get(section_id, [])
                
                if not team_ids:
                    continue
                    
                # Collect team engagement data
                team_engagement_data = self._analyze_team_engagement()
                team_metrics = team_engagement_data.get("team_metrics", {})
                
                # Calculate section-level metrics
                section_teams = [team_metrics.get(str(team_id), {}) for team_id in team_ids]
                section_teams = [team for team in section_teams if team]  # Filter out empty teams
                
                if not section_teams:
                    continue
                    
                # Calculate averages
                avg_ideas_per_team = sum(team.get("total_ideas", 0) for team in section_teams) / len(section_teams)
                avg_steps_per_team = sum(team.get("total_steps", 0) for team in section_teams) / len(section_teams)
                avg_idea_progress = sum(team.get("avg_idea_progress", 0) for team in section_teams) / len(section_teams)
                
                # Framework preferences
                framework_preferences = {
                    "disciplined-entrepreneurship": sum(1 for team in section_teams if team.get("preferred_framework") == "disciplined-entrepreneurship"),
                    "startup-tactics": sum(1 for team in section_teams if team.get("preferred_framework") == "startup-tactics"),
                    "both": sum(1 for team in section_teams if team.get("preferred_framework") == "both"),
                    "none": sum(1 for team in section_teams if team.get("preferred_framework") is None)
                }
                
                # Store section metrics
                section_comparison["sections"][section] = {
                    "team_count": len(section_teams),
                    "avg_ideas_per_team": avg_ideas_per_team,
                    "avg_steps_per_team": avg_steps_per_team,
                    "avg_idea_progress": avg_idea_progress,
                    "framework_preferences": framework_preferences
                }
            
            # Add comparisons between sections
            if len(section_comparison["sections"]) > 1:
                comparisons = []
                section_keys = list(section_comparison["sections"].keys())
                
                for i in range(len(section_keys)):
                    for j in range(i + 1, len(section_keys)):
                        section1 = section_keys[i]
                        section2 = section_keys[j]
                        
                        s1_data = section_comparison["sections"][section1]
                        s2_data = section_comparison["sections"][section2]
                        
                        # Calculate differences
                        ideas_diff = s1_data["avg_ideas_per_team"] - s2_data["avg_ideas_per_team"]
                        steps_diff = s1_data["avg_steps_per_team"] - s2_data["avg_steps_per_team"]
                        progress_diff = s1_data["avg_idea_progress"] - s2_data["avg_idea_progress"]
                        
                        comparisons.append({
                            "section_pair": f"{section1} vs {section2}",
                            "ideas_difference": ideas_diff,
                            "steps_difference": steps_diff,
                            "progress_difference": progress_diff
                        })
                
                section_comparison["section_comparisons"] = comparisons
            
            # Store term data
            section_data[term_key] = section_comparison
        
        return section_data

    def _analyze_semester_comparison(self) -> Dict[str, Any]:
        """
        Compare team performance across different semesters.

        Returns:
            Dictionary with semester comparison metrics
        """
        self.logger.info("Analyzing semester comparisons")
        
        semester_data = {}
        
        # Group terms by tool version
        tool_version_terms = defaultdict(list)
        
        for term_key, term_info in self.relationships.term_section_map.items():
            tool_version = term_info.get("tool_version")
            tool_version_terms[tool_version].append(term_key)
        
        # Calculate semester-level metrics
        for term_key, term_info in self.relationships.term_section_map.items():
            term_parts = term_key.split("_")
            if len(term_parts) < 2:
                continue
                
            term = term_parts[0]
            try:
                year = int(term_parts[1])
            except ValueError:
                continue
                
            # Get teams across all sections for this term
            all_section_teams = []
            for section in term_info.get("sections", []):
                section_id = f"{term}_{year}_{section}"
                team_ids = self.relationships.section_team_map.get(section_id, [])
                all_section_teams.extend(team_ids)
            
            # Get unique teams
            unique_teams = list(set(all_section_teams))
            
            if not unique_teams:
                continue
                
            # Collect team metrics for these teams
            team_metrics = self._analyze_team_engagement().get("team_metrics", {})
            
            # Calculate semester-level metrics
            semester_teams = [team_metrics.get(str(team_id), {}) for team_id in unique_teams]
            semester_teams = [team for team in semester_teams if team]  # Filter out empty teams
            
            if not semester_teams:
                continue
                
            # Calculate averages
            avg_ideas_per_team = sum(team.get("total_ideas", 0) for team in semester_teams) / len(semester_teams)
            avg_steps_per_team = sum(team.get("total_steps", 0) for team in semester_teams) / len(semester_teams)
            avg_idea_progress = sum(team.get("avg_idea_progress", 0) for team in semester_teams) / len(semester_teams)
            
            # Framework preferences
            framework_preferences = {
                "disciplined-entrepreneurship": sum(1 for team in semester_teams if team.get("preferred_framework") == "disciplined-entrepreneurship"),
                "startup-tactics": sum(1 for team in semester_teams if team.get("preferred_framework") == "startup-tactics"),
                "both": sum(1 for team in semester_teams if team.get("preferred_framework") == "both"),
                "none": sum(1 for team in semester_teams if team.get("preferred_framework") is None)
            }
            
            # Store semester metrics
            semester_data[term_key] = {
                "term": term,
                "year": year,
                "tool_version": term_info.get("tool_version"),
                "team_count": len(semester_teams),
                "section_count": len(term_info.get("sections", [])),
                "avg_ideas_per_team": avg_ideas_per_team,
                "avg_steps_per_team": avg_steps_per_team,
                "avg_idea_progress": avg_idea_progress,
                "framework_preferences": framework_preferences
            }
        
        # Calculate comparisons between semesters
        semester_comparisons = []
        semesters = list(semester_data.keys())
        
        for i in range(len(semesters)):
            for j in range(i + 1, len(semesters)):
                sem1 = semesters[i]
                sem2 = semesters[j]
                
                s1_data = semester_data[sem1]
                s2_data = semester_data[sem2]
                
                # Calculate differences
                ideas_diff = s1_data["avg_ideas_per_team"] - s2_data["avg_ideas_per_team"]
                steps_diff = s1_data["avg_steps_per_team"] - s2_data["avg_steps_per_team"]
                progress_diff = s1_data["avg_idea_progress"] - s2_data["avg_idea_progress"]
                
                # Check if this is a tool version change
                tool_change = s1_data["tool_version"] != s2_data["tool_version"]
                
                semester_comparisons.append({
                    "semester_pair": f"{sem1} vs {sem2}",
                    "display_pair": f"{s1_data['term']} {s1_data['year']} vs {s2_data['term']} {s2_data['year']}",
                    "tool_version_change": tool_change,
                    "tool_versions": f"{s1_data['tool_version']} → {s2_data['tool_version']}",
                    "ideas_difference": ideas_diff,
                    "steps_difference": steps_diff,
                    "progress_difference": progress_diff
                })
        
        return {
            "semester_metrics": semester_data,
            "semester_comparisons": semester_comparisons
        }

    def _analyze_team_size_impact(self) -> Dict[str, Any]:
        """
        Analyze how team size impacts engagement and productivity.

        Returns:
            Dictionary with team size impact analysis
        """
        self.logger.info("Analyzing team size impact")
        
        # Group teams by size
        teams_by_size = defaultdict(list)
        
        # Get team metrics data first
        team_metrics = self._analyze_team_engagement().get("team_metrics", {})
        
        for team_id, metrics in team_metrics.items():
            team_size = metrics.get("member_count", 0)
            teams_by_size[team_size].append(metrics)
        
        # Calculate metrics for each team size
        size_metrics = {}
        
        for size, teams in teams_by_size.items():
            if size == 0 or not teams:  # Skip empty teams
                continue
                
            # Calculate averages
            avg_ideas = sum(team.get("total_ideas", 0) for team in teams) / len(teams)
            avg_steps = sum(team.get("total_steps", 0) for team in teams) / len(teams)
            avg_progress = sum(team.get("avg_idea_progress", 0) for team in teams) / len(teams)
            
            # Calculate per-member metrics
            avg_ideas_per_member = sum(team.get("avg_ideas_per_member", 0) for team in teams) / len(teams)
            avg_steps_per_member = sum(team.get("avg_steps_per_member", 0) for team in teams) / len(teams)
            
            size_metrics[size] = {
                "team_count": len(teams),
                "avg_ideas_per_team": avg_ideas,
                "avg_steps_per_team": avg_steps,
                "avg_idea_progress": avg_progress,
                "avg_ideas_per_member": avg_ideas_per_member,
                "avg_steps_per_member": avg_steps_per_member
            }
        
        # Calculate correlation between team size and metrics
        if len(size_metrics) > 1:
            sizes = list(size_metrics.keys())
            ideas_per_team = [size_metrics[size]["avg_ideas_per_team"] for size in sizes]
            steps_per_team = [size_metrics[size]["avg_steps_per_team"] for size in sizes]
            ideas_per_member = [size_metrics[size]["avg_ideas_per_member"] for size in sizes]
            steps_per_member = [size_metrics[size]["avg_steps_per_member"] for size in sizes]
            
            correlation_with_size = {
                "ideas_per_team": StatsUtils.calculate_correlation(sizes, ideas_per_team),
                "steps_per_team": StatsUtils.calculate_correlation(sizes, steps_per_team),
                "ideas_per_member": StatsUtils.calculate_correlation(sizes, ideas_per_member),
                "steps_per_member": StatsUtils.calculate_correlation(sizes, steps_per_member)
            }
        else:
            correlation_with_size = {
                "ideas_per_team": None,
                "steps_per_team": None,
                "ideas_per_member": None,
                "steps_per_member": None
            }
        
        return {
            "size_metrics": size_metrics,
            "correlation_with_size": correlation_with_size
        }

    def _analyze_work_distribution(self) -> Dict[str, Any]:
        """
        Analyze how work is distributed within teams.

        Returns:
            Dictionary with work distribution analysis
        """
        self.logger.info("Analyzing work distribution within teams")
        
        # Get team activity data
        team_activity = self._analyze_team_activity()
        
        # Calculate distribution metrics across all teams
        gini_coefficients = []
        collaboration_patterns = defaultdict(int)
        
        for team_id, activity in team_activity.items():
            gini = activity.get("activity_distribution", {}).get("gini_coefficient")
            pattern = activity.get("collaboration_pattern")
            
            if gini is not None:
                gini_coefficients.append(gini)
                
            if pattern:
                collaboration_patterns[pattern] += 1
        
        # Calculate distribution of Gini coefficients
        if gini_coefficients:
            gini_distribution = {
                "min": min(gini_coefficients),
                "max": max(gini_coefficients),
                "mean": sum(gini_coefficients) / len(gini_coefficients),
                "median": sorted(gini_coefficients)[len(gini_coefficients) // 2],
                "std_dev": StatsUtils.calculate_standard_deviation(gini_coefficients)
            }
        else:
            gini_distribution = {
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "std_dev": 0
            }
        
        # Look for patterns by semester
        semester_patterns = {}
        
        for team_id, activity in team_activity.items():
            term = activity.get("term")
            year = activity.get("year")
            
            if not term or not year:
                continue
                
            term_key = f"{term}_{year}"
            if term_key not in semester_patterns:
                semester_patterns[term_key] = {
                    "team_count": 0,
                    "gini_values": [],
                    "patterns": defaultdict(int)
                }
                
            semester_patterns[term_key]["team_count"] += 1
            
            gini = activity.get("activity_distribution", {}).get("gini_coefficient")
            if gini is not None:
                semester_patterns[term_key]["gini_values"].append(gini)
                
            pattern = activity.get("collaboration_pattern")
            if pattern:
                semester_patterns[term_key]["patterns"][pattern] += 1
        
        # Calculate averages for each semester
        for term_key, data in semester_patterns.items():
            if data["gini_values"]:
                data["avg_gini"] = sum(data["gini_values"]) / len(data["gini_values"])
            else:
                data["avg_gini"] = 0
                
            # Convert defaultdict to regular dict
            data["patterns"] = dict(data["patterns"])
        
        return {
            "overall_gini_distribution": gini_distribution,
            "collaboration_patterns": dict(collaboration_patterns),
            "semester_patterns": semester_patterns
        }

    def _analyze_tool_version_impact(self) -> Dict[str, Any]:
        """
        Analyze how different tool versions impact team performance.

        Returns:
            Dictionary with tool version impact analysis
        """
        self.logger.info("Analyzing tool version impact")
        
        # Group semester metrics by tool version
        tool_metrics = defaultdict(list)
        
        # First gather semester metrics
        semester_data = self._analyze_semester_comparison().get("semester_metrics", {})
        
        for term_key, metrics in semester_data.items():
            tool_version = metrics.get("tool_version")
            tool_metrics[tool_version].append(metrics)
        
        # Calculate metrics for each tool version
        version_metrics = {}
        
        for version, semesters in tool_metrics.items():
            if not semesters:
                continue
                
            # Calculate averages
            avg_ideas = sum(sem.get("avg_ideas_per_team", 0) for sem in semesters) / len(semesters)
            avg_steps = sum(sem.get("avg_steps_per_team", 0) for sem in semesters) / len(semesters)
            avg_progress = sum(sem.get("avg_idea_progress", 0) for sem in semesters) / len(semesters)
            
            # Calculate framework preferences
            framework_prefs = defaultdict(int)
            for sem in semesters:
                for framework, count in sem.get("framework_preferences", {}).items():
                    framework_prefs[framework] += count
            
            # Store metrics
            version_metrics[version] = {
                "semester_count": len(semesters),
                "semesters": [f"{sem.get('term')} {sem.get('year')}" for sem in semesters],
                "avg_ideas_per_team": avg_ideas,
                "avg_steps_per_team": avg_steps,
                "avg_idea_progress": avg_progress,
                "framework_preferences": dict(framework_prefs)
            }
        
        # Calculate improvements between versions
        improvements = []
        versions = [None, "v1", "v2"]  # Expected progression
        
        for i in range(1, len(versions)):
            prev_version = versions[i-1]
            curr_version = versions[i]
            
            if prev_version in version_metrics and curr_version in version_metrics:
                prev_metrics = version_metrics[prev_version]
                curr_metrics = version_metrics[curr_version]
                
                # Calculate differences
                ideas_diff = curr_metrics["avg_ideas_per_team"] - prev_metrics["avg_ideas_per_team"]
                steps_diff = curr_metrics["avg_steps_per_team"] - prev_metrics["avg_steps_per_team"]
                progress_diff = curr_metrics["avg_idea_progress"] - prev_metrics["avg_idea_progress"]
                
                # Calculate percentage changes
                ideas_pct = (ideas_diff / prev_metrics["avg_ideas_per_team"]) * 100 if prev_metrics["avg_ideas_per_team"] else None
                steps_pct = (steps_diff / prev_metrics["avg_steps_per_team"]) * 100 if prev_metrics["avg_steps_per_team"] else None
                progress_pct = (progress_diff / prev_metrics["avg_idea_progress"]) * 100 if prev_metrics["avg_idea_progress"] else None
                
                improvements.append({
                    "from_version": prev_version if prev_version is not None else "No Tool",
                    "to_version": curr_version,
                    "ideas_diff": ideas_diff,
                    "ideas_percent_change": ideas_pct,
                    "steps_diff": steps_diff,
                    "steps_percent_change": steps_pct,
                    "progress_diff": progress_diff,
                    "progress_percent_change": progress_pct
                })
        
        return {
            "version_metrics": version_metrics,
            "version_improvements": improvements
        }
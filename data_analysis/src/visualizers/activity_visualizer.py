"""
Activity visualizer for data analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger, DateUtils

logger = get_logger("activity_visualizer")


class ActivityVisualizer(BaseVisualizer):
    """Visualizes activity and usage analysis results."""

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for activity analysis.

        Args:
            data: Activity analysis results

        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            "idea_counts": (
                self._visualize_idea_generation,
                {"data_key": "idea_generation"},
            ),
            "ideas_by_ranking": (
                self._visualize_ideas_by_ranking,
                {"data_key": "idea_generation.ideas_by_ranking"},
            ),
            "engagement_levels": (
                self._visualize_engagement_levels,
                {"data_key": "engagement_levels.engagement_levels"},
            ),
            "framework_engagement": (
                self._visualize_framework_engagement,
                {"data_key": "engagement_levels.framework_engagement"},
            ),
            "monthly_active_users": (
                self._visualize_monthly_active_users,
                {
                    "data_key": "engagement_levels.temporal_engagement.monthly_active_users"
                },
            ),
            "step_distribution": (
                self._visualize_step_distribution,
                {"data_key": "process_completion.step_distribution"},
            ),
            "framework_completion": (
                self._visualize_framework_completion,
                {"data_key": "process_completion.completion_by_framework"},
            ),
            "step_progression": (
                self._visualize_step_progression,
                {"data_key": "dropout_points"},
            ),
            "time_based": (
                self._visualize_time_based_engagement,
                {"data_key": "timeline"},
            ),
            "idea_characterization": (
                self._visualize_idea_characterization,
                {"data_key": "engagement_levels.idea_characterization"},
            ),
            "framework_usage": (
                self._visualize_framework_usage,
                {"data_key": "framework_usage"},
            ),
            "timeline": (self._visualize_timeline, {"data_key": "timeline"}),
            "view_action_correlation": (
                self._visualize_view_action_correlation,
                {"data_key": "view_action_correlation"},
            ),
            "process_flow": (
                self._visualize_process_flow,
                {"data_key": "process_flow"},
            ),
        }

        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_idea_generation(
        self, idea_generation: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of idea generation metrics.

        Args:
            idea_generation: Idea generation statistics
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract data
        total_ideas = idea_generation.get("total_ideas", 0)
        unique_owners = idea_generation.get("unique_owners", 0)
        max_ideas_per_owner = idea_generation.get("max_ideas_per_owner", 0)
        avg_ideas_per_owner = idea_generation.get("avg_ideas_per_owner", 0)

        # Create bar chart for counts
        labels = ["Total Ideas", "Unique Owners", "Max Ideas/Owner"]
        values = [total_ideas, unique_owners, max_ideas_per_owner]
        colors = ["royalblue", "green", "orange"]

        result = self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="Idea Generation Overview",
            ylabel="Count",
            color=colors,
        )

        # Add annotation for average ideas per owner
        if result:
            plt_fig = self.setup_figure()
            plt.annotate(
                f"Avg Ideas per Owner: {avg_ideas_per_owner:.2f}",
                xy=(0.5, 0.05),
                xycoords="figure fraction",
                bbox=dict(
                    boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8
                ),
                ha="center",
            )
            plt.close()

        return result

    def _visualize_ideas_by_ranking(
        self, ideas_by_ranking: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of ideas by ranking.

        Args:
            ideas_by_ranking: Counts of ideas by ranking
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not ideas_by_ranking:
            return None

        # Convert ranking keys to integers for proper sorting
        rankings = []
        counts = []

        # Extract and sort data
        for ranking, count in sorted(
            ideas_by_ranking.items(),
            key=lambda item: (
                int(item[0])
                if isinstance(item[0], str) and item[0].isdigit()
                else (int(float(item[0])) if isinstance(item[0], str) else item[0])
            ),
        ):
            rankings.append(str(ranking))
            counts.append(count)

        # Create color gradient
        colors = self.get_color_gradient(len(rankings), "sequential")

        # Create bar chart
        result = self.create_bar_chart(
            labels=rankings,
            values=counts,
            filename=filename,
            title="Ideas by Ranking",
            xlabel="Idea Ranking",
            ylabel="Number of Ideas",
            color=colors,
        )

        # Add explanation
        if result:
            plt_fig = self.setup_figure()
            plt.figtext(
                0.5,
                0.01,
                "Ranking represents the nth idea created by a user (1=first idea, 2=second idea, etc.)",
                ha="center",
                fontsize=10,
                bbox={"facecolor": "orange", "alpha": 0.2, "pad": 5},
            )
            plt.close()

        return result

    def _visualize_engagement_levels(
        self, engagement_levels: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user engagement levels.

        Args:
            engagement_levels: Counts by engagement level
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not engagement_levels:
            return None

        # Define custom labels and colors
        label_map = {
            "high": "High (>5 ideas)",
            "medium": "Medium (2-5 ideas)",
            "low": "Low (1 idea)",
            "none": "None (0 ideas)",
        }

        # Extract data in order
        ordered_levels = ["high", "medium", "low", "none"]
        labels = []
        values = []
        colors = []

        for level in ordered_levels:
            if level in engagement_levels:
                labels.append(label_map.get(level, level.title()))
                values.append(engagement_levels[level])
                colors.append(self.STANDARD_COLORS[level])

        # Create pie chart
        explode = [0.05] * len(labels)  # Add slight explosion to all slices

        return self.create_pie_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Engagement Levels",
            colors=colors,
            explode=explode,
        )

    def _visualize_framework_engagement(
        self, framework_engagement: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of framework engagement.

        Args:
            framework_engagement: Counts by framework
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not framework_engagement:
            return None

        # Order of frameworks to display
        frameworks = [
            "disciplined-entrepreneurship",
            "startup-tactics",
            "both_frameworks",
            "no_framework",
        ]

        # Custom labels
        label_map = {
            "both_frameworks": "Both Frameworks",
            "no_framework": "No Framework",
            "disciplined-entrepreneurship": "Disciplined Entrepreneurship",
            "startup-tactics": "Startup Tactics",
        }

        # Extract data
        labels = []
        values = []

        for framework in frameworks:
            if framework in framework_engagement:
                labels.append(label_map.get(framework, framework))
                values.append(framework_engagement[framework])

        # Define colors
        colors = ["dodgerblue", "darkorange", "mediumseagreen", "lightgray"]

        # Create bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="Framework Engagement",
            ylabel="Number of Users",
            color=colors,
        )

    def _visualize_monthly_active_users(
        self, monthly_active_users: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of monthly active users.

        Args:
            monthly_active_users: Active users by month
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Need at least 2 data points for a meaningful timeline
        if len(monthly_active_users) < 2:
            return None

        # Convert string dates to datetime objects
        dates = []
        counts = []

        for date_str, count in sorted(monthly_active_users.items()):
            date_obj = DateUtils.parse_date(
                f"{date_str}-01"
            )  # Add day to create valid date
            if date_obj:
                dates.append(date_obj)
                counts.append(count)

        # Create line chart
        return self.create_line_chart(
            x=dates,
            y=counts,
            filename=filename,
            title="Monthly Active Users",
            xlabel="Month",
            ylabel="Number of Active Users",
            color="crimson",
            add_trend=True,
            fill=True,
            date_format="%b %Y",
        )

    def _visualize_step_distribution(
        self, step_distribution: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of idea step distribution.

        Args:
            step_distribution: Counts of ideas by number of steps
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not step_distribution:
            return None

        # Extract data and sort by step count
        steps = []
        counts = []

        for step_count, count in sorted(
            step_distribution.items(),
            key=lambda item: (
                int(item[0])
                if isinstance(item[0], str) and item[0].isdigit()
                else (int(float(item[0])) if isinstance(item[0], str) else item[0])
            ),
        ):
            steps.append(str(step_count))
            counts.append(count)

        # Calculate mean steps
        if steps and counts:
            steps_numeric = [int(step) for step in steps]
            total_ideas = sum(counts)
            weighted_sum = sum(s * c for s, c in zip(steps_numeric, counts))
            mean_steps = weighted_sum / total_ideas if total_ideas > 0 else 0

        # Create color gradient based on step count
        colors = self.get_color_gradient(len(steps), "viridis")

        # Setup figure
        fig = self.setup_figure(
            figsize=(12, 7),
            title="Distribution of Ideas by Number of Steps Completed",
            xlabel="Number of Steps",
            ylabel="Number of Ideas",
        )

        # Create bar chart
        bars = plt.bar(steps, counts, color=colors)

        # Add value labels
        self.add_value_labels(plt.gca(), bars)

        # Add mean as a vertical line if calculated
        if steps and counts:
            plt.axvline(
                x=mean_steps,
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f"Mean: {mean_steps:.1f} steps",
            )
            plt.legend()

        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_framework_completion(
        self, completion_by_framework: Dict[str, Dict[str, Any]], filename: str
    ) -> Optional[str]:
        """
        Create visualization of framework completion comparison.

        Args:
            completion_by_framework: Completion statistics by framework
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not completion_by_framework:
            return None

        # Extract data
        frameworks = []
        avg_completion = []
        total_ideas = []

        for framework, data in completion_by_framework.items():
            # Format framework name for display
            framework_name = framework
            if framework == "disciplined-entrepreneurship":
                framework_name = "Disciplined Entrepreneurship"
            elif framework == "startup-tactics":
                framework_name = "Startup Tactics"

            frameworks.append(framework_name)
            avg_completion.append(data.get("avg_completion", 0))
            total_ideas.append(data.get("total_ideas", 0))

        # Create grouped bar chart using the enhanced BaseVisualizer method
        data_dict = {"Avg Completion": avg_completion, "Total Ideas": total_ideas}

        colors = {"Avg Completion": "teal", "Total Ideas": "darkorange"}

        return self.create_grouped_bar_chart(
            labels=frameworks,
            data_dict=data_dict,
            filename=filename,
            title="Framework Completion Comparison",
            ylabel="Value",
            colors=colors,
            add_value_labels=True,
            format_str="{:.2f}",
        )

    def _visualize_step_progression(
        self, dropout_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of step progression and dropout points.

        Args:
            dropout_data: Step progression and dropout data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        step_progression = dropout_data.get("step_progression", {})
        final_steps = dropout_data.get("final_steps", {})
        dropout_rates = dropout_data.get("dropout_rates", {})

        # Identify common steps between progression and final steps
        common_steps = set(step_progression.keys()).intersection(
            set(final_steps.keys())
        )

        # Need at least a few steps for meaningful visualization
        if len(common_steps) < 3:
            logger.warning("Not enough step data for progression visualization")
            return None

        # Create figure with multiple subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 15))

        # Sort steps by progression count to identify the common path
        sorted_steps = sorted(
            step_progression.items(), key=lambda x: x[1], reverse=True
        )
        top_steps = [step for step, _ in sorted_steps[:15]]  # Top 15 steps

        # Visualization 1: Step Progression (Funnel)
        steps_for_funnel = []
        progression_counts = []

        # Extract data for top steps in decreasing order
        for step in top_steps:
            steps_for_funnel.append(step)
            progression_counts.append(step_progression[step])

        # Reverse the order for proper funnel display
        steps_for_funnel.reverse()
        progression_counts.reverse()

        # Truncate long step names
        display_steps = [s[:30] + "..." if len(s) > 30 else s for s in steps_for_funnel]

        # Create horizontal bar chart for funnel
        bars1 = ax1.barh(display_steps, progression_counts, color="steelblue")

        # Add value labels
        for bar in bars1:
            width = bar.get_width()
            ax1.text(
                width + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                ha="left",
                va="center",
            )

        ax1.set_title("Step Progression (Ideas that reached each step)", fontsize=14)
        ax1.set_xlabel("Number of Ideas", fontsize=12)

        # Visualization 2: Final Steps (where users stopped)
        top_final_steps = sorted(final_steps.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        final_step_names = [step for step, _ in top_final_steps]
        final_step_counts = [count for _, count in top_final_steps]

        # Truncate long step names
        display_final_steps = [
            s[:30] + "..." if len(s) > 30 else s for s in final_step_names
        ]

        # Create horizontal bar chart for final steps
        bars2 = ax2.barh(display_final_steps, final_step_counts, color="coral")

        # Add value labels
        for bar in bars2:
            width = bar.get_width()
            ax2.text(
                width + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                ha="left",
                va="center",
            )

        ax2.set_title("Final Steps (Where Users Stopped)", fontsize=14)
        ax2.set_xlabel("Number of Ideas", fontsize=12)

        # Visualization 3: Dropout Rates
        dropout_step_names = []
        dropout_pcts = []

        # Get dropout rates for top final steps
        for step in final_step_names:
            if step in dropout_rates:
                dropout_step_names.append(step)
                dropout_pcts.append(dropout_rates[step] * 100)  # Convert to percentage

        # Truncate long step names
        display_dropout_steps = [
            s[:30] + "..." if len(s) > 30 else s for s in dropout_step_names
        ]

        # Sort by dropout rate
        sorted_indices = np.argsort(dropout_pcts)[::-1]  # Descending order
        sorted_steps = [display_dropout_steps[i] for i in sorted_indices]
        sorted_rates = [dropout_pcts[i] for i in sorted_indices]

        # Color bars by dropout rate (higher = more red)
        cmap = plt.cm.get_cmap("RdYlGn_r")
        colors = [cmap(rate / 100) for rate in sorted_rates]

        bars3 = ax3.barh(sorted_steps, sorted_rates, color=colors)

        # Add value labels
        for bar in bars3:
            width = bar.get_width()
            ax3.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
            )

        ax3.set_title("Dropout Rates by Step", fontsize=14)
        ax3.set_xlabel("Dropout Rate (%)", fontsize=12)
        ax3.set_xlim(0, 100)

        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_time_based_engagement(
        self, time_based_engagement: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of time-based engagement patterns.

        Args:
            time_based_engagement: Time-based engagement data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Check if monthly data is available
        monthly_active_users = time_based_engagement.get("monthly_active_users", {})

        if not monthly_active_users or len(monthly_active_users) < 2:
            return None

        # Convert string dates to datetime objects for proper timeline
        dates = []
        counts = []

        for date_str, count in sorted(monthly_active_users.items()):
            date_obj = DateUtils.parse_date(
                f"{date_str}-01"
            )  # Add day to create valid date
            if date_obj:
                dates.append(date_obj)
                counts.append(count)

        # Setup figure
        fig = self.setup_figure(
            figsize=(14, 7),
            title="Monthly Active Users Over Time",
            xlabel="Month",
            ylabel="Number of Active Users",
        )

        # Create line chart
        plt.plot(
            dates,
            counts,
            marker="o",
            linestyle="-",
            color="royalblue",
            linewidth=2,
            markersize=8,
        )

        # Fill area under the line
        plt.fill_between(dates, counts, alpha=0.3, color="royalblue")

        # Format x-axis as dates
        self.format_date_axis(plt.gca())

        # Calculate and add trend line
        if len(dates) >= 3:
            trend = np.polyfit(range(len(dates)), counts, 1)
            trend_line = [trend[0] * i + trend[1] for i in range(len(dates))]
            plt.plot(
                dates, trend_line, "r--", label=f"Trend (slope: {trend[0]:.2f}/month)"
            )
            plt.legend()

        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_idea_characterization(
        self, idea_characterization: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of idea characterization data.

        Args:
            idea_characterization: Idea characterization data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Check if necessary data exists
        if not idea_characterization:
            return None

        # Create a figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

        # Plot 1: Iteration patterns
        iteration_patterns = idea_characterization.get("iteration_patterns", {})
        users_by_iteration = iteration_patterns.get("users_by_max_iteration", {})

        if users_by_iteration:
            # Extract data
            iterations = []
            counts = []

            for iteration, count in sorted(
                users_by_iteration.items(),
                key=lambda item: (
                    int(item[0])
                    if isinstance(item[0], str) and item[0].isdigit()
                    else (int(float(item[0])) if isinstance(item[0], str) else item[0])
                ),
            ):
                iterations.append(f"{iteration} iteration(s)")
                counts.append(count)

            # Create bar chart
            bars1 = ax1.bar(iterations, counts, color="cornflowerblue")

            # Add value labels
            self.add_value_labels(ax1, bars1)

            ax1.set_title("Users by Maximum Iteration Count", fontsize=14)
            ax1.set_ylabel("Number of Users", fontsize=12)
            ax1.tick_params(axis="x", rotation=45)
        else:
            ax1.text(
                0.5,
                0.5,
                "No iteration data available",
                ha="center",
                va="center",
                fontsize=14,
                transform=ax1.transAxes,
            )
            ax1.axis("off")

        # Plot 2: Progress distributions
        progress_stats = idea_characterization.get("progress_stats", {})
        progress_distribution = progress_stats.get("progress_distribution", {})

        if progress_distribution:
            # Extract data
            progress_levels = []
            counts = []

            for level, count in sorted(
                progress_distribution.items(),
                key=lambda item: (
                    int(item[0])
                    if isinstance(item[0], str) and item[0].isdigit()
                    else (int(float(item[0])) if isinstance(item[0], str) else item[0])
                ),
            ):
                progress_levels.append(f"{level}%")
                counts.append(count)

            # Create bar chart
            color_map = plt.cm.get_cmap("viridis")
            progress_values = [int(p.replace("%", "")) for p in progress_levels]
            normalized_values = [p / 100 for p in progress_values]
            colors = [color_map(v) for v in normalized_values]

            bars2 = ax2.bar(progress_levels, counts, color=colors)

            # Add value labels
            self.add_value_labels(ax2, bars2)

            ax2.set_title("Idea Progress Distribution", fontsize=14)
            ax2.set_xlabel("Progress Level", fontsize=12)
            ax2.set_ylabel("Number of Ideas", fontsize=12)
            ax2.tick_params(axis="x", rotation=45)
        else:
            ax2.text(
                0.5,
                0.5,
                "No progress distribution data available",
                ha="center",
                va="center",
                fontsize=14,
                transform=ax2.transAxes,
            )
            ax2.axis("off")

        # Add overall metrics
        avg_progress = progress_stats.get("avg_progress", 0)
        fig.text(
            0.5,
            0.01,
            f"Average Overall Progress: {avg_progress:.1f}%",
            ha="center",
            fontsize=12,
            bbox={"facecolor": "lightyellow", "alpha": 0.8, "pad": 5},
        )

        plt.tight_layout(rect=[0, 0.03, 1, 0.97])

        # Save and return
        return self.save_figure(filename)

    def _visualize_framework_usage(
        self, framework_usage: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of framework usage data.

        Args:
            framework_usage: Framework usage data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Check if necessary data exists
        framework_counts = framework_usage.get("framework_counts", {})

        if not framework_counts:
            return None

        # Extract data
        frameworks = []
        counts = []

        for framework, count in framework_counts.items():
            if count > 0:
                # Format framework name for display
                if framework == "disciplined-entrepreneurship":
                    framework_name = "Disciplined Entrepreneurship"
                elif framework == "startup-tactics":
                    framework_name = "Startup Tactics"
                else:
                    framework_name = framework.replace("-", " ").title()

                frameworks.append(framework_name)
                counts.append(count)

        # Define colors for frameworks
        colors = ["dodgerblue", "darkorange", "mediumseagreen", "lightgray"]
        if len(frameworks) > len(colors):
            colors = self.get_color_gradient(len(frameworks), "categorical")

        # Create pie chart
        fig = self.setup_figure(figsize=(10, 8), title="Framework Usage Distribution")

        plt.pie(
            counts,
            labels=frameworks,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors[: len(frameworks)],
            shadow=True,
            wedgeprops={"edgecolor": "w", "linewidth": 1},
        )

        # Add legend with counts
        legend_labels = [
            f"{framework} ({count})" for framework, count in zip(frameworks, counts)
        ]
        plt.legend(legend_labels, loc="best", bbox_to_anchor=(1, 0.5))

        # Equal aspect ratio ensures the pie chart is circular
        plt.axis("equal")
        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_timeline(
        self, timeline_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of timeline data.

        Args:
            timeline_data: Timeline data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Check if daily or monthly data exists
        daily_counts = timeline_data.get("daily_counts", {})
        monthly_stats = timeline_data.get("monthly_stats", {})

        if not daily_counts and not monthly_stats:
            return None

        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        # Plot 1: Daily idea counts if available
        if daily_counts and len(daily_counts) >= 5:
            # Extract data
            dates = []
            idea_counts = []

            for date_str, data in sorted(daily_counts.items()):
                date_obj = DateUtils.parse_date(date_str)
                if date_obj:
                    dates.append(date_obj)
                    idea_counts.append(data.get("count", 0))

            # Create line chart
            ax1.plot(
                dates,
                idea_counts,
                marker="o",
                linestyle="-",
                color="royalblue",
                linewidth=2,
                markersize=6,
                alpha=0.8,
            )

            # Format x-axis as dates
            self.format_date_axis(ax1, date_format="%Y-%m-%d", interval=7)

            ax1.set_title("Daily Idea Creation", fontsize=14)
            ax1.set_ylabel("Number of Ideas", fontsize=12)
            ax1.grid(True, linestyle="--", alpha=0.7)
        else:
            ax1.text(
                0.5,
                0.5,
                "Insufficient daily data available",
                ha="center",
                va="center",
                fontsize=14,
                transform=ax1.transAxes,
            )
            ax1.axis("off")

        # Plot 2: Monthly statistics if available
        if monthly_stats and len(monthly_stats) >= 2:
            # Extract data
            months = []
            total_ideas = []
            avg_ideas_per_day = []

            for month_str, data in sorted(monthly_stats.items()):
                date_obj = DateUtils.parse_date(
                    f"{month_str}-01"
                )  # Add day to create valid date
                if date_obj:
                    months.append(date_obj)
                    total_ideas.append(data.get("total_ideas", 0))
                    avg_ideas_per_day.append(data.get("avg_ideas_per_day", 0))

            # Plot monthly total ideas as a bar chart
            bars = ax2.bar(months, total_ideas, color="mediumseagreen", alpha=0.7)

            # Format x-axis as dates
            self.format_date_axis(ax2)

            # Add trend line
            self.add_trend_line(ax2, months, total_ideas, "Trend")

            ax2.set_title("Monthly Total Ideas", fontsize=14)
            ax2.set_xlabel("Month", fontsize=12)
            ax2.set_ylabel("Number of Ideas", fontsize=12)
            ax2.grid(True, linestyle="--", alpha=0.7)
            ax2.legend()
        else:
            ax2.text(
                0.5,
                0.5,
                "Insufficient monthly data available",
                ha="center",
                va="center",
                fontsize=14,
                transform=ax2.transAxes,
            )
            ax2.axis("off")

        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_view_action_correlation(
        self, correlation_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of view-to-action correlation analysis.

        Args:
            correlation_data: View-action correlation data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have sufficient data
            if not correlation_data or "interval_distribution" not in correlation_data:
                self.logger.warning(
                    "Insufficient data for view-action correlation visualization"
                )
                return None

            # Create multiple visualizations
            outputs = {}

            # 1. Interval Distribution Visualization
            interval_plot = self._visualize_interval_distribution(
                correlation_data, f"{filename}_intervals"
            )
            if interval_plot:
                outputs["interval_distribution"] = interval_plot

            # 2. Session Analysis Visualization
            session_plot = self._visualize_session_analysis(
                correlation_data, f"{filename}_sessions"
            )
            if session_plot:
                outputs["session_analysis"] = session_plot

            # 3. User Engagement Patterns
            patterns_plot = self._visualize_user_patterns(
                correlation_data, f"{filename}_patterns"
            )
            if patterns_plot:
                outputs["user_patterns"] = patterns_plot

            # Return the primary visualization path or None if none were created
            return interval_plot if interval_plot else None

        except Exception as e:
            self.logger.error(
                f"Error creating view-action correlation visualization: {str(e)}"
            )
            plt.close("all")  # Close any open figures
            return None

    def _visualize_interval_distribution(
        self, correlation_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of interval distribution between views and actions.

        Args:
            correlation_data: View-action correlation data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Extract interval distribution data
            interval_distribution = correlation_data.get("interval_distribution", {})
            if not interval_distribution:
                return None

            # Create figure
            fig = self.setup_figure(
                figsize=(12, 8),
                title="Time Between Views and Actions",
                xlabel="Time Interval",
                ylabel="Number of Actions",
            )

            # Define time interval order (from shortest to longest)
            interval_order = [
                "< 1 min",
                "1-5 min",
                "5-15 min",
                "15-30 min",
                "30-60 min",
                "1-2 hours",
                "2-24 hours",
                "> 24 hours",
            ]

            # Filter to intervals that exist in our data
            labels = [
                label for label in interval_order if label in interval_distribution
            ]
            values = [interval_distribution.get(label, 0) for label in labels]

            # Create color gradient based on time (shorter times = darker colors)
            colors = self.get_color_gradient(len(labels), "viridis")

            # Create bar chart
            bars = plt.bar(labels, values, color=colors)

            # Add value labels
            self.add_value_labels(plt.gca(), bars)

            # Add interval statistics as text annotation
            interval_stats = correlation_data.get("interval_stats", {})
            if interval_stats:
                stats_text = (
                    f"Mean Interval: {interval_stats.get('mean', 0)/60:.1f} min\n"
                    f"Median Interval: {interval_stats.get('median', 0)/60:.1f} min\n"
                    f"Immediate Actions: {interval_stats.get('immediate_action_percentage', 0):.1f}%"
                )
                plt.annotate(
                    stats_text,
                    xy=(0.02, 0.95),
                    xycoords="axes fraction",
                    bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", alpha=0.8),
                    verticalalignment="top",
                    fontsize=10,
                )

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha="right")

            # Highlight immediate action threshold
            threshold_mins = (
                correlation_data.get("immediate_action_threshold", 300) / 60
            )
            plt.axvline(
                x=-0.5 + labels.index("1-5 min") if "1-5 min" in labels else 0,
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f"Immediate Action Threshold ({threshold_mins:.0f} min)",
            )

            plt.legend()
            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            self.logger.error(
                f"Error creating interval distribution visualization: {str(e)}"
            )
            plt.close()
            return None

    def _visualize_session_analysis(
        self, correlation_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of session-based analysis.

        Args:
            correlation_data: View-action correlation data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if session data exists
            session_stats = correlation_data.get("session_stats", {})
            if not session_stats:
                return None

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

            # First subplot: Session composition
            if (
                "avg_views_per_session" in session_stats
                and "avg_actions_per_session" in session_stats
            ):
                # Data for stacked bar chart
                session_composition = [
                    session_stats["avg_views_per_session"],
                    session_stats["avg_actions_per_session"],
                ]

                # Create stacked bar
                ax1.bar(
                    ["Average Session"],
                    [session_composition[0]],
                    color="cornflowerblue",
                    label="Views",
                )
                ax1.bar(
                    ["Average Session"],
                    [session_composition[1]],
                    bottom=[session_composition[0]],
                    color="coral",
                    label="Actions",
                )

                # Add labels
                ax1.set_title("Average Session Composition", fontsize=14)
                ax1.set_ylabel("Count", fontsize=12)

                # Add text labels on bars
                ax1.text(
                    0,
                    session_composition[0] / 2,
                    f"{session_composition[0]:.1f} views",
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )

                ax1.text(
                    0,
                    session_composition[0] + session_composition[1] / 2,
                    f"{session_composition[1]:.1f} actions",
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )

                ax1.legend()

            # Second subplot: Session duration distribution
            sessions = correlation_data.get("sessions", [])
            if sessions:
                # Get session durations in minutes
                durations = [s["duration"] / 60 for s in sessions]

                # Define bins
                max_duration = min(
                    max(durations), 120
                )  # Cap at 2 hours for readability
                bins = np.linspace(0, max_duration, 20)

                # Create histogram
                ax2.hist(
                    durations,
                    bins=bins,
                    color="mediumseagreen",
                    alpha=0.7,
                    edgecolor="black",
                    linewidth=1,
                )

                # Add mean line
                mean_duration = session_stats.get("avg_session_duration", 0) / 60
                ax2.axvline(
                    mean_duration,
                    color="red",
                    linestyle="--",
                    label=f"Mean: {mean_duration:.1f} min",
                )

                # Add labels
                ax2.set_title("Session Duration Distribution", fontsize=14)
                ax2.set_xlabel("Duration (minutes)", fontsize=12)
                ax2.set_ylabel("Number of Sessions", fontsize=12)
                ax2.legend()

            # Add overall title
            fig.suptitle("User Session Analysis", fontsize=16)

            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for main title

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            self.logger.error(
                f"Error creating session analysis visualization: {str(e)}"
            )
            plt.close()
            return None

    def _visualize_user_patterns(
        self, correlation_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user engagement patterns.

        Args:
            correlation_data: View-action correlation data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if user pattern data exists
            user_patterns = correlation_data.get("user_patterns", {})
            if not user_patterns:
                return None

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

            # Extract user metrics for scatter plot
            view_counts = []
            action_counts = []

            for email, data in user_patterns.items():
                view_count = data.get("view_count", 0)
                action_count = data.get("idea_count", 0) + data.get("step_count", 0)

                view_counts.append(view_count)
                action_counts.append(action_count)

            # First plot: Scatter plot of views vs actions
            if view_counts and action_counts:
                # Create scatter plot with transparency for overlapping points
                ax1.scatter(
                    view_counts,
                    action_counts,
                    alpha=0.5,
                    color="royalblue",
                    edgecolors="navy",
                )

                # Add trend line
                if len(view_counts) > 1:
                    z = np.polyfit(view_counts, action_counts, 1)
                    p = np.poly1d(z)

                    # Generate points for trend line
                    x_trend = np.linspace(min(view_counts), max(view_counts), 100)
                    y_trend = p(x_trend)

                    # Plot trend line
                    ax1.plot(
                        x_trend,
                        y_trend,
                        "r--",
                        label=f"Trend: y = {z[0]:.2f}x + {z[1]:.2f}",
                    )

                    # Calculate and show correlation
                    correlation = np.corrcoef(view_counts, action_counts)[0, 1]
                    ax1.text(
                        0.05,
                        0.95,
                        f"Correlation: {correlation:.2f}",
                        transform=ax1.transAxes,
                        verticalalignment="top",
                        bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
                    )

                # Add labels
                ax1.set_title("Views vs. Actions by User", fontsize=14)
                ax1.set_xlabel("Number of Views", fontsize=12)
                ax1.set_ylabel("Number of Actions", fontsize=12)

                # Add diagonal line (1:1 ratio)
                max_val = max(max(view_counts), max(action_counts))
                ax1.plot([0, max_val], [0, max_val], "k--", alpha=0.3)

                # Add legend if we have a trend line
                if len(view_counts) > 1:
                    ax1.legend()

            # Second plot: User typology (stacked bar of view/action ratios)
            # Classify users based on view-to-action ratio
            user_types = {
                "Viewers (>5:1)": 0,  # Many views, few actions
                "Balanced (2-5:1)": 0,  # Balanced views and actions
                "Doers (<2:1)": 0,  # Few views, many actions
                "Inactive (0 actions)": 0,  # No actions
            }

            for email, data in user_patterns.items():
                view_count = data.get("view_count", 0)
                action_count = data.get("idea_count", 0) + data.get("step_count", 0)

                if action_count == 0:
                    user_types["Inactive (0 actions)"] += 1
                elif view_count / action_count > 5:
                    user_types["Viewers (>5:1)"] += 1
                elif view_count / action_count >= 2:
                    user_types["Balanced (2-5:1)"] += 1
                else:
                    user_types["Doers (<2:1)"] += 1

            # Create pie chart of user types
            labels = list(user_types.keys())
            sizes = list(user_types.values())

            # Use a custom colormap
            colors = ["lightcoral", "goldenrod", "mediumseagreen", "lightgray"]

            ax2.pie(
                sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors
            )
            ax2.axis("equal")  # Equal aspect ratio ensures circular pie
            ax2.set_title("User Engagement Typology", fontsize=14)

            # Add overall title
            fig.suptitle("User Engagement Patterns", fontsize=16)

            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for main title

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            self.logger.error(f"Error creating user patterns visualization: {str(e)}")
            plt.close()
            return None

    def _visualize_process_flow(
        self, process_flow: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of process flow analysis.

        Args:
            process_flow: Process flow analysis data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have process flow data
            if not process_flow or "global_transition_matrix" not in process_flow:
                self.logger.warning("Insufficient data for process flow visualization")
                return None

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

            # 1. Transition Matrix Heatmap
            transition_matrix = process_flow.get("global_transition_matrix", {})

            if transition_matrix:
                # Extract from/to types
                all_types = set()
                for from_type in transition_matrix:
                    all_types.add(from_type)
                    for to_type in transition_matrix[from_type]:
                        all_types.add(to_type)

                # Convert to sorted list
                sorted_types = sorted(all_types)

                # Create matrix for heatmap
                matrix_size = len(sorted_types)
                heatmap_data = np.zeros((matrix_size, matrix_size))

                # Fill matrix
                for i, from_type in enumerate(sorted_types):
                    for j, to_type in enumerate(sorted_types):
                        if (
                            from_type in transition_matrix
                            and to_type in transition_matrix[from_type]
                        ):
                            heatmap_data[i, j] = transition_matrix[from_type][to_type]

                # Create heatmap
                im = ax1.imshow(heatmap_data, cmap="Blues")

                # Add colorbar
                cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
                cbar.set_label("Transition Probability", fontsize=10)

                # Set tick labels
                ax1.set_xticks(np.arange(matrix_size))
                ax1.set_yticks(np.arange(matrix_size))
                ax1.set_xticklabels(sorted_types)
                ax1.set_yticklabels(sorted_types)

                # Rotate x tick labels
                plt.setp(
                    ax1.get_xticklabels(),
                    rotation=45,
                    ha="right",
                    rotation_mode="anchor",
                )

                # Add grid
                for edge, spine in ax1.spines.items():
                    spine.set_visible(False)

                ax1.set_xticks(np.arange(matrix_size + 1) - 0.5, minor=True)
                ax1.set_yticks(np.arange(matrix_size + 1) - 0.5, minor=True)
                ax1.grid(which="minor", color="w", linestyle="-", linewidth=2)

                # Add title
                ax1.set_title("Transition Probabilities Between Actions", fontsize=14)
                ax1.set_xlabel("To Action", fontsize=12)
                ax1.set_ylabel("From Action", fontsize=12)

            # 2. Common Sequences Bar Chart
            common_paths = process_flow.get("most_common_full_paths", {})

            if common_paths:
                # Get top paths
                paths = list(common_paths.keys())[:6]  # Limit to top 6 for readability
                counts = [common_paths[p] for p in paths]

                # Create bar chart
                bars = ax2.barh(paths, counts, color="mediumseagreen")

                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    ax2.text(
                        width + 0.3,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(width)}",
                        ha="left",
                        va="center",
                    )

                ax2.set_title("Most Common Action Paths", fontsize=14)
                ax2.set_xlabel("Frequency", fontsize=12)

            # Add overall title
            fig.suptitle("User Process Flow Analysis", fontsize=16)

            plt.tight_layout(rect=[0, 0, 1, 0.95])

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            self.logger.error(f"Error creating process flow visualization: {str(e)}")
            plt.close()
            return None

"""
Course evaluation visualizer for data analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("course_eval_visualizer")


class CourseEvaluationVisualizer(BaseVisualizer):
    """Visualizes course evaluation analysis results."""

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for course evaluation analysis.

        Args:
            data: Course evaluation analysis results

        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            "semester_comparison": (
                self._visualize_semester_comparison,
                {"data_key": "semester_comparison"},
            ),
            "tool_impact": (self._visualize_tool_impact, {"data_key": "tool_impact"}),
            "section_performance": (
                self._visualize_section_performance,
                {"data_key": "section_analysis"},
            ),
            "key_questions": (
                self._visualize_key_questions,
                {"data_key": "question_analysis"},
            ),
            "rating_trends": (
                self._visualize_rating_trends,
                {"data_key": "trend_analysis"},
            ),
            "time_spent": (
                self._visualize_time_spent,
                {"data_key": "time_spent_analysis"},
            ),
            "overall_rating": (
                self._visualize_overall_rating,
                {"data_key": "overall_rating_analysis"},
            ),
            "rating_time_correlation": (
                self._visualize_rating_time_correlation,
                {"data_key": "overall_rating_analysis.correlation_with_time"},
            ),
        }

        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_semester_comparison(
        self, comparison_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of semester comparison.

        Args:
            comparison_data: Semester comparison data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Extract data
            semesters = comparison_data.get("display_names", [])
            overall_avg = comparison_data.get("overall_avg", [])
            tool_versions = comparison_data.get("tool_versions", [])

            if not semesters or not overall_avg:
                logger.warning(
                    "Insufficient data for semester comparison visualization"
                )
                return None

            # Create figure
            fig = self.setup_figure(
                figsize=(12, 8),
                title="Overall Evaluation Scores by Semester",
                ylabel="Average Score",
            )

            # Define colors based on tool version
            colors = [self.get_tool_color(v) for v in tool_versions]

            # Create bar chart
            bars = plt.bar(semesters, overall_avg, color=colors)

            # Add value labels on top of bars
            self.add_value_labels(plt.gca(), bars, "{:.2f}")

            # Add tool version annotations
            for i, version in enumerate(tool_versions):
                tool_label = "No Tool" if version is None else f"Jetpack {version}"
                plt.annotate(
                    tool_label,
                    (i, 0.2),
                    xytext=(0, -20),
                    textcoords="offset points",
                    ha="center",
                    rotation=45,
                )

            # Add term comparison if available
            term_comparisons = comparison_data.get("term_comparisons", {})
            fall_avg = term_comparisons.get("fall_avg")
            spring_avg = term_comparisons.get("spring_avg")

            if fall_avg is not None and spring_avg is not None:
                # Add a horizontal line for fall and spring averages
                plt.axhline(
                    y=fall_avg,
                    color="orange",
                    linestyle="--",
                    label=f"Fall Avg: {fall_avg:.2f}",
                )
                plt.axhline(
                    y=spring_avg,
                    color="green",
                    linestyle="--",
                    label=f"Spring Avg: {spring_avg:.2f}",
                )
                plt.legend()

            plt.ylim(0, max(overall_avg) * 1.2)  # Add some space at the top
            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating semester comparison visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_tool_impact(
        self, impact_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of tool impact.

        Args:
            impact_data: Tool impact data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check for necessary data
            version_metrics = impact_data.get("version_metrics", {})
            seasonal_impact = impact_data.get("seasonal_impact", {})

            if not version_metrics:
                logger.warning("Insufficient data for tool impact visualization")
                return None

            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))

            # Extract data for overall comparison
            tool_versions = []
            avg_scores = []
            num_semesters = []

            for version, metrics in sorted(
                version_metrics.items(), key=lambda item: (item[0] is not None, item[0])
            ):
                # Format the version name
                version_name = "No Tool" if not version else f"Jetpack {version}"

                tool_versions.append(version_name)
                avg_scores.append(metrics.get("avg_score", 0))
                num_semesters.append(metrics.get("num_semesters", 0))

            # Define colors for tool versions
            colors = [
                self.get_tool_color(
                    v.replace("Jetpack ", "") if "Jetpack" in v else None
                )
                for v in tool_versions
            ]

            # Plot 1: Overall comparison by tool version
            bars1 = ax1.bar(tool_versions, avg_scores, color=colors)

            # Add value labels
            self.add_value_labels(ax1, bars1, "{:.2f}")

            # Add semester count annotation
            for i, count in enumerate(num_semesters):
                ax1.text(
                    i,
                    0.2,
                    f"{count} semester(s)",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                )

            ax1.set_title("Average Evaluation Score by Tool Version", fontsize=16)
            ax1.set_ylabel("Average Score", fontsize=12)
            ax1.set_ylim(0, max(avg_scores) * 1.2)  # Add some space at the top

            # Plot 2: Seasonal comparison by tool version
            if seasonal_impact:
                tool_versions_seasonal = []
                fall_avgs = []
                spring_avgs = []

                for version, metrics in sorted(
                    seasonal_impact.items(),
                    key=lambda item: (item[0] is not None, item[0]),
                ):
                    # Format the version name
                    version_name = (
                        "No Tool" if version == "none" else f"Jetpack {version}"
                    )

                    fall_avg = metrics.get("fall_avg")
                    spring_avg = metrics.get("spring_avg")

                    if fall_avg is not None or spring_avg is not None:
                        tool_versions_seasonal.append(version_name)
                        fall_avgs.append(fall_avg if fall_avg is not None else 0)
                        spring_avgs.append(spring_avg if spring_avg is not None else 0)

                # Set width for grouped bars
                if tool_versions_seasonal:
                    x = np.arange(len(tool_versions_seasonal))
                    width = 0.35

                    # Create grouped bar chart
                    ax2.bar(
                        x - width / 2, fall_avgs, width, label="Fall", color="orange"
                    )
                    ax2.bar(
                        x + width / 2, spring_avgs, width, label="Spring", color="green"
                    )

                    # Add labels and title
                    ax2.set_xlabel("Tool Version", fontsize=12)
                    ax2.set_ylabel("Average Score", fontsize=12)
                    ax2.set_title(
                        "Fall vs Spring Comparison by Tool Version", fontsize=16
                    )
                    ax2.set_xticks(x)
                    ax2.set_xticklabels(tool_versions_seasonal)
                    ax2.legend()

                    # Add annotations for missing data
                    for i, (fall, spring) in enumerate(zip(fall_avgs, spring_avgs)):
                        if fall == 0:
                            ax2.text(
                                i - width / 2,
                                0.5,
                                "No data",
                                ha="center",
                                va="bottom",
                                color="gray",
                                fontsize=10,
                            )
                        if spring == 0:
                            ax2.text(
                                i + width / 2,
                                0.5,
                                "No data",
                                ha="center",
                                va="bottom",
                                color="gray",
                                fontsize=10,
                            )
                else:
                    ax2.text(
                        0.5,
                        0.5,
                        "Insufficient data for seasonal comparison",
                        ha="center",
                        va="center",
                        fontsize=14,
                        transform=ax2.transAxes,
                    )
                    ax2.axis("off")
            else:
                ax2.text(
                    0.5,
                    0.5,
                    "No seasonal data available",
                    ha="center",
                    va="center",
                    fontsize=14,
                    transform=ax2.transAxes,
                )
                ax2.axis("off")

            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating tool impact visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_section_performance(
        self, section_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of section performance.

        Args:
            section_data: Section performance data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Extract data
            sections = section_data.get("sections", [])
            semester_data = section_data.get("by_semester", {})

            if not sections or not semester_data:
                logger.warning(
                    "Insufficient data for section performance visualization"
                )
                return None

            # Sort semesters by year and then by order (Spring then Fall)
            # Create a list of tuples (code, year, order) for sorting
            semester_sort_data = []
            for semester_code, data in semester_data.items():
                year = data.get("year", 0)  # Extract year if available
                # Extract order, using a default ordering where needed
                if "order" in data:
                    order = data["order"]
                else:
                    # If order is not specified, infer from term (Spring=1, Fall=2)
                    order = 1 if data.get("term", "").lower() == "spring" else 2

                semester_sort_data.append((semester_code, year, order))

            # Sort by year (ascending) and then by order (ascending)
            sorted_semester_data = sorted(
                semester_sort_data, key=lambda x: (x[1], x[2])
            )

            # Extract just the sorted semester codes
            sorted_semesters = [code for code, _, _ in sorted_semester_data]

            # Create a heatmap of section scores by semester
            section_scores = np.zeros((len(sections), len(sorted_semesters)))
            section_scores.fill(np.nan)  # Fill with NaN for missing data

            # Fill in available data
            for i, section in enumerate(sections):
                for j, semester in enumerate(sorted_semesters):
                    section_averages = semester_data[semester].get(
                        "section_averages", {}
                    )
                    if section in section_averages:
                        section_scores[i, j] = section_averages[section]

            # Prepare display names for x-axis labels
            x_labels = [
                semester_data[s].get("display_name", s) for s in sorted_semesters
            ]

            # Create heatmap
            result = self.create_heatmap(
                data=section_scores,
                row_labels=sections,
                col_labels=x_labels,
                filename=filename,
                title="Section Performance by Semester",
                cmap="viridis",
                add_values=True,
            )

            # Add tool version annotations
            if result:
                for i, semester in enumerate(sorted_semesters):
                    tool_version = semester_data[semester].get("tool_version")
                    if tool_version is not None:
                        tool_label = f"({tool_version})"
                    elif tool_version is None:
                        tool_label = "(no tool)"
                    else:
                        tool_label = ""

                    if tool_label:
                        plt.annotate(
                            tool_label,
                            (i, -0.5),
                            xytext=(0, -15),
                            textcoords="offset points",
                            ha="center",
                            fontsize=9,
                        )

                plt.tight_layout()
                result = self.save_figure(filename)  # Re-save with annotations

            return result

        except Exception as e:
            logger.error(f"Error creating section performance visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_key_questions(
        self, question_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of key question responses.

        Args:
            question_data: Key question analysis data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            if not question_data:
                logger.warning("No key question data to visualize")
                return None

            # Determine number of categories to visualize
            categories = list(question_data.keys())
            num_categories = len(categories)

            if num_categories == 0:
                return None

            # Create figure with subplots - one per category
            fig, axes = plt.subplots(
                num_categories, 1, figsize=(12, 5 * num_categories)
            )

            # Handle case of single category
            if num_categories == 1:
                axes = [axes]

            # Process each category
            for i, category in enumerate(categories):
                category_data = question_data[category]
                semester_data = category_data.get("semesters", {})

                if not semester_data:
                    axes[i].text(
                        0.5,
                        0.5,
                        f"No data for {category}",
                        ha="center",
                        va="center",
                        transform=axes[i].transAxes,
                    )
                    axes[i].set_title(category.replace("_", " ").title(), fontsize=14)
                    axes[i].axis("off")
                    continue

                # Sort semesters chronologically
                sorted_semesters = sorted(semester_data.keys())
                x_labels = [
                    semester_data[s].get("display_name", s) for s in sorted_semesters
                ]
                scores = [
                    semester_data[s].get("avg_score", 0) for s in sorted_semesters
                ]
                tool_versions = [
                    semester_data[s].get("tool_version") for s in sorted_semesters
                ]

                # Define colors based on tool version
                colors = [self.get_tool_color(v) for v in tool_versions]

                # Create bar chart
                bars = axes[i].bar(x_labels, scores, color=colors)

                # Add value labels on top of bars
                self.add_value_labels(axes[i], bars, "{:.2f}")

                # Add tool version annotations
                for j, version in enumerate(tool_versions):
                    tool_label = "No Tool" if version is None else f"Jetpack {version}"
                    axes[i].annotate(
                        tool_label,
                        (j, 0.2),
                        xytext=(0, -15),
                        textcoords="offset points",
                        ha="center",
                        rotation=45,
                        fontsize=8,
                    )

                # Format category name for title
                category_title = category.replace("_", " ").title()
                axes[i].set_title(f"{category_title} Questions", fontsize=14)
                axes[i].set_ylabel("Average Score", fontsize=12)
                axes[i].set_ylim(
                    0, max(scores) * 1.2 if scores else 7
                )  # Add some space at the top

            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating key questions visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_rating_trends(
        self, trend_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of rating trends over time.

        Args:
            trend_data: Rating trend data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check for timeline data
            timeline = trend_data.get("timeline", [])
            if not timeline:
                logger.warning("No timeline data for rating trends visualization")
                return None

            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

            # Extract data for overall trend
            semester_labels = [item.get("display_name", "") for item in timeline]
            overall_scores = [item.get("overall_avg", 0) for item in timeline]
            tool_versions = [item.get("tool_version") for item in timeline]
            terms = [item.get("term", "") for item in timeline]

            # Define colors based on term
            term_colors = ["orange" if term == "fall" else "green" for term in terms]

            # Plot 1: Overall trend with term highlighting
            ax1.plot(
                semester_labels,
                overall_scores,
                "o-",
                color="navy",
                linewidth=2,
                markersize=8,
            )

            # Add colored markers for terms
            for i, (score, color) in enumerate(zip(overall_scores, term_colors)):
                ax1.plot(i, score, "o", color=color, markersize=12, alpha=0.5)

            # Add tool version annotations
            for i, version in enumerate(tool_versions):
                tool_label = "No Tool" if version is None else f"Jetpack {version}"
                ax1.annotate(
                    tool_label,
                    (i, min(overall_scores) - 0.2),
                    xytext=(0, -20),
                    textcoords="offset points",
                    ha="center",
                    fontsize=10,
                )

            # Highlight tool version changes
            self.highlight_tool_changes(ax1, tool_versions)

            ax1.set_title("Overall Evaluation Score Trend", fontsize=16)
            ax1.set_ylabel("Average Score", fontsize=12)
            ax1.set_ylim(
                min(overall_scores) * 0.9 if overall_scores else 0,
                max(overall_scores) * 1.1 if overall_scores else 7,
            )

            # Add legend for terms
            fall_patch = plt.Line2D(
                [0],
                [0],
                marker="o",
                color="white",
                markerfacecolor="orange",
                markersize=10,
                label="Fall",
            )
            spring_patch = plt.Line2D(
                [0],
                [0],
                marker="o",
                color="white",
                markerfacecolor="green",
                markersize=10,
                label="Spring",
            )
            tool_change = plt.Line2D(
                [0], [0], color="red", linestyle="--", label="Tool Version Change"
            )

            ax1.legend(
                handles=[fall_patch, spring_patch, tool_change], loc="lower right"
            )

            # Plot 2: Semester-to-semester changes
            changes = trend_data.get("changes", [])
            if changes:
                change_labels = [
                    f"{change.get('from_semester', '')} → {change.get('to_semester', '')}"
                    for change in changes
                ]
                change_values = [change.get("change", 0) for change in changes]

                # Color based on direction and tool change
                change_colors = []
                for change in changes:
                    if change.get("tool_change", False):
                        # Tool change - use purple for highlighting
                        change_colors.append("purple")
                    elif change.get("change", 0) > 0:
                        # Positive change - green
                        change_colors.append("green")
                    else:
                        # Negative change - red
                        change_colors.append("red")

                # Create bar chart
                bars = ax2.bar(
                    change_labels, change_values, color=change_colors, alpha=0.7
                )

                # Add value labels
                self.add_value_labels(ax2, bars, "{:.2f}")

                ax2.set_title("Semester-to-Semester Changes", fontsize=16)
                ax2.set_ylabel("Score Change", fontsize=12)

                # Add a horizontal line at y=0
                ax2.axhline(y=0, color="black", linestyle="-", alpha=0.3)

                # Annotate tool version changes
                for i, change in enumerate(changes):
                    if change.get("tool_change", False):
                        from_tool = (
                            "No Tool"
                            if change.get("from_tool") is None
                            else f"Jetpack {change.get('from_tool')}"
                        )
                        to_tool = (
                            "No Tool"
                            if change.get("to_tool") is None
                            else f"Jetpack {change.get('to_tool')}"
                        )

                        ax2.annotate(
                            f"{from_tool} → {to_tool}",
                            (i, 0),
                            xytext=(0, -30 if change.get("change", 0) > 0 else 20),
                            textcoords="offset points",
                            ha="center",
                            fontsize=9,
                            bbox=dict(
                                boxstyle="round,pad=0.3",
                                fc="lavender",
                                ec="purple",
                                alpha=0.8,
                            ),
                        )
            else:
                ax2.text(
                    0.5,
                    0.5,
                    "Insufficient data for change analysis",
                    ha="center",
                    va="center",
                    fontsize=14,
                    transform=ax2.transAxes,
                )
                ax2.axis("off")

            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating rating trends visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_time_spent(
        self, time_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of time spent on the course.

        Args:
            time_data: Time spent analysis data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have data on total time spent
            by_semester = time_data.get("by_semester", {})

            if not by_semester:
                logger.warning("No semester data for time spent visualization")
                return None

            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

            # Sort semesters chronologically
            sorted_semesters = sorted(by_semester.keys())
            semester_data = [by_semester[s] for s in sorted_semesters]

            # Extract data for visualization
            semester_labels = [data.get("display_name", "") for data in semester_data]
            classroom_times = [data.get("classroom_time", 0) for data in semester_data]
            outside_times = [data.get("outside_time", 0) for data in semester_data]
            total_times = [data.get("total_time", 0) for data in semester_data]
            tool_versions = [data.get("tool_version") for data in semester_data]
            terms = [data.get("term", "") for data in semester_data]

            # Define colors based on term
            term_colors = ["orange" if term == "fall" else "green" for term in terms]

            # Plot 1: Stacked bar chart showing classroom vs outside time
            bar_width = 0.7

            # Create bars for classroom time
            bars1 = ax1.bar(
                semester_labels,
                classroom_times,
                bar_width,
                label="Classroom Time",
                color="lightblue",
            )

            # Create bars for outside time, stacked on top of classroom time
            bars2 = ax1.bar(
                semester_labels,
                outside_times,
                bar_width,
                bottom=classroom_times,
                label="Outside Classroom",
                color="coral",
            )

            # Add value labels for total time
            for i, (c_time, o_time) in enumerate(zip(classroom_times, outside_times)):
                total = c_time + o_time
                ax1.text(
                    i,
                    total + 0.3,
                    f"Total: {total:.1f}h",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

                # Add breakdown
                ax1.text(
                    i,
                    c_time / 2,
                    f"{c_time:.1f}h",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=9,
                    fontweight="bold",
                )
                ax1.text(
                    i,
                    c_time + o_time / 2,
                    f"{o_time:.1f}h",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=9,
                    fontweight="bold",
                )

            # Add tool version annotations
            for i, version in enumerate(tool_versions):
                tool_label = "No Tool" if version is None else f"Jetpack {version}"
                ax1.annotate(
                    tool_label,
                    (i, 0.3),
                    xytext=(0, -20),
                    textcoords="offset points",
                    ha="center",
                    fontsize=10,
                )

            # Highlight tool version changes
            self.highlight_tool_changes(ax1, tool_versions)

            # Add trend line for total time
            if len(semester_labels) >= 2:
                x = np.arange(len(semester_labels))

                # Calculate trend line
                z = np.polyfit(x, total_times, 1)
                p = np.poly1d(z)
                trend_line = p(x)

                ax1.plot(x, trend_line, "r--", label=f"Trend (slope: {z[0]:.2f})")

                # Add trend analysis annotation
                if z[0] > 0.2:
                    trend_text = f"↗ Increasing: +{z[0]:.2f} hours/semester"
                    trend_color = (
                        "red"  # Red because increasing time is generally negative
                    )
                elif z[0] < -0.2:
                    trend_text = f"↘ Decreasing: {z[0]:.2f} hours/semester"
                    trend_color = (
                        "green"  # Green because decreasing time is generally positive
                    )
                else:
                    trend_text = f"→ Stable: {z[0]:.2f} hours/semester"
                    trend_color = "black"

                ax1.annotate(
                    trend_text,
                    xy=(0.02, 0.95),
                    xycoords="axes fraction",
                    bbox=dict(
                        boxstyle="round,pad=0.3", fc="white", ec=trend_color, alpha=0.8
                    ),
                    ha="left",
                    fontsize=11,
                    color=trend_color,
                )

            ax1.set_title("Time Spent on Course by Semester", fontsize=16)
            ax1.set_ylabel("Hours per Week", fontsize=12)
            ax1.set_ylim(0, max(total_times) * 1.2 if total_times else 10)
            ax1.legend(loc="upper right")

            # Add text explanation
            ax1.text(
                0.5,
                -0.15,
                "Stacked bars show division between classroom time (bottom) and outside classroom time (top).",
                transform=ax1.transAxes,
                ha="center",
                fontsize=10,
                style="italic",
            )

            # Plot 2: Tool version comparison
            avg_by_tool = time_data.get("avg_by_tool_version", {})

            if avg_by_tool:
                # Extract data
                tool_labels = []
                avg_times = []
                sample_sizes = []

                for version, metrics in sorted(
                    avg_by_tool.items(), key=lambda item: (item[0] is not None, item[0])
                ):
                    # Format version name
                    version_name = (
                        "No Tool" if version == "none" else f"Jetpack {version}"
                    )
                    tool_labels.append(version_name)
                    avg_times.append(metrics.get("avg_time", 0))
                    sample_sizes.append(metrics.get("num_data_points", 0))

                # Define colors
                colors = [
                    self.get_tool_color(
                        v.replace("Jetpack ", "") if "Jetpack" in v else None
                    )
                    for v in tool_labels
                ]

                # Create bar chart
                bars2 = ax2.bar(tool_labels, avg_times, color=colors, width=0.6)

                # Add value labels
                self.add_value_labels(ax2, bars2, "{:.1f}h")

                # Add sample size annotations
                for i, count in enumerate(sample_sizes):
                    ax2.text(
                        i,
                        avg_times[i] * 0.15,
                        f"n={count}",
                        ha="center",
                        va="bottom",
                        color="black",
                        fontsize=9,
                    )

                ax2.set_title("Average Time Spent by Tool Version", fontsize=16)
                ax2.set_ylabel("Hours per Week", fontsize=12)
                ax2.set_ylim(0, max(avg_times) * 1.2 if avg_times else 10)

                # Add percentage change annotations between versions
                for i in range(1, len(tool_labels)):
                    prev_time = avg_times[i - 1]
                    curr_time = avg_times[i]

                    if prev_time > 0:
                        pct_change = (curr_time - prev_time) / prev_time * 100
                        change_text = (
                            f"{pct_change:.1f}% {'↑' if pct_change > 0 else '↓'}"
                        )

                        # Color based on direction - decreasing time is positive
                        color = "green" if pct_change < 0 else "red"

                        x_pos = (i - 1 + i) / 2
                        y_pos = max(prev_time, curr_time) * 1.1

                        ax2.annotate(
                            change_text,
                            (x_pos, y_pos),
                            ha="center",
                            fontsize=11,
                            color=color,
                            weight="bold",
                        )
            else:
                ax2.text(
                    0.5,
                    0.5,
                    "Insufficient data for tool version comparison",
                    ha="center",
                    va="center",
                    fontsize=14,
                    transform=ax2.transAxes,
                )
                ax2.axis("off")

            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating time spent visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_overall_rating(
        self, rating_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of overall rating analysis.

        Args:
            rating_data: Overall rating analysis data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have timeline data
            timeline = rating_data.get("timeline", [])
            if not timeline:
                logger.warning("No timeline data for overall rating visualization")
                return None

            # Sort timeline chronologically
            sorted_timeline = sorted(timeline, key=lambda x: x["semester_code"])

            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

            # Extract data
            semester_labels = [item.get("display_name", "") for item in sorted_timeline]
            rating_values = [item.get("avg_rating", 0) for item in sorted_timeline]
            tool_versions = [item.get("tool_version") for item in sorted_timeline]
            terms = [item.get("term", "") for item in sorted_timeline]

            # Define colors based on term
            term_colors = ["orange" if term == "fall" else "green" for term in terms]
            line_colors = ["#FF8C00" if term == "fall" else "#2E8B57" for term in terms]

            # Plot 1: Overall rating trend with detailed view
            # Connect points only within the same term
            term_segments = []
            current_term = None
            current_segment = []

            for i, term in enumerate(terms):
                if term != current_term:
                    if current_segment:
                        term_segments.append((current_term, current_segment))
                    current_term = term
                    current_segment = [(i, rating_values[i])]
                else:
                    current_segment.append((i, rating_values[i]))

            if current_segment:
                term_segments.append((current_term, current_segment))

            # Plot each term's segment with appropriate color
            for term, segment in term_segments:
                x_vals = [x for x, _ in segment]
                y_vals = [y for _, y in segment]
                x_labels = [semester_labels[x] for x in x_vals]
                color = "#FF8C00" if term == "fall" else "#2E8B57"
                ax1.plot(
                    x_labels,
                    y_vals,
                    "o-",
                    color=color,
                    linewidth=2,
                    alpha=0.8,
                    label=(
                        f"{term.capitalize()} Semesters"
                        if term
                        not in [
                            s[0]
                            for s in term_segments[
                                : term_segments.index((term, segment))
                            ]
                        ]
                        else ""
                    ),
                )

            # Add colored markers for terms
            for i, (rating, color) in enumerate(zip(rating_values, term_colors)):
                ax1.scatter(i, rating, color=color, s=100, zorder=5)

            # Add tool version annotations
            for i, version in enumerate(tool_versions):
                tool_label = "No Tool" if version is None else f"Jetpack {version}"
                ax1.annotate(
                    tool_label,
                    (i, min(rating_values) * 0.97),
                    xytext=(0, -15),
                    textcoords="offset points",
                    ha="center",
                    fontsize=9,
                )

            # Highlight tool version changes
            self.highlight_tool_changes(ax1, tool_versions)

            # Add trend line if available
            if "trend" in rating_data:
                trend = rating_data["trend"]
                slope = trend.get("slope")
                intercept = trend.get("intercept")
                r_squared = trend.get("r_squared")

                if slope is not None and intercept is not None:
                    x = np.arange(len(semester_labels))
                    trend_y = slope * x + intercept
                    ax1.plot(
                        semester_labels,
                        trend_y,
                        "k--",
                        alpha=0.6,
                        label=f"Overall Trend (R² = {r_squared:.2f})",
                    )

                    # Add slope direction annotation
                    if slope > 0:
                        trend_direction = f"↗ Improving: +{slope:.3f} per semester"
                        trend_color = "green"
                    elif slope < 0:
                        trend_direction = f"↘ Declining: {slope:.3f} per semester"
                        trend_color = "red"
                    else:
                        trend_direction = "→ Stable"
                        trend_color = "blue"

                    ax1.annotate(
                        trend_direction,
                        xy=(0.98, 0.05),
                        xycoords="axes fraction",
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            fc="white",
                            ec=trend_color,
                            alpha=0.8,
                        ),
                        ha="right",
                        fontsize=11,
                        color=trend_color,
                        weight="bold",
                    )

            ax1.set_title("Overall Course Rating Trend by Semester", fontsize=16)
            ax1.set_ylabel("Average Rating", fontsize=12)
            ax1.set_xticks(range(len(semester_labels)))
            ax1.set_xticklabels(semester_labels, rotation=45, ha="right")

            # Set reasonable y-axis limits to highlight differences
            y_min = min(rating_values) * 0.95
            y_max = max(rating_values) * 1.05
            ax1.set_ylim(y_min, y_max)

            # Add legend
            ax1.legend(loc="upper left")

            # Plot 2: Tool version comparison
            avg_by_tool = rating_data.get("avg_by_tool_version", {})

            if avg_by_tool:
                # Extract data
                tool_labels = []
                avg_ratings = []
                sample_sizes = []

                for version, metrics in sorted(
                    avg_by_tool.items(), key=lambda item: (item[0] is not None, item[0])
                ):
                    # Format version name
                    version_name = (
                        "No Tool" if version == "none" else f"Jetpack {version}"
                    )
                    tool_labels.append(version_name)
                    avg_ratings.append(metrics.get("avg_rating", 0))
                    sample_sizes.append(metrics.get("num_semesters", 0))

                # Define colors
                bar_colors = [
                    self.get_tool_color(
                        v.replace("Jetpack ", "") if "Jetpack" in v else None
                    )
                    for v in tool_labels
                ]

                # Create bar chart
                bars2 = ax2.bar(tool_labels, avg_ratings, color=bar_colors)

                # Add value labels
                self.add_value_labels(ax2, bars2, "{:.2f}")

                # Add sample size annotations
                for i, count in enumerate(sample_sizes):
                    ax2.text(
                        i,
                        avg_ratings[i] * 0.95,
                        f"n={count}",
                        ha="center",
                        va="bottom",
                        color="black",
                        fontsize=9,
                    )

                ax2.set_title("Average Rating by Tool Version", fontsize=16)
                ax2.set_ylabel("Average Rating", fontsize=12)

                # Set reasonable y-axis limits to highlight differences
                y_min = min(avg_ratings) * 0.95
                y_max = max(avg_ratings) * 1.05
                ax2.set_ylim(y_min, y_max)

                # Add percentage change annotations between versions
                version_changes = rating_data.get("version_changes", [])

                for i, change in enumerate(version_changes):
                    pct_change = change.get("percent_change")
                    if pct_change is not None:
                        change_text = (
                            f"{pct_change:.1f}% {'↑' if pct_change > 0 else '↓'}"
                        )

                        # Position between bars
                        x_pos = i + 0.5
                        y_pos = max(avg_ratings[i], avg_ratings[i + 1]) * 1.03

                        ax2.annotate(
                            change_text,
                            (x_pos, y_pos),
                            ha="center",
                            fontsize=11,
                            color="green" if pct_change > 0 else "red",
                            weight="bold",
                        )
            else:
                ax2.text(
                    0.5,
                    0.5,
                    "Insufficient data for tool version comparison",
                    ha="center",
                    va="center",
                    fontsize=14,
                    transform=ax2.transAxes,
                )
                ax2.axis("off")

            plt.tight_layout()

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating overall rating visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_rating_time_correlation(
        self, correlation_data: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of correlation between time spent and overall rating.

        Args:
            correlation_data: Correlation analysis data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have paired data
            paired_data = correlation_data.get("paired_data", [])
            if not paired_data:
                logger.warning("No paired data for correlation visualization")
                return None

            # Extract data
            time_spent = [item.get("time_spent", 0) for item in paired_data]
            ratings = [item.get("rating", 0) for item in paired_data]
            semesters = [item.get("semester", "") for item in paired_data]
            tool_versions = [item.get("tool_version") for item in paired_data]

            # Create figure
            fig = self.setup_figure(
                figsize=(12, 10),
                title="Correlation: Time Spent vs. Overall Rating",
                xlabel="Average Hours per Week",
                ylabel="Overall Rating",
            )

            # Define colors based on tool version
            colors = [self.get_tool_color(v) for v in tool_versions]

            # Create scatter plot
            scatter = plt.scatter(time_spent, ratings, c=colors, s=100, alpha=0.7)

            # Add semester labels to points
            for i, semester in enumerate(semesters):
                plt.annotate(
                    semester,
                    (time_spent[i], ratings[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=9,
                )

            # Add correlation line if correlation is available
            correlation_info = correlation_data.get("correlation", {})
            correlation = correlation_info.get("correlation")
            direction = correlation_info.get("direction")
            strength = correlation_info.get("strength")

            if correlation is not None:
                # Add trend line
                z = np.polyfit(time_spent, ratings, 1)
                p = np.poly1d(z)
                plt.plot(time_spent, p(time_spent), "r--", alpha=0.7)

                # Add correlation annotation
                plt.annotate(
                    f"Correlation: {correlation:.2f} ({direction} {strength})",
                    xy=(0.05, 0.95),
                    xycoords="axes fraction",
                    bbox=dict(
                        boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8
                    ),
                    ha="left",
                    va="top",
                    fontsize=12,
                )

            # Add legend for tool versions
            handles = [
                plt.Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="lightgray",
                    markersize=10,
                    label="No Tool",
                ),
                plt.Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="lightblue",
                    markersize=10,
                    label="Jetpack v1",
                ),
                plt.Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="cornflowerblue",
                    markersize=10,
                    label="Jetpack v2",
                ),
            ]
            plt.legend(handles=handles, loc="lower right")

            plt.grid(True, linestyle="--", alpha=0.5)

            # Save figure
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating correlation visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

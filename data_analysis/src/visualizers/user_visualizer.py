"""
User visualizer for data analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger, DateUtils

logger = get_logger("user_visualizer")


class UserVisualizer(BaseVisualizer):
    """Visualizes user analysis results."""

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for user analysis.

        Args:
            data: User analysis results

        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            "user_counts": (self._visualize_user_counts, {"data_key": "user_counts"}),
            "affiliations": (
                self._visualize_affiliations,
                {"data_key": "affiliations.affiliation_counts"},
            ),
            "user_types": (
                self._visualize_user_types,
                {"data_key": "cohorts.user_types"},
            ),
            "activity_cohorts": (
                self._visualize_activity_cohorts,
                {"data_key": "cohorts.activity"},
            ),
            "creation_timeline": (
                self._visualize_user_creation,
                {"data_key": "cohorts.creation_dates"},
            ),
            "enrollments": (self._visualize_enrollments, {"data_key": "enrollment"}),
            "top_courses": (
                self._visualize_top_courses,
                {"data_key": "enrollment.top_courses"},
            ),
            "interests": (
                self._visualize_interests,
                {"data_key": "demographics.interests"},
            ),
            "institutions": (
                self._visualize_institutions,
                {"data_key": "institutions.institution_counts"},
            ),
            "demographics": (
                self._visualize_demographics,
                {"data_key": "demographics"},
            ),
        }

        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_affiliations(
        self, affiliations: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user affiliations.

        Args:
            affiliations: Counts by affiliation
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Filter out low-count affiliations and sort by count
        min_count = 3  # Minimum count to include
        sorted_affiliations = sorted(
            [(k, v) for k, v in affiliations.items() if v >= min_count],
            key=lambda x: x[1],
            reverse=True,
        )

        # Limit to top 10 for readability
        if len(sorted_affiliations) > 10:
            sorted_affiliations = sorted_affiliations[:10]

        if not sorted_affiliations:
            return None

        # Extract data
        labels = [item[0].replace("_", " ").title() for item in sorted_affiliations]
        values = [item[1] for item in sorted_affiliations]

        # Create bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Affiliations",
            xlabel="Count",
            horizontal=True,
            color="lightsteelblue",
        )

    def _visualize_user_types(
        self, user_types: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user types.

        Args:
            user_types: Counts by user type
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not user_types:
            return None

        # Filter out very small segments (less than 1% of total)
        total = sum(user_types.values())
        threshold = total * 0.01

        # Combine small segments into "Other"
        significant_types = {}
        other_count = 0

        for key, value in user_types.items():
            if value >= threshold:
                significant_types[key] = value
            else:
                other_count += value

        if other_count > 0:
            significant_types["Other"] = other_count

        # Extract data
        labels = [k.replace("_", " ").title() for k in significant_types.keys()]
        values = list(significant_types.values())

        # Create pie chart
        return self.create_pie_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Types Distribution",
            add_legend=True,
        )

    def _visualize_activity_cohorts(
        self, activity_cohorts: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of activity cohorts.

        Args:
            activity_cohorts: Counts by activity cohort
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not activity_cohorts:
            return None

        # Define custom labels and colors
        label_map = {
            "active_last_30d": "Active (Last 30 Days)",
            "active_31d_90d": "Active (31-90 Days)",
            "active_91d_180d": "Active (91-180 Days)",
            "active_181d_365d": "Active (181-365 Days)",
            "inactive_over_365d": "Inactive (>365 Days)",
        }

        # Extract data in order
        ordered_levels = [
            "active_last_30d",
            "active_31d_90d",
            "active_91d_180d",
            "active_181d_365d",
            "inactive_over_365d",
        ]
        labels = []
        values = []
        colors = []

        for level in ordered_levels:
            if level in activity_cohorts:
                labels.append(label_map.get(level, level.title()))
                values.append(activity_cohorts[level])
                if "active_last_30d" in level:
                    colors.append(self.STANDARD_COLORS["high"])
                elif "active_31d_90d" in level:
                    colors.append(self.STANDARD_COLORS["medium"])
                elif "active_91d_180d" in level or "active_181d_365d" in level:
                    colors.append(self.STANDARD_COLORS["low"])
                else:
                    colors.append("firebrick")

        # Create pie chart
        explode = [0.05] * len(labels)  # Add slight explosion to all slices

        return self.create_pie_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Activity Cohorts",
            colors=colors,
            explode=explode,
        )

    def _visualize_user_creation(
        self, creation_dates: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user creation over time.

        Args:
            creation_dates: Counts by creation date
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Need at least 2 data points for a meaningful timeline
        if len(creation_dates) < 2:
            return None

        # Convert string dates to datetime objects for proper timeline
        dates = []
        counts = []

        for date_str, count in sorted(creation_dates.items()):
            date_obj = DateUtils.parse_date(
                f"{date_str}-01"
            )  # Add day to create valid date
            if date_obj:
                dates.append(date_obj)
                counts.append(count)

        # Create line chart
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Plot line chart for new users
        ax1.plot(
            dates,
            counts,
            marker="o",
            linestyle="-",
            color="royalblue",
            linewidth=2,
            markersize=8,
        )

        # Fill area under the line
        ax1.fill_between(dates, counts, alpha=0.3, color="royalblue")

        # Format x-axis as dates
        self.format_date_axis(ax1)

        # Add title and labels
        ax1.set_title("User Registration Timeline", fontsize=16)
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("New Users", fontsize=12)

        # Add cumulative trendline
        cumulative_counts = np.cumsum(counts)
        ax2 = ax1.twinx()
        ax2.plot(
            dates,
            cumulative_counts,
            linestyle="--",
            color="forestgreen",
            alpha=0.7,
            label="Cumulative Users",
        )
        ax2.set_ylabel("Cumulative Users", fontsize=12, color="forestgreen")
        ax2.tick_params(axis="y", colors="forestgreen")

        # Add grid and legend
        ax1.grid(True, linestyle="--", alpha=0.7)
        ax2.legend(loc="upper left")

        plt.tight_layout()

        # Save and return
        return self.save_figure(filename)

    def _visualize_enrollments(
        self, enrollments: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of enrollment statistics.

        Args:
            enrollments: Enrollment statistics
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not enrollments:
            return None

        # Extract data
        users_with_enrollments = enrollments.get("users_with_enrollments", 0)
        total_enrollments = enrollments.get("total_enrollments", 0)
        avg_enrollments = enrollments.get("avg_enrollments_per_user", 0)

        # Create stats labels
        stats = ["Users With Enrollments", "Total Enrollments"]
        values = [users_with_enrollments, total_enrollments]

        # Create bar chart
        result = self.create_bar_chart(
            labels=stats,
            values=values,
            filename=filename,
            title="Enrollment Statistics",
            ylabel="Count",
            color=["cornflowerblue", "mediumseagreen"],
        )

        # Add the average as text annotation if it's very small compared to total
        if result and avg_enrollments < total_enrollments / 10:
            # Get the figure and add an annotation
            fig = plt.figure()
            plt.annotate(
                f"Avg Enrollments Per User: {avg_enrollments:.2f}",
                xy=(0.5, 0.05),
                xycoords="figure fraction",
                bbox=dict(
                    boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8
                ),
                ha="center",
            )
            plt.close(fig)

        return result

    def _visualize_top_courses(
        self, top_courses: List[tuple], filename: str
    ) -> Optional[str]:
        """
        Create visualization of top courses.

        Args:
            top_courses: List of (course, count) tuples
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Check if we have course data
        if not top_courses:
            return None

        # Extract data
        courses = []
        counts = []

        for course, count in top_courses:
            # Truncate long course names
            course_name = str(course)
            if len(course_name) > 30:
                course_name = course_name[:27] + "..."

            courses.append(course_name)
            counts.append(count)

        # Reverse lists for bottom-to-top display
        courses.reverse()
        counts.reverse()

        # Create horizontal bar chart
        return self.create_bar_chart(
            labels=courses,
            values=counts,
            filename=filename,
            title="Top Courses by Enrollment",
            xlabel="Number of Enrollments",
            horizontal=True,
            color="lightskyblue",
        )

    def _visualize_interests(
        self, interests: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user interests.

        Args:
            interests: Counts by interest
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Filter out low-count interests and sort by count
        min_count = 3  # Minimum count to include
        sorted_interests = sorted(
            [(k, v) for k, v in interests.items() if v >= min_count],
            key=lambda x: x[1],
            reverse=True,
        )

        # Limit to top 15 for readability
        if len(sorted_interests) > 15:
            sorted_interests = sorted_interests[:15]

        if not sorted_interests:
            return None

        # Extract data
        labels = [item[0].replace("_", " ").title() for item in sorted_interests]
        values = [item[1] for item in sorted_interests]

        # Create horizontal bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Interests",
            xlabel="Count",
            horizontal=True,
            color="lightgreen",
        )

    def _visualize_user_counts(
        self, user_counts: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user counts.

        Args:
            user_counts: User counts by category
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Skip if no data
        if not user_counts:
            return None

        # Extract data
        labels = []
        values = []

        for key, value in user_counts.items():
            if key not in ("total_users"):  # Skip total for the bar chart
                labels.append(key.replace("_", " ").title())
                values.append(value)

        # Add total as a separate category
        if "total_users" in user_counts:
            labels.append("Total Users")
            values.append(user_counts["total_users"])

        # Create bar chart from data
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title="User Counts",
            ylabel="Count",
            color=self.STANDARD_COLORS["primary"],
            rotation=45,
        )

    def _visualize_institutions(
        self, institutions: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of user institutions.

        Args:
            institutions: Counts by institution
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Filter out low-count institutions and sort by count
        min_count = 2  # Minimum count to include
        sorted_institutions = sorted(
            [(k, v) for k, v in institutions.items() if v >= min_count],
            key=lambda x: x[1],
            reverse=True,
        )

        # Limit to top 10 for readability
        if len(sorted_institutions) > 10:
            sorted_institutions = sorted_institutions[:10]

        if not sorted_institutions:
            return None

        # Extract data
        labels = [item[0].replace("_", " ").title() for item in sorted_institutions]
        values = [item[1] for item in sorted_institutions]

        # Calculate percentage of total
        total = sum(values)

        # Create figure
        self.setup_figure(figsize=(12, 8), title="User Institutions", xlabel="Count")

        # Create horizontal bar chart
        bars = plt.barh(labels, values, color="mediumpurple")

        # Add value labels with percentages
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = values[i] / total * 100
            plt.text(
                width + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)} ({percentage:.1f}%)",
                ha="left",
                va="center",
            )

        plt.tight_layout()

        # Save and return using the BaseVisualizer method
        return self.save_figure(filename)

    def _visualize_demographics(
        self, demographics: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of various demographic data.

        Args:
            demographics: Demographics data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not demographics:
            return None

        # Create a figure with subplots for different demographic categories
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Gender distribution (top left)
        gender_counts = demographics.get("gender", {})
        if gender_counts:
            # Extract data
            genders = []
            counts = []

            for gender, count in gender_counts.items():
                if count > 0:
                    genders.append(gender.title())
                    counts.append(count)

            # Create a pie chart
            if genders:
                ax1.pie(
                    counts,
                    labels=genders,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=self.get_color_gradient(len(genders), "categorical"),
                )
                ax1.set_title("Gender Distribution", fontsize=14)
                ax1.axis("equal")
            else:
                ax1.text(0.5, 0.5, "No gender data available", ha="center", va="center")
                ax1.axis("off")
        else:
            ax1.text(0.5, 0.5, "No gender data available", ha="center", va="center")
            ax1.axis("off")

        # Plot 2: User personas (top right)
        personas = demographics.get("personas", {})
        if personas:
            # Filter and sort
            sorted_personas = sorted(personas.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_personas) > 8:
                sorted_personas = sorted_personas[:8]

            # Extract data
            persona_labels = [p[0].title() for p in sorted_personas]
            persona_counts = [p[1] for p in sorted_personas]

            # Create a horizontal bar chart
            bars = ax2.barh(persona_labels, persona_counts, color="lightseagreen")

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

            ax2.set_title("User Personas", fontsize=14)
            ax2.set_xlabel("Count", fontsize=12)
        else:
            ax2.text(0.5, 0.5, "No persona data available", ha="center", va="center")
            ax2.axis("off")

        # Plot 3: Top interests (bottom left)
        interests = demographics.get("interests", {})
        top_interests = demographics.get("top_interests", [])

        if top_interests:
            # Extract data
            interest_labels = [i[0].title() for i in top_interests[:8]]
            interest_counts = [i[1] for i in top_interests[:8]]

            # Create a horizontal bar chart
            bars = ax3.barh(interest_labels, interest_counts, color="lightcoral")

            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax3.text(
                    width + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                )

            ax3.set_title("Top Interests", fontsize=14)
            ax3.set_xlabel("Count", fontsize=12)
        else:
            ax3.text(0.5, 0.5, "No interest data available", ha="center", va="center")
            ax3.axis("off")

        # Plot 4: User types (bottom right)
        user_types = demographics.get("user_types", {})
        if user_types:
            # Extract data
            type_labels = []
            type_counts = []

            for type_name, count in user_types.items():
                if count > 0:
                    type_labels.append(type_name.replace("_", " ").title())
                    type_counts.append(count)

            # Create a pie chart
            if type_labels:
                ax4.pie(
                    type_counts,
                    labels=type_labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=self.get_color_gradient(len(type_labels), "categorical"),
                )
                ax4.set_title("User Types", fontsize=14)
                ax4.axis("equal")
            else:
                ax4.text(
                    0.5, 0.5, "No user type data available", ha="center", va="center"
                )
                ax4.axis("off")
        else:
            ax4.text(0.5, 0.5, "No user type data available", ha="center", va="center")
            ax4.axis("off")

        # Add a title for the whole figure
        fig.suptitle("Demographic Overview", fontsize=16)

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for main title

        # Save and return
        return self.save_figure(filename)

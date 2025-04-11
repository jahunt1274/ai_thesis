#!/usr/bin/env python
"""
User Views Analysis Script

This script analyzes the distribution of user views from the thesis dataset.
It dynamically groups view counts based on the actual data distribution
and creates visualizations to help understand user engagement patterns.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional
import logging
import pandas as pd
from pathlib import Path

# Add the project root to Python path to import from the existing codebase
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Import necessary modules from the existing codebase
from src.utils import FileHandler, get_logger, DataFilter
from config import USER_DATA_FILE, OUTPUT_DIR

# Configure logging
logger = get_logger("user_views_analysis")


class UserViewsAnalyzer:
    """Analyzes user view patterns from the dataset."""

    def __init__(self, user_file: str = USER_DATA_FILE):
        """
        Initialize the analyzer.

        Args:
            user_file: Path to the user data file
        """
        self.user_file = user_file
        self.file_handler = FileHandler()
        self.users = None
        self.view_counts = {}
        self.stats = {}
        self.distribution = {}
        self.dynamic_buckets = []

    def load_data(self) -> None:
        """Load user data from the file."""
        logger.info(f"Loading user data from {self.user_file}")

        try:
            all_users = self.file_handler.load_json(self.user_file)
            logger.info(f"Loaded {len(all_users)} user records")

            # filtered_users, _, _ = DataFilter.filter_by_course(
            #     users=all_users, ideas=[], steps=[], course_code="15.390"
            # )

            de_users = {
                "yanpengl@mit.edu",
                "jorge_lc@mit.edu",
                "ywang123@mit.edu",
                "willr343@mit.edu",
                "pcadel@mit.edu",
                "sofia_ch@mit.edu",
                "matmoral@mit.edu",
                "saaid@mit.edu",
                "sultanal@mit.edu",
                "ramirjos@mit.edu",
                "achrafao@mit.edu",
                "omar2001@mit.edu",
                "joehakim@mit.edu",
                "fotis072@mit.edu",
                "ptoso@mit.edu",
                # "",
                "mariazou@mit.edu",
                "mjusto@mit.edu",
                "Julieliu@mit.edu",
                "jcdyer@mit.edu",
                "bld@mit.edu",
                "marounej@mit.edu",
                "makark@mit.edu",
                "haohengt@mit.edu",
                "carlylave@gsd.harvard.edu",
                "cjcjcjcj@mit.edu",
                "cming@mit.edu",
                "wdale@mit.edu",
                "cbradley@mit.edu",
                "karentk@mit.edu",
                "natasha1@mit.edu",
                "flanus22@mit.edu",
                "ticha@mit.edu",
                "anupsk@mit.edu",
                "jqk@mit.edu",
                "mqu@college.harvard.edu",
                "mvivas@mit.edu",
                "toritse1@mit.edu",
                "gabe_a@mit.edu",
                "dingruiw@mit.edu",
                "jaggersu@mit.edu",
                "hongxiny@mit.edu",
                "gelizhou@mit.edu",
                "liuyf23@mit.edu",
                "cecizhan@mit.edu",
                "xiyaj@mit.edu",
                "lingyi@mit.edu",
                "yzhou11@mit.edu",
                "bcbrower@mit.edu",
                "yefeili@mit.edu",
                "rrocke@mit.edu",
                "kapoora@mit.edu",
                "ksimha@mit.edu",
                "pfalk@mit.edu",
                "m_gaafar@mit.edu",
                "wzunker@mit.edu",
                "balza248@mit.edu",
                "limmer@mit.edu",
                # "",
                "garoxa@mit.edu",
                "diegoort@mit.edu",
                "pcadel@mit.edu",
                "nabate@mit.edu",
                "fatima19@mit.edu",
                "mr113@wellesley.edu",
                "lk109@wellesley.edu",
                "mqu@college.harvard.edu",
            }

            filtered_users = []
            for user in all_users:
                if user.get("email") in de_users:
                    filtered_users.append(user)

            self.users = filtered_users
            logger.info(f"Filtered to {len(self.users)} user records")

        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            sys.exit(1)

    def compute_view_counts(self) -> None:
        """
        Compute the number of views for each user.
        Stores the results in self.view_counts.
        """
        logger.info("Computing view counts for each user")

        self.view_counts = {}
        users_with_views = 0

        for user in self.users:
            user_id = user.get("_id", {}).get("$oid", "unknown")
            email = user.get("email", "unknown")
            views = user.get("views", [])

            # Count the number of views
            view_count = len(views)

            # Store in dictionary with email as key (or id if email not available)
            key = email if email != "unknown" else user_id
            self.view_counts[key] = view_count

            if view_count > 0:
                users_with_views += 1

        logger.info(f"Found {users_with_views} users with at least one view")

    def compute_basic_statistics(self) -> None:
        """
        Compute basic statistics for the view counts.
        Stores the results in self.stats.
        """
        logger.info("Computing basic statistics for view counts")

        view_counts_array = np.array(list(self.view_counts.values()))

        # Compute statistics
        self.stats = {
            "count": len(view_counts_array),
            "min": int(np.min(view_counts_array)),
            "max": int(np.max(view_counts_array)),
            "mean": float(np.mean(view_counts_array)),
            "median": float(np.median(view_counts_array)),
            "std": float(np.std(view_counts_array)),
            "percentiles": {
                "25": float(np.percentile(view_counts_array, 25)),
                "50": float(np.percentile(view_counts_array, 50)),
                "75": float(np.percentile(view_counts_array, 75)),
                "90": float(np.percentile(view_counts_array, 90)),
                "95": float(np.percentile(view_counts_array, 95)),
                "99": float(np.percentile(view_counts_array, 99)),
            },
            "users_with_zero_views": sum(
                1 for count in view_counts_array if count == 0
            ),
            "users_with_one_view": sum(1 for count in view_counts_array if count == 1),
        }

    def create_distribution(self) -> None:
        """
        Create a distribution of view counts.
        Stores the results in self.distribution.
        """
        logger.info("Creating view count distribution")

        distribution = defaultdict(int)

        for count in self.view_counts.values():
            distribution[count] += 1

        # Convert to regular dict for easier handling
        self.distribution = dict(distribution)

    def determine_dynamic_buckets(self) -> None:
        """
        Determine appropriate bucket boundaries based on the data distribution.
        Uses knowledge of the data to create meaningful groups.
        """
        logger.info("Determining dynamic buckets for view counts")

        view_counts_array = np.array(list(self.view_counts.values()))

        # Check the distribution characteristics
        max_views = self.stats["max"]
        median_views = self.stats["median"]
        p75 = self.stats["percentiles"]["75"]
        p90 = self.stats["percentiles"]["90"]
        p95 = self.stats["percentiles"]["95"]
        p99 = self.stats["percentiles"]["99"]

        # Strategy depends on data shape
        if max_views > 100 and p75 < 10:
            # Heavily skewed distribution - use logarithmic-like buckets
            logger.info("Using logarithmic-like buckets for skewed distribution")

            self.dynamic_buckets = [
                (0, 0, "0 views"),
                (1, 1, "1 view"),
                (2, 2, "2 views"),
                (3, 5, "3-5 views"),
                (6, 10, "6-10 views"),
                (11, 20, "11-20 views"),
                (21, 50, "21-50 views"),
                (51, 100, "51-100 views"),
                (101, max_views, f"101+ views"),
            ]
        elif max_views > 50 and p90 < 20:
            # Moderately skewed
            logger.info("Using moderately skewed bucketing approach")

            self.dynamic_buckets = [
                (0, 0, "0 views"),
                (1, 1, "1 view"),
                (2, 3, "2-3 views"),
                (4, 6, "4-6 views"),
                (7, 10, "7-10 views"),
                (11, 15, "11-15 views"),
                (16, 25, "16-25 views"),
                (26, 50, "26-50 views"),
                (51, max_views, f"51+ views"),
            ]
        else:
            # More evenly distributed - use percentile-based approach
            logger.info("Using percentile-based bucketing approach")

            # Create roughly equal-sized buckets based on percentiles
            percentiles = [0, 10, 25, 50, 75, 90, 95, 99, 100]
            percentile_values = [0]  # Start with 0

            for p in percentiles[1:]:
                if p == 100:
                    percentile_values.append(max_views)
                else:
                    pv = np.percentile(view_counts_array, p)
                    # Round to nearest integer and ensure it's distinct
                    pv_int = max(int(np.ceil(pv)), percentile_values[-1] + 1)
                    percentile_values.append(pv_int)

            # Create buckets from percentile boundaries, merging very close ones
            merged_boundaries = [percentile_values[0]]

            for i in range(1, len(percentile_values)):
                if percentile_values[i] > merged_boundaries[-1] + 1:
                    merged_boundaries.append(percentile_values[i])

            # Convert boundaries to buckets
            self.dynamic_buckets = []
            for i in range(len(merged_boundaries) - 1):
                start = merged_boundaries[i]
                end = merged_boundaries[i + 1] - 1

                if start == end:
                    label = f"{start} views" if start != 1 else "1 view"
                else:
                    label = f"{start}-{end} views"

                self.dynamic_buckets.append((start, end, label))

            # Add the last bucket
            last_start = merged_boundaries[-1]
            last_end = max_views
            last_label = f"{last_start}+ views"
            self.dynamic_buckets.append((last_start, last_end, last_label))

        # Ensure we don't have too many buckets
        if len(self.dynamic_buckets) > 15:
            logger.info("Too many buckets, consolidating...")
            # Implement bucket consolidation if needed

        logger.info(f"Created {len(self.dynamic_buckets)} dynamic buckets")

    def group_by_dynamic_buckets(self) -> Dict[str, int]:
        """
        Group view counts using the dynamic buckets.

        Returns:
            Dictionary mapping bucket labels to user counts
        """
        logger.info("Grouping users by dynamic view count buckets")

        bucketed_counts = defaultdict(int)

        for count in self.view_counts.values():
            for start, end, label in self.dynamic_buckets:
                if start <= count <= end:
                    bucketed_counts[label] += 1
                    break

        # Convert to regular dict and sort by bucket boundaries
        sorted_buckets = dict(
            sorted(
                bucketed_counts.items(),
                key=lambda x: next(
                    i for i, (s, e, l) in enumerate(self.dynamic_buckets) if l == x[0]
                ),
            )
        )

        return sorted_buckets

    def analyze_views_over_time(self) -> Optional[Dict[str, Any]]:
        """
        Analyze view timestamps to understand engagement patterns over time.

        Returns:
            Dictionary of time-based analysis results or None if timestamp data is insufficient
        """
        logger.info("Analyzing view timestamps")

        # Check if we have sufficient timestamp data
        timestamps_available = False

        for user in self.users:
            views = user.get("views", [])
            if views and isinstance(views[0], (int, float)):
                timestamps_available = True
                break

        if not timestamps_available:
            logger.warning("Insufficient timestamp data for time-based analysis")
            return None

        # Aggregate view timestamps by day of week and hour of day
        view_days = defaultdict(int)
        view_hours = defaultdict(int)
        views_by_date = defaultdict(int)

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        total_timestamps = 0

        for user in self.users:
            views = user.get("views", [])

            for view_timestamp in views:
                try:
                    # Convert epoch timestamp to datetime
                    if isinstance(view_timestamp, (int, float)):
                        # Check if timestamp needs to be divided by 1000 (milliseconds vs seconds)
                        if (
                            view_timestamp > 1e11
                        ):  # Large values likely represent milliseconds
                            view_timestamp /= 1000

                        view_dt = datetime.fromtimestamp(view_timestamp)

                        # Increment counts
                        day_of_week = days[view_dt.weekday()]
                        hour_of_day = view_dt.hour
                        date_str = view_dt.strftime("%Y-%m-%d")

                        view_days[day_of_week] += 1
                        view_hours[hour_of_day] += 1
                        views_by_date[date_str] += 1

                        total_timestamps += 1
                except Exception as e:
                    continue  # Skip invalid timestamps

        if total_timestamps == 0:
            logger.warning("No valid timestamps found for time-based analysis")
            return None

        logger.info(f"Analyzed {total_timestamps} view timestamps")

        # Return time-based analysis results
        return {
            "day_of_week": dict(
                sorted(view_days.items(), key=lambda x: days.index(x[0]))
            ),
            "hour_of_day": dict(sorted(view_hours.items())),
            "views_by_date": dict(sorted(views_by_date.items())),
            "total_timestamps": total_timestamps,
        }

    def visualize_distribution(
        self, bucketed_counts: Dict[str, int], output_dir: str = "output"
    ) -> None:
        """
        Create visualizations of the view count distribution.

        Args:
            bucketed_counts: Dictionary of bucketed view counts
            output_dir: Directory to save visualization files
        """
        logger.info("Creating visualizations")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Set up plot style
        plt.style.use("seaborn-v0_8-whitegrid")
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 6))

        # Create bar chart of bucketed view counts
        ax = sns.barplot(
            x=list(bucketed_counts.keys()),
            y=list(bucketed_counts.values()),
            palette="viridis",
        )
        plt.title("Distribution of User View Counts", fontsize=16)
        plt.xlabel("Number of Views", fontsize=12)
        plt.ylabel("Number of Users", fontsize=12)
        plt.xticks(rotation=45, ha="right")

        # Add count labels on top of bars
        for i, count in enumerate(bucketed_counts.values()):
            ax.text(i, count + 5, str(count), ha="center", fontsize=10)

        # Add summary statistics as text
        stats_text = (
            f"Total Users: {self.stats['count']}\n"
            f"Mean Views: {self.stats['mean']:.2f}\n"
            f"Median Views: {self.stats['median']:.1f}\n"
            f"Max Views: {self.stats['max']}"
        )
        plt.figtext(
            0.15,
            0.80,
            stats_text,
            fontsize=12,
            bbox=dict(facecolor="white", alpha=0.8, boxstyle="round,pad=0.5"),
        )

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "view_distribution_buckets.png"), dpi=300)
        logger.info(
            f"Saved bucketed distribution visualization to {output_dir}/view_distribution_buckets.png"
        )

        # Create histogram of raw view counts (limited to 95th percentile for readability)
        plt.figure(figsize=(12, 6))
        max_view_for_hist = np.percentile(list(self.view_counts.values()), 95)

        sns.histplot(
            [v for v in self.view_counts.values() if v <= max_view_for_hist],
            kde=True,
            bins=min(30, len(set(self.view_counts.values()))),
            color="royalblue",
        )

        plt.title(
            f"Histogram of User View Counts (up to 95th percentile: {max_view_for_hist:.0f} views)",
            fontsize=16,
        )
        plt.xlabel("Number of Views", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)

        # Add reference lines for statistics
        if self.stats["mean"] <= max_view_for_hist:
            plt.axvline(
                self.stats["mean"],
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f'Mean: {self.stats["mean"]:.2f}',
            )
        if self.stats["median"] <= max_view_for_hist:
            plt.axvline(
                self.stats["median"],
                color="green",
                linestyle="--",
                alpha=0.7,
                label=f'Median: {self.stats["median"]:.2f}',
            )

        plt.legend()
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_dir, "view_distribution_histogram.png"), dpi=300
        )
        logger.info(
            f"Saved histogram visualization to {output_dir}/view_distribution_histogram.png"
        )

        # If we have time-based analysis, visualize it
        time_analysis = self.analyze_views_over_time()
        if time_analysis:
            # Day of week visualization
            plt.figure(figsize=(10, 6))
            day_order = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            day_counts = [time_analysis["day_of_week"].get(day, 0) for day in day_order]

            sns.barplot(x=day_order, y=day_counts, palette="viridis")
            plt.title("View Activity by Day of Week", fontsize=16)
            plt.xlabel("Day", fontsize=12)
            plt.ylabel("Number of Views", fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "views_by_day.png"), dpi=300)

            # Hour of day visualization
            plt.figure(figsize=(12, 6))
            hour_order = list(range(24))
            hour_counts = [
                time_analysis["hour_of_day"].get(hour, 0) for hour in hour_order
            ]

            sns.barplot(
                x=[f"{h:02d}:00" for h in hour_order], y=hour_counts, palette="viridis"
            )
            plt.title("View Activity by Hour of Day", fontsize=16)
            plt.xlabel("Hour", fontsize=12)
            plt.ylabel("Number of Views", fontsize=12)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "views_by_hour.png"), dpi=300)

            # Time series visualization if we have enough dates
            if len(time_analysis["views_by_date"]) > 5:
                plt.figure(figsize=(14, 6))

                # Convert to DataFrame for better time series handling
                date_df = pd.DataFrame(
                    list(time_analysis["views_by_date"].items()),
                    columns=["date", "views"],
                )
                date_df["date"] = pd.to_datetime(date_df["date"])
                date_df = date_df.sort_values("date")

                # Plot time series
                plt.plot(
                    date_df["date"],
                    date_df["views"],
                    marker="o",
                    linestyle="-",
                    alpha=0.7,
                )
                plt.title("View Activity Over Time", fontsize=16)
                plt.xlabel("Date", fontsize=12)
                plt.ylabel("Number of Views", fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, "views_over_time.png"), dpi=300)

            logger.info(f"Saved time-based visualizations to {output_dir}")

        plt.close("all")  # Close all figures

    def generate_report(
        self, bucketed_counts: Dict[str, int], output_dir: str = "output"
    ) -> None:
        """
        Generate a text report of the analysis results.

        Args:
            bucketed_counts: Dictionary of bucketed view counts
            output_dir: Directory to save the report file
        """
        logger.info("Generating text report")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Create the report content
        report_content = [
            "===================================================",
            "            USER VIEWS ANALYSIS REPORT             ",
            "===================================================",
            "",
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Users Analyzed: {self.stats['count']}",
            "",
            "BASIC STATISTICS:",
            f"  - Minimum Views: {self.stats['min']}",
            f"  - Maximum Views: {self.stats['max']}",
            f"  - Mean Views: {self.stats['mean']:.2f}",
            f"  - Median Views: {self.stats['median']:.2f}",
            f"  - Standard Deviation: {self.stats['std']:.2f}",
            "",
            "PERCENTILES:",
            f"  - 25th Percentile: {self.stats['percentiles']['25']:.2f}",
            f"  - 50th Percentile: {self.stats['percentiles']['50']:.2f}",
            f"  - 75th Percentile: {self.stats['percentiles']['75']:.2f}",
            f"  - 90th Percentile: {self.stats['percentiles']['90']:.2f}",
            f"  - 95th Percentile: {self.stats['percentiles']['95']:.2f}",
            f"  - 99th Percentile: {self.stats['percentiles']['99']:.2f}",
            "",
            "SPECIAL CASES:",
            f"  - Users with Zero Views: {self.stats['users_with_zero_views']} ({self.stats['users_with_zero_views']/self.stats['count']*100:.1f}%)",
            f"  - Users with One View: {self.stats['users_with_one_view']} ({self.stats['users_with_one_view']/self.stats['count']*100:.1f}%)",
            "",
            "VIEW COUNT DISTRIBUTION (DYNAMIC BUCKETS):",
        ]

        # Add the bucketed counts
        max_label_len = max(len(label) for label in bucketed_counts.keys())
        for label, count in bucketed_counts.items():
            percentage = count / self.stats["count"] * 100
            report_content.append(
                f"  - {label.ljust(max_label_len)}: {count} users ({percentage:.1f}%)"
            )

        # Add bucket boundaries used
        report_content.append("")
        report_content.append("DYNAMIC BUCKETING INFORMATION:")
        for start, end, label in self.dynamic_buckets:
            report_content.append(f"  - {label}: {start} to {end}")

        # Write the report to a file
        report_path = os.path.join(output_dir, "user_views_analysis_report.txt")
        with open(report_path, "w") as f:
            f.write("\n".join(report_content))

        logger.info(f"Saved analysis report to {report_path}")

    def run_analysis(self, output_dir: str = "output") -> None:
        """
        Run the complete analysis pipeline.

        Args:
            output_dir: Directory to save output files
        """
        logger.info("Starting user views analysis")

        # Execute the analysis pipeline
        self.load_data()
        self.compute_view_counts()
        self.compute_basic_statistics()
        self.create_distribution()
        self.determine_dynamic_buckets()
        bucketed_counts = self.group_by_dynamic_buckets()

        # Generate outputs
        self.visualize_distribution(bucketed_counts, output_dir)
        self.generate_report(bucketed_counts, output_dir)

        logger.info("User views analysis completed")

        # Print basic results to console
        print("\nUser Views Analysis Summary:")
        print(f"Total Users: {self.stats['count']}")
        print(f"Mean Views: {self.stats['mean']:.2f}")
        print(f"Median Views: {self.stats['median']:.2f}")
        print(f"Max Views: {self.stats['max']}")
        print(
            f"Users with Zero Views: {self.stats['users_with_zero_views']} ({self.stats['users_with_zero_views']/self.stats['count']*100:.1f}%)"
        )
        print("\nDetailed results available in the output directory")


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Analyze user views distribution")
    parser.add_argument(
        "--user-file", type=str, default=USER_DATA_FILE, help="Path to user data file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=f"{OUTPUT_DIR}/user_views_analysis",
        help="Directory to save output files",
    )

    args = parser.parse_args()

    # Run the analysis
    analyzer = UserViewsAnalyzer(user_file=args.user_file)
    analyzer.run_analysis(output_dir=args.output_dir)


if __name__ == "__main__":
    main()

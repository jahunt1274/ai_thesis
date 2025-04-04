"""
Idea visualizer for data analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional
from collections import defaultdict

from src.constants.data_constants import IDEA_DOMAIN_CATEGORIES
from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("idea_visualizer")


class IdeaVisualizer(BaseVisualizer):
    """Visualizes idea analysis results."""

    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the idea visualizer.

        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format

        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "idea")
        os.makedirs(self.vis_dir, exist_ok=True)

        # Set default style
        plt.style.use("seaborn-v0_8-whitegrid")

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for idea analysis.

        Args:
            data: Idea analysis results

        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            "category_distribution": (
                self._visualize_category_distribution,
                {"data_key": "category_distribution"},
            ),
            "top_categories": (
                self._visualize_top_categories,
                {"data_key": "top_categories"},
            ),
            "category_percentages": (
                self._visualize_category_percentages,
                {"data_key": "category_percentages"},
            ),
            "category_clusters": (
                self._visualize_category_clusters,
                {"data_key": "category_counts"},
            ),
            "domain_grouping": (
                self._visualize_domain_grouping,
                {"data_key": "domain_grouping"},
            ),
        }

        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_category_distribution(
        self, category_counts: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of idea category distribution.

        Args:
            category_counts: Counts by category
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Sort categories by count (descending)
            sorted_categories = sorted(
                category_counts.items(), key=lambda x: x[1], reverse=True
            )

            # For readability, limit to top 20 categories if there are many
            if len(sorted_categories) > 20:
                sorted_categories = sorted_categories[:20]
                truncated = True
            else:
                truncated = False

            # Extract data
            categories = [c[0] for c in sorted_categories]
            counts = [c[1] for c in sorted_categories]

            # Create horizontal bar chart for better readability with many categories
            fig = self.setup_figure(
                figsize=(12, max(8, len(categories) * 0.4)),
                title="Idea Category Distribution"
                + (" (Top 20 Categories)" if truncated else ""),
                xlabel="Number of Ideas",
            )

            # Create gradient colors based on counts
            cmap = plt.cm.viridis
            colors = cmap(np.linspace(0.1, 0.9, len(counts)))

            # Create horizontal bar chart
            bars = plt.barh(categories, counts, color=colors)

            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(
                    width + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                )

            plt.tight_layout()

            # Save figure
            output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            logger.error(
                f"Error creating category distribution visualization: {str(e)}"
            )
            plt.close("all")  # Close any open figures
            return None

    def _visualize_top_categories(
        self, top_categories: List[tuple], filename: str
    ) -> Optional[str]:
        """
        Create visualization of top idea categories.

        Args:
            top_categories: List of (category, count) tuples
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a few categories
            if not top_categories or len(top_categories) < 3:
                logger.warning("Not enough categories for top categories visualization")
                return None

            # Extract data
            categories = [c[0] for c in top_categories]
            counts = [c[1] for c in top_categories]

            # Create pie chart for top categories
            fig = self.setup_figure(figsize=(12, 10), title="Top Idea Categories")

            # Define explode to emphasize top categories
            explode = [0.1 if i < 3 else 0 for i in range(len(categories))]

            # Custom color map
            colors = plt.cm.tab20(np.linspace(0, 1, len(categories)))

            # Create pie chart
            plt.pie(
                counts,
                labels=categories,
                autopct="%1.1f%%",
                startangle=90,
                explode=explode,
                colors=colors,
                shadow=True,
            )

            # Equal aspect ratio ensures the pie chart is circular
            plt.axis("equal")

            # Add legend with counts
            legend_labels = [
                f"{cat} ({count})" for cat, count in zip(categories, counts)
            ]
            plt.legend(legend_labels, loc="best", bbox_to_anchor=(1, 0.5))

            plt.tight_layout()

            # Save figure
            output_path = os.path.join(self.vis_dir, f"{filename}_pie.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            logger.error(f"Error creating top categories visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_category_percentages(
        self, category_percentages: Dict[str, float], filename: str
    ) -> Optional[str]:
        """
        Create visualization of category percentages.

        Args:
            category_percentages: Percentage by category
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Sort categories by percentage (descending)
            sorted_categories = sorted(
                category_percentages.items(), key=lambda x: x[1], reverse=True
            )

            # Group small categories into "Other" for readability
            threshold = 2.0  # Categories with less than 2% are grouped as "Other"
            significant_categories = []
            other_percentage = 0.0

            for category, percentage in sorted_categories:
                if percentage >= threshold:
                    significant_categories.append((category, percentage))
                else:
                    other_percentage += percentage

            if other_percentage > 0:
                significant_categories.append(("Other", other_percentage))

            # Extract data
            categories = [c[0] for c in significant_categories]
            percentages = [c[1] for c in significant_categories]

            # Create stacked horizontal bar chart for percentage breakdown
            fig = self.setup_figure(
                figsize=(12, 6), title="Category Percentage Breakdown"
            )

            # Custom color map
            colors = plt.cm.tab20(np.linspace(0, 1, len(categories)))

            # Create stacked bar
            left = 0
            for i, (cat, pct) in enumerate(zip(categories, percentages)):
                plt.barh(
                    [0], [pct], left=left, color=colors[i], label=f"{cat} ({pct:.1f}%)"
                )

                # Add percentage label in the middle of each segment
                if pct >= 5:  # Only add label if segment is wide enough
                    plt.text(
                        left + pct / 2,
                        0,
                        f"{pct:.1f}%",
                        ha="center",
                        va="center",
                        fontsize=10,
                        color="white",
                        fontweight="bold",
                    )

                left += pct

            # Add title and labels
            plt.xlabel("Percentage (%)", fontsize=12)
            plt.yticks([])  # Hide y-axis ticks

            # Add percentage markers on x-axis
            plt.xticks(np.arange(0, 101, 10))
            plt.xlim(0, 100)

            # Add legend
            plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)

            plt.tight_layout()

            # Save figure
            output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            logger.error(f"Error creating category percentages visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_category_clusters(
        self, category_counts: Dict[str, int], filename: str
    ) -> Optional[str]:
        """
        Create visualization of category clusters.

        Args:
            category_counts: Counts by category
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Map categories to domains and count
            domain_counts = defaultdict(int)
            unmapped_categories = []

            for category, count in category_counts.items():
                mapped = False
                for domain, domain_categories in IDEA_DOMAIN_CATEGORIES.items():
                    if category in domain_categories:
                        domain_counts[domain] += count
                        mapped = True
                        break

                if not mapped:
                    unmapped_categories.append(category)
                    domain_counts["Miscellaneous"] += count

            # Sort domains by count
            sorted_domains = sorted(
                domain_counts.items(), key=lambda x: x[1], reverse=True
            )
            domains = [d[0] for d in sorted_domains]
            counts = [d[1] for d in sorted_domains]

            # Calculate percentages for labels
            total = sum(counts)
            percentages = [count / total * 100 for count in counts]

            # Create pie chart
            fig = self.setup_figure(
                figsize=(12, 10), title="Idea Categories by Domain Cluster"
            )

            # Create color map
            cmap = plt.cm.viridis
            colors = cmap(np.linspace(0.1, 0.9, len(domains)))

            # Create pie chart
            plt.pie(
                counts,
                labels=domains,
                autopct="%1.1f%%",
                startangle=90,
                colors=colors,
                shadow=True,
            )

            # Equal aspect ratio ensures the pie chart is circular
            plt.axis("equal")

            # Add domain counts as legend
            legend_labels = [
                f"{domain} ({count})" for domain, count in zip(domains, counts)
            ]
            plt.legend(legend_labels, loc="best", bbox_to_anchor=(1, 0.5))

            plt.tight_layout()

            # Save figure
            output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            logger.error(f"Error creating category clusters visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

    def _visualize_domain_grouping(
        self, domain_grouping: Dict[str, Any], filename: str
    ) -> Optional[str]:
        """
        Create visualization of domain grouping data.

        Args:
            domain_grouping: Domain grouping data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        try:
            # Extract domain counts
            domain_counts = domain_grouping.get("domain_counts", {})
            domain_percentages = domain_grouping.get("domain_percentages", {})

            if not domain_counts:
                logger.warning(
                    "No domain counts available for domain grouping visualization"
                )
                return None

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

            # Plot 1: Domain counts as bar chart (left subplot)
            # Sort domains by count
            sorted_domains = sorted(
                domain_counts.items(), key=lambda x: x[1], reverse=True
            )
            domains = [d[0] for d in sorted_domains]
            counts = [d[1] for d in sorted_domains]

            # Create bar chart
            bars = ax1.barh(
                domains,
                counts,
                color=self.get_color_gradient(len(domains), "categorical"),
            )

            # Add count labels
            for bar in bars:
                width = bar.get_width()
                ax1.text(
                    width + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                )

            ax1.set_title("Ideas by Domain Category", fontsize=14)
            ax1.set_xlabel("Number of Ideas", fontsize=12)

            # Plot 2: Domain percentages as pie chart (right subplot)
            # Use same order as domain counts
            percentages = [domain_percentages.get(domain, 0) for domain in domains]

            # Create pie chart
            ax2.pie(
                percentages,
                labels=domains,
                autopct="%1.1f%%",
                startangle=90,
                colors=self.get_color_gradient(len(domains), "categorical"),
            )

            # Equal aspect ratio ensures the pie chart is circular
            ax2.axis("equal")
            ax2.set_title("Domain Category Distribution", fontsize=14)

            # Add overall title
            fig.suptitle("Idea Domains Overview", fontsize=16)

            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for main title

            # Save figure
            output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            logger.error(f"Error creating domain grouping visualization: {str(e)}")
            plt.close("all")  # Close any open figures
            return None

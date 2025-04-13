"""
Team visualizer for data analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("team_visualizer")


class TeamVisualizer(BaseVisualizer):
    """Visualizes team analysis results."""

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for team analysis.

        Args:
            data: Team analysis results

        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            "team_engagement": (
                self._visualize_team_engagement,
                {"data_key": "team_engagement"},
            ),
            "team_activity": (
                self._visualize_team_activity,
                {"data_key": "team_activity"},
            ),
            "section_comparison": (
                self._visualize_section_comparison,
                {"data_key": "section_comparison"},
            ),
            "semester_comparison": (
                self._visualize_semester_comparison,
                {"data_key": "semester_comparison"},
            ),
            "team_size_impact": (
                self._visualize_team_size_impact,
                {"data_key": "team_size_impact"},
            ),
            "work_distribution": (
                self._visualize_work_distribution,
                {"data_key": "work_distribution"},
            ),
            "tool_impact": (
                self._visualize_tool_impact,
                {"data_key": "tool_version_impact"},
            ),
        }

        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_team_engagement(self, engagement_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of team engagement metrics.

        Args:
            engagement_data: Team engagement data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract team metrics and overall stats
        team_metrics = engagement_data.get("team_metrics", {})
        overall_stats = engagement_data.get("overall_stats", {})
        
        if not team_metrics:
            logger.warning("No team metrics data available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Plot 1: Top teams by idea count
        # Sort teams by total ideas
        sorted_teams = sorted(team_metrics.items(), key=lambda x: x[1].get("total_ideas", 0), reverse=True)
        # Take top 10 teams
        top_teams = sorted_teams[:10]
        
        # Extract data for plotting
        team_labels = [f"{metrics.get('name', team_id)} ({metrics.get('term', '')} {metrics.get('year', '')})" 
                      for team_id, metrics in top_teams]
        idea_counts = [metrics.get("total_ideas", 0) for _, metrics in top_teams]
        
        # Create horizontal bar chart
        bars1 = ax1.barh(team_labels, idea_counts, color="steelblue")
        
        # Add value labels
        for bar in bars1:
            width = bar.get_width()
            ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                    f"{int(width)}", ha='left', va='center')
                    
        ax1.set_title("Top Teams by Idea Count", fontsize=14)
        ax1.set_xlabel("Number of Ideas", fontsize=12)
        
        # Plot 2: Framework preferences
        framework_counts = overall_stats.get("framework_preference_counts", {})
        
        if framework_counts:
            # Extract data for plotting
            frameworks = ["disciplined-entrepreneurship", "startup-tactics", "both", "none"]
            framework_labels = ["Disciplined Entrepreneurship", "Startup Tactics", "Both", "None"]
            counts = [framework_counts.get(f, 0) for f in frameworks]
            
            # Create pie chart
            colors = ["dodgerblue", "darkorange", "mediumseagreen", "lightgray"]
            wedges, texts, autotexts = ax2.pie(counts, labels=framework_labels, 
                                             autopct="%1.1f%%", startangle=90, 
                                             colors=colors)
            
            # Customize text
            for text in texts:
                text.set_size(10)
            for autotext in autotexts:
                autotext.set_size(9)
                
            ax2.set_title("Team Framework Preferences", fontsize=14)
            ax2.axis('equal')  # Equal aspect ratio ensures circular pie
        else:
            ax2.text(0.5, 0.5, "No framework preference data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Team Engagement Overview", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_team_activity(self, activity_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of team activity patterns.

        Args:
            activity_data: Team activity data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not activity_data:
            logger.warning("No team activity data available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Plot 1: Collaboration Patterns Distribution
        # Count collaboration patterns
        collaboration_patterns = {}
        for team_id, team_data in activity_data.items():
            pattern = team_data.get("collaboration_pattern")
            if pattern:
                collaboration_patterns[pattern] = collaboration_patterns.get(pattern, 0) + 1
        
        if collaboration_patterns:
            # Extract data for plotting
            patterns = list(collaboration_patterns.keys())
            counts = list(collaboration_patterns.values())
            
            # Create bar chart
            bars1 = ax1.bar(patterns, counts, color="cornflowerblue")
            
            # Add value labels
            self.add_value_labels(ax1, bars1)
                    
            ax1.set_title("Team Collaboration Patterns", fontsize=14)
            ax1.set_ylabel("Number of Teams", fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, "No collaboration pattern data available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
        
        # Plot 2: Work Distribution (Gini Coefficients)
        gini_values = []
        team_labels = []
        
        for team_id, team_data in list(activity_data.items())[:15]:  # Limit to 15 teams for readability
            gini = team_data.get("activity_distribution", {}).get("gini_coefficient")
            if gini is not None:
                gini_values.append(gini)
                team_labels.append(f"{team_data.get('name', team_id)} ({team_data.get('member_count')} members)")
        
        if gini_values:
            # Sort by Gini coefficient
            sorted_indices = np.argsort(gini_values)
            sorted_gini = [gini_values[i] for i in sorted_indices]
            sorted_labels = [team_labels[i] for i in sorted_indices]
            
            # Color bars based on Gini value (lower is more equal)
            cmap = plt.cm.get_cmap('RdYlGn_r')
            colors = [cmap(g) for g in sorted_gini]
            
            # Create horizontal bar chart
            bars2 = ax2.barh(sorted_labels, sorted_gini, color=colors)
            
            # Add value labels
            for bar in bars2:
                width = bar.get_width()
                ax2.text(width + 0.02, bar.get_y() + bar.get_height()/2, 
                       f"{width:.2f}", ha='left', va='center')
                        
            ax2.set_title("Work Distribution Within Teams (Gini Coefficient)", fontsize=14)
            ax2.set_xlabel("Gini Coefficient (0=Equal, 1=Unequal)", fontsize=12)
            
            # Add explanatory note
            ax2.text(0.5, -0.1, 
                   "Lower values indicate more equal work distribution", 
                   ha='center', va='center', transform=ax2.transAxes,
                   bbox=dict(facecolor='lightyellow', alpha=0.5, boxstyle='round'))
        else:
            ax2.text(0.5, 0.5, "No work distribution data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Team Activity and Collaboration Analysis", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_section_comparison(self, section_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of section comparisons.

        Args:
            section_data: Section comparison data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        if not section_data:
            logger.warning("No section comparison data available for visualization")
            return None
            
        # Select a term with multiple sections for comparison
        target_term = None
        for term_key, term_data in section_data.items():
            if len(term_data.get("sections", {})) > 1:
                target_term = term_key
                target_data = term_data
                break
                
        if not target_term:
            logger.warning("No terms with multiple sections found for comparison")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Extract section data
        sections = list(target_data.get("sections", {}).keys())
        tool_version = target_data.get("tool_version")
        term_display = f"{target_data.get('term')} {target_data.get('year')}"
        
        # Plot 1: Ideas and Steps by Section
        if sections:
            # Extract data for plotting
            ideas_per_team = [target_data["sections"][s].get("avg_ideas_per_team", 0) for s in sections]
            steps_per_team = [target_data["sections"][s].get("avg_steps_per_team", 0) for s in sections]
            
            # Set up bar positions
            x = np.arange(len(sections))
            width = 0.35
            
            # Create grouped bar chart
            bars1_1 = ax1.bar(x - width/2, ideas_per_team, width, label='Ideas per Team', color='steelblue')
            bars1_2 = ax1.bar(x + width/2, steps_per_team, width, label='Steps per Team', color='darkorange')
            
            # Add value labels
            self.add_value_labels(ax1, bars1_1, "{:.1f}")
            self.add_value_labels(ax1, bars1_2, "{:.1f}")
            
            # Set up axis labels and ticks
            ax1.set_xlabel("Section", fontsize=12)
            ax1.set_ylabel("Average Count", fontsize=12)
            ax1.set_title(f"Ideas and Steps by Section ({term_display})", fontsize=14)
            ax1.set_xticks(x)
            ax1.set_xticklabels(sections)
            ax1.legend()
        else:
            ax1.text(0.5, 0.5, "No section data available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
            
        # Plot 2: Framework Preferences by Section
        if sections:
            # Stack data for each framework
            de_counts = []
            st_counts = []
            both_counts = []
            none_counts = []
            
            for section in sections:
                framework_prefs = target_data["sections"][section].get("framework_preferences", {})
                de_counts.append(framework_prefs.get("disciplined-entrepreneurship", 0))
                st_counts.append(framework_prefs.get("startup-tactics", 0))
                both_counts.append(framework_prefs.get("both", 0))
                none_counts.append(framework_prefs.get("none", 0))
                
            # Create stacked bar chart
            bottom_vals = np.zeros(len(sections))
            
            bars2_1 = ax2.bar(sections, de_counts, label='Disciplined Entrepreneurship', color='dodgerblue')
            
            bottom_vals = np.array(de_counts)
            bars2_2 = ax2.bar(sections, st_counts, bottom=bottom_vals, label='Startup Tactics', color='darkorange')
            
            bottom_vals = bottom_vals + np.array(st_counts)
            bars2_3 = ax2.bar(sections, both_counts, bottom=bottom_vals, label='Both', color='mediumseagreen')
            
            bottom_vals = bottom_vals + np.array(both_counts)
            bars2_4 = ax2.bar(sections, none_counts, bottom=bottom_vals, label='None', color='lightgray')
            
            ax2.set_xlabel("Section", fontsize=12)
            ax2.set_ylabel("Number of Teams", fontsize=12)
            ax2.set_title(f"Framework Preferences by Section ({term_display})", fontsize=14)
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, "No framework preference data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add tool version information
        tool_text = f"Tool Version: {tool_version if tool_version else 'None (Control Group)'}"
        fig.text(0.5, 0.01, tool_text, ha='center', fontsize=12, 
               bbox=dict(facecolor='lightyellow', alpha=0.5, boxstyle='round'))
            
        # Add overall title
        fig.suptitle(f"Section Comparison Analysis for {term_display}", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_semester_comparison(self, semester_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of semester comparisons.

        Args:
            semester_data: Semester comparison data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract semester metrics and comparisons
        semester_metrics = semester_data.get("semester_metrics", {})
        semester_comparisons = semester_data.get("semester_comparisons", [])
        
        if not semester_metrics:
            logger.warning("No semester metrics data available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))
        
        # Plot 1: Metrics by Semester
        # Sort semesters chronologically
        sorted_semesters = sorted(semester_metrics.keys(), 
                                 key=lambda x: (semester_metrics[x].get("year", 0), 
                                               1 if semester_metrics[x].get("term") == "Spring" else 2))
        
        if sorted_semesters:
            # Extract data for plotting
            sem_labels = [f"{semester_metrics[s].get('term')} {semester_metrics[s].get('year')}" 
                        for s in sorted_semesters]
            ideas_per_team = [semester_metrics[s].get("avg_ideas_per_team", 0) for s in sorted_semesters]
            steps_per_team = [semester_metrics[s].get("avg_steps_per_team", 0) for s in sorted_semesters]
            progress_values = [semester_metrics[s].get("avg_idea_progress", 0) for s in sorted_semesters]
            tool_versions = [semester_metrics[s].get("tool_version") for s in sorted_semesters]
            
            # Create combined line and bar chart
            # Bars for ideas and steps
            x = np.arange(len(sem_labels))
            width = 0.35
            
            bars1_1 = ax1.bar(x - width/2, ideas_per_team, width, label='Ideas per Team', color='steelblue')
            bars1_2 = ax1.bar(x + width/2, steps_per_team, width, label='Steps per Team', color='darkorange')
            
            # Add value labels
            self.add_value_labels(ax1, bars1_1, "{:.1f}")
            self.add_value_labels(ax1, bars1_2, "{:.1f}")
            
            # Line for progress
            ax1_twin = ax1.twinx()
            line1 = ax1_twin.plot(x, progress_values, 'ro-', linewidth=2, label='Avg Progress (%)')
            
            # Set up axis labels and ticks
            ax1.set_xlabel("Semester", fontsize=12)
            ax1.set_ylabel("Average Count", fontsize=12)
            ax1_twin.set_ylabel("Average Progress (%)", fontsize=12, color='r')
            ax1.set_title("Team Metrics by Semester", fontsize=14)
            ax1.set_xticks(x)
            ax1.set_xticklabels(sem_labels)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add tool version indicators
            for i, version in enumerate(tool_versions):
                tool_text = version if version else "None"
                ax1.annotate(f"Tool: {tool_text}", 
                           xy=(i, 0), 
                           xytext=(0, -30),
                           textcoords="offset points",
                           ha='center', 
                           rotation=45,
                           fontsize=9)
                
            # Highlight tool version changes
            prev_version = None
            for i, version in enumerate(tool_versions):
                if i > 0 and version != prev_version:
                    ax1.axvline(x=i-0.5, color='r', linestyle='--', alpha=0.3)
                prev_version = version
        else:
            ax1.text(0.5, 0.5, "No semester metrics available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
            
        # Plot 2: Semester Comparisons with Tool Version Changes
        if semester_comparisons:
            # Filter to only show comparisons with tool version changes
            tool_change_comparisons = [comp for comp in semester_comparisons 
                                     if comp.get("tool_version_change", False)]
            
            if tool_change_comparisons:
                # Extract data for plotting
                comp_labels = [comp.get("display_pair", "") for comp in tool_change_comparisons]
                ideas_diff = [comp.get("ideas_difference", 0) for comp in tool_change_comparisons]
                steps_diff = [comp.get("steps_difference", 0) for comp in tool_change_comparisons]
                progress_diff = [comp.get("progress_difference", 0) for comp in tool_change_comparisons]
                tool_changes = [comp.get("tool_versions", "") for comp in tool_change_comparisons]
                
                # Create grouped bar chart
                x = np.arange(len(comp_labels))
                width = 0.25
                
                # Create bars with appropriate colors
                ideas_colors = ['green' if val > 0 else 'red' for val in ideas_diff]
                steps_colors = ['green' if val > 0 else 'red' for val in steps_diff]
                progress_colors = ['green' if val > 0 else 'red' for val in progress_diff]
                
                bars2_1 = ax2.bar(x - width, ideas_diff, width, label='Ideas Difference', color=ideas_colors)
                bars2_2 = ax2.bar(x, steps_diff, width, label='Steps Difference', color=steps_colors)
                bars2_3 = ax2.bar(x + width, progress_diff, width, label='Progress Difference', color=progress_colors)
                
                # Add value labels
                self.add_value_labels(ax2, bars2_1, "{:.1f}")
                self.add_value_labels(ax2, bars2_2, "{:.1f}")
                self.add_value_labels(ax2, bars2_3, "{:.1f}")
                
                # Set up axis labels and ticks
                ax2.set_xlabel("Semester Comparison", fontsize=12)
                ax2.set_ylabel("Difference in Metrics", fontsize=12)
                ax2.set_title("Impact of Tool Version Changes", fontsize=14)
                ax2.set_xticks(x)
                ax2.set_xticklabels(comp_labels, rotation=45, ha='right')
                ax2.legend()
                
                # Add zero line
                ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                
                # Add tool version change annotations
                for i, version_change in enumerate(tool_changes):
                    ax2.annotate(version_change, 
                               xy=(i, 0), 
                               xytext=(0, -40),
                               textcoords="offset points",
                               ha='center', 
                               fontsize=9)
            else:
                ax2.text(0.5, 0.5, "No tool version changes to compare", 
                       ha='center', va='center', fontsize=12)
                ax2.axis('off')
        else:
            ax2.text(0.5, 0.5, "No semester comparison data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Semester Comparison Analysis", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_team_size_impact(self, size_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of team size impact.

        Args:
            size_data: Team size impact data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract size metrics and correlation data
        size_metrics = size_data.get("size_metrics", {})
        correlation_with_size = size_data.get("correlation_with_size", {})
        
        if not size_metrics:
            logger.warning("No team size metrics available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Plot 1: Metrics by Team Size
        # Sort sizes
        sorted_sizes = sorted([int(size) for size in size_metrics.keys()])
        
        if sorted_sizes:
            # Extract data for plotting
            size_labels = [str(size) for size in sorted_sizes]
            ideas_per_team = [size_metrics[str(size)].get("avg_ideas_per_team", 0) for size in sorted_sizes]
            steps_per_team = [size_metrics[str(size)].get("avg_steps_per_team", 0) for size in sorted_sizes]
            progress_values = [size_metrics[str(size)].get("avg_idea_progress", 0) for size in sorted_sizes]
            
            # Create line chart
            line1_1 = ax1.plot(size_labels, ideas_per_team, 'bo-', linewidth=2, label='Ideas per Team')
            line1_2 = ax1.plot(size_labels, steps_per_team, 'go-', linewidth=2, label='Steps per Team')
            
            # Add second y-axis for progress
            ax1_twin = ax1.twinx()
            line1_3 = ax1_twin.plot(size_labels, progress_values, 'ro-', linewidth=2, label='Avg Progress (%)')
            
            # Set up axis labels and ticks
            ax1.set_xlabel("Team Size (Number of Members)", fontsize=12)
            ax1.set_ylabel("Average Count", fontsize=12)
            ax1_twin.set_ylabel("Average Progress (%)", fontsize=12, color='r')
            ax1.set_title("Team Metrics by Team Size", fontsize=14)
            
            # Add grid
            ax1.grid(True, linestyle='--', alpha=0.3)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add team counts below x-axis
            for i, size in enumerate(sorted_sizes):
                team_count = size_metrics[str(size)].get("team_count", 0)
                ax1.annotate(f"n={team_count}", 
                           xy=(i, 0), 
                           xytext=(0, -30),
                           textcoords="offset points",
                           ha='center', 
                           fontsize=9)
        else:
            ax1.text(0.5, 0.5, "No team size metrics available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
            
        # Plot 2: Per-Member Metrics by Team Size
        if sorted_sizes:
            # Extract data for plotting
            ideas_per_member = [size_metrics[str(size)].get("avg_ideas_per_member", 0) for size in sorted_sizes]
            steps_per_member = [size_metrics[str(size)].get("avg_steps_per_member", 0) for size in sorted_sizes]
            
            # Create line chart
            line2_1 = ax2.plot(size_labels, ideas_per_member, 'bo-', linewidth=2, label='Ideas per Member')
            line2_2 = ax2.plot(size_labels, steps_per_member, 'go-', linewidth=2, label='Steps per Member')
            
            # Set up axis labels and ticks
            ax2.set_xlabel("Team Size (Number of Members)", fontsize=12)
            ax2.set_ylabel("Average Per-Member Count", fontsize=12)
            ax2.set_title("Per-Member Productivity by Team Size", fontsize=14)
            
            # Add grid
            ax2.grid(True, linestyle='--', alpha=0.3)
            
            # Add legend
            ax2.legend(loc='upper right')
            
            # Add correlation information
            corr_ideas = correlation_with_size.get("ideas_per_member", {})
            corr_steps = correlation_with_size.get("steps_per_member", {})
            
            if corr_ideas and corr_steps:
                corr_text = (
                    f"Correlation with Team Size:\n"
                    f"Ideas per Member: {corr_ideas.get('correlation', 0):.2f} "
                    f"({corr_ideas.get('strength', '')} {corr_ideas.get('direction', '')})\n"
                    f"Steps per Member: {corr_steps.get('correlation', 0):.2f} "
                    f"({corr_steps.get('strength', '')} {corr_steps.get('direction', '')})"
                )
                
                ax2.text(0.05, 0.05, corr_text,
                       transform=ax2.transAxes,
                       fontsize=10,
                       verticalalignment='bottom',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        else:
            ax2.text(0.5, 0.5, "No per-member metrics available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Team Size Impact Analysis", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_work_distribution(self, distribution_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of work distribution within teams.

        Args:
            distribution_data: Work distribution data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract distribution data
        gini_distribution = distribution_data.get("overall_gini_distribution", {})
        collaboration_patterns = distribution_data.get("collaboration_patterns", {})
        semester_patterns = distribution_data.get("semester_patterns", {})
        
        if not gini_distribution and not collaboration_patterns:
            logger.warning("No work distribution data available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Plot 1: Collaboration Patterns Distribution
        if collaboration_patterns:
            # Extract data for plotting
            patterns = list(collaboration_patterns.keys())
            counts = list(collaboration_patterns.values())
            
            # Create pie chart
            colors = ['darkgreen', 'lightgreen', 'gold', 'tomato']
            wedges, texts, autotexts = ax1.pie(counts, labels=patterns, 
                                             autopct="%1.1f%%", startangle=90, 
                                             colors=colors)
            
            # Customize text
            for text in texts:
                text.set_size(10)
            for autotext in autotexts:
                autotext.set_size(9)
                
            ax1.set_title("Team Collaboration Patterns", fontsize=14)
            ax1.axis('equal')  # Equal aspect ratio ensures circular pie
            
            # Add raw counts
            legend_labels = [f"{pattern} ({count})" for pattern, count in zip(patterns, counts)]
            ax1.legend(wedges, legend_labels, loc="best", bbox_to_anchor=(0.9, 0))
        else:
            ax1.text(0.5, 0.5, "No collaboration pattern data available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
        
        # Plot 2: Gini Coefficients by Semester
        if semester_patterns:
            # Sort semesters chronologically
            sorted_semesters = sorted(semester_patterns.keys())
            
            if sorted_semesters:
                # Extract data for plotting
                sem_labels = []
                avg_gini = []
                tool_versions = []
                
                for term_key in sorted_semesters:
                    # Get term/year from key
                    parts = term_key.split('_')
                    if len(parts) >= 2:
                        term = parts[0]
                        year = parts[1]
                        sem_labels.append(f"{term} {year}")
                    else:
                        sem_labels.append(term_key)
                    
                    # Get average Gini and tool version
                    avg_gini.append(semester_patterns[term_key].get("avg_gini", 0))
                    
                    # Determine tool version (would need to be added to data structure)
                    tool_versions.append("Unknown")
                
                # Create bar chart
                bars = ax2.bar(sem_labels, avg_gini, color='purple')
                
                # Add value labels
                self.add_value_labels(ax2, bars, "{:.2f}")
                
                # Set up axis labels and ticks
                ax2.set_xlabel("Semester", fontsize=12)
                ax2.set_ylabel("Average Gini Coefficient", fontsize=12)
                ax2.set_title("Work Distribution Inequality by Semester", fontsize=14)
                ax2.set_ylim(0, 1)  # Gini coefficient range is 0-1
                
                # Rotate x-axis labels for better readability
                plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
                
                # Add explanatory note
                ax2.text(0.5, -0.15, 
                       "Lower values indicate more equal work distribution", 
                       ha='center', va='center', transform=ax2.transAxes,
                       bbox=dict(facecolor='lightyellow', alpha=0.5, boxstyle='round'))
            else:
                ax2.text(0.5, 0.5, "No semester pattern data available", 
                       ha='center', va='center', fontsize=12)
                ax2.axis('off')
        else:
            ax2.text(0.5, 0.5, "No semester pattern data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Work Distribution Analysis", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)

    def _visualize_tool_impact(self, tool_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of tool version impact.

        Args:
            tool_data: Tool version impact data
            filename: Base filename for saving

        Returns:
            Path to the visualization file
        """
        # Extract tool version metrics and improvements
        version_metrics = tool_data.get("version_metrics", {})
        version_improvements = tool_data.get("version_improvements", [])
        
        if not version_metrics:
            logger.warning("No tool version metrics available for visualization")
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Plot 1: Metrics by Tool Version
        # Define tool versions in order
        tool_versions = [None, "v1", "v2"]  # Expected progression
        tool_labels = ["No Tool", "v1", "v2"]
        
        # Filter to versions with data
        valid_versions = []
        valid_labels = []
        
        for v, label in zip(tool_versions, tool_labels):
            if v in version_metrics:
                valid_versions.append(v)
                valid_labels.append(label)
        
        if valid_versions:
            # Extract data for plotting
            ideas_per_team = [version_metrics[v].get("avg_ideas_per_team", 0) for v in valid_versions]
            steps_per_team = [version_metrics[v].get("avg_steps_per_team", 0) for v in valid_versions]
            progress_values = [version_metrics[v].get("avg_idea_progress", 0) for v in valid_versions]
            
            # Set up bar positions
            x = np.arange(len(valid_labels))
            width = 0.35
            
            # Create grouped bar chart
            bars1_1 = ax1.bar(x - width/2, ideas_per_team, width, label='Ideas per Team', color='steelblue')
            bars1_2 = ax1.bar(x + width/2, steps_per_team, width, label='Steps per Team', color='darkorange')
            
            # Add value labels
            self.add_value_labels(ax1, bars1_1, "{:.1f}")
            self.add_value_labels(ax1, bars1_2, "{:.1f}")
            
            # Add progress line on secondary axis
            ax1_twin = ax1.twinx()
            line1 = ax1_twin.plot(x, progress_values, 'ro-', linewidth=2, label='Avg Progress (%)')
            
            # Set up axis labels and ticks
            ax1.set_xlabel("Tool Version", fontsize=12)
            ax1.set_ylabel("Average Count", fontsize=12)
            ax1_twin.set_ylabel("Average Progress (%)", fontsize=12, color='r')
            ax1.set_title("Team Metrics by Tool Version", fontsize=14)
            ax1.set_xticks(x)
            ax1.set_xticklabels(valid_labels)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add semester counts
            for i, v in enumerate(valid_versions):
                sem_count = version_metrics[v].get("semester_count", 0)
                if sem_count:
                    semesters = version_metrics[v].get("semesters", [])
                    sem_list = ", ".join(semesters) if len(semesters) <= 2 else f"{semesters[0]}... ({len(semesters)} semesters)"
                    ax1.annotate(f"n={sem_count} ({sem_list})", 
                               xy=(i, -0.5), 
                               xytext=(0, -30),
                               textcoords="offset points",
                               ha='center', 
                               fontsize=8)
        else:
            ax1.text(0.5, 0.5, "No valid tool version metrics available", 
                   ha='center', va='center', fontsize=12)
            ax1.axis('off')
            
        # Plot 2: Version Improvements
        if version_improvements:
            # Extract data for plotting
            version_pairs = [f"{imp.get('from_version')} → {imp.get('to_version')}" for imp in version_improvements]
            ideas_pct = [imp.get("ideas_percent_change", 0) for imp in version_improvements]
            steps_pct = [imp.get("steps_percent_change", 0) for imp in version_improvements]
            progress_pct = [imp.get("progress_percent_change", 0) for imp in version_improvements]
            
            # Set up bar positions
            x = np.arange(len(version_pairs))
            width = 0.25
            
            # Create grouped bar chart with appropriate colors
            ideas_colors = ['green' if val > 0 else 'red' for val in ideas_pct]
            steps_colors = ['green' if val > 0 else 'red' for val in steps_pct]
            progress_colors = ['green' if val > 0 else 'red' for val in progress_pct]
            
            bars2_1 = ax2.bar(x - width, ideas_pct, width, label='Ideas per Team', color=ideas_colors)
            bars2_2 = ax2.bar(x, steps_pct, width, label='Steps per Team', color=steps_colors)
            bars2_3 = ax2.bar(x + width, progress_pct, width, label='Progress', color=progress_colors)
            
            # Add value labels
            self.add_value_labels(ax2, bars2_1, "{:.1f}%")
            self.add_value_labels(ax2, bars2_2, "{:.1f}%")
            self.add_value_labels(ax2, bars2_3, "{:.1f}%")
            
            # Set up axis labels and ticks
            ax2.set_xlabel("Tool Version Change", fontsize=12)
            ax2.set_ylabel("Percent Change in Metrics", fontsize=12)
            ax2.set_title("Impact of Tool Version Changes (% Improvement)", fontsize=14)
            ax2.set_xticks(x)
            ax2.set_xticklabels(version_pairs)
            
            # Add zero line
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add legend
            ax2.legend()
            
            # Add explanatory note
            ax2.text(0.5, -0.15, 
                   "Green bars indicate improvements, red bars indicate declines", 
                   ha='center', va='center', transform=ax2.transAxes,
                   bbox=dict(facecolor='lightyellow', alpha=0.5, boxstyle='round'))
        else:
            ax2.text(0.5, 0.5, "No version improvement data available", 
                   ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
        # Add overall title
        fig.suptitle("Tool Version Impact Analysis", fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for overall title
        
        # Save figure
        return self.save_figure(filename)
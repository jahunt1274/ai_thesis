"""
Usage visualizer for the AI thesis analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("usage_visualizer")


class UsageVisualizer(BaseVisualizer):
    """Visualizes usage analysis results."""

    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for usage analysis.
        
        Args:
            data: Usage analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            'idea_counts': (self._visualize_idea_counts, {'data_key': 'idea_generation'}),
            'ideas_by_ranking': (self._visualize_ideas_by_ranking, {'data_key': 'idea_generation.ideas_by_ranking'}),
            'engagement_levels': (self._visualize_engagement_levels, {'data_key': 'engagement_levels.engagement_levels'}),
            'framework_engagement': (self._visualize_framework_engagement, {'data_key': 'engagement_levels.framework_engagement'}),
            'monthly_active_users': (self._visualize_monthly_active_users, 
                                    {'data_key': 'engagement_levels.temporal_engagement.monthly_active_users'}),
            'iteration_patterns': (self._visualize_iteration_patterns, {'data_key': 'idea_characterization.iteration_patterns'}),
            'progress_stats': (self._visualize_progress_stats, {'data_key': 'idea_characterization.progress_stats'}),
            'framework_counts': (self._visualize_framework_counts, {'data_key': 'framework_usage.framework_counts'}),
            'framework_completion': (self._visualize_framework_completion, 
                                    {'data_key': 'framework_usage'}),
            'daily_usage': (self._visualize_daily_usage, {'data_key': 'timeline.daily_counts'}),
            'monthly_usage': (self._visualize_monthly_usage, {'data_key': 'timeline.monthly_stats'})
        }
        
        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)
    
    def _visualize_idea_counts(self, idea_generation: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of idea counts.
        
        Args:
            idea_generation: Idea generation statistics
            filename: name for the file to be saved
            
        Returns:
            figure
        """
        # Extract data
        total_ideas = idea_generation.get('total_ideas', 0)
        unique_owners = idea_generation.get('unique_owners', 0)
        max_ideas_per_owner = idea_generation.get('max_ideas_per_owner', 0)
        avg_ideas_per_owner = idea_generation.get('avg_ideas_per_owner', 0)
        
        # Create bar chart for counts
        labels = ['Total Ideas', 'Unique Owners', 'Max Ideas/Owner']
        values = [total_ideas, unique_owners, max_ideas_per_owner]
        colors = ['royalblue', 'green', 'orange']
        
        plt_fig = self.setup_figure(
            figsize=(10, 6),
            title='Idea Generation Overview'
        )
        
        result = self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='Idea Generation Overview',
            ylabel='Count',
            color=colors
        )
        
        # Add annotation for average ideas per owner
        if result:
            plt_fig = self.setup_figure()
            plt.annotate(f'Avg Ideas per Owner: {avg_ideas_per_owner:.2f}', 
                    xy=(0.5, 0.05), xycoords='figure fraction',
                    bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8),
                    ha='center')
            plt.close()
            
        return result
    
    def _visualize_ideas_by_ranking(self, ideas_by_ranking: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of ideas by ranking.
        
        Args:
            ideas_by_ranking: Counts of ideas by ranking
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        if not ideas_by_ranking:
            return None
        
        # Convert ranking keys to integers for proper sorting
        rankings = []
        counts = []
        
        # Extract and sort data
        for ranking, count in sorted(ideas_by_ranking.items(), 
                                    key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                                        int(float(item[0])) if isinstance(item[0], str) else item[0]
                                    )):
            rankings.append(str(ranking))
            counts.append(count)
        
        # Create a color gradient based on ranking
        colors = self.get_color_gradient(len(rankings), 'sequential')
        
        # Create bar chart
        result = self.create_bar_chart(
            labels=rankings,
            values=counts,
            filename=filename,
            title='Ideas by Ranking',
            xlabel='Idea Ranking',
            ylabel='Number of Ideas',
            color=colors
        )
        
        # Add explanation text
        if result:
            plt_fig = self.setup_figure()
            plt.figtext(0.5, 0.01, 
                      'Ranking represents the nth idea created by a user (1=first idea, 2=second idea, etc.)',
                      ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
            plt.close()
            
        return result
    
    def _visualize_engagement_levels(self, engagement_levels: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user engagement levels.
        
        Args:
            engagement_levels: Counts by engagement level
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        if not engagement_levels:
            return None
        
        # Define custom labels and colors
        label_map = {
            'high': 'High (>5 ideas)',
            'medium': 'Medium (2-5 ideas)',
            'low': 'Low (1 idea)',
            'none': 'None (0 ideas)'
        }
        
        # Extract data in order
        ordered_levels = ['high', 'medium', 'low', 'none']
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
            title='User Engagement Levels',
            colors=colors,
            explode=explode
        )
    
    def _visualize_framework_engagement(self, framework_engagement: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of framework engagement.
        
        Args:
            framework_engagement: Counts by framework
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        if not framework_engagement:
            return None
        
        # Order of frameworks to display
        frameworks = ['disciplined-entrepreneurship', 'startup-tactics', 
                     'both_frameworks', 'no_framework']
        
        # Custom labels
        label_map = {
            'both_frameworks': 'Both Frameworks',
            'no_framework': 'No Framework',
            'disciplined-entrepreneurship': 'Disciplined Entrepreneurship',
            'startup-tactics': 'Startup Tactics'
        }
        
        # Extract data
        labels = []
        values = []
        
        for framework in frameworks:
            if framework in framework_engagement:
                labels.append(label_map.get(framework, framework))
                values.append(framework_engagement[framework])
        
        # Define colors
        colors = ['dodgerblue', 'darkorange', 'mediumseagreen', 'lightgray']
        
        # Create bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='Framework Engagement',
            ylabel='Number of Users',
            color=colors
        )
    
    def _visualize_monthly_active_users(self, monthly_active_users: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of monthly active users.
        
        Args:
            monthly_active_users: Active users by month
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        # Need at least 2 data points for a meaningful timeline
        if len(monthly_active_users) < 2:
            return None
        
        # Convert string dates to datetime objects
        dates = []
        counts = []
        
        for date_str, count in sorted(monthly_active_users.items()):
            date_obj = self.parse_date(f"{date_str}-01")  # Add day to create valid date
            if date_obj:
                dates.append(date_obj)
                counts.append(count)
        
        # Create line chart
        return self.create_line_chart(
            x=dates,
            y=counts,
            filename=filename,
            title='Monthly Active Users',
            xlabel='Month',
            ylabel='Number of Active Users',
            color='crimson',
            add_trend=True,
            fill=True,
            date_format='%b %Y'
        )
    
    def _visualize_iteration_patterns(self, iteration_patterns: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of idea iteration patterns.
        
        Args:
            iteration_patterns: Iteration pattern data
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        # Check for users_by_max_iteration data
        if 'users_by_max_iteration' not in iteration_patterns:
            return None
        
        users_by_max_iteration = iteration_patterns['users_by_max_iteration']
        
        # Extract and sort data
        labels = []
        values = []
        
        for iteration, count in sorted(
            users_by_max_iteration.items(), 
            key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                int(float(item[0])) if isinstance(item[0], str) else item[0]
            )):
            if iteration == 0:
                label = "No iterations"
            elif iteration == 1:
                label = "1 iteration"
            else:
                label = f"{iteration} iterations"
            
            labels.append(label)
            values.append(count)
        
        # Create a colormap gradient based on number of iterations
        colors = self.get_color_gradient(len(values), 'sequential')
        
        # Create bar chart
        result = self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='Users by Maximum Iteration Count',
            ylabel='Number of Users',
            color=colors,
            rotation=45
        )
        
        # Add explanation
        if result:
            plt_fig = self.setup_figure()
            plt.figtext(0.5, 0.01, 
                      'Iterations refer to the number of different ideas created by a user',
                      ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
            plt.close()
            
        return result
    
    def _visualize_progress_stats(self, progress_stats: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of idea progress statistics.
        
        Args:
            progress_stats: Progress statistics data
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        if not progress_stats:
            return None
        
        # Setup figure with multiple subplots
        fig, (ax1, ax2) = self.setup_subplots(2, 1, figsize=(12, 12))
        
        # Plot 1: Progress Distribution
        if 'progress_distribution' in progress_stats:
            progress_distribution = progress_stats['progress_distribution']
            
            # Extract data
            progress_levels = []
            counts = []
            
            # Sort by progress level
            for level, count in sorted(progress_distribution.items(), 
                                      key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                                          int(float(item[0])) if isinstance(item[0], str) else item[0]
                                      )):
                # Format the label
                if level == 0:
                    label = "0%"
                elif int(level) == 100:
                    label = "100%"
                else:
                    label = f"{level}%-{int(level)+9}%"
                
                progress_levels.append(label)
                counts.append(count)
            
            # Create color gradient
            colors = self.get_color_gradient(len(progress_levels), 'sequential')
            
            # Create bar chart in first subplot
            bars = ax1.bar(progress_levels, counts, color=colors)
            
            # Add value labels
            self.add_value_labels(ax1, bars)
            
            # Add title and labels
            ax1.set_title('Progress Distribution', fontsize=14)
            ax1.set_xlabel('Progress Level', fontsize=12)
            ax1.set_ylabel('Number of Ideas', fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: Framework Progress Comparison
        if 'framework_progress' in progress_stats:
            framework_progress = progress_stats['framework_progress']
            
            # Extract data
            frameworks = []
            avg_progress = []
            total_ideas = []
            
            for framework, data in framework_progress.items():
                if data.get('total_ideas', 0) > 0:
                    frameworks.append(framework)
                    avg_progress.append(data.get('avg_progress', 0))
                    total_ideas.append(data.get('total_ideas', 0))
            
            # Create grouped bar chart
            x = np.arange(len(frameworks))
            width = 0.35
            
            # Plot average progress
            bars1 = ax2.bar(x - width/2, avg_progress, width, label='Avg Progress %', color='lightseagreen')
            
            # Create twin axis for total ideas
            ax2_twin = ax2.twinx()
            bars2 = ax2_twin.bar(x + width/2, total_ideas, width, label='Total Ideas', color='coral')
            
            # Add labels and title
            ax2.set_title('Framework Progress Comparison', fontsize=14)
            ax2.set_xticks(x)
            ax2.set_xticklabels(frameworks)
            ax2.set_xlabel('Framework', fontsize=12)
            ax2.set_ylabel('Average Progress %', fontsize=12)
            ax2_twin.set_ylabel('Total Ideas', fontsize=12)
            
            # Set y-limits
            ax2.set_ylim(0, max(100, max(avg_progress) * 1.1))
            ax2_twin.set_ylim(0, max(total_ideas) * 1.1)
            
            # Add value labels
            self.add_value_labels(ax2, bars1, '{:.1f}%')
            self.add_value_labels(ax2_twin, bars2, '{:.0f}')
            
            # Add legend
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        # Add overall stats as text
        fig.text(0.5, 0.01, 
                f"Total Ideas: {progress_stats.get('total_ideas', 0)} | " +
                f"Average Progress: {progress_stats.get('avg_progress', 0):.1f}%",
                ha="center", fontsize=12, bbox={"facecolor":"lightblue", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Save figure
        return self.save_figure(filename)
    
    def _visualize_framework_counts(self, framework_counts: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of framework usage counts.
        
        Args:
            framework_counts: Counts by framework
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        if not framework_counts:
            return None
        
        # Extract data
        frameworks = []
        counts = []
        
        for framework, count in framework_counts.items():
            if count > 0:  # Filter out unused frameworks
                frameworks.append(framework)
                counts.append(count)
        
        # Define colors for known frameworks
        colors = ['dodgerblue' if f == 'disciplined-entrepreneurship' else
                 'darkorange' if f == 'startup-tactics' else
                 'gray' for f in frameworks]
        
        # Create bar chart
        return self.create_bar_chart(
            labels=frameworks,
            values=counts,
            filename=filename,
            title='Framework Usage',
            ylabel='Number of Ideas',
            color=colors,
            rotation=45
        )
    
    def _visualize_framework_completion(self, framework_usage: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of framework completion rates.
        
        Args:
            framework_usage: Frmework completion statistics
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        # Extract data
        de_completion = framework_usage.get('de_completion', {})
        st_completion = framework_usage.get('st_completion', {})
        
        if not de_completion and not st_completion:
            return None
        
        # Setup figure with multiple subplots
        fig, axes = self.setup_subplots(2, 2, figsize=(14, 12))
        
        # Extract data
        frameworks = ['disciplined-entrepreneurship', 'startup-tactics']
        completions = [de_completion, st_completion]
        colors = ['dodgerblue', 'darkorange']
        
        # Completion rates (top left)
        completion_rates = [c.get('completion_rate', 0) * 100 for c in completions]
        avg_progress = [c.get('avg_progress', 0) for c in completions]
        
        ax = axes[0, 0]
        bars = ax.bar(frameworks, completion_rates, color=colors, alpha=0.7)
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.1f}%')
        
        ax.set_title('Completion Rates', fontsize=16)
        ax.set_ylabel('Completion Rate (%)', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Average progress (top right)
        ax = axes[0, 1]
        bars = ax.bar(frameworks, avg_progress, color=colors, alpha=0.7)
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.1f}%')
        
        ax.set_title('Average Progress', fontsize=16)
        ax.set_ylabel('Progress (%)', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Completed vs. Incomplete (bottom row)
        for i, (framework, completion, color) in enumerate(zip(frameworks, completions, colors)):
            ax = axes[1, i]
            
            # Extract data
            completed = completion.get('completed_ideas', 0)
            incomplete = completion.get('total_ideas', 0) - completed
            
            # Data for pie chart
            sizes = [completed, incomplete]
            labels = ['Completed', 'In Progress']
            
            # Create pie chart
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                  startangle=90, colors=[color, 'lightgray'])
            
            # Equal aspect ratio ensures the pie chart is circular
            ax.axis('equal')
            
            # Add title and counts
            ax.set_title(f'{framework}\nTotal Ideas: {completion.get("total_ideas", 0)}', fontsize=14)
        
        plt.tight_layout()
        
        # Save figure
        return self.save_figure(filename)
    
    def _visualize_daily_usage(self, daily_counts: Dict[str, Dict[str, Any]], filename: str) -> Optional[str]:
        """
        Create visualization of daily usage patterns.
        
        Args:
            daily_counts: Daily activity statistics
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
        # Need at least a few days of data for a meaningful visualization
        if len(daily_counts) < 5:
            return None
        
        # Setup figure with multiple subplots
        fig, (ax1, ax2) = self.setup_subplots(2, 1, figsize=(14, 8))
        
        # Extract data
        dates = []
        idea_counts = []
        avg_progress_values = []
        
        for date_str, data in sorted(daily_counts.items()):
            date_obj = self.parse_date(date_str)
            if date_obj:
                dates.append(date_obj)
                idea_counts.append(data.get('count', 0))
                avg_progress_values.append(data.get('avg_progress', 0))
        
        # Plot idea counts (top)
        ax1.plot(dates, idea_counts, marker='o', linestyle='-', color='royalblue', 
                linewidth=2, markersize=6, alpha=0.8)
        
        # Format x-axis as dates
        self.format_date_axis(ax1)
        
        # Add title and labels
        ax1.set_title('Daily Idea Creation', fontsize=14)
        ax1.set_ylabel('Number of Ideas', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot average progress (bottom)
        ax2.plot(dates, avg_progress_values, marker='s', linestyle='-', color='green', 
                linewidth=2, markersize=6, alpha=0.8)
        
        # Format x-axis as dates
        self.format_date_axis(ax2)
        
        # Add title and labels
        ax2.set_title('Daily Average Progress', fontsize=14)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Average Progress (%)', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save figure
        return self.save_figure(filename)
    
    def _visualize_monthly_usage(self, monthly_stats: Dict[str, Dict[str, Any]], filename: str) -> Optional[str]:
        """
        Create visualization of monthly usage patterns.
        
        Args:
            monthly_stats: Monthly statistics
            filename: name for the file to be saved
            
        Returns:
            Figure
        """
       # Need at least a few months of data
        if len(monthly_stats) < 2:
            return None
        
        # Setup figure with multiple subplots
        fig, (ax1, ax2) = self.setup_subplots(2, 1, figsize=(14, 8))
        
        # Extract data
        months = []
        total_ideas = []
        avg_ideas_per_day = []
        
        for month_str, data in sorted(monthly_stats.items()):
            date_obj = self.parse_date(f"{month_str}-01")  # Add day to create valid date
            if date_obj:
                months.append(date_obj)
                total_ideas.append(data.get('total_ideas', 0))
                avg_ideas_per_day.append(data.get('avg_ideas_per_day', 0))
        
        # Plot total ideas (top)
        bars = ax1.bar(months, total_ideas, color='cornflowerblue', alpha=0.7)
        
        # Format x-axis as dates
        self.format_date_axis(ax1)
        
        # Add trend line
        self.add_trend_line(ax1, months, total_ideas, "Trend")
        
        # Add title and labels
        ax1.set_title('Monthly Total Ideas', fontsize=14)
        ax1.set_ylabel('Number of Ideas', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Plot average ideas per day (bottom)
        bars = ax2.bar(months, avg_ideas_per_day, color='mediumseagreen', alpha=0.7)
        
        # Format x-axis as dates
        self.format_date_axis(ax2)
        
        # Add title and labels
        ax2.set_title('Average Ideas Per Day', fontsize=14)
        ax2.set_xlabel('Month', fontsize=12)
        ax2.set_ylabel('Avg Ideas/Day', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save figure
        return self.save_figure(filename)
"""
Engagement visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("engagement_visualizer")


class EngagementVisualizer(BaseVisualizer):
    """Visualizes engagement analysis results."""
    
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for engagement analysis.
        
        Args:
            data: Engagement analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            'step_distribution': (self._visualize_step_distribution, 
                                 {'data_key': 'process_completion.step_distribution'}),
            'framework_completion': (self._visualize_framework_completion, 
                                   {'data_key': 'process_completion.completion_by_framework'}),
            'step_progression': (self._visualize_step_progression, 
                               {'data_key': 'dropout_points'}),
            'monthly_activity': (self._visualize_monthly_activity, 
                               {'data_key': 'time_based_engagement.monthly_activity'}),
            'seasonal_patterns': (self._visualize_seasonal_patterns, 
                                {'data_key': 'time_based_engagement.seasonal_patterns'}),
            'step_intervals': (self._visualize_step_intervals, 
                             {'data_key': 'time_based_engagement.step_intervals'}),
            'user_type_cohorts': (self._visualize_user_type_cohorts, 
                                {'data_key': 'cohort_comparison.by_user_type'}),
            'institution_cohorts': (self._visualize_institution_cohorts, 
                                  {'data_key': 'cohort_comparison.by_institution'}),
            'enrollment_cohorts': (self._visualize_enrollment_cohorts, 
                                 {'data_key': 'cohort_comparison.by_enrollment'})
        }
        
        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)
    
    def _visualize_step_distribution(self, step_distribution: Dict[str, int], filename: str) -> Optional[str]:
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
        
        for step_count, count in sorted(step_distribution.items(), 
                                      key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                                          int(float(item[0])) if isinstance(item[0], str) else item[0]
                                      )):
            steps.append(str(step_count))
            counts.append(count)
        
        # Create color gradient based on step count
        colors = self.get_color_gradient(len(steps), 'viridis')
        
        # Setup figure
        fig = self.setup_figure(
            figsize=(12, 7),
            title='Distribution of Ideas by Number of Steps Completed',
            xlabel='Number of Steps',
            ylabel='Number of Ideas'
        )
        
        # Create bar chart
        bars = plt.bar(steps, counts, color=colors)
        
        # Add value labels
        self.add_value_labels(plt.gca(), bars)
        
        # Calculate mean and median steps
        if steps and counts:
            steps_numeric = [int(step) for step in steps]
            total_ideas = sum(counts)
            weighted_sum = sum(s * c for s, c in zip(steps_numeric, counts))
            mean_steps = weighted_sum / total_ideas if total_ideas > 0 else 0
            
            # Add mean as a vertical line
            plt.axvline(x=mean_steps, color='red', linestyle='--', alpha=0.7,
                       label=f'Mean: {mean_steps:.1f} steps')
            plt.legend()
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_framework_completion(self, completion_by_framework: Dict[str, Dict[str, Any]], 
                                      filename: str) -> Optional[str]:
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
            frameworks.append(framework)
            avg_completion.append(data.get('avg_completion', 0))
            total_ideas.append(data.get('total_ideas', 0))
        
        # Create grouped bar chart using the enhanced BaseVisualizer method
        data_dict = {
            'Avg Completion': avg_completion,
            'Total Ideas': total_ideas
        }
        
        colors = {
            'Avg Completion': 'teal',
            'Total Ideas': 'darkorange'
        }
        
        return self.create_grouped_bar_chart(
            labels=frameworks,
            data_dict=data_dict,
            filename=filename,
            title='Framework Completion Comparison',
            ylabel='Value',
            colors=colors,
            add_value_labels=True,
            format_str='{:.2f}'
        )
    
    def _visualize_step_progression(self, dropout_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of step progression and dropout points.
        
        Args:
            dropout_data: Step progression and dropout data
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        step_progression = dropout_data.get('step_progression', {})
        final_steps = dropout_data.get('final_steps', {})
        dropout_rates = dropout_data.get('dropout_rates', {})
        
        # Identify common steps between progression and final steps
        common_steps = set(step_progression.keys()).intersection(set(final_steps.keys()))
        
        # Need at least a few steps for meaningful visualization
        if len(common_steps) < 3:
            logger.warning("Not enough step data for progression visualization")
            return None
        
        # Create figure with multiple subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 15))
        
        # Sort steps by progression count to identify the common path
        sorted_steps = sorted(step_progression.items(), key=lambda x: x[1], reverse=True)
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
        display_steps = [s[:30] + '...' if len(s) > 30 else s for s in steps_for_funnel]
        
        # Create horizontal bar chart for funnel
        bars1 = ax1.barh(display_steps, progression_counts, color='steelblue')
        
        # Add value labels
        for bar in bars1:
            width = bar.get_width()
            ax1.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center')
        
        ax1.set_title('Step Progression (Ideas that reached each step)', fontsize=14)
        ax1.set_xlabel('Number of Ideas', fontsize=12)
        
        # Visualization 2: Final Steps (where users stopped)
        top_final_steps = sorted(final_steps.items(), key=lambda x: x[1], reverse=True)[:10]
        final_step_names = [step for step, _ in top_final_steps]
        final_step_counts = [count for _, count in top_final_steps]
        
        # Truncate long step names
        display_final_steps = [s[:30] + '...' if len(s) > 30 else s for s in final_step_names]
        
        # Create horizontal bar chart for final steps
        bars2 = ax2.barh(display_final_steps, final_step_counts, color='coral')
        
        # Add value labels
        for bar in bars2:
            width = bar.get_width()
            ax2.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center')
        
        ax2.set_title('Final Steps (Where Users Stopped)', fontsize=14)
        ax2.set_xlabel('Number of Ideas', fontsize=12)
        
        # Visualization 3: Dropout Rates
        dropout_step_names = []
        dropout_pcts = []
        
        # Get dropout rates for top final steps
        for step in final_step_names:
            if step in dropout_rates:
                dropout_step_names.append(step)
                dropout_pcts.append(dropout_rates[step] * 100)  # Convert to percentage
        
        # Truncate long step names
        display_dropout_steps = [s[:30] + '...' if len(s) > 30 else s for s in dropout_step_names]
        
        # Sort by dropout rate
        sorted_indices = np.argsort(dropout_pcts)[::-1]  # Descending order
        sorted_steps = [display_dropout_steps[i] for i in sorted_indices]
        sorted_rates = [dropout_pcts[i] for i in sorted_indices]
        
        # Color bars by dropout rate (higher = more red)
        cmap = plt.cm.get_cmap('RdYlGn_r')
        colors = [cmap(rate/100) for rate in sorted_rates]
        
        bars3 = ax3.barh(sorted_steps, sorted_rates, color=colors)
        
        # Add value labels
        for bar in bars3:
            width = bar.get_width()
            ax3.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}%',
                    ha='left', va='center')
        
        ax3.set_title('Dropout Rates by Step', fontsize=14)
        ax3.set_xlabel('Dropout Rate (%)', fontsize=12)
        ax3.set_xlim(0, 100)
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_monthly_activity(self, monthly_activity: Dict[str, Dict[str, Any]], 
                                  filename: str) -> Optional[str]:
        """
        Create visualization of monthly activity.
        
        Args:
            monthly_activity: Monthly activity statistics
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Need at least a few months of data
        if len(monthly_activity) < 2:
            logger.warning("Not enough monthly activity data for visualization")
            return None
        
        # Create figure with multiple panels
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 15))
        
        # Convert string dates to datetime objects for proper timeline
        months = []
        steps = []
        ideas = []
        users = []
        
        for month_str, data in sorted(monthly_activity.items()):
            try:
                # Parse date (YYYY-MM format)
                month_obj = datetime.strptime(month_str, '%Y-%m')
                months.append(month_obj)
                steps.append(data.get('steps_count', 0))
                ideas.append(data.get('unique_ideas', 0))
                users.append(data.get('unique_users', 0))
            except (ValueError, KeyError):
                continue
        
        # Plot 1: Steps Count
        ax1.plot(months, steps, marker='o', linestyle='-', color='royalblue', 
                linewidth=2, markersize=8)
        ax1.fill_between(months, steps, alpha=0.3, color='royalblue')
        
        # Format x-axis as dates
        self.format_date_axis(ax1)
        
        # Add title and labels
        ax1.set_title('Monthly Steps Creation', fontsize=14)
        ax1.set_ylabel('Number of Steps', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Unique Ideas
        ax2.plot(months, ideas, marker='s', linestyle='-', color='green', 
               linewidth=2, markersize=8)
        ax2.fill_between(months, ideas, alpha=0.3, color='green')
        
        # Format x-axis as dates
        self.format_date_axis(ax2)
        
        # Add title and labels
        ax2.set_title('Monthly Unique Ideas', fontsize=14)
        ax2.set_ylabel('Number of Ideas', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 3: Unique Users
        ax3.plot(months, users, marker='d', linestyle='-', color='crimson', 
               linewidth=2, markersize=8)
        ax3.fill_between(months, users, alpha=0.3, color='crimson')
        
        # Format x-axis as dates
        self.format_date_axis(ax3)
        
        # Add title and labels
        ax3.set_title('Monthly Active Users', fontsize=14)
        ax3.set_xlabel('Month', fontsize=12)
        ax3.set_ylabel('Number of Users', fontsize=12)
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_seasonal_patterns(self, seasonal_patterns: Dict[str, Any], 
                                   filename: str) -> Optional[str]:
        """
        Create visualization of seasonal patterns.
        
        Args:
            seasonal_patterns: Seasonal pattern data
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Check if we have monthly averages
        if 'monthly_averages' not in seasonal_patterns or not seasonal_patterns['monthly_averages']:
            logger.warning("No monthly average data for seasonal patterns visualization")
            return None
        
        # Create figure with multiple panels
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Extract data for monthly averages
        monthly_avg = seasonal_patterns['monthly_averages']
        months = []
        avgs = []
        
        # Convert string months to datetime objects and numeric months
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for month_num, avg in sorted(monthly_avg.items()):
            try:
                month_idx = int(month_num) - 1  # 0-based index
                months.append(month_labels[month_idx])
                avgs.append(avg)
            except (ValueError, IndexError):
                continue
        
        # Define colors based on academic calendar
        colors = []
        for i, month in enumerate(months):
            if month in ['Jan', 'Feb', 'Aug', 'Sep']:  # Semester start
                colors.append('green')
            elif month in ['May', 'Dec']:  # Semester end
                colors.append('orange')
            elif month in ['Jun', 'Jul']:  # Summer
                colors.append('lightblue')
            else:
                colors.append('steelblue')
        
        # Plot 1: Monthly Averages (Bar Chart)
        bars = ax1.bar(months, avgs, color=colors)
        
        # Add value labels
        self.add_value_labels(ax1, bars, '{:.1f}')
        
        # Add title and labels
        ax1.set_title('Average Activity by Month', fontsize=14)
        ax1.set_xlabel('Month', fontsize=12)
        ax1.set_ylabel('Average Activity', fontsize=12)
        
        # Add semester annotations
        ax1.axvspan(-0.5, 1.5, alpha=0.2, color='green', label='Spring Semester Start')
        ax1.axvspan(4.5, 5.5, alpha=0.2, color='orange', label='Spring Semester End')
        ax1.axvspan(5.5, 7.5, alpha=0.2, color='lightblue', label='Summer Break')
        ax1.axvspan(7.5, 9.5, alpha=0.2, color='green', label='Fall Semester Start')
        ax1.axvspan(11.5, 12.5, alpha=0.2, color='orange', label='Fall Semester End')
        
        ax1.legend(loc='upper right')
        
        # Plot 2: Academic Calendar Patterns (Pie chart)
        academic_patterns = seasonal_patterns.get('academic_patterns', {})
        
        # Prepare data for pie chart
        labels = []
        values = []
        colors_pie = []
        
        patterns = [
            ('semester_start', 'Semester Start Peaks', 'green'),
            ('semester_end', 'Semester End Peaks', 'orange'),
            ('summer_slump', 'Summer Activity Drop', 'lightblue')
        ]
        
        for key, label, color in patterns:
            if academic_patterns.get(key, False):
                labels.append(label)
                values.append(1)
                colors_pie.append(color)
            else:
                labels.append(f"No {label}")
                values.append(1)
                colors_pie.append('lightgray')
        
        # Create pie chart
        if labels and values:
            ax2.pie(values, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                   startangle=90, wedgeprops={'edgecolor': 'w'})
            ax2.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
            ax2.set_title('Academic Calendar Patterns', fontsize=14)
        else:
            ax2.text(0.5, 0.5, "No academic calendar patterns detected",
                    ha='center', va='center', fontsize=14)
            ax2.axis('off')
        
        # Add peak months information
        peak_months = seasonal_patterns.get('peak_months', [])
        if peak_months:
            peak_month_labels = [month_labels[m-1] for m in peak_months if 1 <= m <= 12]
            peak_text = "Peak Activity Months: " + ", ".join(peak_month_labels)
            fig.text(0.5, 0.01, peak_text, ha='center', fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8))
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_step_intervals(self, step_intervals: Dict[str, Any], 
                                filename: str) -> Optional[str]:
        """
        Create visualization of time intervals between steps.
        
        Args:
            step_intervals: Step interval data
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Extract interval data
        all_intervals = []
        intervals_by_idea = step_intervals.get('intervals_by_idea', {})
        avg_interval = step_intervals.get('avg_interval_days', 0)
        max_interval = step_intervals.get('max_interval_days', 0)
        min_interval = step_intervals.get('min_interval_days', 0)
        
        # Collect all intervals for histogram
        for idea_id, intervals in intervals_by_idea.items():
            all_intervals.extend(intervals)
        
        # Need at least a few data points
        if len(all_intervals) < 5:
            logger.warning("Not enough interval data for step intervals visualization")
            return None
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Determine appropriate bins based on data range
        max_days = max(all_intervals) if all_intervals else 30
        if max_days <= 30:
            bins = np.arange(0, max_days + 3, 1)  # Daily bins up to 30 days
            xlabel = 'Days Between Steps'
        elif max_days <= 90:
            bins = np.arange(0, max_days + 7, 7)  # Weekly bins up to 90 days
            xlabel = 'Weeks Between Steps'
        else:
            bins = np.arange(0, max_days + 30, 30)  # Monthly bins for longer periods
            xlabel = 'Months Between Steps (approx)'
        
        # Plot 1: Histogram of intervals
        ax1.hist(all_intervals, bins=bins, color='mediumseagreen', alpha=0.7, edgecolor='black')
        
        # Add vertical line for average
        ax1.axvline(x=avg_interval, color='red', linestyle='--', linewidth=2,
                  label=f'Average: {avg_interval:.1f} days')
        
        # Add title and labels
        ax1.set_title('Distribution of Time Between Steps', fontsize=14)
        ax1.set_xlabel(xlabel, fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend()
        
        # Plot 2: Box plot of intervals by ideas with many steps
        # Select ideas with at least 3 intervals for meaningful box plots
        ideas_with_many_steps = {id_: intervals for id_, intervals in intervals_by_idea.items() 
                                if len(intervals) >= 3}
        
        if ideas_with_many_steps:
            # Sort by median interval and take top 10
            idea_medians = [(id_, np.median(intervals)) for id_, intervals in ideas_with_many_steps.items()]
            sorted_ideas = sorted(idea_medians, key=lambda x: x[1])
            
            # Take top 10 ideas with lowest median (most consistent)
            top_ideas = sorted_ideas[:10]
            
            # Prepare data for box plot
            box_data = []
            labels = []
            
            for i, (idea_id, _) in enumerate(top_ideas):
                box_data.append(intervals_by_idea[idea_id])
                labels.append(f"Idea {i+1}")
            
            # Create box plot
            ax2.boxplot(box_data, vert=False, labels=labels)
            
            # Add title and labels
            ax2.set_title('Step Intervals for Most Consistent Ideas', fontsize=14)
            ax2.set_xlabel('Days Between Steps', fontsize=12)
            
            # Add overall statistics as text
            ax2.text(0.05, 0.05, 
                    f"Min: {min_interval:.1f} days | Max: {max_interval:.1f} days | Avg: {avg_interval:.1f} days",
                    transform=ax2.transAxes,
                    bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8))
        else:
            # Not enough data for box plot
            ax2.text(0.5, 0.5, "Not enough ideas with multiple steps for box plot",
                    ha='center', va='center', fontsize=14)
            ax2.axis('off')
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_user_type_cohorts(self, user_type_cohorts: Dict[str, Dict[str, Any]], 
                                   filename: str) -> Optional[str]:
        """
        Create visualization of user type cohort engagement.
        
        Args:
            user_type_cohorts: Engagement metrics by user type
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Need at least a couple of cohorts
        if len(user_type_cohorts) < 2:
            logger.warning("Not enough user type cohorts for visualization")
            return None
        
        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Extract data
        cohort_names = list(user_type_cohorts.keys())
        
        # Limit to top 6 cohorts if there are many
        if len(cohort_names) > 6:
            # Sort by cohort size
            sorted_cohorts = sorted(user_type_cohorts.items(), 
                                  key=lambda x: x[1].get('cohort_size', 0), 
                                  reverse=True)
            cohort_names = [c[0] for c in sorted_cohorts[:6]]
        
        # Extract metrics for each cohort
        metrics = {
            'active_rate': [user_type_cohorts[c].get('active_rate', 0) * 100 for c in cohort_names],
            'ideas_per_active_user': [user_type_cohorts[c].get('ideas_per_active_user', 0) for c in cohort_names],
            'steps_per_idea': [user_type_cohorts[c].get('steps_per_idea', 0) for c in cohort_names],
            'cohort_size': [user_type_cohorts[c].get('cohort_size', 0) for c in cohort_names]
        }
        
        # Plot 1: Active Rate (top left)
        ax = axes[0, 0]
        bars = ax.bar(cohort_names, metrics['active_rate'], color='lightblue')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.1f}%')
        
        ax.set_title('Active Rate by User Type', fontsize=14)
        ax.set_ylabel('Active Rate (%)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.set_ylim(0, 100)
        
        # Plot 2: Ideas per Active User (top right)
        ax = axes[0, 1]
        bars = ax.bar(cohort_names, metrics['ideas_per_active_user'], color='lightgreen')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.2f}')
        
        ax.set_title('Ideas per Active User', fontsize=14)
        ax.set_ylabel('Average Ideas', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Plot 3: Steps per Idea (bottom left)
        ax = axes[1, 0]
        bars = ax.bar(cohort_names, metrics['steps_per_idea'], color='coral')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.2f}')
        
        ax.set_title('Steps per Idea', fontsize=14)
        ax.set_ylabel('Average Steps', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Plot 4: Cohort Size (bottom right)
        ax = axes[1, 1]
        bars = ax.bar(cohort_names, metrics['cohort_size'], color='mediumpurple')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.0f}')
        
        ax.set_title('Cohort Size', fontsize=14)
        ax.set_ylabel('Number of Users', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_institution_cohorts(self, institution_cohorts: Dict[str, Dict[str, Any]], 
                                     filename: str) -> Optional[str]:
        """
        Create visualization of institution cohort engagement.
        
        Args:
            institution_cohorts: Engagement metrics by institution
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Need at least a couple of cohorts
        if len(institution_cohorts) < 2:
            logger.warning("Not enough institution cohorts for visualization")
            return None
        
        # Limit to top 5 institutions by size
        sorted_institutions = sorted(institution_cohorts.items(), 
                                    key=lambda x: x[1].get('cohort_size', 0), 
                                    reverse=True)
        top_institutions = sorted_institutions[:5]
        
        # Extract data
        institution_names = []
        metrics = {
            'active_rate': [],
            'ideas_per_user': [],
            'steps_per_idea': []
        }
        
        for institution, data in top_institutions:
            # Truncate long institution names
            inst_name = institution[:15] + '...' if len(institution) > 15 else institution
            institution_names.append(inst_name)
            metrics['active_rate'].append(data.get('active_rate', 0) * 100)
            metrics['ideas_per_user'].append(data.get('ideas_per_active_user', 0))
            metrics['steps_per_idea'].append(data.get('steps_per_idea', 0))
        
        # Create grouped bar chart using the BaseVisualizer method
        return self.create_grouped_bar_chart(
            labels=institution_names,
            data_dict=metrics,
            filename=filename,
            title='Engagement Metrics by Institution',
            ylabel='Value',
            colors={
                'active_rate': 'lightblue',
                'ideas_per_user': 'lightgreen',
                'steps_per_idea': 'coral'
            },
            rotation=45,
            add_value_labels=True,
            format_str='{:.1f}'
        )
    
    def _visualize_enrollment_cohorts(self, enrollment_cohorts: Dict[str, Dict[str, Any]], 
                                    filename: str) -> Optional[str]:
        """
        Create visualization of enrollment cohort engagement.
        
        Args:
            enrollment_cohorts: Engagement metrics by enrollment
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Need at least a couple of cohorts
        if len(enrollment_cohorts) < 2:
            logger.warning("Not enough enrollment cohorts for visualization")
            return None
        
        # Extract data
        enrollments = []
        active_rates = []
        ideas_per_user = []
        cohort_sizes = []
        
        for enrollment, data in enrollment_cohorts.items():
            # Skip very small cohorts
            if data.get('cohort_size', 0) < 5:
                continue
                
            # Truncate long enrollment names
            enrollment_name = enrollment[:20] + '...' if len(enrollment) > 20 else enrollment
            enrollments.append(enrollment_name)
            active_rates.append(data.get('active_rate', 0) * 100)
            ideas_per_user.append(data.get('ideas_per_active_user', 0))
            cohort_sizes.append(data.get('cohort_size', 0))
        
        # Need at least a few points for the scatter plot
        if len(enrollments) < 3:
            logger.warning("Not enough significant enrollment cohorts for visualization")
            return None
        
        # Create scatter plot using the BaseVisualizer method
        fig = self.setup_figure(
            figsize=(12, 10),
            title='Enrollment Cohort Engagement Comparison',
            xlabel='Active Rate (%)',
            ylabel='Ideas per Active User'
        )
        
        # Create scatter plot with sized points
        scatter = plt.scatter(active_rates, ideas_per_user, 
                             s=[size*10 for size in cohort_sizes], 
                             alpha=0.6, c=cohort_sizes, cmap='viridis')
        
        # Add labels for each point
        for i, enrollment in enumerate(enrollments):
            plt.annotate(enrollment, 
                        (active_rates[i], ideas_per_user[i]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=9)
        
        # Add colorbar for cohort size
        cbar = plt.colorbar(scatter)
        cbar.set_label('Cohort Size', fontsize=12)
        
        # Add reference lines
        plt.axhline(y=sum(ideas_per_user)/len(ideas_per_user), color='r', linestyle='--', 
                   alpha=0.5, label='Avg Ideas/User')
        plt.axvline(x=sum(active_rates)/len(active_rates), color='g', linestyle='--', 
                   alpha=0.5, label='Avg Active Rate')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Save and return
        return self.save_figure(filename)
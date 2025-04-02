"""
Cohort visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("cohort_visualizer")


class CohortVisualizer(BaseVisualizer):
    """Visualizes cohort analysis results."""
    
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for cohort analysis.
        
        Args:
            data: Cohort analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            'time_cohorts': (self._visualize_time_cohorts, 
                            {'data_key': 'time_cohorts'}),
            'usage_by_time': (self._visualize_usage_by_time, 
                             {'data_key': 'usage_cohorts.usage_by_time_cohort'}),
            'usage_metrics': (self._visualize_usage_metrics, 
                             {'data_key': 'usage_cohorts.usage_stats'}),
            'categorization_methods': (self._visualize_categorization_methods, 
                                      {'data_key': 'usage_cohorts'}),
            'tool_adoption': (self._visualize_tool_adoption, 
                             {'data_key': 'tool_adoption.adoption_by_cohort'}),
            'framework_completion': (self._visualize_framework_completion, 
                                    {'data_key': 'learning_metrics.framework_completion'}),
            'content_metrics': (self._visualize_content_metrics, 
                               {'data_key': 'learning_metrics.content_metrics'}),
            'key_metrics_comparison': (self._visualize_key_metrics_comparison, 
                                      {'data_key': 'cohort_comparison.key_metrics'})
        }
        
        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)
    
    def _visualize_time_cohorts(self, time_cohorts: Dict[str, Dict[str, Any]], 
                              filename: str) -> Optional[str]:
        """
        Create visualization comparing time-based cohorts.
        
        Args:
            time_cohorts: Time cohort statistics
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not time_cohorts:
            return None
            
        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle('Time Cohort Comparison', fontsize=16)
        
        # Extract cohort names and ensure consistent order
        cohort_names = sorted(time_cohorts.keys())
        
        # Extract tool versions for display
        tool_versions = [time_cohorts[cohort].get('tool_version', 'unknown') for cohort in cohort_names]
        
        # Format x-axis labels to show cohort name and tool version
        x_labels = [f"{cohort.replace('_', ' ').title()}\n({version})" 
                  for cohort, version in zip(cohort_names, tool_versions)]
        
        # Metrics to display in each subplot
        metrics = {
            'active_rate': [time_cohorts[cohort].get('active_rate', 0) * 100 for cohort in cohort_names],
            'ideas_per_active_user': [time_cohorts[cohort].get('ideas_per_active_user', 0) for cohort in cohort_names],
            'steps_per_idea': [time_cohorts[cohort].get('steps_per_idea', 0) for cohort in cohort_names],
            'user_counts': {
                'total_users': [time_cohorts[cohort].get('total_users', 0) for cohort in cohort_names],
                'active_users': [time_cohorts[cohort].get('active_users', 0) for cohort in cohort_names]
            }
        }
        
        # Plot 1: Active User Rate (top left)
        ax = axes[0, 0]
        bars = ax.bar(x_labels, metrics['active_rate'], color='cornflowerblue')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.1f}%')
        
        ax.set_title('Active User Rate', fontsize=14)
        ax.set_ylabel('Percentage of Users (%)', fontsize=12)
        ax.set_ylim(0, max(max(metrics['active_rate']) + 10, 100))
        
        # Plot 2: Ideas per Active User (top right)
        ax = axes[0, 1]
        bars = ax.bar(x_labels, metrics['ideas_per_active_user'], color='lightgreen')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.2f}')
        
        ax.set_title('Ideas per Active User', fontsize=14)
        ax.set_ylabel('Average Ideas', fontsize=12)
        
        # Plot 3: Steps per Idea (bottom left)
        ax = axes[1, 0]
        bars = ax.bar(x_labels, metrics['steps_per_idea'], color='lightsalmon')
        
        # Add value labels
        self.add_value_labels(ax, bars, '{:.2f}')
        
        ax.set_title('Steps per Idea', fontsize=14)
        ax.set_ylabel('Average Steps', fontsize=12)
        
        # Plot 4: User Counts (bottom right)
        # Create grouped bar chart for user counts
        ax = axes[1, 1]
        
        # Create grouped bar chart
        x = np.arange(len(x_labels))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, metrics['user_counts']['total_users'], width, 
                      label='Total Users', color='mediumslateblue', alpha=0.7)
        bars2 = ax.bar(x + width/2, metrics['user_counts']['active_users'], width, 
                      label='Active Users', color='mediumpurple', alpha=0.7)
        
        # Add value labels
        self.add_value_labels(ax, bars1, '{:.0f}')
        self.add_value_labels(ax, bars2, '{:.0f}')
        
        ax.set_title('User Counts', fontsize=14)
        ax.set_ylabel('Number of Users', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.legend()
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_usage_by_time(self, usage_by_time: Dict[str, Dict[str, Any]], 
                               filename: str) -> Optional[str]:
        """
        Create visualization of usage levels across time cohorts.
        
        Args:
            usage_by_time: Usage statistics by time cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not usage_by_time:
            return None
            
        # Extract cohort names and ensure consistent order
        cohort_names = sorted(usage_by_time.keys())
        
        # Usage levels to display
        usage_levels = ['high', 'medium', 'low', 'none']
        
        # Build data structure for stacked bar chart
        data_dict = {level: [] for level in usage_levels}
        total_counts = []
        
        for cohort in cohort_names:
            counts = usage_by_time[cohort].get('counts', {})
            total = sum(counts.values())
            total_counts.append(total)
            
            for level in usage_levels:
                data_dict[level].append(counts.get(level, 0))
        
        # Format x-axis labels
        x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
        
        # Colors for usage levels
        colors = {
            'high': self.STANDARD_COLORS['high'],
            'medium': self.STANDARD_COLORS['medium'],
            'low': self.STANDARD_COLORS['low'],
            'none': self.STANDARD_COLORS['none']
        }
        
        # Create stacked bar chart
        return self.create_stacked_bar_chart(
            labels=x_labels,
            data_dict=data_dict,
            filename=filename,
            title='User Engagement Levels by Cohort',
            ylabel='Number of Users',
            colors=colors,
            show_percentages=True
        )
    
    def _visualize_usage_metrics(self, usage_stats: Dict[str, Dict[str, Any]], 
                               filename: str) -> Optional[str]:
        """
        Create visualization of usage cohort metrics.
        
        Args:
            usage_stats: Usage cohort statistics
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Check if we have the updated structure with multiple categorization methods
        has_methods = False
        for key in usage_stats:
            if key in ['usage_level', 'usage_by_ideas', 'usage_by_steps', 'usage_by_completion', 'usage_by_interactions']:
                has_methods = True
                break
        
        if not has_methods or not usage_stats:
            return None
            
        # Create a figure with multiple method comparisons
        # Choose 2-3 key methods to visualize
        target_methods = ['usage_level', 'usage_by_ideas', 'usage_by_completion']
        available_methods = [m for m in target_methods if m in usage_stats]
        n_methods = len(available_methods)
        
        if n_methods == 0:
            logger.warning("No valid categorization methods found in usage_stats")
            return None
            
        # Create a figure with subplots
        fig, axes = plt.subplots(n_methods, 2, figsize=(18, 6 * n_methods))
        plt.suptitle('Usage Metrics by Categorization Method', fontsize=16)
        
        # Handle single method case
        if n_methods == 1:
            axes = [axes]
        
        # Process each method
        for i, method in enumerate(available_methods):
            method_stats = usage_stats[method]
            
            # Extract usage levels and ensure consistent order
            usage_levels = ['high', 'medium', 'low', 'none']
            usage_levels = [level for level in usage_levels if level in method_stats]
            
            # Format x-axis labels
            x_labels = [level.capitalize() for level in usage_levels]
            
            # Extract metrics
            ideas_per_user = [method_stats[level].get('ideas_per_user', 0) for level in usage_levels]
            steps_per_idea = [method_stats[level].get('steps_per_idea', 0) for level in usage_levels]
            
            # Create color gradient based on usage level
            colors = [self.STANDARD_COLORS[level] for level in usage_levels]
            
            # Plot left: Ideas per User
            ax1 = axes[i][0]
            bars = ax1.bar(x_labels, ideas_per_user, color=colors)
            
            # Add value labels
            self.add_value_labels(ax1, bars, '{:.2f}')
            
            # Format method name for title
            if method == 'usage_level':
                title = 'Combined Metric'
            elif method == 'usage_by_ideas':
                title = 'By Ideas Count'
            elif method == 'usage_by_steps':
                title = 'By Steps Count'
            elif method == 'usage_by_completion':
                title = 'By Framework Completion'
            elif method == 'usage_by_interactions':
                title = 'By Total Interactions'
            else:
                title = method.replace('usage_', '').replace('_', ' ').title()
            
            ax1.set_title(f'Ideas per User - {title}', fontsize=14)
            ax1.set_ylabel('Average Ideas', fontsize=12)
            
            # Plot right: Steps per Idea
            ax2 = axes[i][1]
            bars = ax2.bar(x_labels, steps_per_idea, color=colors)
            
            # Add value labels
            self.add_value_labels(ax2, bars, '{:.2f}')
            
            ax2.set_title(f'Steps per Idea - {title}', fontsize=14)
            ax2.set_ylabel('Average Steps', fontsize=12)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_categorization_methods(self, usage_cohorts: Dict[str, Any], 
                                        filename: str) -> Optional[str]:
        """
        Create visualization of categorization method comparison.
        
        Args:
            usage_cohorts: Usage cohort data
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        method_comparison = usage_cohorts.get('method_comparison', {})
        categorization_methods = usage_cohorts.get('categorization_methods', [])
        
        # Check if we have the necessary data
        if not method_comparison or not categorization_methods:
            logger.warning("Not enough data for categorization methods visualization")
            return None
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(16, 14))
        gs = fig.add_gridspec(3, 2)
        
        # Plot 1: Method Distribution Comparison (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Extract method distributions
        distributions = method_comparison.get('method_distributions', {})
        
        if distributions:
            # Format method names for display
            method_labels = []
            for method in categorization_methods:
                # Convert method name to more readable form
                if method == 'usage_level':
                    label = 'Combined'
                elif method == 'usage_by_ideas':
                    label = 'By Ideas'
                elif method == 'usage_by_steps':
                    label = 'By Steps'
                elif method == 'usage_by_completion':
                    label = 'By Completion'
                elif method == 'usage_by_interactions':
                    label = 'By Interactions'
                else:
                    label = method.replace('usage_', '').replace('_', ' ').title()
                
                method_labels.append(label)
            
            # Extract values for each level
            high_values = [distributions[method].get('high', 0) * 100 for method in categorization_methods]
            medium_values = [distributions[method].get('medium', 0) * 100 for method in categorization_methods]
            low_values = [distributions[method].get('low', 0) * 100 for method in categorization_methods]
            none_values = [distributions[method].get('none', 0) * 100 for method in categorization_methods]
            
            # Prepare data for stacked bar chart
            data_dict = {
                'high': high_values,
                'medium': medium_values,
                'low': low_values,
                'none': none_values
            }
            
            # Create stacked bar chart
            bar_width = 0.65
            
            # Build stacked bars
            bottom_values = np.zeros(len(method_labels))
            
            colors = {
                'high': self.STANDARD_COLORS['high'],
                'medium': self.STANDARD_COLORS['medium'],
                'low': self.STANDARD_COLORS['low'],
                'none': self.STANDARD_COLORS['none']
            }
            
            # Create bars for each usage level
            for level in ['high', 'medium', 'low', 'none']:
                values = data_dict[level]
                ax1.bar(method_labels, values, bar_width, label=level.capitalize(), 
                       bottom=bottom_values, color=colors[level])
                
                # Add percentage labels to larger segments
                for i, value in enumerate(values):
                    if value > 5:  # Only show label if segment is large enough
                        ax1.text(i, bottom_values[i] + value/2, f"{value:.1f}%", 
                               ha='center', va='center', color='black' if level in ['low', 'none'] else 'white',
                               fontweight='bold')
                
                bottom_values += values
            
            ax1.set_title('User Distribution by Categorization Method', fontsize=14)
            ax1.set_ylabel('Percentage of Users (%)', fontsize=12)
            ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
            
        else:
            ax1.text(0.5, 0.5, "No distribution data available",
                   ha='center', va='center', fontsize=14, transform=ax1.transAxes)
            ax1.axis('off')
        
        # Plot 2: Method Agreement Heatmap (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        
        # Extract agreement rates
        agreement_rates = method_comparison.get('agreement_rates', {})
        
        if agreement_rates and categorization_methods:
            # Create the agreement matrix
            n_methods = len(categorization_methods)
            agreement_matrix = np.zeros((n_methods, n_methods))
            
            # Fill the agreement matrix
            for i, method1 in enumerate(categorization_methods):
                for j, method2 in enumerate(categorization_methods):
                    if i == j:
                        # Self-agreement is always 100%
                        agreement_matrix[i, j] = 1.0
                    else:
                        # Look up the agreement rate
                        key = f"{method1}_vs_{method2}" if i < j else f"{method2}_vs_{method1}"
                        if key in agreement_rates:
                            agreement_matrix[i, j] = agreement_rates[key]
            
            # Create heatmap
            im = ax2.imshow(agreement_matrix, cmap='YlGnBu', vmin=0, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax2, format=lambda x, _: f'{x:.0%}')
            cbar.set_label('Agreement Rate', fontsize=12)
            
            # Add labels
            ax2.set_xticks(np.arange(n_methods))
            ax2.set_yticks(np.arange(n_methods))
            ax2.set_xticklabels(method_labels)
            ax2.set_yticklabels(method_labels)
            
            # Rotate the tick labels and set their alignment
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Add values in each cell
            for i in range(n_methods):
                for j in range(n_methods):
                    ax2.text(j, i, f"{agreement_matrix[i, j]:.0%}",
                           ha="center", va="center",
                           color="black" if agreement_matrix[i, j] > 0.5 else "white")
            
            ax2.set_title('Agreement Rate Between Categorization Methods', fontsize=14)
            
        else:
            ax2.text(0.5, 0.5, "No agreement data available",
                   ha='center', va='center', fontsize=14, transform=ax2.transAxes)
            ax2.axis('off')
        
        # Plot 3-4: Confusion matrices for selected method pairs (bottom row)
        confusion_matrices = method_comparison.get('confusion_matrices', {})
        
        if confusion_matrices and len(confusion_matrices) >= 2:
            # Select two interesting method pairs to show
            # Typically, we want to compare the default (combined) method with others
            key_pairs = []
            
            # Try to find comparisons involving the default method
            for key in confusion_matrices.keys():
                if 'usage_level_vs' in key:
                    key_pairs.append(key)
            
            # If we don't have enough, add other pairs
            if len(key_pairs) < 2:
                for key in confusion_matrices.keys():
                    if key not in key_pairs:
                        key_pairs.append(key)
                        if len(key_pairs) >= 2:
                            break
            
            # Limit to 2 pairs
            key_pairs = key_pairs[:2]
            
            # Plot selected confusion matrices
            for i, key in enumerate(key_pairs):
                ax = fig.add_subplot(gs[2, i])
                
                # Extract method names from key
                method1, method2 = key.split('_vs_')
                
                # Create confusion matrix
                matrix = confusion_matrices[key]
                levels = ['high', 'medium', 'low', 'none']
                
                # Convert to numpy array
                cm_array = np.zeros((4, 4))
                for i_row, level1 in enumerate(levels):
                    for i_col, level2 in enumerate(levels):
                        cm_array[i_row, i_col] = matrix[level1][level2]
                
                # Create heatmap
                im = ax.imshow(cm_array, cmap='Blues')
                
                # Add labels
                ax.set_xticks(np.arange(len(levels)))
                ax.set_yticks(np.arange(len(levels)))
                ax.set_xticklabels([level.capitalize() for level in levels])
                ax.set_yticklabels([level.capitalize() for level in levels])
                
                # Add axis labels
                method1_label = method1.replace('usage_', '').replace('_', ' ').title()
                method2_label = method2.replace('usage_', '').replace('_', ' ').title()
                ax.set_xlabel(method2_label, fontsize=12)
                ax.set_ylabel(method1_label, fontsize=12)
                
                # Add values in each cell
                for i_row in range(len(levels)):
                    for i_col in range(len(levels)):
                        ax.text(i_col, i_row, f"{int(cm_array[i_row, i_col])}",
                               ha="center", va="center",
                               color="black" if cm_array[i_row, i_col] < cm_array.max()/2 else "white")
                
                ax.set_title(f'Confusion Matrix: {method1_label} vs {method2_label}', fontsize=14)
            
        else:
            # If no confusion matrices, use a single subplot for additional information
            ax = fig.add_subplot(gs[2, :])
            ax.text(0.5, 0.5, "No confusion matrix data available",
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.axis('off')
        
        # Add explanation of categorization methods
        explanation_text = """
        Categorization Methods:
        - Combined: Uses both ideas and steps counts
        - By Ideas: Based only on number of ideas created
        - By Steps: Based only on number of steps completed
        - By Completion: Based on framework completion percentage
        - By Interactions: Based on total interactions (ideas + steps)
        """
        
        plt.figtext(0.5, 0.01, explanation_text,
                   ha="center", fontsize=12, bbox={"facecolor":"lightyellow", "alpha":0.8, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.suptitle('Comparison of User Categorization Methods', fontsize=16)
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_tool_adoption(self, adoption_by_cohort: Dict[str, Dict[str, Any]], 
                               filename: str) -> Optional[str]:
        """
        Create visualization of tool adoption across cohorts.
        
        Args:
            adoption_by_cohort: Tool adoption statistics by cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not adoption_by_cohort:
            return None
            
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Extract cohort names and ensure consistent order
        cohort_names = sorted(adoption_by_cohort.keys())
        
        # Format x-axis labels
        x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
        
        # Plot 1: Adoption Rate by Cohort
        adoption_rates = [adoption_by_cohort[cohort].get('adoption_rate', 0) * 100 for cohort in cohort_names]
        engaged_users = [adoption_by_cohort[cohort].get('engaged_users', 0) for cohort in cohort_names]
        tool_versions = [adoption_by_cohort[cohort].get('tool_version') for cohort in cohort_names]
        
        # Define colors based on tool version
        colors = [self.get_tool_color(v) for v in tool_versions]
        
        # Create bar chart for adoption rates
        bars = ax1.bar(x_labels, adoption_rates, color=colors)
        
        # Add value labels
        self.add_value_labels(ax1, bars, '{:.1f}%')
        
        # Add a line for number of engaged users
        ax1_twin = ax1.twinx()
        ax1_twin.plot(x_labels, engaged_users, 'o-', color='darkred', label='Engaged Users')
        ax1_twin.set_ylabel('Number of Users', fontsize=12, color='darkred')
        
        # Add title and labels
        ax1.set_title('Tool Adoption Rate by Cohort', fontsize=14)
        ax1.set_ylabel('Adoption Rate (%)', fontsize=12)
        ax1.set_ylim(0, 100)
        
        # Add a legend for the twin axis
        ax1_twin.legend(loc='upper right')
        
        # Plot 2: Adoption Timeline for a specific cohort
        # Only show if there's adoption timeline data
        has_timeline = False
        for cohort in cohort_names:
            if 'adoption_timeline' in adoption_by_cohort[cohort] and adoption_by_cohort[cohort]['adoption_timeline']:
                has_timeline = True
                break
        
        if has_timeline:
            # Use the latest cohort with data for the timeline
            selected_cohort = None
            for cohort in reversed(cohort_names):
                if 'adoption_timeline' in adoption_by_cohort[cohort] and adoption_by_cohort[cohort]['adoption_timeline']:
                    selected_cohort = cohort
                    break
            
            if selected_cohort:
                timeline = adoption_by_cohort[selected_cohort]['adoption_timeline']
                
                # Convert to list of dates and values
                dates = []
                values = []
                
                for date_str, value in sorted(timeline.items()):
                    try:
                        date = datetime.strptime(date_str, '%Y-%m')
                        dates.append(date)
                        values.append(value)
                    except ValueError:
                        continue
                
                if dates and values:
                    # Calculate adoption percentage
                    total = adoption_by_cohort[selected_cohort]['total_users']
                    percentages = [v / total * 100 if total > 0 else 0 for v in values]
                    
                    # Create line chart
                    ax2.plot(dates, percentages, 'o-', color='forestgreen', linewidth=2)
                    
                    # Format x-axis as dates
                    self.format_date_axis(ax2)
                    
                    # Add title and labels
                    cohort_label = selected_cohort.replace('_', ' ').title()
                    ax2.set_title(f'Adoption Timeline for {cohort_label} Cohort', fontsize=14)
                    ax2.set_xlabel('Month', fontsize=12)
                    ax2.set_ylabel('Cumulative Adoption (%)', fontsize=12)
                    ax2.set_ylim(0, 100)
                    ax2.grid(True, linestyle='--', alpha=0.7)
                else:
                    ax2.text(0.5, 0.5, "No timeline data available",
                           ha='center', va='center', fontsize=14, transform=ax2.transAxes)
                    ax2.axis('off')
            else:
                ax2.text(0.5, 0.5, "No timeline data available",
                       ha='center', va='center', fontsize=14, transform=ax2.transAxes)
                ax2.axis('off')
        else:
            ax2.text(0.5, 0.5, "No timeline data available",
                   ha='center', va='center', fontsize=14, transform=ax2.transAxes)
            ax2.axis('off')
        
        # Add tool version annotations
        plt.figtext(0.5, 0.01, 
                  f"Tool versions: {', '.join([f'{c}: {v}' for c, v in zip(x_labels, tool_versions)])}",
                  ha="center", fontsize=12, bbox={"facecolor":"lightyellow", "alpha":0.8, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_framework_completion(self, framework_completion: Dict[str, Dict[str, Any]], 
                                      filename: str) -> Optional[str]:
        """
        Create visualization of framework completion across cohorts.
        
        Args:
            framework_completion: Framework completion statistics by cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not framework_completion:
            return None
            
        # Extract cohort names and ensure consistent order
        cohort_names = sorted(framework_completion.keys())
        
        # Extract completion percentages
        de_completion = [framework_completion[cohort].get('avg_de_completion', 0) for cohort in cohort_names]
        st_completion = [framework_completion[cohort].get('avg_st_completion', 0) for cohort in cohort_names]
        
        # Extract idea counts for each framework
        de_counts = [framework_completion[cohort].get('de_ideas_count', 0) for cohort in cohort_names]
        st_counts = [framework_completion[cohort].get('st_ideas_count', 0) for cohort in cohort_names]
        
        # Format x-axis labels
        x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
        
        # Create grouped bar chart
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Define data and colors for grouped bar chart
        completion_data = {
            'DE Completion': de_completion,
            'ST Completion': st_completion
        }
        
        colors = {
            'DE Completion': 'dodgerblue',
            'ST Completion': 'darkorange'
        }
        
        # Create grouped bar chart
        return self.create_grouped_bar_chart(
            labels=x_labels,
            data_dict=completion_data,
            filename=filename,
            title='Framework Completion by Cohort',
            ylabel='Average Completion (%)',
            colors=colors,
            add_value_labels=True,
            format_str='{:.1f}%'
        )
    
    def _visualize_content_metrics(self, content_metrics: Dict[str, Dict[str, Any]], 
                                 filename: str) -> Optional[str]:
        """
        Create visualization of content metrics across cohorts.
        
        Args:
            content_metrics: Content metrics statistics by cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not content_metrics:
            return None
            
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Extract cohort names and ensure consistent order
        cohort_names = sorted(content_metrics.keys())
        
        # Format x-axis labels
        x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
        
        # Plot 1: Average Word Count
        avg_word_counts = [content_metrics[cohort].get('avg_word_count', 0) for cohort in cohort_names]
        bars = ax1.bar(x_labels, avg_word_counts, color='mediumseagreen')
        
        # Add value labels
        self.add_value_labels(ax1, bars, '{:.1f}')
        
        ax1.set_title('Average Word Count per Step', fontsize=14)
        ax1.set_ylabel('Average Words', fontsize=12)
        
        # Plot 2: Steps with Content
        steps_with_content = [content_metrics[cohort].get('steps_with_content', 0) for cohort in cohort_names]
        bars = ax2.bar(x_labels, steps_with_content, color='mediumpurple')
        
        # Add value labels
        self.add_value_labels(ax2, bars, '{:.0f}')
        
        ax2.set_title('Steps with Content', fontsize=14)
        ax2.set_ylabel('Number of Steps', fontsize=12)
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_key_metrics_comparison(self, key_metrics: Dict[str, Dict[str, float]], 
                                        filename: str) -> Optional[str]:
        """
        Create visualization comparing key metrics across cohorts.
        
        Args:
            key_metrics: Dictionary of key metrics by cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Extract metrics and cohorts
        metrics = list(key_metrics.keys())
        cohorts = set()
        for metric_data in key_metrics.values():
            cohorts.update(metric_data.keys())
        
        cohorts = sorted(cohorts)
        
        # Need at least one metric and one cohort
        if not metrics or not cohorts:
            logger.warning("Not enough data for key metrics comparison")
            return None
        
        # Create a figure with subplots for each metric
        num_metrics = len(metrics)
        fig, axes = plt.subplots(num_metrics, 1, figsize=(12, 4 * num_metrics))
        
        # Handle case with only one metric
        if num_metrics == 1:
            axes = [axes]
        
        # Format x-axis labels
        x_labels = [cohort.replace('_', ' ').title() for cohort in cohorts]
        
        # Plot each metric
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            # Extract values for this metric across cohorts
            values = [key_metrics[metric].get(cohort, 0) for cohort in cohorts]
            
            # Create bar chart
            bars = ax.bar(x_labels, values, color='steelblue')
            
            # Add value labels
            self.add_value_labels(ax, bars, '{:.2f}')
            
            # Make the metric name more readable
            metric_name = metric.replace('_', ' ').title()
            
            ax.set_title(f'{metric_name}', fontsize=14)
            
            # Add percentage sign for metrics that are percentages
            if 'rate' in metric.lower() or 'completion' in metric.lower():
                ax.set_ylabel('Percentage (%)', fontsize=12)
                # Set y-limit for percentage metrics
                ax.set_ylim(0, max(max(values) * 1.2, 100))
            else:
                ax.set_ylabel('Value', fontsize=12)
        
        # Add an overall title
        fig.suptitle('Key Metrics Comparison Across Cohorts', fontsize=16)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Save and return
        return self.save_figure(filename)
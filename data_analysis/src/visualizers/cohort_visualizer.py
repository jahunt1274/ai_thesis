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
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the cohort visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format
        
        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "cohorts")
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for cohort analysis.
        
        Args:
            data: Cohort analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info("Generating cohort visualizations")
        
        visualizations = {}
        
        # Check if necessary data exists
        if not data:
            logger.warning("No cohort data to visualize")
            return visualizations
        
        # Create various cohort visualizations
        try:
            # Time cohorts
            if 'time_cohorts' in data:
                vis_path = self._visualize_time_cohorts(data['time_cohorts'])
                if vis_path:
                    visualizations['time_cohorts'] = vis_path
            
            # Usage cohorts
            if 'usage_cohorts' in data:
                if 'usage_by_time_cohort' in data['usage_cohorts']:
                    vis_path = self._visualize_usage_by_time(data['usage_cohorts']['usage_by_time_cohort'])
                    if vis_path:
                        visualizations['usage_by_time'] = vis_path
                
                if 'usage_stats' in data['usage_cohorts']:
                    vis_path = self._visualize_usage_metrics(data['usage_cohorts']['usage_stats'])
                    if vis_path:
                        visualizations['usage_metrics'] = vis_path
                
                # Visualize method comparison if available
                if 'method_comparison' in data['usage_cohorts']:
                    vis_path = self._visualize_categorization_methods(
                        data['usage_cohorts']['method_comparison'],
                        data['usage_cohorts'].get('categorization_methods', [])
                    )
                    if vis_path:
                        visualizations['categorization_methods'] = vis_path
            
            # Tool adoption
            if 'tool_adoption' in data and 'adoption_by_cohort' in data['tool_adoption']:
                vis_path = self._visualize_tool_adoption(data['tool_adoption']['adoption_by_cohort'])
                if vis_path:
                    visualizations['tool_adoption'] = vis_path
            
            # Learning metrics
            if 'learning_metrics' in data:
                if 'framework_completion' in data['learning_metrics']:
                    vis_path = self._visualize_framework_completion(data['learning_metrics']['framework_completion'])
                    if vis_path:
                        visualizations['framework_completion'] = vis_path
                
                if 'content_metrics' in data['learning_metrics']:
                    vis_path = self._visualize_content_metrics(data['learning_metrics']['content_metrics'])
                    if vis_path:
                        visualizations['content_metrics'] = vis_path
            
            # Cohort comparison
            if 'cohort_comparison' in data and 'key_metrics' in data['cohort_comparison']:
                vis_path = self._visualize_key_metrics_comparison(data['cohort_comparison']['key_metrics'])
                if vis_path:
                    visualizations['key_metrics_comparison'] = vis_path
            
            logger.info(f"Generated {len(visualizations)} cohort visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating cohort visualizations: {str(e)}")
            return visualizations
    
    def _visualize_time_cohorts(self, time_cohorts: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization comparing time-based cohorts.
        
        Args:
            time_cohorts: Time cohort statistics
            
        Returns:
            Path to the visualization file
        """
        try:
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
            
            # Plot 1: Active User Rate (top left)
            ax = axes[0, 0]
            active_rates = [time_cohorts[cohort].get('active_rate', 0) * 100 for cohort in cohort_names]
            bars = ax.bar(x_labels, active_rates, color='cornflowerblue')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
            
            ax.set_title('Active User Rate', fontsize=14)
            ax.set_ylabel('Percentage of Users (%)', fontsize=12)
            ax.set_ylim(0, max(max(active_rates) + 10, 100))
            
            # Plot 2: Ideas per Active User (top right)
            ax = axes[0, 1]
            ideas_per_user = [time_cohorts[cohort].get('ideas_per_active_user', 0) for cohort in cohort_names]
            bars = ax.bar(x_labels, ideas_per_user, color='lightgreen')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.2f}',
                       ha='center', va='bottom')
            
            ax.set_title('Ideas per Active User', fontsize=14)
            ax.set_ylabel('Average Ideas', fontsize=12)
            
            # Plot 3: Steps per Idea (bottom left)
            ax = axes[1, 0]
            steps_per_idea = [time_cohorts[cohort].get('steps_per_idea', 0) for cohort in cohort_names]
            bars = ax.bar(x_labels, steps_per_idea, color='lightsalmon')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.2f}',
                       ha='center', va='bottom')
            
            ax.set_title('Steps per Idea', fontsize=14)
            ax.set_ylabel('Average Steps', fontsize=12)
            
            # Plot 4: User Counts (bottom right)
            ax = axes[1, 1]
            total_users = [time_cohorts[cohort].get('total_users', 0) for cohort in cohort_names]
            active_users = [time_cohorts[cohort].get('active_users', 0) for cohort in cohort_names]
            
            # Create grouped bar chart
            x = np.arange(len(x_labels))
            width = 0.35
            
            ax.bar(x - width/2, total_users, width, label='Total Users', color='mediumslateblue', alpha=0.7)
            ax.bar(x + width/2, active_users, width, label='Active Users', color='mediumpurple', alpha=0.7)
            
            ax.set_title('User Counts', fontsize=14)
            ax.set_ylabel('Number of Users', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(x_labels)
            ax.legend()
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"time_cohorts_comparison.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating content metrics visualization: {str(e)}")
            return None
    
    def _visualize_key_metrics_comparison(self, key_metrics: Dict[str, Dict[str, float]]) -> Optional[str]:
        """
        Create visualization comparing key metrics across cohorts.
        
        Args:
            key_metrics: Dictionary of key metrics by cohort
            
        Returns:
            Path to the visualization file
        """
        try:
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
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.05,
                           f'{height:.2f}',
                           ha='center', va='bottom')
                
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
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"key_metrics_comparison.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating key metrics comparison visualization: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Error creating time cohorts visualization: {str(e)}")
            return None
    
    def _visualize_usage_by_time(self, usage_by_time: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of usage levels across time cohorts.
        
        Args:
            usage_by_time: Usage statistics by time cohort
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Extract cohort names and ensure consistent order
            cohort_names = sorted(usage_by_time.keys())
            
            # Extract usage levels for each cohort
            usage_data = {
                'high': [],
                'medium': [],
                'low': [],
                'none': []
            }
            
            for cohort in cohort_names:
                counts = usage_by_time[cohort].get('counts', {})
                for level in usage_data:
                    usage_data[level].append(counts.get(level, 0))
            
            # Calculate total height for each bar
            totals = [sum(usage_by_time[cohort].get('counts', {}).values()) for cohort in cohort_names]
            
            # Format x-axis labels
            x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
            
            # Create stacked bar chart
            bottom = np.zeros(len(cohort_names))
            
            # Define colors for usage levels
            colors = {
                'high': 'darkgreen',
                'medium': 'yellowgreen',
                'low': 'gold',
                'none': 'lightcoral'
            }
            
            # Create bars for each usage level
            bars = {}
            for level in ['high', 'medium', 'low', 'none']:
                bars[level] = plt.bar(x_labels, usage_data[level], bottom=bottom, 
                                    label=f'{level.capitalize()} Usage', color=colors[level])
                bottom += usage_data[level]
            
            # Add percentage labels to each segment
            for level in ['high', 'medium', 'low', 'none']:
                for i, bar in enumerate(bars[level]):
                    height = bar.get_height()
                    if height > 0:
                        percentage = height / totals[i] * 100 if totals[i] > 0 else 0
                        plt.text(bar.get_x() + bar.get_width()/2., 
                               bar.get_y() + height/2,
                               f'{percentage:.1f}%',
                               ha='center', va='center',
                               color='white' if level in ['high', 'medium'] else 'black',
                               fontweight='bold')
            
            # Add title and labels
            plt.title('User Engagement Levels by Cohort', fontsize=16)
            plt.ylabel('Number of Users', fontsize=12)
            plt.legend(loc='upper right')
            
            # Add tool version annotations if available
            for i, cohort in enumerate(cohort_names):
                if 'tool_version' in usage_by_time[cohort]:
                    version = usage_by_time[cohort]['tool_version']
                    plt.annotate(f"Tool: {version}",
                              (i, 5),
                              xytext=(0, -30),
                              textcoords='offset points',
                              ha='center')
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"usage_by_time_cohort.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating usage by time visualization: {str(e)}")
            return None
    
    def _visualize_usage_metrics(self, usage_stats: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of usage cohort metrics.
        
        Args:
            usage_stats: Usage cohort statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have the updated structure with multiple categorization methods
            has_methods = False
            for key in usage_stats:
                if key in ['usage_level', 'usage_by_ideas', 'usage_by_steps', 'usage_by_completion', 'usage_by_interactions']:
                    has_methods = True
                    break
            
            if has_methods:
                # Create a figure with multiple method comparisons
                # Choose 2-3 key methods to visualize
                target_methods = ['usage_level', 'usage_by_ideas', 'usage_by_completion']
                n_methods = len([m for m in target_methods if m in usage_stats])
                
                # Create a figure with subplots
                if n_methods == 0:
                    logger.warning("No valid categorization methods found in usage_stats")
                    return None
                    
                fig, axes = plt.subplots(n_methods, 2, figsize=(18, 6 * n_methods))
                plt.suptitle('Usage Metrics by Categorization Method', fontsize=16)
                
                # If only one method, reshape axes for consistent indexing
                if n_methods == 1:
                    axes = [axes]
                
                # Process each method
                for i, method in enumerate([m for m in target_methods if m in usage_stats]):
                    method_stats = usage_stats[method]
                    
                    # Extract usage levels and ensure consistent order
                    usage_levels = ['high', 'medium', 'low', 'none']
                    usage_levels = [level for level in usage_levels if level in method_stats]
                    
                    # Format x-axis labels
                    x_labels = [level.capitalize() for level in usage_levels]
                    
                    # Plot left: Ideas per User by Usage Level
                    ax1 = axes[i][0]
                    ideas_per_user = [method_stats[level].get('ideas_per_user', 0) for level in usage_levels]
                    
                    # Create a color gradient based on usage level
                    colors = ['darkgreen', 'yellowgreen', 'gold', 'lightcoral']
                    colors = colors[:len(usage_levels)]
                    
                    bars = ax1.bar(x_labels, ideas_per_user, color=colors)
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{height:.2f}',
                               ha='center', va='bottom')
                    
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
                    
                    # Plot right: Steps per Idea by Usage Level
                    ax2 = axes[i][1]
                    steps_per_idea = [method_stats[level].get('steps_per_idea', 0) for level in usage_levels]
                    
                    bars = ax2.bar(x_labels, steps_per_idea, color=colors)
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{height:.2f}',
                               ha='center', va='bottom')
                    
                    ax2.set_title(f'Steps per Idea - {title}', fontsize=14)
                    ax2.set_ylabel('Average Steps', fontsize=12)
                
                plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            else:
                # Use original implementation for backward compatibility
                # Create figure with multiple subplots
                fig, axes = plt.subplots(2, 2, figsize=(14, 10))
                fig.suptitle('Usage Cohort Metrics', fontsize=16)
                
                # Extract usage levels and ensure consistent order
                usage_levels = ['high', 'medium', 'low', 'none']
                usage_levels = [level for level in usage_levels if level in usage_stats]
                
                # Format x-axis labels
                x_labels = [level.capitalize() for level in usage_levels]
                
                # Plot 1: User Counts (top left)
                ax = axes[0, 0]
                user_counts = [usage_stats[level].get('user_count', 0) for level in usage_levels]
                
                # Create a color gradient based on usage level
                colors = ['darkgreen', 'yellowgreen', 'gold', 'lightcoral']
                colors = colors[:len(usage_levels)]
                
                bars = ax.bar(x_labels, user_counts, color=colors)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height)}',
                           ha='center', va='bottom')
                
                ax.set_title('User Counts by Usage Level', fontsize=14)
                ax.set_ylabel('Number of Users', fontsize=12)
                
                # Plot 2: Ideas per User (top right)
                ax = axes[0, 1]
                ideas_per_user = [usage_stats[level].get('ideas_per_user', 0) for level in usage_levels]
                
                bars = ax.bar(x_labels, ideas_per_user, color=colors)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}',
                           ha='center', va='bottom')
                
                ax.set_title('Ideas per User', fontsize=14)
                ax.set_ylabel('Average Ideas', fontsize=12)
                
                # Plot 3: Steps per Idea (bottom left)
                ax = axes[1, 0]
                steps_per_idea = [usage_stats[level].get('steps_per_idea', 0) for level in usage_levels]
                
                bars = ax.bar(x_labels, steps_per_idea, color=colors)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}',
                           ha='center', va='bottom')
                
                ax.set_title('Steps per Idea', fontsize=14)
                ax.set_ylabel('Average Steps', fontsize=12)
                
                # Plot 4: Average Steps per User (bottom right)
                ax = axes[1, 1]
                steps_per_user = [usage_stats[level].get('avg_steps_per_user', 0) for level in usage_levels]
                
                bars = ax.bar(x_labels, steps_per_user, color=colors)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}',
                           ha='center', va='bottom')
                
                ax.set_title('Average Steps per User', fontsize=14)
                ax.set_ylabel('Average Steps', fontsize=12)
                
                plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"usage_cohort_metrics.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating usage metrics visualization: {str(e)}")
            return None
    
    def _visualize_tool_adoption(self, adoption_by_cohort: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of tool adoption across cohorts.
        
        Args:
            adoption_by_cohort: Tool adoption statistics by cohort
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
            
            # Extract cohort names and ensure consistent order
            cohort_names = sorted(adoption_by_cohort.keys())
            
            # Format x-axis labels
            x_labels = [cohort.replace('_', ' ').title() for cohort in cohort_names]
            
            # Plot 1: Adoption Rate by Cohort
            adoption_rates = [adoption_by_cohort[cohort].get('adoption_rate', 0) * 100 for cohort in cohort_names]
            engaged_users = [adoption_by_cohort[cohort].get('engaged_users', 0) for cohort in cohort_names]
            total_users = [adoption_by_cohort[cohort].get('total_users', 0) for cohort in cohort_names]
            
            # Define colors based on tool version
            tool_versions = [adoption_by_cohort[cohort].get('tool_version', 'unknown') for cohort in cohort_names]
            colors = ['lightgray' if v == 'none' else 'lightblue' if v == 'v1' else 'cornflowerblue' 
                    for v in tool_versions]
            
            # Create bar chart for adoption rates
            bars = ax1.bar(x_labels, adoption_rates, color=colors)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
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
                        
                        # Plot line chart
                        ax2.plot(dates, percentages, 'o-', color='forestgreen', linewidth=2)
                        
                        # Format x-axis as dates
                        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                        plt.xticks(rotation=45, ha='right')
                        
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
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"tool_adoption.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating tool adoption visualization: {str(e)}")
            return None
    
    def _visualize_framework_completion(self, framework_completion: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of framework completion across cohorts.
        
        Args:
            framework_completion: Framework completion statistics by cohort
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 8))
            
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
            x = np.arange(len(x_labels))
            width = 0.35
            
            fig, ax1 = plt.subplots(figsize=(12, 8))
            
            bars1 = ax1.bar(x - width/2, de_completion, width, label='DE Completion', color='dodgerblue')
            bars2 = ax1.bar(x + width/2, st_completion, width, label='ST Completion', color='darkorange')
            
            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            for bar in bars2:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            # Add title and labels
            ax1.set_title('Framework Completion by Cohort', fontsize=16)
            ax1.set_xlabel('Cohort', fontsize=12)
            ax1.set_ylabel('Average Completion (%)', fontsize=12)
            ax1.set_xticks(x)
            ax1.set_xticklabels(x_labels)
            ax1.set_ylim(0, 100)
            ax1.legend(loc='upper left')
            
            # Add idea count annotations
            for i, (de, st) in enumerate(zip(de_counts, st_counts)):
                plt.annotate(f"DE: {de} ideas\nST: {st} ideas",
                           (x[i], 5),
                           xytext=(0, 10),
                           textcoords='offset points',
                           ha='center',
                           bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"framework_completion.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating framework completion visualization: {str(e)}")
            return None
    
    def _visualize_categorization_methods(self, method_comparison: Dict[str, Any], 
                                    categorization_methods: List[str]) -> Optional[str]:
        """
        Create visualization of categorization method comparison.
        
        Args:
            method_comparison: Comparison statistics between methods
            categorization_methods: List of categorization method names
            
        Returns:
            Path to the visualization file
        """
        try:
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
                
                # Create stacked bar chart
                bar_width = 0.65
                bottom_values = np.zeros(len(method_labels))
                
                p1 = ax1.bar(method_labels, high_values, bar_width, label='High', bottom=bottom_values, color='darkgreen')
                bottom_values += high_values
                
                p2 = ax1.bar(method_labels, medium_values, bar_width, label='Medium', bottom=bottom_values, color='yellowgreen')
                bottom_values += medium_values
                
                p3 = ax1.bar(method_labels, low_values, bar_width, label='Low', bottom=bottom_values, color='gold')
                bottom_values += low_values
                
                p4 = ax1.bar(method_labels, none_values, bar_width, label='None', bottom=bottom_values, color='lightcoral')
                
                # Add percentage labels
                def add_labels(bars, values, bottom):
                    for i, bar in enumerate(bars):
                        if values[i] > 5:  # Only show label if segment is large enough
                            ax1.text(bar.get_x() + bar.get_width()/2,
                                   bottom[i] + values[i]/2,
                                   f"{values[i]:.1f}%",
                                   ha='center', va='center', color='black' if values[i] > 15 else 'white',
                                   fontweight='bold')
                
                # Add labels to each segment
                bottom_for_labels = np.zeros(len(method_labels))
                add_labels(p1, high_values, bottom_for_labels)
                bottom_for_labels += high_values
                add_labels(p2, medium_values, bottom_for_labels)
                bottom_for_labels += medium_values
                add_labels(p3, low_values, bottom_for_labels)
                bottom_for_labels += low_values
                add_labels(p4, none_values, bottom_for_labels)
                
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
            
            if agreement_rates:
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
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"categorization_methods_comparison.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating categorization methods visualization: {str(e)}")
            return None
    
    def _visualize_content_metrics(self, content_metrics: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of content metrics across cohorts.
        
        Args:
            content_metrics: Content metrics statistics by cohort
            
        Returns:
            Path to the visualization file
        """
        try:
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
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}',
                        ha='center', va='bottom')
            
            ax1.set_title('Average Word Count per Step', fontsize=14)
            ax1.set_ylabel('Average Words', fontsize=12)
            
            # Plot 2: Steps with Content
            steps_with_content = [content_metrics[cohort].get('steps_with_content', 0) for cohort in cohort_names]
            bars = ax2.bar(x_labels, steps_with_content, color='mediumpurple')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            ax2.set_title('Steps with Content', fontsize=14)
            ax2.set_ylabel('Number of Steps', fontsize=12)
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"content_metrics.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path

        except Exception as e:
            logger.error(f"Error creating content metrics visualization: {str(e)}")
            return None
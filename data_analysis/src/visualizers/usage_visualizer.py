"""
Usage visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib_venn import venn2
import seaborn as sns
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("usage_visualizer")


class UsageVisualizer(BaseVisualizer):
    """Visualizes usage analysis results."""
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the usage visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format
        
        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "usage")
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for usage analysis.
        
        Args:
            data: Usage analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info("Generating usage visualizations")
        
        visualizations = {}
        
        # Check if necessary data exists
        if not data:
            logger.warning("No usage data to visualize")
            return visualizations
        
        # Create various usage visualizations
        try:
            # Idea generation
            if 'idea_generation' in data:
                # Visualize idea counts
                vis_path = self._visualize_idea_counts(data['idea_generation'])
                if vis_path:
                    visualizations['idea_counts'] = vis_path
                
                # Visualize ideas by ranking
                if 'ideas_by_ranking' in data['idea_generation']:
                    vis_path = self._visualize_ideas_by_ranking(data['idea_generation']['ideas_by_ranking'])
                    if vis_path:
                        visualizations['ideas_by_ranking'] = vis_path
            
            # Engagement levels
            if 'engagement_levels' in data:
                # Visualize user engagement distribution
                if 'engagement_levels' in data['engagement_levels']:
                    vis_path = self._visualize_engagement_levels(data['engagement_levels']['engagement_levels'])
                    if vis_path:
                        visualizations['engagement_levels'] = vis_path
                
                # Visualize framework engagement
                if 'framework_engagement' in data['engagement_levels']:
                    vis_path = self._visualize_framework_engagement(data['engagement_levels']['framework_engagement'])
                    if vis_path:
                        visualizations['framework_engagement'] = vis_path
                
                # Visualize temporal engagement
                if 'temporal_engagement' in data['engagement_levels']:
                    if 'monthly_active_users' in data['engagement_levels']['temporal_engagement']:
                        vis_path = self._visualize_monthly_active_users(
                            data['engagement_levels']['temporal_engagement']['monthly_active_users']
                        )
                        if vis_path:
                            visualizations['monthly_active_users'] = vis_path
            
            # Idea characterization
            if 'idea_characterization' in data:
                # Visualize iteration patterns
                if 'iteration_patterns' in data['idea_characterization']:
                    vis_path = self._visualize_iteration_patterns(data['idea_characterization']['iteration_patterns'])
                    if vis_path:
                        visualizations['iteration_patterns'] = vis_path
                
                # Visualize progress statistics
                if 'progress_stats' in data['idea_characterization']:
                    vis_path = self._visualize_progress_stats(data['idea_characterization']['progress_stats'])
                    if vis_path:
                        visualizations['progress_stats'] = vis_path
            
            # Framework usage
            if 'framework_usage' in data:
                # Visualize framework counts
                if 'framework_counts' in data['framework_usage']:
                    vis_path = self._visualize_framework_counts(data['framework_usage']['framework_counts'])
                    if vis_path:
                        visualizations['framework_counts'] = vis_path
                
                # Visualize framework completion rates
                vis_path = self._visualize_framework_completion(
                    data['framework_usage'].get('de_completion', {}),
                    data['framework_usage'].get('st_completion', {})
                )
                if vis_path:
                    visualizations['framework_completion'] = vis_path
            
            # Usage timeline
            if 'timeline' in data:
                # Visualize daily counts
                if 'daily_counts' in data['timeline']:
                    vis_path = self._visualize_daily_usage(data['timeline']['daily_counts'])
                    if vis_path:
                        visualizations['daily_usage'] = vis_path
                
                # Visualize monthly stats
                if 'monthly_stats' in data['timeline']:
                    vis_path = self._visualize_monthly_usage(data['timeline']['monthly_stats'])
                    if vis_path:
                        visualizations['monthly_usage'] = vis_path
            
            logger.info(f"Generated {len(visualizations)} usage visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating usage visualizations: {str(e)}")
            return visualizations
    
    def _visualize_idea_counts(self, idea_generation: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of idea counts.
        
        Args:
            idea_generation: Idea generation statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Extract data
            total_ideas = idea_generation.get('total_ideas', 0)
            unique_owners = idea_generation.get('unique_owners', 0)
            avg_ideas_per_owner = idea_generation.get('avg_ideas_per_owner', 0)
            max_ideas_per_owner = idea_generation.get('max_ideas_per_owner', 0)
            
            # Create bar chart
            labels = ['Total Ideas', 'Unique Owners', 'Max Ideas/Owner']
            values = [total_ideas, unique_owners, max_ideas_per_owner]
            
            bars = plt.bar(labels, values, color=['royalblue', 'green', 'orange'])
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Idea Generation Overview', fontsize=16)
            plt.ylabel('Count', fontsize=12)
            
            # Add average ideas per owner as text annotation
            plt.annotate(f'Avg Ideas per Owner: {avg_ideas_per_owner:.2f}', 
                       xy=(0.5, 0.05), xycoords='figure fraction',
                       bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8),
                       ha='center')
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"idea_counts.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating idea counts visualization: {str(e)}")
            return None
    
    def _visualize_ideas_by_ranking(self, ideas_by_ranking: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of ideas by ranking.
        
        Args:
            ideas_by_ranking: Counts of ideas by ranking
            
        Returns:
            Path to the visualization file
        """
        try:
            # Convert ranking keys to integers for proper sorting
            rankings = []
            counts = []
            
            # Handle different key formats (string or int)
            for ranking, count in sorted(ideas_by_ranking.items(), 
                                        key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                                            int(float(item[0])) if isinstance(item[0], str) else item[0]
                                        )):
                rankings.append(str(ranking))
                counts.append(count)
            
            # Create figure
            plt.figure(figsize=(12, 6))
            
            # Create bar chart
            bars = plt.bar(rankings, counts, color='lightseagreen')
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Ideas by Ranking', fontsize=16)
            plt.xlabel('Idea Ranking', fontsize=12)
            plt.ylabel('Number of Ideas', fontsize=12)
            
            # Add explanation text
            plt.figtext(0.5, 0.01, 
                      'Ranking represents the nth idea created by a user (1=first idea, 2=second idea, etc.)',
                      ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
            
            plt.tight_layout(rect=[0, 0.05, 1, 1])  # Adjust layout to make room for the explanation
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"ideas_by_ranking.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating ideas by ranking visualization: {str(e)}")
            return None
    
    def _visualize_engagement_levels(self, engagement_levels: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user engagement levels.
        
        Args:
            engagement_levels: Counts by engagement level
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(10, 7))
            
            # Extract data
            labels = []
            values = []
            colors = []
            
            # Define order and colors
            color_map = {
                'high': 'darkgreen',
                'medium': 'yellowgreen',
                'low': 'gold',
                'none': 'lightcoral'
            }
            
            # Custom labels
            label_map = {
                'high': 'High (>5 ideas)',
                'medium': 'Medium (2-5 ideas)',
                'low': 'Low (1 idea)',
                'none': 'None (0 ideas)'
            }
            
            # Sort by engagement level (high to none)
            for key in ['high', 'medium', 'low', 'none']:
                if key in engagement_levels:
                    labels.append(label_map.get(key, key.title()))
                    values.append(engagement_levels[key])
                    colors.append(color_map.get(key, 'gray'))
            
            # Create pie chart
            plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', 
                   startangle=90, shadow=True, explode=[0.05] * len(values))
            
            # Equal aspect ratio ensures the pie chart is circular
            plt.axis('equal')
            
            # Add title
            plt.title('User Engagement Levels', fontsize=16)
            
            # Add a legend with count
            legend_labels = [f"{label} ({count})" for label, count in zip(labels, values)]
            plt.legend(legend_labels, loc="best")
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"engagement_levels.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating engagement levels visualization: {str(e)}")
            return None
    
    def _visualize_framework_engagement(self, framework_engagement: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of framework engagement.
        
        Args:
            framework_engagement: Counts by framework
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 7))
            
            # Extract data
            labels = []
            values = []
            
            # Order of frameworks to display
            frameworks = ['disciplined-entrepreneurship', 'startup-tactics', 
                         'both_frameworks', 'no_framework']
            
            # Custom labels
            label_map = {
                'both_frameworks': 'Both Frameworks',
                'no_framework': 'No Framework'
            }
            
            for framework in frameworks:
                if framework in framework_engagement:
                    label = label_map.get(framework, framework)
                    labels.append(label)
                    values.append(framework_engagement[framework])
            
            # Define colors
            colors = ['dodgerblue', 'darkorange', 'mediumseagreen', 'lightgray']
            
            # Create bar chart
            bars = plt.bar(labels, values, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Framework Engagement', fontsize=16)
            plt.ylabel('Number of Users', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"framework_engagement.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Create Venn diagram view
            plt.figure(figsize=(10, 8))
            
            # Extract counts for Venn diagram
            de_count = framework_engagement.get('disciplined-entrepreneurship', 0)
            st_count = framework_engagement.get('startup-tactics', 0)
            both_count = framework_engagement.get('both_frameworks', 0)
            
            # Adjust counts for Venn diagram (subtract overlap)
            de_only = de_count - both_count
            st_only = st_count - both_count
            
            # Create Venn diagram
            venn = venn2(subsets=(de_only, st_only, both_count), 
                       set_labels=('disciplined-entrepreneurship', 'startup-tactics'))
            
            # Set colors
            venn.get_patch_by_id('10').set_color('dodgerblue')
            venn.get_patch_by_id('01').set_color('darkorange')
            venn.get_patch_by_id('11').set_color('mediumseagreen')
            
            # Set alpha for better visibility
            venn.get_patch_by_id('10').set_alpha(0.7)
            venn.get_patch_by_id('01').set_alpha(0.7)
            venn.get_patch_by_id('11').set_alpha(0.7)
            
            # Add title
            plt.title('Framework Usage Overlap', fontsize=16)
            
            # Add no framework count as text
            no_framework = framework_engagement.get('no_framework', 0)
            plt.figtext(0.5, 0.01, 
                      f'Users with no framework: {no_framework}',
                      ha="center", fontsize=12, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
            
            plt.tight_layout(rect=[0, 0.05, 1, 1])
            
            # Save figure
            venn_output_path = os.path.join(self.vis_dir, f"framework_venn.{self.format}")
            plt.savefig(venn_output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating framework engagement visualization: {str(e)}")
            return None
    
    def _visualize_monthly_active_users(self, monthly_active_users: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of monthly active users.
        
        Args:
            monthly_active_users: Active users by month
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least 2 data points for a meaningful timeline
            if len(monthly_active_users) < 2:
                logger.warning("Not enough monthly active user data for visualization")
                return None
            
            # Create figure
            plt.figure(figsize=(14, 7))
            
            # Convert string dates to datetime objects for proper timeline
            dates = []
            counts = []
            
            for date_str, count in sorted(monthly_active_users.items()):
                try:
                    # Parse date (YYYY-MM format)
                    date_obj = datetime.strptime(date_str, '%Y-%m')
                    dates.append(date_obj)
                    counts.append(count)
                except ValueError:
                    continue
            
            # Plot line chart with markers
            plt.plot(dates, counts, marker='o', linestyle='-', color='crimson', 
                    linewidth=2, markersize=8)
            
            # Fill area under the line
            plt.fill_between(dates, counts, alpha=0.3, color='crimson')
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45, ha='right')
            
            # Add moving average trendline (3-month)
            if len(counts) >= 3:
                ma_window = 3
                ma = []
                for i in range(len(counts)):
                    if i < ma_window - 1:
                        ma.append(None)
                    else:
                        ma.append(sum(counts[i-(ma_window-1):i+1]) / ma_window)
                
                # Remove None values for plotting
                ma_dates = [date for i, date in enumerate(dates) if i >= ma_window - 1]
                ma_values = [val for val in ma if val is not None]
                
                plt.plot(ma_dates, ma_values, linestyle='--', color='navy', 
                        linewidth=2, label=f'{ma_window}-Month Moving Average')
            
            # Add title and labels
            plt.title('Monthly Active Users', fontsize=16)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Number of Active Users', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            if len(counts) >= 3:
                plt.legend()
                
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"monthly_active_users.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating monthly active users visualization: {str(e)}")
            return None
    
    def _visualize_iteration_patterns(self, iteration_patterns: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of idea iteration patterns.
        
        Args:
            iteration_patterns: Iteration pattern data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check for users_by_max_iteration data
            if 'users_by_max_iteration' not in iteration_patterns:
                logger.warning("No iteration pattern data to visualize")
                return None
            
            users_by_max_iteration = iteration_patterns['users_by_max_iteration']
            
            # Create figure
            plt.figure(figsize=(12, 7))
            
            # Extract data
            labels = []
            values = []
            
            # Sort by iteration count
            for iteration, count in sorted(users_by_max_iteration.items(), 
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
            colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(values)))
            
            # Create bar chart
            bars = plt.bar(labels, values, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Users by Maximum Iteration Count', fontsize=16)
            plt.ylabel('Number of Users', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Add explanation
            plt.figtext(0.5, 0.01, 
                      'Iterations refer to the number of different ideas created by a user',
                      ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
            
            plt.tight_layout(rect=[0, 0.05, 1, 1])
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"iteration_patterns.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating iteration patterns visualization: {str(e)}")
            return None
    
    def _visualize_progress_stats(self, progress_stats: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of idea progress statistics.
        
        Args:
            progress_stats: Progress statistics data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create a 2x1 subplot grid
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
            
            # Visualization 1: Progress Distribution
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
                
                # Create a colormap gradient based on progress level
                colors = plt.cm.RdYlGn(np.linspace(0.1, 0.9, len(progress_levels)))
                
                # Create bar chart
                bars = ax1.bar(progress_levels, counts, color=colors)
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{int(height)}',
                            ha='center', va='bottom')
                
                # Add title and labels
                ax1.set_title('Progress Distribution', fontsize=14)
                ax1.set_xlabel('Progress Level', fontsize=12)
                ax1.set_ylabel('Number of Ideas', fontsize=12)
                
                # Rotate x-axis labels for better readability
                ax1.tick_params(axis='x', rotation=45)
            
            # Visualization 2: Framework Progress Comparison
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
                
                # Create a side-by-side bar chart for average progress and total ideas
                x = np.arange(len(frameworks))
                width = 0.35
                
                # Plot average progress
                bars1 = ax2.bar(x - width/2, avg_progress, width, label='Avg Progress %', color='lightseagreen')
                
                # Create a twin axis for total ideas
                ax2_twin = ax2.twinx()
                bars2 = ax2_twin.bar(x + width/2, total_ideas, width, label='Total Ideas', color='coral')
                
                # Add labels and title
                ax2.set_title('Framework Progress Comparison', fontsize=14)
                ax2.set_xticks(x)
                ax2.set_xticklabels(frameworks)
                ax2.set_xlabel('Framework', fontsize=12)
                ax2.set_ylabel('Average Progress %', fontsize=12)
                ax2_twin.set_ylabel('Total Ideas', fontsize=12)
                
                # Set y-limits to start from 0
                ax2.set_ylim(0, max(100, max(avg_progress) * 1.1))
                ax2_twin.set_ylim(0, max(total_ideas) * 1.1)
                
                # Add value labels
                for i, bar in enumerate(bars1):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.1f}%',
                            ha='center', va='bottom')
                
                for i, bar in enumerate(bars2):
                    height = bar.get_height()
                    ax2_twin.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{int(height)}',
                                ha='center', va='bottom')
                
                # Add a legend
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
            output_path = os.path.join(self.vis_dir, f"progress_stats.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating progress stats visualization: {str(e)}")
            return None
    
    def _visualize_framework_counts(self, framework_counts: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of framework usage counts.
        
        Args:
            framework_counts: Counts by framework
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Extract data
            frameworks = []
            counts = []
            
            for framework, count in framework_counts.items():
                if count > 0:  # Filter out unused frameworks
                    frameworks.append(framework)
                    counts.append(count)
            
            # Create a simple bar chart
            # Define colors for known frameworks
            colors = ['dodgerblue' if f == 'disciplined-entrepreneurship' else
                     'darkorange' if f == 'startup-tactics' else
                     'gray' for f in frameworks]
            
            bars = plt.bar(frameworks, counts, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Framework Usage', fontsize=16)
            plt.ylabel('Number of Ideas', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"framework_counts.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating framework counts visualization: {str(e)}")
            return None
    
    def _visualize_framework_completion(self, de_completion: Dict[str, Any], 
                                       st_completion: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of framework completion rates.
        
        Args:
            de_completion: Disciplined Entrepreneurship completion statistics
            st_completion: Startup Tactics completion statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 10))
            
            # Create a 2x2 subplot grid
            fig, axes = plt.subplots(2, 2, figsize=(14, 12))
            
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
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
            
            ax.set_title('Completion Rates', fontsize=14)
            ax.set_ylabel('Completion Rate (%)', fontsize=12)
            ax.set_ylim(0, 100)
            
            # Average progress (top right)
            ax = axes[0, 1]
            bars = ax.bar(frameworks, avg_progress, color=colors, alpha=0.7)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
            
            ax.set_title('Average Progress', fontsize=14)
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
            output_path = os.path.join(self.vis_dir, f"framework_completion.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating framework completion visualization: {str(e)}")
            return None
    
    def _visualize_daily_usage(self, daily_counts: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of daily usage patterns.
        
        Args:
            daily_counts: Daily activity statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a few days of data for a meaningful visualization
            if len(daily_counts) < 5:
                logger.warning("Not enough daily usage data for visualization")
                return None
            
            # Create figure
            plt.figure(figsize=(14, 8))
            
            # Convert string dates to datetime objects for proper timeline
            dates = []
            counts = []
            avg_progress_values = []
            
            for date_str, data in sorted(daily_counts.items()):
                try:
                    # Parse date (YYYY-MM-DD format)
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date_obj)
                    counts.append(data.get('count', 0))
                    avg_progress_values.append(data.get('avg_progress', 0))
                except (ValueError, KeyError):
                    continue
            
            # Plot idea counts
            plt.subplot(2, 1, 1)
            plt.plot(dates, counts, marker='o', linestyle='-', color='royalblue', 
                    linewidth=2, markersize=6, alpha=0.8)
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
            plt.xticks(rotation=45, ha='right')
            
            # Add title and labels
            plt.title('Daily Idea Creation', fontsize=14)
            plt.ylabel('Number of Ideas', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Plot average progress
            plt.subplot(2, 1, 2)
            plt.plot(dates, avg_progress_values, marker='s', linestyle='-', color='green', 
                    linewidth=2, markersize=6, alpha=0.8)
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
            plt.xticks(rotation=45, ha='right')
            
            # Add title and labels
            plt.title('Daily Average Progress', fontsize=14)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Average Progress (%)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"daily_usage.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating daily usage visualization: {str(e)}")
            return None
    
    def _visualize_monthly_usage(self, monthly_stats: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Create visualization of monthly usage patterns.
        
        Args:
            monthly_stats: Monthly statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a few months of data
            if len(monthly_stats) < 2:
                logger.warning("Not enough monthly usage data for visualization")
                return None
            
            # Create figure
            plt.figure(figsize=(14, 8))
            
            # Convert string dates to datetime objects for proper timeline
            months = []
            total_ideas = []
            avg_ideas_per_day = []
            
            for month_str, data in sorted(monthly_stats.items()):
                try:
                    # Parse date (YYYY-MM format)
                    month_obj = datetime.strptime(month_str, '%Y-%m')
                    months.append(month_obj)
                    total_ideas.append(data.get('total_ideas', 0))
                    avg_ideas_per_day.append(data.get('avg_ideas_per_day', 0))
                except (ValueError, KeyError):
                    continue
            
            # Plot total ideas
            plt.subplot(2, 1, 1)
            plt.bar(months, total_ideas, color='cornflowerblue', alpha=0.7)
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45, ha='right')
            
            # Add trend line
            x = mdates.date2num(months)
            z = np.polyfit(x, total_ideas, 1)
            p = np.poly1d(z)
            plt.plot(months, p(x), "r--", alpha=0.7, 
                    label=f'Trend ({z[0]:.2f} ideas/month)')
            plt.legend()
            
            # Add title and labels
            plt.title('Monthly Total Ideas', fontsize=14)
            plt.ylabel('Number of Ideas', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Plot average ideas per day
            plt.subplot(2, 1, 2)
            plt.bar(months, avg_ideas_per_day, color='mediumseagreen', alpha=0.7)
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45, ha='right')
            
            # Add title and labels
            plt.title('Average Ideas Per Day', fontsize=14)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Avg Ideas/Day', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"monthly_usage.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating monthly usage visualization: {str(e)}")
            return None
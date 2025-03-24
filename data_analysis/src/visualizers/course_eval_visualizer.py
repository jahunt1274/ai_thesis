"""
Course evaluation visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("course_eval_visualizer")


class CourseEvaluationVisualizer(BaseVisualizer):
    """Visualizes course evaluation analysis results."""
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the course evaluation visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format
        
        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "course_evaluations")
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for course evaluation analysis.
        
        Args:
            data: Course evaluation analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info("Generating course evaluation visualizations")
        
        visualizations = {}
        
        # Check if necessary data exists
        if not data:
            logger.warning("No course evaluation data to visualize")
            return visualizations
        
        # Create various evaluation visualizations
        try:
            # Semester comparison
            if 'semester_comparison' in data:
                vis_path = self._visualize_semester_comparison(data['semester_comparison'])
                if vis_path:
                    visualizations['semester_comparison'] = vis_path
            
            # Tool impact
            if 'tool_impact' in data:
                vis_path = self._visualize_tool_impact(data['tool_impact'])
                if vis_path:
                    visualizations['tool_impact'] = vis_path
            
            # Section analysis
            if 'section_analysis' in data:
                vis_path = self._visualize_section_performance(data['section_analysis'])
                if vis_path:
                    visualizations['section_performance'] = vis_path
            
            # Question analysis
            if 'question_analysis' in data:
                vis_path = self._visualize_key_questions(data['question_analysis'])
                if vis_path:
                    visualizations['key_questions'] = vis_path
            
            # Rating trends
            if 'trend_analysis' in data:
                vis_path = self._visualize_rating_trends(data['trend_analysis'])
                if vis_path:
                    visualizations['rating_trends'] = vis_path
            
            logger.info(f"Generated {len(visualizations)} course evaluation visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating course evaluation visualizations: {str(e)}")
            return visualizations
    
    def _visualize_semester_comparison(self, comparison_data: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of semester comparison.
        
        Args:
            comparison_data: Semester comparison data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Extract data
            semesters = comparison_data.get('display_names', [])
            overall_avg = comparison_data.get('overall_avg', [])
            tool_versions = comparison_data.get('tool_versions', [])
            
            if not semesters or not overall_avg:
                logger.warning("Insufficient data for semester comparison visualization")
                return None
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Define colors based on tool version
            colors = ['lightgray' if v is None else 'lightblue' if v == 'v1' else 'cornflowerblue' 
                    for v in tool_versions]
            
            # Create bar chart
            bars = plt.bar(semesters, overall_avg, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        f'{height:.2f}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Overall Evaluation Scores by Semester', fontsize=16)
            plt.ylabel('Average Score', fontsize=12)
            plt.ylim(0, max(overall_avg) * 1.2)  # Add some space at the top
            
            # Add tool version annotations
            for i, (semester, version) in enumerate(zip(semesters, tool_versions)):
                tool_label = 'No Tool' if version is None else f'Jetpack {version}'
                plt.annotate(tool_label,
                           (i, 0.2),
                           xytext=(0, -20),
                           textcoords='offset points',
                           ha='center',
                           rotation=45)
            
            # Add term comparison if available
            term_comparisons = comparison_data.get('term_comparisons', {})
            fall_avg = term_comparisons.get('fall_avg')
            spring_avg = term_comparisons.get('spring_avg')
            
            if fall_avg is not None and spring_avg is not None:
                # Add a horizontal line for fall and spring averages
                plt.axhline(y=fall_avg, color='orange', linestyle='--', 
                         label=f'Fall Avg: {fall_avg:.2f}')
                plt.axhline(y=spring_avg, color='green', linestyle='--',
                         label=f'Spring Avg: {spring_avg:.2f}')
                plt.legend()
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"semester_comparison.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating semester comparison visualization: {str(e)}")
            return None
    
    def _visualize_tool_impact(self, impact_data: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of tool impact.
        
        Args:
            impact_data: Tool impact data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check for necessary data
            version_metrics = impact_data.get('version_metrics', {})
            seasonal_impact = impact_data.get('seasonal_impact', {})
            
            if not version_metrics:
                logger.warning("Insufficient data for tool impact visualization")
                return None
            
            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))
            
            # Extract data for overall comparison
            tool_versions = []
            avg_scores = []
            num_semesters = []
            
            for version, metrics in sorted(version_metrics.items()):
                # Format the version name
                version_name = 'No Tool' if version == 'none' else f'Jetpack {version}'
                
                tool_versions.append(version_name)
                avg_scores.append(metrics.get('avg_score', 0))
                num_semesters.append(metrics.get('num_semesters', 0))
            
            # Colors for tool versions
            colors = ['lightgray' if v == 'No Tool' else 'lightblue' if v == 'Jetpack v1' else 'cornflowerblue' 
                    for v in tool_versions]
            
            # Plot 1: Overall comparison by tool version
            bars1 = ax1.bar(tool_versions, avg_scores, color=colors)
            
            # Add value labels on top of bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        f'{height:.2f}',
                        ha='center', va='bottom')
            
            # Add semester count annotation
            for i, count in enumerate(num_semesters):
                ax1.text(i, 0.2, f'{count} semester(s)',
                       ha='center', va='bottom',
                       color='black', fontsize=10)
            
            ax1.set_title('Average Evaluation Score by Tool Version', fontsize=16)
            ax1.set_ylabel('Average Score', fontsize=12)
            ax1.set_ylim(0, max(avg_scores) * 1.2)  # Add some space at the top
            
            # Plot 2: Seasonal comparison by tool version
            tool_versions_seasonal = []
            fall_avgs = []
            spring_avgs = []
            
            for version, metrics in sorted(seasonal_impact.items()):
                # Format the version name
                version_name = 'No Tool' if version == 'none' else f'Jetpack {version}'
                
                fall_avg = metrics.get('fall_avg')
                spring_avg = metrics.get('spring_avg')
                
                if fall_avg is not None or spring_avg is not None:
                    tool_versions_seasonal.append(version_name)
                    fall_avgs.append(fall_avg if fall_avg is not None else 0)
                    spring_avgs.append(spring_avg if spring_avg is not None else 0)
            
            # Set width for grouped bars
            if tool_versions_seasonal:
                x = np.arange(len(tool_versions_seasonal))
                width = 0.35
                
                # Create grouped bar chart
                ax2.bar(x - width/2, fall_avgs, width, label='Fall', color='orange')
                ax2.bar(x + width/2, spring_avgs, width, label='Spring', color='green')
                
                # Add labels and title
                ax2.set_xlabel('Tool Version', fontsize=12)
                ax2.set_ylabel('Average Score', fontsize=12)
                ax2.set_title('Fall vs Spring Comparison by Tool Version', fontsize=16)
                ax2.set_xticks(x)
                ax2.set_xticklabels(tool_versions_seasonal)
                ax2.legend()
                
                # Add annotations for missing data
                for i, (fall, spring) in enumerate(zip(fall_avgs, spring_avgs)):
                    if fall == 0:
                        ax2.text(i - width/2, 0.5, 'No data',
                               ha='center', va='bottom', color='gray', fontsize=10)
                    if spring == 0:
                        ax2.text(i + width/2, 0.5, 'No data',
                               ha='center', va='bottom', color='gray', fontsize=10)
            else:
                ax2.text(0.5, 0.5, "Insufficient data for seasonal comparison",
                       ha='center', va='center', fontsize=14, transform=ax2.transAxes)
                ax2.axis('off')
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"tool_impact.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating tool impact visualization: {str(e)}")
            return None
    
    def _visualize_section_performance(self, section_data: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of section performance.
        
        Args:
            section_data: Section performance data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Extract data
            sections = section_data.get('sections', [])
            semester_data = section_data.get('by_semester', {})
            
            if not sections or not semester_data:
                logger.warning("Insufficient data for section performance visualization")
                return None
            
            # Sort semesters chronologically
            sorted_semesters = sorted(semester_data.keys())
            
            # Create a heatmap of section scores by semester
            section_scores = np.zeros((len(sections), len(sorted_semesters)))
            section_scores.fill(np.nan)  # Fill with NaN for missing data
            
            # Fill in available data
            for i, section in enumerate(sections):
                for j, semester in enumerate(sorted_semesters):
                    section_averages = semester_data[semester].get('section_averages', {})
                    if section in section_averages:
                        section_scores[i, j] = section_averages[section]
            
            # Prepare display names for x-axis labels
            x_labels = [semester_data[s].get('display_name', s) for s in sorted_semesters]
            
            # Calculate overall min/max for consistent colormap
            valid_scores = section_scores[~np.isnan(section_scores)]
            vmin = np.min(valid_scores) if len(valid_scores) > 0 else 0
            vmax = np.max(valid_scores) if len(valid_scores) > 0 else 7
            
            # Create figure
            plt.figure(figsize=(14, 10))
            
            # Create heatmap
            im = plt.imshow(section_scores, cmap='viridis', aspect='auto', vmin=vmin, vmax=vmax)
            
            # Add colorbar
            cbar = plt.colorbar(im)
            cbar.set_label('Average Score', fontsize=12)
            
            # Add labels
            plt.xticks(np.arange(len(x_labels)), x_labels, rotation=45, ha='right')
            plt.yticks(np.arange(len(sections)), sections)
            
            # Add tool version annotations if available
            for i, semester in enumerate(sorted_semesters):
                tool_version = semester_data[semester].get('tool_version')
                if tool_version is not None:
                    tool_label = f"({tool_version})"
                elif tool_version is None:
                    tool_label = "(no tool)"
                else:
                    tool_label = ""
                
                if tool_label:
                    plt.annotate(tool_label,
                               (i, -0.5),
                               xytext=(0, -15),
                               textcoords='offset points',
                               ha='center',
                               fontsize=9)
            
            # Add title
            plt.title('Section Performance by Semester', fontsize=16)
            
            # Add values in each cell
            for i in range(len(sections)):
                for j in range(len(sorted_semesters)):
                    value = section_scores[i, j]
                    if not np.isnan(value):
                        plt.text(j, i, f"{value:.2f}",
                               ha="center", va="center",
                               color="white" if value < (vmin + vmax) / 2 else "black")
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"section_performance.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating section performance visualization: {str(e)}")
            return None
    
    def _visualize_key_questions(self, question_data: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of key question responses.
        
        Args:
            question_data: Key question analysis data
            
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
            fig, axes = plt.subplots(num_categories, 1, figsize=(12, 5 * num_categories))
            
            # Handle case of single category
            if num_categories == 1:
                axes = [axes]
            
            # Process each category
            for i, category in enumerate(categories):
                category_data = question_data[category]
                semester_data = category_data.get('semesters', {})
                
                if not semester_data:
                    axes[i].text(0.5, 0.5, f"No data for {category}",
                               ha='center', va='center', transform=axes[i].transAxes)
                    axes[i].set_title(category.replace('_', ' ').title(), fontsize=14)
                    axes[i].axis('off')
                    continue
                
                # Sort semesters chronologically
                sorted_semesters = sorted(semester_data.keys())
                x_labels = [semester_data[s].get('display_name', s) for s in sorted_semesters]
                scores = [semester_data[s].get('avg_score', 0) for s in sorted_semesters]
                tool_versions = [semester_data[s].get('tool_version') for s in sorted_semesters]
                
                # Define colors based on tool version
                colors = ['lightgray' if v is None else 'lightblue' if v == 'v1' else 'cornflowerblue' 
                        for v in tool_versions]
                
                # Create bar chart
                bars = axes[i].bar(x_labels, scores, color=colors)
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    axes[i].text(bar.get_x() + bar.get_width()/2., height + 0.05,
                               f'{height:.2f}',
                               ha='center', va='bottom')
                
                # Add tool version annotations
                for j, version in enumerate(tool_versions):
                    tool_label = 'No Tool' if version is None else f'Jetpack {version}'
                    axes[i].annotate(tool_label,
                                  (j, 0.2),
                                  xytext=(0, -15),
                                  textcoords='offset points',
                                  ha='center',
                                  rotation=45,
                                  fontsize=8)
                
                # Format category name for title
                category_title = category.replace('_', ' ').title()
                axes[i].set_title(f'{category_title} Questions', fontsize=14)
                axes[i].set_ylabel('Average Score', fontsize=12)
                axes[i].set_ylim(0, max(scores) * 1.2 if scores else 7)  # Add some space at the top
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"key_questions.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating key questions visualization: {str(e)}")
            return None
    
    def _visualize_rating_trends(self, trend_data: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of rating trends over time.
        
        Args:
            trend_data: Rating trend data
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check for timeline data
            timeline = trend_data.get('timeline', [])
            if not timeline:
                logger.warning("No timeline data for rating trends visualization")
                return None
            
            # Create figure with multiple subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
            
            # Extract data for overall trend
            semester_labels = [item.get('display_name', '') for item in timeline]
            overall_scores = [item.get('overall_avg', 0) for item in timeline]
            tool_versions = [item.get('tool_version') for item in timeline]
            terms = [item.get('term', '') for item in timeline]
            
            # Define colors based on term
            term_colors = ['orange' if term == 'fall' else 'green' for term in terms]
            
            # Plot 1: Overall trend with term highlighting
            ax1.plot(semester_labels, overall_scores, 'o-', color='navy', linewidth=2, markersize=8)
            
            # Add colored markers for terms
            for i, (score, color) in enumerate(zip(overall_scores, term_colors)):
                ax1.plot(i, score, 'o', color=color, markersize=12, alpha=0.5)
            
            # Add tool version annotations
            for i, version in enumerate(tool_versions):
                tool_label = 'No Tool' if version is None else f'Jetpack {version}'
                ax1.annotate(tool_label,
                          (i, min(overall_scores) - 0.2),
                          xytext=(0, -20),
                          textcoords='offset points',
                          ha='center',
                          fontsize=10)
            
            # Highlight tool version changes
            for i in range(1, len(tool_versions)):
                if tool_versions[i] != tool_versions[i-1]:
                    ax1.axvline(x=i-0.5, color='red', linestyle='--', alpha=0.5)
            
            ax1.set_title('Overall Evaluation Score Trend', fontsize=16)
            ax1.set_ylabel('Average Score', fontsize=12)
            ax1.set_ylim(min(overall_scores) * 0.9 if overall_scores else 0, 
                         max(overall_scores) * 1.1 if overall_scores else 7)
            
            # Add legend for terms
            fall_patch = plt.Line2D([0], [0], marker='o', color='white', markerfacecolor='orange', 
                                  markersize=10, label='Fall')
            spring_patch = plt.Line2D([0], [0], marker='o', color='white', markerfacecolor='green', 
                                    markersize=10, label='Spring')
            tool_change = plt.Line2D([0], [0], color='red', linestyle='--', label='Tool Version Change')
            
            ax1.legend(handles=[fall_patch, spring_patch, tool_change], loc='lower right')
            
            # Plot 2: Semester-to-semester changes
            changes = trend_data.get('changes', [])
            if changes:
                change_labels = [f"{change.get('from_semester', '')} → {change.get('to_semester', '')}" 
                               for change in changes]
                change_values = [change.get('change', 0) for change in changes]
                
                # Color based on direction and tool change
                change_colors = []
                for change in changes:
                    if change.get('tool_change', False):
                        # Tool change - use purple for highlighting
                        change_colors.append('purple')
                    elif change.get('change', 0) > 0:
                        # Positive change - green
                        change_colors.append('green')
                    else:
                        # Negative change - red
                        change_colors.append('red')
                
                # Create bar chart
                bars = ax2.bar(change_labels, change_values, color=change_colors, alpha=0.7)
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    y_pos = height + 0.05 if height > 0 else height - 0.15
                    ax2.text(bar.get_x() + bar.get_width()/2., y_pos,
                           f'{height:.2f}',
                           ha='center', va='bottom')
                
                ax2.set_title('Semester-to-Semester Changes', fontsize=16)
                ax2.set_ylabel('Score Change', fontsize=12)
                
                # Add a horizontal line at y=0
                ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                
                # Annotate tool version changes
                for i, change in enumerate(changes):
                    if change.get('tool_change', False):
                        from_tool = 'No Tool' if change.get('from_tool') is None else f"Jetpack {change.get('from_tool')}"
                        to_tool = 'No Tool' if change.get('to_tool') is None else f"Jetpack {change.get('to_tool')}"
                        
                        ax2.annotate(f"{from_tool} → {to_tool}",
                                   (i, 0),
                                   xytext=(0, -30 if change.get('change', 0) > 0 else 20),
                                   textcoords='offset points',
                                   ha='center',
                                   fontsize=9,
                                   bbox=dict(boxstyle="round,pad=0.3", fc="lavender", ec="purple", alpha=0.8))
            else:
                ax2.text(0.5, 0.5, "Insufficient data for change analysis",
                       ha='center', va='center', fontsize=14, transform=ax2.transAxes)
                ax2.axis('off')
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"rating_trends.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating rating trends visualization: {str(e)}")
            return None
"""
Demographic visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("demographic_visualizer")


class DemographicVisualizer(BaseVisualizer):
    """Visualizes demographic analysis results."""
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the demographic visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format
        
        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "demographics")
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for demographic analysis.
        
        Args:
            data: Demographic analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info("Generating demographic visualizations")
        
        visualizations = {}
        
        # Check if necessary data exists
        if not data:
            logger.warning("No demographic data to visualize")
            return visualizations
        
        # Create various demographic visualizations
        try:
            # User counts
            if 'user_counts' in data:
                vis_path = self._visualize_user_counts(data['user_counts'])
                if vis_path:
                    visualizations['user_counts'] = vis_path
            
            # Affiliations
            if 'affiliations' in data:
                vis_path = self._visualize_affiliations(data['affiliations'])
                if vis_path:
                    visualizations['affiliations'] = vis_path
            
            # Cohorts
            if 'cohorts' in data and 'user_types' in data['cohorts']:
                vis_path = self._visualize_user_types(data['cohorts']['user_types'])
                if vis_path:
                    visualizations['cohorts_user_types'] = vis_path
            
            # Activity cohorts
            if 'cohorts' in data and 'activity' in data['cohorts']:
                vis_path = self._visualize_activity_cohorts(data['cohorts']['activity'])
                if vis_path:
                    visualizations['cohorts_activity'] = vis_path
            
            # User creation over time
            if 'cohorts' in data and 'creation_dates' in data['cohorts']:
                vis_path = self._visualize_user_creation(data['cohorts']['creation_dates'])
                if vis_path:
                    visualizations['cohorts_creation_timeline'] = vis_path
            
            # Enrollments
            if 'enrollments' in data:
                vis_path = self._visualize_enrollments(data['enrollments'])
                if vis_path:
                    visualizations['enrollments'] = vis_path
                
                if 'top_courses' in data['enrollments']:
                    vis_path = self._visualize_top_courses(data['enrollments']['top_courses'])
                    if vis_path:
                        visualizations['enrollments_top_courses'] = vis_path
            
            # Interests
            if 'interests' in data and 'interests' in data['interests']:
                vis_path = self._visualize_interests(data['interests']['interests'])
                if vis_path:
                    visualizations['interests'] = vis_path
            
            # Institutions
            if 'institutions' in data:
                vis_path = self._visualize_institutions(data['institutions'])
                if vis_path:
                    visualizations['institutions'] = vis_path
            
            logger.info(f"Generated {len(visualizations)} demographic visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating demographic visualizations: {str(e)}")
            return visualizations
    
    def _visualize_user_counts(self, user_counts: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user counts.
        
        Args:
            user_counts: User count statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Extract data
            labels = []
            values = []
            
            for key, value in user_counts.items():
                if key not in ('total_users'):  # Skip total for the bar chart
                    labels.append(key.replace('_', ' ').title())
                    values.append(value)
            
            # Add total as a separate category
            if 'total_users' in user_counts:
                labels.append('Total Users')
                values.append(user_counts['total_users'])
            
            # Create bar chart
            bars = plt.bar(labels, values, color='steelblue')
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('User Counts', fontsize=16)
            plt.ylabel('Count', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"user_counts.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating user counts visualization: {str(e)}")
            return None
    
    def _visualize_affiliations(self, affiliations: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user affiliations.
        
        Args:
            affiliations: User affiliation counts
            
        Returns:
            Path to the visualization file
        """
        try:
            # Filter out low-count affiliations and sort by count
            min_count = 3  # Minimum count to include
            sorted_affiliations = sorted(
                [(k, v) for k, v in affiliations.items() if v >= min_count],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Limit to top 10 for readability
            if len(sorted_affiliations) > 10:
                sorted_affiliations = sorted_affiliations[:10]
                
            if not sorted_affiliations:
                logger.warning("No significant affiliations to visualize")
                return None
            
            # Extract data
            labels = [item[0].replace('_', ' ').title() for item in sorted_affiliations]
            values = [item[1] for item in sorted_affiliations]
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create horizontal bar chart for better readability with many categories
            bars = plt.barh(labels, values, color='lightsteelblue')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left', va='center')
            
            # Add title and labels
            plt.title('User Affiliations', fontsize=16)
            plt.xlabel('Count', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"affiliations.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating affiliations visualization: {str(e)}")
            return None
    
    def _visualize_user_types(self, user_types: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user types.
        
        Args:
            user_types: Counts by user type
            
        Returns:
            Path to the visualization file
        """
        try:
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
                significant_types['Other'] = other_count
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            
            # Extract data
            labels = [k.replace('_', ' ').title() for k in significant_types.keys()]
            values = list(significant_types.values())
            
            # Add percentage to labels
            labels = [f'{label} ({value/total:.1%})' for label, value in zip(labels, values)]
            
            # Create pie chart with shadow for depth
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True,
                   wedgeprops={'edgecolor': 'w', 'linewidth': 1})
            
            # Equal aspect ratio ensures the pie chart is circular
            plt.axis('equal')
            
            # Add title
            plt.title('User Types Distribution', fontsize=16)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"user_types.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating user types visualization: {str(e)}")
            return None
    
    def _visualize_activity_cohorts(self, activity_cohorts: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of activity cohorts.
        
        Args:
            activity_cohorts: User counts by activity level
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(12, 7))
            
            # Extract data and convert keys to readable labels
            labels = []
            values = []
            colors = []
            
            # Define order and colors for activity levels
            color_map = {
                'active_last_30d': 'darkgreen',
                'active_31d_90d': 'yellowgreen', 
                'active_91d_180d': 'gold',
                'active_181d_365d': 'orange',
                'inactive_over_365d': 'firebrick'
            }
            
            # Custom labels map
            label_map = {
                'active_last_30d': 'Active (Last 30 Days)',
                'active_31d_90d': 'Active (31-90 Days)',
                'active_91d_180d': 'Active (91-180 Days)',
                'active_181d_365d': 'Active (181-365 Days)',
                'inactive_over_365d': 'Inactive (>365 Days)'
            }
            
            # Sort by order defined in the maps
            for key in color_map.keys():
                if key in activity_cohorts:
                    labels.append(label_map.get(key, key.replace('_', ' ').title()))
                    values.append(activity_cohorts[key])
                    colors.append(color_map[key])
            
            # Create bar chart
            bars = plt.bar(labels, values, color=colors)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('User Activity Cohorts', fontsize=16)
            plt.ylabel('Number of Users', fontsize=12)
            plt.xticks(rotation=20, ha='right')
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"activity_cohorts.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating activity cohorts visualization: {str(e)}")
            return None
    
    def _visualize_user_creation(self, creation_dates: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user creation over time.
        
        Args:
            creation_dates: User counts by creation date (YYYY-MM)
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least 2 data points for a meaningful timeline
            if len(creation_dates) < 2:
                logger.warning("Not enough creation date data for visualization")
                return None
            
            # Create figure
            plt.figure(figsize=(14, 7))
            
            # Convert string dates to datetime objects for proper timeline
            dates = []
            counts = []
            
            for date_str, count in sorted(creation_dates.items()):
                try:
                    # Parse date (YYYY-MM format)
                    date_obj = datetime.strptime(date_str, '%Y-%m')
                    dates.append(date_obj)
                    counts.append(count)
                except ValueError:
                    continue
            
            # Plot line chart with markers
            plt.plot(dates, counts, marker='o', linestyle='-', color='royalblue', 
                    linewidth=2, markersize=8)
            
            # Fill area under the line
            plt.fill_between(dates, counts, alpha=0.3, color='royalblue')
            
            # Format x-axis as dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.xticks(rotation=45, ha='right')
            
            # Add cumulative trendline
            cumulative_counts = np.cumsum(counts)
            ax2 = plt.gca().twinx()
            ax2.plot(dates, cumulative_counts, linestyle='--', color='forestgreen', 
                    alpha=0.7, label='Cumulative Users')
            ax2.set_ylabel('Cumulative Users', color='forestgreen', fontsize=12)
            ax2.tick_params(axis='y', colors='forestgreen')
            
            # Add title and labels
            plt.title('User Registration Timeline', fontsize=16)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('New Users', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"user_registration_timeline.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating user creation timeline visualization: {str(e)}")
            return None
    
    def _visualize_enrollments(self, enrollments: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization of enrollment statistics.
        
        Args:
            enrollments: Enrollment statistics
            
        Returns:
            Path to the visualization file
        """
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Extract data
            users_with_enrollments = enrollments.get('users_with_enrollments', 0)
            total_enrollments = enrollments.get('total_enrollments', 0)
            avg_enrollments = enrollments.get('avg_enrollments_per_user', 0)
            
            # Create bar chart for enrollment stats
            stats = ['Users With Enrollments', 'Total Enrollments', 'Avg Enrollments Per User']
            values = [users_with_enrollments, total_enrollments, avg_enrollments]
            
            # Special handling for avg_enrollments which is typically a float
            if isinstance(avg_enrollments, float):
                # Format the display value but keep the bar height accurate
                stats[2] = f'Avg Enrollments\nPer User: {avg_enrollments:.2f}'
            
            # Create bars with different colors
            bars = plt.bar(stats[:2], values[:2], color=['cornflowerblue', 'mediumseagreen'])
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # Add title and labels
            plt.title('Enrollment Statistics', fontsize=16)
            plt.ylabel('Count', fontsize=12)
            plt.tight_layout()
            
            # Add the average as text instead of a bar if it's very small compared to total
            if avg_enrollments < total_enrollments / 10:
                plt.annotate(f'Avg Enrollments Per User: {avg_enrollments:.2f}', 
                           xy=(0.5, 0.05), xycoords='figure fraction',
                           bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8),
                           ha='center')
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"enrollment_stats.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating enrollments visualization: {str(e)}")
            return None
    
    def _visualize_top_courses(self, top_courses: List[tuple]) -> Optional[str]:
        """
        Create visualization of top courses.
        
        Args:
            top_courses: List of (course_name, count) tuples
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have course data
            if not top_courses:
                logger.warning("No course data to visualize")
                return None
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
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
            bars = plt.barh(courses, counts, color='lightskyblue')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left', va='center')
            
            # Add title and labels
            plt.title('Top Courses by Enrollment', fontsize=16)
            plt.xlabel('Number of Enrollments', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"top_courses.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating top courses visualization: {str(e)}")
            return None
    
    def _visualize_interests(self, interests: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user interests.
        
        Args:
            interests: Counts by interest
            
        Returns:
            Path to the visualization file
        """
        try:
            # Filter out low-count interests and sort by count
            min_count = 3  # Minimum count to include
            sorted_interests = sorted(
                [(k, v) for k, v in interests.items() if v >= min_count],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Limit to top 15 for readability
            if len(sorted_interests) > 15:
                sorted_interests = sorted_interests[:15]
                
            if not sorted_interests:
                logger.warning("No significant interests to visualize")
                return None
            
            # Extract data
            labels = [item[0].replace('_', ' ').title() for item in sorted_interests]
            values = [item[1] for item in sorted_interests]
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create horizontal bar chart for better readability with many categories
            bars = plt.barh(labels, values, color='lightgreen')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left', va='center')
            
            # Add title and labels
            plt.title('User Interests', fontsize=16)
            plt.xlabel('Count', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"interests.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating interests visualization: {str(e)}")
            return None
    
    def _visualize_institutions(self, institutions: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of user institutions.
        
        Args:
            institutions: Counts by institution
            
        Returns:
            Path to the visualization file
        """
        try:
            # Filter out low-count institutions and sort by count
            min_count = 2  # Minimum count to include
            sorted_institutions = sorted(
                [(k, v) for k, v in institutions.items() if v >= min_count],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Limit to top 10 for readability
            if len(sorted_institutions) > 10:
                sorted_institutions = sorted_institutions[:10]
                
            if not sorted_institutions:
                logger.warning("No significant institutions to visualize")
                return None
            
            # Extract data
            labels = [item[0].replace('_', ' ').title() for item in sorted_institutions]
            values = [item[1] for item in sorted_institutions]
            
            # Calculate percentage of total
            total = sum(values)
            percentages = [val/total*100 for val in values]
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create horizontal bar chart
            bars = plt.barh(labels, values, color='mediumpurple')
            
            # Add value labels with percentages
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                        f'{int(width)} ({percentages[i]:.1f}%)',
                        ha='left', va='center')
            
            # Add title and labels
            plt.title('User Institutions', fontsize=16)
            plt.xlabel('Count', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"institutions.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating institutions visualization: {str(e)}")
            return None
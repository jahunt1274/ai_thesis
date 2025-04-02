"""
Demographic visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("demographic_visualizer")


class DemographicVisualizer(BaseVisualizer):
    """Visualizes demographic analysis results."""
    
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for demographic analysis.
        
        Args:
            data: Demographic analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Define visualization mapping
        visualization_map = {
            'user_counts': (self._visualize_user_counts, {'data_key': 'user_counts'}),
            'affiliations': (self._visualize_affiliations, {'data_key': 'affiliations'}),
            'user_types': (self._visualize_user_types, {'data_key': 'cohorts.user_types'}),
            'activity_cohorts': (self._visualize_activity_cohorts, {'data_key': 'cohorts.activity'}),
            'creation_timeline': (self._visualize_user_creation, {'data_key': 'cohorts.creation_dates'}),
            'enrollments': (self._visualize_enrollments, {'data_key': 'enrollments'}),
            'top_courses': (self._visualize_top_courses, {'data_key': 'enrollments.top_courses'}),
            'interests': (self._visualize_interests, {'data_key': 'interests.interests'}),
            'institutions': (self._visualize_institutions, {'data_key': 'institutions'})
        }
        
        # Use the helper method from BaseVisualizer
        return self.visualize_all(data, visualization_map)

    def _visualize_affiliations(self, affiliations: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user affiliations.
        
        Args:
            affiliations: Counts by affiliation
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
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
            return None
        
        # Extract data
        labels = [item[0].replace('_', ' ').title() for item in sorted_affiliations]
        values = [item[1] for item in sorted_affiliations]
        
        # Create bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='User Affiliations',
            xlabel='Count',
            horizontal=True,
            color='lightsteelblue'
        )
    
    def _visualize_user_types(self, user_types: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user types.
        
        Args:
            user_types: Counts by user type
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not user_types:
            return None
            
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
        
        # Extract data
        labels = [k.replace('_', ' ').title() for k in significant_types.keys()]
        values = list(significant_types.values())
        
        # Create pie chart
        return self.create_pie_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='User Types Distribution',
            add_legend=True
        )
    
    def _visualize_activity_cohorts(self, activity_cohorts: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of activity cohorts.
        
        Args:
            activity_cohorts: Counts by activity cohort
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not activity_cohorts:
            return None
        
        # Define order and colors for activity levels
        color_map = {
            'active_last_30d': self.STANDARD_COLORS['high'],
            'active_31d_90d': self.STANDARD_COLORS['medium'],
            'active_91d_180d': self.STANDARD_COLORS['low'],
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
        
        # Extract data in the correct order
        labels = []
        values = []
        colors = []
        
        for key in color_map.keys():
            if key in activity_cohorts:
                labels.append(label_map.get(key, key.replace('_', ' ').title()))
                values.append(activity_cohorts[key])
                colors.append(color_map[key])
        
        # Create bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='User Activity Cohorts',
            ylabel='Number of Users',
            color=colors,
            rotation=20
        )
    
    def _visualize_user_creation(self, creation_dates: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user creation over time.
        
        Args:
            creation_dates: Counts by creation date
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Need at least 2 data points for a meaningful timeline
        if len(creation_dates) < 2:
            return None
        
        # Convert string dates to datetime objects for proper timeline
        dates = []
        counts = []
        
        for date_str, count in sorted(creation_dates.items()):
            date_obj = self.parse_date(date_str)
            if date_obj:
                dates.append(date_obj)
                counts.append(count)
        
        # Setup figure and subplots
        fig, ax1 = plt.subplots(figsize=(14, 7))
        
        # Plot line chart for new users
        ax1.plot(dates, counts, marker='o', linestyle='-', color='royalblue', 
                linewidth=2, markersize=8)
        
        # Fill area under the line
        ax1.fill_between(dates, counts, alpha=0.3, color='royalblue')
        
        # Format x-axis as dates
        self.format_date_axis(ax1)
        
        # Add title and labels
        ax1.set_title('User Registration Timeline', fontsize=16)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('New Users', fontsize=12)
        
        # Add cumulative trendline
        cumulative_counts = np.cumsum(counts)
        ax2 = ax1.twinx()
        ax2.plot(dates, cumulative_counts, linestyle='--', color='forestgreen', 
                alpha=0.7, label='Cumulative Users')
        ax2.set_ylabel('Cumulative Users', fontsize=12, color='forestgreen')
        ax2.tick_params(axis='y', colors='forestgreen')
        
        # Add grid and legend
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax2.legend(loc='upper left')
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_enrollments(self, enrollments: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of enrollment statistics.
        
        Args:
            enrollments: Enrollment statistics
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        if not enrollments:
            return None
    
        # Extract data
        users_with_enrollments = enrollments.get('users_with_enrollments', 0)
        total_enrollments = enrollments.get('total_enrollments', 0)
        avg_enrollments = enrollments.get('avg_enrollments_per_user', 0)
        
        # Create stats labels
        stats = ['Users With Enrollments', 'Total Enrollments']
        values = [users_with_enrollments, total_enrollments]
        
        # Create bar chart
        result = self.create_bar_chart(
            labels=stats,
            values=values,
            filename=filename,
            title='Enrollment Statistics',
            ylabel='Count',
            color=['cornflowerblue', 'mediumseagreen']
        )
        
        # Add the average as text annotation if it's very small compared to total
        if result and avg_enrollments < total_enrollments / 10:
            # Get the figure and add an annotation
            fig = plt.figure()
            plt.annotate(f'Avg Enrollments Per User: {avg_enrollments:.2f}', 
                       xy=(0.5, 0.05), xycoords='figure fraction',
                       bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8),
                       ha='center')
            plt.close(fig)
            
        return result
    
    def _visualize_top_courses(self, top_courses: List[tuple], filename: str) -> Optional[str]:
        """
        Create visualization of top courses.
        
        Args:
            top_courses: List of (course, count) tuples
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Check if we have course data
        if not top_courses:
            return None
        
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
        return self.create_bar_chart(
            labels=courses,
            values=counts,
            filename=filename,
            title='Top Courses by Enrollment',
            xlabel='Number of Enrollments',
            horizontal=True,
            color='lightskyblue'
        )
    
    def _visualize_interests(self, interests: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user interests.
        
        Args:
            interests: Counts by interest
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
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
            return None
        
        # Extract data
        labels = [item[0].replace('_', ' ').title() for item in sorted_interests]
        values = [item[1] for item in sorted_interests]
        
        # Create horizontal bar chart
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='User Interests',
            xlabel='Count',
            horizontal=True,
            color='lightgreen'
        )
    
    def _visualize_user_counts(self, user_counts: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user counts.
        
        Args:
            user_counts: User counts by category
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
        # Skip if no data
        if not user_counts:
            return None
        
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
        
        # Create bar chart from data
        return self.create_bar_chart(
            labels=labels,
            values=values,
            filename=filename,
            title='User Counts',
            ylabel='Count',
            color=self.STANDARD_COLORS['primary'],
            rotation=45
        )
    
    def _visualize_institutions(self, institutions: Dict[str, int], filename: str) -> Optional[str]:
        """
        Create visualization of user institutions.
        
        Args:
            institutions: Counts by institution
            filename: Base filename for saving
            
        Returns:
            Path to the visualization file
        """
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
            return None
        
        # Extract data
        labels = [item[0].replace('_', ' ').title() for item in sorted_institutions]
        values = [item[1] for item in sorted_institutions]
        
        # Calculate percentage of total
        total = sum(values)
        
        # Create figure
        self.setup_figure(
            figsize=(12, 8),
            title='User Institutions',
            xlabel='Count'
        )
        
        # Create horizontal bar chart
        bars = plt.barh(labels, values, color='mediumpurple')
        
        # Add value labels with percentages
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = values[i]/total*100
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)} ({percentage:.1f}%)',
                    ha='left', va='center')
        
        plt.tight_layout()
        
        # Save and return using the BaseVisualizer method
        return self.save_figure(filename)
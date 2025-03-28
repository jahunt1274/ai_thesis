"""
Demographic visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.visualizers.base_visualizer import BaseVisualizer


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
        if not data:
            self.logger.warning("No demographic data to visualize")
            return {}
            
        visualizations = {}
        
        # Create visualizations using standardized error handling
        vis_functions = [
            ('user_counts', self._visualize_user_counts, data.get('user_counts', {})),
            ('affiliations', self._visualize_affiliations, data.get('affiliations', {})),
            ('user_types', self._visualize_user_types, data.get('cohorts', {}).get('user_types', {})),
            ('activity_cohorts', self._visualize_activity_cohorts, data.get('cohorts', {}).get('activity', {})),
            ('creation_timeline', self._visualize_user_creation, data.get('cohorts', {}).get('creation_dates', {})),
            ('enrollments', self._visualize_enrollments, data.get('enrollments', {})),
            ('top_courses', self._visualize_top_courses, data.get('enrollments', {}).get('top_courses', [])),
            ('interests', self._visualize_interests, data.get('interests', {}).get('interests', {})),
            ('institutions', self._visualize_institutions, data.get('institutions', {}))
        ]
        
        for name, func, func_data in vis_functions:
            if func_data:  # Only process if data exists
                vis_path = self.create_visualization(func, func_data, name)
                if vis_path:
                    visualizations[name] = vis_path
        
        self.logger.info(f"Generated {len(visualizations)} demographic visualizations")
        return visualizations
    
    def _visualize_affiliations(self, affiliations: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user affiliations."""
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
        
        # Create figure
        self.setup_figure(
            figsize=(12, 8),
            title='User Affiliations',
            xlabel='Count'
        )
        
        # Create horizontal bar chart for better readability with many categories
        bars = plt.barh(labels, values, color='lightsteelblue')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center')
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_user_types(self, user_types: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user types."""
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
        
        # Create figure
        self.setup_figure(
            figsize=(10, 8),
            title='User Types Distribution'
        )
        
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
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_activity_cohorts(self, activity_cohorts: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of activity cohorts."""
        if not activity_cohorts:
            return None
            
        # Create figure
        self.setup_figure(
            figsize=(12, 7),
            title='User Activity Cohorts',
            ylabel='Number of Users'
        )
        
        # Extract data and convert keys to readable labels
        labels = []
        values = []
        colors = []
        
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
        
        # Sort by order defined in the maps
        for key in color_map.keys():
            if key in activity_cohorts:
                labels.append(label_map.get(key, key.replace('_', ' ').title()))
                values.append(activity_cohorts[key])
                colors.append(color_map[key])
        
        # Create bar chart
        bars = plt.bar(labels, values, color=colors)
        self.add_value_labels(plt.gca(), bars, '{:.0f}')
        
        plt.xticks(rotation=20, ha='right')
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_user_creation(self, creation_dates: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user creation over time."""
        # Need at least 2 data points for a meaningful timeline
        if len(creation_dates) < 2:
            return None
        
        # Create figure
        self.setup_figure(
            figsize=(14, 7),
            title='User Registration Timeline',
            xlabel='Date',
            ylabel='New Users'
        )
        
        # Convert string dates to datetime objects for proper timeline
        dates = []
        counts = []
        
        for date_str, count in sorted(creation_dates.items()):
            date_obj = self.parse_date(date_str)
            if date_obj:
                dates.append(date_obj)
                counts.append(count)
        
        # Plot line chart with markers
        plt.plot(dates, counts, marker='o', linestyle='-', color='royalblue', 
                linewidth=2, markersize=8)
        
        # Fill area under the line
        plt.fill_between(dates, counts, alpha=0.3, color='royalblue')
        
        # Format x-axis as dates
        self.format_date_axis(plt.gca())
        
        # Add cumulative trendline
        cumulative_counts = np.cumsum(counts)
        ax2 = plt.gca().twinx()
        ax2.plot(dates, cumulative_counts, linestyle='--', color='forestgreen', 
                alpha=0.7, label='Cumulative Users')
        ax2.set_ylabel('Cumulative Users', fontsize=12, color='forestgreen')
        ax2.tick_params(axis='y', colors='forestgreen')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_enrollments(self, enrollments: Dict[str, Any], filename: str) -> Optional[str]:
        """Create visualization of enrollment statistics."""
        if not enrollments:
            return None
            
        # Create figure
        self.setup_figure(
            figsize=(10, 6),
            title='Enrollment Statistics',
            ylabel='Count'
        )
        
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
        self.add_value_labels(plt.gca(), bars, '{:.0f}')
        
        plt.tight_layout()
        
        # Add the average as text instead of a bar if it's very small compared to total
        if avg_enrollments < total_enrollments / 10:
            plt.annotate(f'Avg Enrollments Per User: {avg_enrollments:.2f}', 
                       xy=(0.5, 0.05), xycoords='figure fraction',
                       bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="orange", alpha=0.8),
                       ha='center')
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_top_courses(self, top_courses: List[tuple], filename: str) -> Optional[str]:
        """Create visualization of top courses."""
        # Check if we have course data
        if not top_courses:
            return None
        
        # Create figure
        self.setup_figure(
            figsize=(12, 8),
            title='Top Courses by Enrollment',
            xlabel='Number of Enrollments'
        )
        
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
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_interests(self, interests: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user interests."""
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
        
        # Create figure
        self.setup_figure(
            figsize=(12, 8),
            title='User Interests',
            xlabel='Count'
        )
        
        # Extract data
        labels = [item[0].replace('_', ' ').title() for item in sorted_interests]
        values = [item[1] for item in sorted_interests]
        
        # Create horizontal bar chart
        bars = plt.barh(labels, values, color='lightgreen')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center')
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_user_counts(self, user_counts: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user counts."""
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
        
        # Create figure
        self.setup_figure(
            title='User Counts',
            ylabel='Count'
        )
        
        # Create bar chart
        bars = plt.bar(labels, values, color=self.STANDARD_COLORS['primary'])
        self.add_value_labels(plt.gca(), bars, '{:.0f}')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
    
    def _visualize_institutions(self, institutions: Dict[str, int], filename: str) -> Optional[str]:
        """Create visualization of user institutions."""
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
        
        # Create figure
        self.setup_figure(
            figsize=(12, 8),
            title='User Institutions',
            xlabel='Count'
        )
        
        # Extract data
        labels = [item[0].replace('_', ' ').title() for item in sorted_institutions]
        values = [item[1] for item in sorted_institutions]
        
        # Calculate percentage of total
        total = sum(values)
        percentages = [val/total*100 for val in values]
        
        # Create horizontal bar chart
        bars = plt.barh(labels, values, color='mediumpurple')
        
        # Add value labels with percentages
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)} ({percentages[i]:.1f}%)',
                    ha='left', va='center')
        
        plt.tight_layout()
        
        # Save and return
        return self.save_figure(filename)
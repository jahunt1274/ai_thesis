"""
Engagement visualizer for the AI thesis analysis.
"""

from typing import Dict, List, Any, Optional
import os
import numpy as np
import matplotlib.pyplot as plt

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
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Extract data and sort by step count
            steps = []
            counts = []
            
            for step_count, count in sorted(step_distribution.items(), 
                                           key=lambda item: int(item[0]) if isinstance(item[0], str) and item[0].isdigit() else (
                                               int(float(item[0])) if isinstance(item[0], str) else item[0]
                                           )):
                steps.append(str(step_count))
                counts.append(count)
            
            # Create figure
            fig = self.setup_figure(
                figsize=(12, 7),
                title='Distribution of Ideas by Number of Steps Completed',
                xlabel='Number of Steps',
                ylabel='Number of Ideas'
            )
            
            # Create bar chart with a color gradient based on step count
            colors = self.get_color_gradient(len(steps), 'sequential')
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating step distribution visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_institution_cohorts(self, institution_cohorts: Dict[str, Dict[str, Any]],
                                     filename: str) -> Optional[str]:
        """
        Create visualization of institution cohort engagement.
        
        Args:
            institution_cohorts: Engagement metrics by institution
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a couple of cohorts
            if len(institution_cohorts) < 2:
                logger.warning("Not enough institution cohorts for visualization")
                return None
            
            # Create a figure for comparative metrics
            fig = self.setup_figure(figsize=(14, 10))
            
            # Limit to top 5 institutions by size
            sorted_institutions = sorted(institution_cohorts.items(), 
                                        key=lambda x: x[1].get('cohort_size', 0), 
                                        reverse=True)
            top_institutions = sorted_institutions[:5]
            
            # Extract data
            institution_names = []
            active_rates = []
            ideas_per_user = []
            steps_per_idea = []
            
            for institution, data in top_institutions:
                # Truncate long institution names
                inst_name = institution[:15] + '...' if len(institution) > 15 else institution
                institution_names.append(inst_name)
                active_rates.append(data.get('active_rate', 0) * 100)
                ideas_per_user.append(data.get('ideas_per_active_user', 0))
                steps_per_idea.append(data.get('steps_per_idea', 0))
            
            # Create grouped bar chart
            x = np.arange(len(institution_names))
            width = 0.25
            
            fig, ax = self.setup_subplots(1, 1, figsize=(12, 8))
            
            # Plot three metrics side by side
            rects1 = ax.bar(x - width, active_rates, width, label='Active Rate (%)', color='lightblue')
            rects2 = ax.bar(x, ideas_per_user, width, label='Ideas/User', color='lightgreen')
            rects3 = ax.bar(x + width, steps_per_idea, width, label='Steps/Idea', color='coral')
            
            # Add labels and title
            ax.set_xlabel('Institution', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.set_title('Engagement Metrics by Institution', fontsize=16)
            ax.set_xticks(x)
            ax.set_xticklabels(institution_names)
            ax.legend()
            
            # Add value labels
            def add_labels(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.1f}',
                               xy=(rect.get_x() + rect.get_width() / 2, height),
                               xytext=(0, 3),  # 3 points vertical offset
                               textcoords="offset points",
                               ha='center', va='bottom')
            
            add_labels(rects1)
            add_labels(rects2)
            add_labels(rects3)
            
            # Add explanation of metrics
            plt.figtext(0.5, 0.01,
                       "Active Rate: Percentage of users who created ideas\n" + 
                       "Ideas/User: Average number of ideas per active user\n" +
                       "Steps/Idea: Average number of steps completed per idea",
                       ha="center", fontsize=10, bbox={"facecolor":"lightyellow", "alpha":0.8, "pad":5})
            
            plt.tight_layout(rect=[0, 0.08, 1, 0.98])
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating institution cohorts visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_enrollment_cohorts(self, enrollment_cohorts: Dict[str, Dict[str, Any]],
                                    filename: str) -> Optional[str]:
        """
        Create visualization of enrollment cohort engagement.
        
        Args:
            enrollment_cohorts: Engagement metrics by enrollment
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a couple of cohorts
            if len(enrollment_cohorts) < 2:
                logger.warning("Not enough enrollment cohorts for visualization")
                return None
            
            # Focus on metrics that differentiate the cohorts
            # Create a scatter plot of active rate vs. ideas per user,
            # with marker size representing cohort size
            
            fig = self.setup_figure(
                figsize=(12, 10),
                title='Enrollment Cohort Engagement Comparison',
                xlabel='Active Rate (%)',
                ylabel='Ideas per Active User'
            )
            
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
            
            # Create scatter plot
            scatter = plt.scatter(active_rates, ideas_per_user, s=[size*10 for size in cohort_sizes], 
                               alpha=0.6, c=cohort_sizes, cmap='viridis')
            
            # Add labels for each point
            for i, enrollment in enumerate(enrollments):
                plt.annotate(enrollment, 
                           (active_rates[i], ideas_per_user[i]),
                           xytext=(5, 5), textcoords='offset points')
            
            # Add colorbar for cohort size
            cbar = plt.colorbar(scatter)
            cbar.set_label('Cohort Size', fontsize=12)
            
            # Add reference lines
            plt.axhline(y=sum(ideas_per_user)/len(ideas_per_user), color='r', linestyle='--', 
                       alpha=0.5, label='Avg Ideas/User')
            plt.axvline(x=sum(active_rates)/len(active_rates), color='g', linestyle='--', 
                       alpha=0.5, label='Avg Active Rate')
            
            # Add grid and legend
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating enrollment cohorts visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_framework_completion(self, completion_by_framework: Dict[str, Dict[str, Any]], 
                                       filename: str) -> Optional[str]:
        """
        Create visualization of framework completion comparison.
        
        Args:
            completion_by_framework: Completion statistics by framework
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Extract data
            frameworks = []
            avg_completion = []
            total_ideas = []
            
            for framework, data in completion_by_framework.items():
                frameworks.append(framework)
                avg_completion.append(data.get('avg_completion', 0))
                total_ideas.append(data.get('total_ideas', 0))
            
            # Create grouped bar chart
            fig, ax1 = self.setup_subplots(1, 1, figsize=(12, 8))
            
            # Plot average completion
            x = np.arange(len(frameworks))
            width = 0.35
            
            bars1 = ax1.bar(x - width/2, avg_completion, width, label='Avg Completion', color='teal')
            ax1.set_ylabel('Average Completion', fontsize=12)
            ax1.set_ylim(0, max(max(avg_completion) * 1.2, 1))
            
            # Create a twin axis for total ideas
            ax2 = ax1.twinx()
            bars2 = ax2.bar(x + width/2, total_ideas, width, label='Total Ideas', color='darkorange')
            ax2.set_ylabel('Total Ideas', fontsize=12)
            ax2.set_ylim(0, max(total_ideas) * 1.2)
            
            # Set x-axis ticks and labels
            ax1.set_xticks(x)
            ax1.set_xticklabels(frameworks)
            
            # Add value labels
            self.add_value_labels(ax1, bars1, '{:.2f}')
            self.add_value_labels(ax2, bars2, '{:.0f}')
            
            # Add title
            plt.title('Framework Completion Comparison', fontsize=16)
            
            # Add a legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.tight_layout()
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating framework completion visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_step_progression(self, dropout_data: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Create visualization of step progression and dropout points.
        
        Args:
            dropout_data: Step progression and dropout data
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Extract required data
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
            fig, (ax1, ax2, ax3) = self.setup_subplots(3, 1, figsize=(14, 15))
            
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating step progression visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_monthly_activity(self, monthly_activity: Dict[str, Dict[str, Any]], 
                                   filename: str) -> Optional[str]:
        """
        Create visualization of monthly activity.
        
        Args:
            monthly_activity: Monthly activity statistics
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a few months of data
            if len(monthly_activity) < 2:
                logger.warning("Not enough monthly activity data for visualization")
                return None
            
            # Create figure with 3 panels
            fig, (ax1, ax2, ax3) = self.setup_subplots(3, 1, figsize=(14, 15))
            
            # Convert string dates to datetime objects for proper timeline
            months = []
            steps = []
            ideas = []
            users = []
            
            for month_str, data in sorted(monthly_activity.items()):
                try:
                    # Parse date (YYYY-MM format)
                    month_obj = self.parse_date(f"{month_str}-01")
                    if month_obj:
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating monthly activity visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_seasonal_patterns(self, seasonal_patterns: Dict[str, Any], 
                                    filename: str) -> Optional[str]:
        """
        Create visualization of seasonal patterns.
        
        Args:
            seasonal_patterns: Seasonal pattern data
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Check if we have monthly averages
            if 'monthly_averages' not in seasonal_patterns or not seasonal_patterns['monthly_averages']:
                logger.warning("No monthly average data for seasonal patterns visualization")
                return None
            
            # Create figure with 2 panels
            fig, (ax1, ax2) = self.setup_subplots(2, 1, figsize=(14, 12))
            
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
            
            # Plot 1: Monthly Averages (Bar Chart)
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
            colors = []
            
            patterns = [
                ('semester_start', 'Semester Start Peaks', 'green'),
                ('semester_end', 'Semester End Peaks', 'orange'),
                ('summer_slump', 'Summer Activity Drop', 'lightblue')
            ]
            
            for key, label, color in patterns:
                if academic_patterns.get(key, False):
                    labels.append(label)
                    values.append(1)
                    colors.append(color)
                else:
                    labels.append(f"No {label}")
                    values.append(1)
                    colors.append('lightgray')
            
            # Create pie chart
            if labels and values:
                ax2.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating seasonal patterns visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_step_intervals(self, step_intervals: Dict[str, Any], 
                                 filename: str) -> Optional[str]:
        """
        Create visualization of time intervals between steps.
        
        Args:
            step_intervals: Step interval data
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
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
            fig, (ax1, ax2) = self.setup_subplots(2, 1, figsize=(12, 10))
            
            # Plot 1: Histogram of intervals
            # Bin the data - use reasonable bin sizes based on data range
            max_days = max(all_intervals) if all_intervals else 30
            if max_days <= 30:
                bins = np.arange(0, max_days + 3, 1)  # Daily bins up to 30 days
                ax1.set_xlabel('Days Between Steps', fontsize=12)
            elif max_days <= 90:
                bins = np.arange(0, max_days + 7, 7)  # Weekly bins up to 90 days
                ax1.set_xlabel('Weeks Between Steps', fontsize=12)
            else:
                bins = np.arange(0, max_days + 30, 30)  # Monthly bins for longer periods
                ax1.set_xlabel('Months Between Steps (approx)', fontsize=12)
            
            # Create histogram
            ax1.hist(all_intervals, bins=bins, color='mediumseagreen', alpha=0.7, edgecolor='black')
            
            # Add vertical line for average
            ax1.axvline(x=avg_interval, color='red', linestyle='--', linewidth=2,
                      label=f'Average: {avg_interval:.1f} days')
            
            # Add title and labels
            ax1.set_title('Distribution of Time Between Steps', fontsize=14)
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating step intervals visualization: {str(e)}")
            plt.close()
            return None
    
    def _visualize_user_type_cohorts(self, user_type_cohorts: Dict[str, Dict[str, Any]],
                                   filename: str) -> Optional[str]:
        """
        Create visualization of user type cohort engagement.
        
        Args:
            user_type_cohorts: Engagement metrics by user type
            filename: Base filename for the output
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a couple of cohorts
            if len(user_type_cohorts) < 2:
                logger.warning("Not enough user type cohorts for visualization")
                return None
            
            # Create figure with multiple subplots
            fig, axes = self.setup_subplots(2, 2, figsize=(14, 12))
            
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
            
            # Save figure
            return self.save_figure(filename)
        
        except Exception as e:
            logger.error(f"Error creating user type cohorts visualization: {str(e)}")
            plt.close()
            return None
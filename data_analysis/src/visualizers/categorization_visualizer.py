"""
Categorization visualizer for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from typing import Dict, List, Any, Optional
from collections import defaultdict

from src.constants.data_constants import IDEA_DOMAIN_CATEGORIES
from src.visualizers.base_visualizer import BaseVisualizer
from src.utils import get_logger

logger = get_logger("categorization_visualizer")


class CategorizationVisualizer(BaseVisualizer):
    """Visualizes idea categorization results."""
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the categorization visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        super().__init__(output_dir)
        self.format = format
        
        # Create output subdirectory
        self.vis_dir = os.path.join(output_dir, "categorization")
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations for categorization analysis.
        
        Args:
            data: Categorization analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        logger.info("Generating categorization visualizations")
        
        visualizations = {}
        
        # Check if necessary data exists
        if not data:
            logger.warning("No categorization data to visualize")
            return visualizations
        
        # Create various categorization visualizations
        try:
            # Category distribution
            if 'category_counts' in data:
                vis_path = self._visualize_category_distribution(data['category_counts'])
                if vis_path:
                    visualizations['category_distribution'] = vis_path
            
            # Top categories
            if 'top_categories' in data:
                vis_path = self._visualize_top_categories(data['top_categories'])
                if vis_path:
                    visualizations['top_categories'] = vis_path
            
            # Category percentages
            if 'category_percentages' in data:
                vis_path = self._visualize_category_percentages(data['category_percentages'])
                if vis_path:
                    visualizations['category_percentages'] = vis_path
            
            # Create category clusters visualization if we have enough data
            if 'category_counts' in data and len(data['category_counts']) >= 5:
                vis_path = self._visualize_category_clusters(data['category_counts'])
                if vis_path:
                    visualizations['category_clusters'] = vis_path
            
            logger.info(f"Generated {len(visualizations)} categorization visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating categorization visualizations: {str(e)}")
            return visualizations
    
    def _visualize_category_distribution(self, category_counts: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of idea category distribution.
        
        Args:
            category_counts: Counts by category
            
        Returns:
            Path to the visualization file
        """
        try:
            # Sort categories by count (descending)
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            
            # For readability, limit to top 20 categories if there are many
            if len(sorted_categories) > 20:
                sorted_categories = sorted_categories[:20]
                truncated = True
            else:
                truncated = False
            
            # Extract data
            categories = [c[0] for c in sorted_categories]
            counts = [c[1] for c in sorted_categories]
            
            # Create horizontal bar chart for better readability with many categories
            plt.figure(figsize=(12, max(8, len(categories) * 0.4)))
            
            # Create gradient colors based on counts
            cmap = plt.cm.viridis
            colors = cmap(np.linspace(0.1, 0.9, len(counts)))
            
            # Create horizontal bar chart
            bars = plt.barh(categories, counts, color=colors)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                        f'{int(width)}',
                        ha='left', va='center')
            
            # Add title and labels
            title = 'Idea Category Distribution'
            if truncated:
                title += ' (Top 20 Categories)'
            plt.title(title, fontsize=16)
            plt.xlabel('Number of Ideas', fontsize=12)
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"category_distribution.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating category distribution visualization: {str(e)}")
            return None
    
    def _visualize_top_categories(self, top_categories: List[tuple]) -> Optional[str]:
        """
        Create visualization of top idea categories.
        
        Args:
            top_categories: List of (category, count) tuples
            
        Returns:
            Path to the visualization file
        """
        try:
            # Need at least a few categories
            if not top_categories or len(top_categories) < 3:
                logger.warning("Not enough categories for top categories visualization")
                return None
            
            # Extract data
            categories = [c[0] for c in top_categories]
            counts = [c[1] for c in top_categories]
            
            # Create pie chart for top categories
            plt.figure(figsize=(12, 10))
            
            # Define explode to emphasize top categories
            explode = [0.1 if i < 3 else 0 for i in range(len(categories))]
            
            # Custom color map
            colors = plt.cm.tab20(np.linspace(0, 1, len(categories)))
            
            # Create pie chart
            plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90,
                   explode=explode, colors=colors, shadow=True)
            
            # Equal aspect ratio ensures the pie chart is circular
            plt.axis('equal')
            
            # Add title
            plt.title('Top Idea Categories', fontsize=16)
            
            # Add legend with counts
            legend_labels = [f"{cat} ({count})" for cat, count in zip(categories, counts)]
            plt.legend(legend_labels, loc="best", bbox_to_anchor=(1, 0.5))
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"top_categories_pie.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating top categories visualization: {str(e)}")
            return None
    
    def _visualize_category_percentages(self, category_percentages: Dict[str, float]) -> Optional[str]:
        """
        Create visualization of category percentages.
        
        Args:
            category_percentages: Percentage by category
            
        Returns:
            Path to the visualization file
        """
        try:
            # Sort categories by percentage (descending)
            sorted_categories = sorted(category_percentages.items(), key=lambda x: x[1], reverse=True)
            
            # Group small categories into "Other" for readability
            threshold = 2.0  # Categories with less than 2% are grouped as "Other"
            significant_categories = []
            other_percentage = 0.0
            
            for category, percentage in sorted_categories:
                if percentage >= threshold:
                    significant_categories.append((category, percentage))
                else:
                    other_percentage += percentage
            
            if other_percentage > 0:
                significant_categories.append(("Other", other_percentage))
            
            # Extract data
            categories = [c[0] for c in significant_categories]
            percentages = [c[1] for c in significant_categories]
            
            # Create stacked horizontal bar chart for percentage breakdown
            plt.figure(figsize=(12, 6))
            
            # Custom color map
            colors = plt.cm.tab20(np.linspace(0, 1, len(categories)))
            
            # Create stacked bar
            left = 0
            for i, (cat, pct) in enumerate(zip(categories, percentages)):
                plt.barh([0], [pct], left=left, color=colors[i], label=f"{cat} ({pct:.1f}%)")
                
                # Add percentage label in the middle of each segment
                if pct >= 5:  # Only add label if segment is wide enough
                    plt.text(left + pct/2, 0, f"{pct:.1f}%", 
                           ha='center', va='center', fontsize=10, color='white',
                           fontweight='bold')
                
                left += pct
            
            # Add title and labels
            plt.title('Category Percentage Breakdown', fontsize=16)
            plt.xlabel('Percentage (%)', fontsize=12)
            plt.yticks([])  # Hide y-axis ticks
            
            # Add percentage markers on x-axis
            plt.xticks(np.arange(0, 101, 10))
            plt.xlim(0, 100)
            
            # Add legend
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.vis_dir, f"category_percentages.{self.format}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating category percentages visualization: {str(e)}")
            return None
    
    def _visualize_category_clusters(self, category_counts: Dict[str, int]) -> Optional[str]:
        """
        Create visualization of category clusters.
        
        Args:
            category_counts: Counts by category
            
        Returns:
            Path to the visualization file
        """
        try:
            # Map categories to domains and count
            domain_counts = defaultdict(int)
            unmapped_categories = []
            
            for category, count in category_counts.items():
                mapped = False
                for domain, domain_categories in IDEA_DOMAIN_CATEGORIES.items():
                    if category in domain_categories:
                        domain_counts[domain] += count
                        mapped = True
                        break
                
                if not mapped:
                    unmapped_categories.append(category)
                    domain_counts["Miscellaneous"] += count
            
            # Create a treemap visualization
            plt.figure(figsize=(14, 10))
            
            try:
                # Sort domains by count
                sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
                domains = [d[0] for d in sorted_domains]
                counts = [d[1] for d in sorted_domains]
                
                # Calculate percentages for labels
                total = sum(counts)
                percentages = [count/total*100 for count in counts]
                
                # Create labels with percentages
                labels = [f"{domain}\n({percentage:.1f}%)" for domain, percentage in zip(domains, percentages)]
                
                # Create color map
                cmap = plt.cm.viridis
                colors = cmap(np.linspace(0.1, 0.9, len(domains)))
                
                # Create treemap
                squarify.plot(sizes=counts, label=labels, alpha=0.8, color=colors)
                plt.axis('off')
                
                # Add title
                plt.title('Idea Categories by Domain Cluster', fontsize=16)
                
                plt.tight_layout()
                
                # Save figure
                output_path = os.path.join(self.vis_dir, f"category_clusters.{self.format}")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_path
                
            except ImportError:
                # Fallback to pie chart if squarify is not available
                logger.warning("squarify package not available, falling back to pie chart")
                
                # Sort domains by count
                sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
                domains = [d[0] for d in sorted_domains]
                counts = [d[1] for d in sorted_domains]
                
                # Create color map
                cmap = plt.cm.viridis
                colors = cmap(np.linspace(0.1, 0.9, len(domains)))
                
                # Create pie chart
                plt.pie(counts, labels=domains, autopct='%1.1f%%', startangle=90,
                       colors=colors, shadow=True)
                
                # Equal aspect ratio ensures the pie chart is circular
                plt.axis('equal')
                
                # Add title
                plt.title('Idea Categories by Domain Cluster', fontsize=16)
                
                plt.tight_layout()
                
                # Save figure
                output_path = os.path.join(self.vis_dir, f"category_clusters.{self.format}")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_path
        
        except Exception as e:
            logger.error(f"Error creating category clusters visualization: {str(e)}")
            return None
"""
Visualization manager for the AI thesis analysis.
"""

import os
from typing import Dict, List, Any, Optional

from src.utils import get_logger
from src.visualizers.demographic_visualizer import DemographicVisualizer
from src.visualizers.usage_visualizer import UsageVisualizer
from src.visualizers.engagement_visualizer import EngagementVisualizer
from src.visualizers.categorization_visualizer import CategorizationVisualizer

logger = get_logger("visualization_manager")


class VisualizationManager:
    """Manages and coordinates visualizations for all analysis components."""
    
    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the visualization manager.
        
        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        self.output_dir = output_dir
        self.format = format
        self.visualization_outputs = {}
        
        # Create visualizers
        vis_output_dir = os.path.join(output_dir, "visualizations")
        os.makedirs(vis_output_dir, exist_ok=True)
        
        self.visualizers = {
            "demographics": DemographicVisualizer(vis_output_dir, format),
            "usage": UsageVisualizer(vis_output_dir, format),
            "engagement": EngagementVisualizer(vis_output_dir, format),
            "categorization": CategorizationVisualizer(vis_output_dir, format)
        }
        
        logger.info(f"Initialized VisualizationManager with output directory: {vis_output_dir}")
    
    def visualize_all(self, analysis_results: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Create visualizations for all analysis components.
        
        Args:
            analysis_results: Combined analysis results
            
        Returns:
            Dictionary mapping component names to visualization outputs
        """
        logger.info("Creating visualizations for all analysis components")
        
        # Process each component that exists in the results
        for component, visualizer in self.visualizers.items():
            if component in analysis_results:
                logger.info(f"Creating visualizations for {component}")
                try:
                    component_visuals = visualizer.visualize(analysis_results[component])
                    self.visualization_outputs[component] = component_visuals
                    
                    logger.info(f"Created {len(component_visuals)} visualizations for {component}")
                except Exception as e:
                    logger.error(f"Error creating visualizations for {component}: {str(e)}")
        
        # Generate an overview HTML report
        self._generate_html_report()
        
        return self.visualization_outputs
    
    def visualize_component(self, component: str, data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Create visualizations for a specific analysis component.
        
        Args:
            component: Component name (demographics, usage, engagement, categorization)
            data: Component's analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths, or None if component not found
        """
        if component not in self.visualizers:
            logger.warning(f"No visualizer found for component: {component}")
            return None
        
        logger.info(f"Creating visualizations for {component}")
        try:
            component_visuals = self.visualizers[component].visualize(data)
            self.visualization_outputs[component] = component_visuals
            
            logger.info(f"Created {len(component_visuals)} visualizations for {component}")
            return component_visuals
        except Exception as e:
            logger.error(f"Error creating visualizations for {component}: {str(e)}")
            return None
    
    def _generate_html_report(self) -> str:
        """
        Generate an HTML report with all visualizations.
        
        Returns:
            Path to the generated HTML report
        """
        logger.info("Generating HTML visualization report")
        
        # Create HTML report directory
        report_dir = os.path.join(self.output_dir, "visualization_report")
        os.makedirs(report_dir, exist_ok=True)
        
        # Create the report
        report_path = os.path.join(report_dir, "visualization_report.html")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                # Write HTML header
                f.write("""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>AI Thesis Analysis Visualization Report</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 20px;
                                color: #333;
                            }
                            header {
                                background-color: #f8f8f8;
                                padding: 20px;
                                border-bottom: 1px solid #ddd;
                                margin-bottom: 20px;
                            }
                            h1 {
                                margin: 0;
                                color: #2c3e50;
                            }
                            h2 {
                                color: #3498db;
                                border-bottom: 1px solid #eee;
                                padding-bottom: 10px;
                                margin-top: 30px;
                            }
                            h3 {
                                color: #2980b9;
                            }
                            .vis-container {
                                margin-bottom: 40px;
                            }
                            .vis-item {
                                margin-bottom: 30px;
                                border: 1px solid #eee;
                                padding: 15px;
                                border-radius: 5px;
                            }
                            .vis-item h4 {
                                margin-top: 0;
                                color: #555;
                            }
                            .vis-item img {
                                max-width: 100%;
                                height: auto;
                                border: 1px solid #ddd;
                            }
                            .timestamp {
                                color: #777;
                                font-size: 0.9em;
                                margin-top: 5px;
                            }
                            nav {
                                background-color: #f0f0f0;
                                padding: 10px;
                                margin-bottom: 20px;
                                border-radius: 5px;
                            }
                            nav a {
                                margin-right: 15px;
                                color: #3498db;
                                text-decoration: none;
                            }
                            nav a:hover {
                                text-decoration: underline;
                            }
                        </style>
                    </head>
                    <body>
                        <header>
                            <h1>AI Thesis Analysis Visualization Report</h1>
                            <p class="timestamp">Generated on: <span id="timestamp"></span></p>
                            <script>
                                document.getElementById('timestamp').textContent = new Date().toLocaleString();
                            </script>
                        </header>
                        
                        <nav>
                            <a href="#demographics">Demographics</a>
                            <a href="#usage">Usage</a>
                            <a href="#engagement">Engagement</a>
                            <a href="#categorization">Categorization</a>
                        </nav>
                    """)
                
                # Write sections for each component
                for component, visuals in self.visualization_outputs.items():
                    if not visuals:
                        continue
                        
                    f.write(f'\n    <section id="{component}" class="vis-container">\n')
                    f.write(f'        <h2>{component.capitalize()} Analysis</h2>\n')
                    
                    # Group by subcategories if they exist
                    subcategories = {}
                    for name, path in visuals.items():
                        # Extract subcategory from name (format: subcategory_name)
                        parts = name.split('_', 1)
                        if len(parts) > 1:
                            subcategory, vis_name = parts
                        else:
                            subcategory = "general"
                            vis_name = name
                        
                        if subcategory not in subcategories:
                            subcategories[subcategory] = []
                        
                        subcategories[subcategory].append({
                            'name': vis_name,
                            'path': path,
                            'full_name': name
                        })
                    
                    # Write visualizations by subcategory
                    for subcategory, vis_items in subcategories.items():
                        if subcategory != "general":
                            f.write(f'        <h3>{subcategory.capitalize()}</h3>\n')
                        
                        for vis in vis_items:
                            # Get relative path for the HTML report
                            rel_path = os.path.relpath(vis['path'], report_dir)
                            
                            f.write('        <div class="vis-item">\n')
                            f.write(f'            <h4>{vis["name"].replace("_", " ").capitalize()}</h4>\n')
                            f.write(f'            <img src="{rel_path}" alt="{vis["full_name"]}">\n')
                            f.write('        </div>\n')
                    
                    f.write('    </section>\n')
                
                # Write HTML footer
                f.write("""
                    <script>
                        // Add any interactive elements here if needed
                    </script>
                </body>
                </html>
                """)
            
            logger.info(f"Generated HTML report at: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return ""
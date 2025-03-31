"""
Visualization manager for the AI thesis analysis.
"""

import os
from typing import Dict, List, Any, Optional
import shutil
from datetime import datetime

from src.utils import get_logger, FileHandler
from src.visualizers import (
    DemographicVisualizer, 
    UsageVisualizer, 
    EngagementVisualizer, 
    CategorizationVisualizer, 
    CohortVisualizer,
    CourseEvaluationVisualizer
)

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
        self.file_handler = FileHandler()
        
        # Create visualizations output directory
        vis_output_dir = os.path.join(output_dir, "visualizations")
        self.file_handler._ensure_directory_exists(vis_output_dir)
        self.vis_output_dir = vis_output_dir
        
        # Create visualizers
        self.visualizers = {
            "demographics": DemographicVisualizer(vis_output_dir, format),
            "usage": UsageVisualizer(vis_output_dir, format),
            "engagement": EngagementVisualizer(vis_output_dir, format),
            "categorization": CategorizationVisualizer(vis_output_dir, format),
            "cohorts": CohortVisualizer(vis_output_dir, format),
            "course_evaluations": CourseEvaluationVisualizer(vis_output_dir, format)
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

                    # Create an index file and report for this component
                    if component_visuals:
                        visualizer.save_visualization_index(component_visuals)
                        visualizer.save_visualization_report(component_visuals)

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
            
            # Create an index file and report for this component
            if component_visuals:
                self.visualizers[component].save_visualization_index(component_visuals)
                self.visualizers[component].save_visualization_report(component_visuals)
            
            logger.info(f"Created {len(component_visuals)} visualizations for {component}")
            
            # Generate an updated HTML report
            self._generate_html_report()
            
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
        report_dir = os.path.join(self.vis_output_dir, "visualization_report")
        self.file_handler.ensure_directory_exists(report_dir)
        
        # Create the report
        report_path = os.path.join(report_dir, "visualization_report.html")
        
        try:
            # Prepare HTML content
            html_content = self._create_report_html()
            
            # Save the report using FileHandler
            success = self.file_handler.save_text(html_content, report_path)
            
            if success:
                logger.info(f"Generated HTML report at: {report_path}")
                return report_path
            else:
                logger.error("Failed to save HTML report")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return ""
    
    def _create_report_html(self) -> str:
        """
        Create HTML content for the report.
        
        Returns:
            HTML content as string
        """
        # HTML header
        html = """<!DOCTYPE html>
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
        """
        
        # Add navigation links
        for component in self.visualization_outputs:
            if self.visualization_outputs[component]:
                component_name = component.capitalize()
                html += f'<a href="#{component}">{component_name}</a>\n'
        
        html += """
            </nav>
        """
        
        # Add sections for each component
        for component, visuals in self.visualization_outputs.items():
            if not visuals:
                continue
                
            html += f'\n    <section id="{component}" class="vis-container">\n'
            html += f'        <h2>{component.capitalize()} Analysis</h2>\n'
            
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
                    html += f'        <h3>{subcategory.capitalize()}</h3>\n'
                
                for vis in vis_items:
                    # Get relative path for the HTML report
                    rel_path = os.path.relpath(vis['path'], report_dir)
                    
                    html += '        <div class="vis-item">\n'
                    html += f'            <h4>{vis["name"].replace("_", " ").capitalize()}</h4>\n'
                    html += f'            <img src="{rel_path}" alt="{vis["full_name"]}">\n'
                    html += '        </div>\n'
            
            html += '    </section>\n'
        
        # HTML footer
        html += """
            <script>
                // Add any interactive elements here if needed
            </script>
        </body>
        </html>
        """
        
        return html
    
    def copy_visualizations_to_directory(self, target_dir: str) -> bool:
        """
        Copy all visualizations to a target directory.
        
        Args:
            target_dir: Target directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure target directory exists
            self.file_handler._ensure_directory_exists(target_dir)
            
            # Copy each visualization
            copy_count = 0
            for component, visuals in self.visualization_outputs.items():
                # Create component subdirectory
                component_dir = os.path.join(target_dir, component)
                self.file_handler._ensure_directory_exists(component_dir)
                
                # Copy each visualization file
                for name, path in visuals.items():
                    if os.path.exists(path):
                        target_path = os.path.join(component_dir, os.path.basename(path))
                        shutil.copy2(path, target_path)
                        copy_count += 1
            
            # Copy HTML report if exists
            report_path = os.path.join(self.vis_output_dir, "visualization_report", "visualization_report.html")
            if os.path.exists(report_path):
                target_report_dir = os.path.join(target_dir, "report")
                self.file_handler._ensure_directory_exists(target_report_dir)
                shutil.copy2(report_path, os.path.join(target_report_dir, "visualization_report.html"))
            
            logger.info(f"Copied {copy_count} visualization files to {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying visualizations: {str(e)}")
            return False
    
    def clear_visualizations(self, component: Optional[str] = None) -> bool:
        """
        Clear visualization files.
        
        Args:
            component: Specific component to clear (None for all)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if component:
                # Clear specific component
                if component in self.visualizers:
                    vis_dir = self.visualizers[component].vis_dir
                    if os.path.exists(vis_dir):
                        # Only delete visualization files, not the directory itself
                        for file in os.listdir(vis_dir):
                            file_path = os.path.join(vis_dir, file)
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        
                        # Update outputs
                        if component in self.visualization_outputs:
                            del self.visualization_outputs[component]
                        
                        logger.info(f"Cleared visualization files for component: {component}")
                    else:
                        logger.warning(f"Visualization directory not found for component: {component}")
                else:
                    logger.warning(f"Component not found: {component}")
            else:
                # Clear all components
                for component, visualizer in self.visualizers.items():
                    vis_dir = visualizer.vis_dir
                    if os.path.exists(vis_dir):
                        # Only delete visualization files, not the directory itself
                        for file in os.listdir(vis_dir):
                            file_path = os.path.join(vis_dir, file)
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                
                # Reset outputs
                self.visualization_outputs = {}
                
                logger.info("Cleared all visualization files")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing visualizations: {str(e)}")
            return False
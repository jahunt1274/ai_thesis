"""
Visualization manager for the AI thesis analysis.
"""

import os
from typing import Dict, List, Any, Optional

from src.utils import get_logger, FileHandler
from src.visualizers import (
    BaseVisualizer,
    UserVisualizer,
    ActivityVisualizer,
    IdeaVisualizer,
    CourseEvaluationVisualizer,
    TeamVisualizer,
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

        # Map component names to visualizer classes
        self.visualizer_classes = {
            "user_analysis": UserVisualizer,
            "activity_analysis": ActivityVisualizer,
            "idea_analysis": IdeaVisualizer,
            "course_evaluations": CourseEvaluationVisualizer,
            "team_analysis": TeamVisualizer
        }

        # Create visualizer instances
        self.visualizers = self._create_visualizers()

        logger.info(
            f"Initialized VisualizationManager with output directory: {self.output_dir}"
        )

    def _create_visualizers(self) -> Dict[str, BaseVisualizer]:
        """
        Create instances of all visualizer classes.

        Returns:
            Dictionary mapping component names to visualizer instances
        """
        visualizers = {}
        for component, visualizer_class in self.visualizer_classes.items():
            try:
                visualizers[component] = visualizer_class(self.output_dir, self.format)
                logger.debug(
                    f"Created {visualizer_class.__name__} for component '{component}'"
                )
            except Exception as e:
                logger.error(f"Error creating visualizer for '{component}': {str(e)}")

        return visualizers

    def visualize_all(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Dict[str, str]]:
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
                self._visualize_component_safe(
                    component, visualizer, analysis_results[component]
                )

        # Generate an overview HTML report
        self._generate_html_report()

        return self.visualization_outputs

    def visualize_component(
        self, component: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Create visualizations for a specific analysis component.

        Args:
            component: Component name (user_analysis, activity_analysis, etc.)
            data: Component's analysis results

        Returns:
            Dictionary mapping visualization names to file paths, or None if component not found
        """
        if component not in self.visualizers:
            logger.warning(f"No visualizer found for component: {component}")
            return None

        visualizer = self.visualizers[component]
        component_visuals = self._visualize_component_safe(component, visualizer, data)

        # Generate an updated HTML report
        self._generate_html_report()

        return component_visuals

    def _visualize_component_safe(
        self, component: str, visualizer: BaseVisualizer, data: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Create visualizations for a component with error handling.

        Args:
            component: Component name
            visualizer: Visualizer instance
            data: Component's analysis results

        Returns:
            Dictionary mapping visualization names to file paths, or None if an error occurred
        """
        logger.info(f"Creating visualizations for {component}")

        try:
            # Create visualizations
            component_visuals = visualizer.visualize(data)

            # Store results
            self.visualization_outputs[component] = component_visuals

            # Create an index file and report for this component
            if component_visuals:
                visualizer.save_visualization_index(component_visuals)
                visualizer.save_visualization_report(component_visuals)

                logger.info(
                    f"Created {len(component_visuals)} visualizations for {component}"
                )
            else:
                logger.warning(f"No visualizations created for {component}")

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
        self.file_handler.ensure_directory_exists(report_dir)

        # Create the report
        report_path = os.path.join(report_dir, "visualization_report.html")

        try:
            # Prepare HTML content
            html_content = self._create_report_html(report_dir)

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

    def _create_report_html(self, report_dir: str) -> str:
        """
        Create HTML content for the report.

        Args:
            report_dir: Directory where the report will be saved

        Returns:
            HTML content as string
        """
        # HTML header with improved styling
        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Analysis Visualization Report</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    line-height: 1.6;
                }
                header {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                h1 {
                    margin: 0;
                    color: #2c3e50;
                    font-weight: 600;
                }
                h2 {
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 30px;
                    font-weight: 500;
                }
                h3 {
                    color: #2980b9;
                    font-weight: 500;
                }
                .vis-container {
                    margin-bottom: 40px;
                }
                .vis-item {
                    margin-bottom: 30px;
                    border: 1px solid #eee;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    transition: transform 0.2s ease-in-out;
                }
                .vis-item:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .vis-item h4 {
                    margin-top: 0;
                    color: #444;
                    font-weight: 500;
                }
                .vis-item img {
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .timestamp {
                    color: #888;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                nav {
                    background-color: #f0f4f8;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    position: sticky;
                    top: 20px;
                    z-index: 100;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                nav a {
                    margin-right: 15px;
                    color: #3498db;
                    text-decoration: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                nav a:hover {
                    background-color: #e1f0fa;
                    text-decoration: none;
                }
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
                    gap: 20px;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Data Analysis Visualization Report</h1>
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
                # Convert component name for display
                if component == "user_analysis":
                    display_name = "User Analysis"
                elif component == "activity_analysis":
                    display_name = "Activity Analysis"
                elif component == "idea_analysis":
                    display_name = "Idea Analysis"
                elif component == "course_evaluations":
                    display_name = "Course Evaluations"
                else:
                    display_name = component.replace("_", " ").title()

                html += f'<a href="#{component}">{display_name}</a>\n'

        html += """
            </nav>
        """

        # Add sections for each component
        for component, visuals in self.visualization_outputs.items():
            if not visuals:
                continue

            # Convert component name for display
            if component == "user_analysis":
                display_name = "User Analysis"
            elif component == "activity_analysis":
                display_name = "Activity Analysis"
            elif component == "idea_analysis":
                display_name = "Idea Analysis"
            elif component == "course_evaluations":
                display_name = "Course Evaluations"
            else:
                display_name = component.replace("_", " ").title()

            html += f'\n    <section id="{component}" class="vis-container">\n'
            html += f"        <h2>{display_name}</h2>\n"

            # Group by subcategories if they exist
            subcategories = self._group_visualizations_by_subcategory(visuals)

            # Write visualizations by subcategory
            for subcategory, vis_items in subcategories.items():
                if subcategory != "general":
                    html += f"        <h3>{subcategory.capitalize()}</h3>\n"

                # Use grid layout for multiple visualizations
                html += '        <div class="grid-container">\n'

                for vis in vis_items:
                    # Get relative path for the HTML report
                    rel_path = os.path.relpath(vis["path"], report_dir)

                    html += '        <div class="vis-item">\n'
                    html += f'            <h4>{vis["name"].replace("_", " ").capitalize()}</h4>\n'
                    html += (
                        f'            <img src="{rel_path}" alt="{vis["full_name"]}">\n'
                    )
                    html += "        </div>\n"

                html += "        </div>\n"

            html += "    </section>\n"

        # HTML footer with interactive features
        html += """
            <script>
                // Smooth scrolling for navigation links
                document.querySelectorAll('nav a').forEach(anchor => {
                    anchor.addEventListener('click', function(e) {
                        e.preventDefault();
                        
                        const targetId = this.getAttribute('href');
                        const targetElement = document.querySelector(targetId);
                        
                        window.scrollTo({
                            top: targetElement.offsetTop - 20,
                            behavior: 'smooth'
                        });
                    });
                });
                
                // Highlight current section in navigation
                window.addEventListener('scroll', function() {
                    const sections = document.querySelectorAll('section');
                    const navLinks = document.querySelectorAll('nav a');
                    
                    let currentSection = '';
                    
                    sections.forEach(section => {
                        const sectionTop = section.offsetTop;
                        const sectionHeight = section.clientHeight;
                        
                        if (pageYOffset >= sectionTop - 100) {
                            currentSection = '#' + section.getAttribute('id');
                        }
                    });
                    
                    navLinks.forEach(link => {
                        link.style.fontWeight = link.getAttribute('href') === currentSection ? 'bold' : 'normal';
                    });
                });
            </script>
        </body>
        </html>
        """

        return html

    def _group_visualizations_by_subcategory(
        self, visuals: Dict[str, str]
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Group visualizations by subcategory based on naming convention.

        Args:
            visuals: Dictionary mapping visualization names to file paths

        Returns:
            Dictionary mapping subcategories to lists of visualization info
        """
        subcategories = {}

        for name, path in visuals.items():
            # Extract subcategory from name (format: subcategory_name)
            parts = name.split("_", 1)
            if len(parts) > 1:
                subcategory, vis_name = parts
            else:
                subcategory = "general"
                vis_name = name

            if subcategory not in subcategories:
                subcategories[subcategory] = []

            subcategories[subcategory].append(
                {"name": vis_name, "path": path, "full_name": name}
            )

        return subcategories

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
            self.file_handler.ensure_directory_exists(target_dir)

            # Copy each visualization
            copy_count = 0
            for component, visuals in self.visualization_outputs.items():
                # Create component subdirectory
                component_dir = os.path.join(target_dir, component)
                self.file_handler.ensure_directory_exists(component_dir)

                # Copy each visualization file
                for name, path in visuals.items():
                    if os.path.exists(path):
                        target_path = os.path.join(
                            component_dir, os.path.basename(path)
                        )
                        self.file_handler.copy_file(path, target_path)
                        copy_count += 1

            # Copy HTML report if exists
            report_path = os.path.join(
                self.output_dir, "visualization_report", "visualization_report.html"
            )
            if os.path.exists(report_path):
                target_report_dir = os.path.join(target_dir, "report")
                self.file_handler.ensure_directory_exists(target_report_dir)
                self.file_handler.copy_file(
                    report_path,
                    os.path.join(target_report_dir, "visualization_report.html"),
                )

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
                        # Delete all files in the directory
                        for file in os.listdir(vis_dir):
                            file_path = os.path.join(vis_dir, file)
                            if os.path.isfile(file_path):
                                os.unlink(file_path)

                        # Update outputs
                        if component in self.visualization_outputs:
                            del self.visualization_outputs[component]

                        logger.info(
                            f"Cleared visualization files for component: {component}"
                        )
                    else:
                        logger.warning(
                            f"Visualization directory not found for component: {component}"
                        )
                else:
                    logger.warning(f"Component not found: {component}")
            else:
                # Clear all components
                for component, visualizer in self.visualizers.items():
                    vis_dir = visualizer.vis_dir
                    if os.path.exists(vis_dir):
                        # Delete all files in the directory
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

    def get_available_components(self) -> List[str]:
        """
        Get list of available visualization components.

        Returns:
            List of component names
        """
        return list(self.visualizers.keys())

    def get_component_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all visualization components.

        Returns:
            Dictionary mapping component names to status info
        """
        status = {}

        for component, visualizer in self.visualizers.items():
            # Check if component has visualizations
            has_visualizations = (
                component in self.visualization_outputs
                and len(self.visualization_outputs[component]) > 0
            )

            # Get visualization count
            vis_count = len(self.visualization_outputs.get(component, {}))

            # Get visualizer directory
            vis_dir = visualizer.vis_dir if hasattr(visualizer, "vis_dir") else None

            status[component] = {
                "has_visualizations": has_visualizations,
                "visualization_count": vis_count,
                "directory": vis_dir,
            }

        return status

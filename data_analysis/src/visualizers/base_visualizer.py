"""
Base visualization module with shared functionality for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime

from src.utils import get_logger, FileHandler, StatsUtils

logger = get_logger("visualizer")


class BaseVisualizer(ABC):
    """Abstract base class for all visualizers with shared functionality."""

    # Default color schemes
    COLOR_SCHEMES = {
        "default": plt.cm.viridis,
        "sequential": plt.cm.Blues,
        "diverging": plt.cm.RdYlGn,
        "categorical": plt.cm.tab20,
        "highlight": plt.cm.Reds,
        "monochrome": plt.cm.Greys,
    }

    # Standard colors for common elements
    STANDARD_COLORS = {
        "primary": "steelblue",
        "secondary": "coral",
        "tertiary": "mediumseagreen",
        "neutral": "gray",
        "highlight": "crimson",
        "toolv1": "lightblue",
        "toolv2": "cornflowerblue",
        "notool": "lightgray",
        "fall": "orange",
        "spring": "green",
        "high": "darkgreen",
        "medium": "yellowgreen",
        "low": "gold",
        "none": "lightcoral",
    }

    def __init__(self, output_dir: str, format: str = "png"):
        """
        Initialize the visualizer.

        Args:
            output_dir: Directory to save visualization outputs
            format: Output format for visualizations (png, pdf, svg)
        """
        self.output_dir = output_dir
        self.format = format
        self.file_handler = FileHandler()

        # Create output directory with component-specific subdirectory
        component_name = self.__class__.__name__.replace("Visualizer", "").lower()
        self.vis_dir = os.path.join(output_dir, component_name)
        self.file_handler.ensure_directory_exists(self.vis_dir)

        # Set default style
        plt.style.use("seaborn-v0_8-whitegrid")

        logger.info(
            f"Initialized {self.__class__.__name__} with output directory: {self.vis_dir}"
        )

    @abstractmethod
    def visualize(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate visualizations from data.

        Args:
            data: Data to visualize

        Returns:
            Dictionary mapping visualization names to file paths
        """
        pass

    def visualize_all(
        self,
        data: Dict[str, Any],
        visualization_map: Dict[str, Tuple[Callable, Dict[str, Any]]],
    ) -> Dict[str, str]:
        """
        Generate all visualizations from a component's data using a visualization map.

        Args:
            data: Component data to visualize
            visualization_map: Dictionary mapping visualization names to
                               tuples of (visualization_function, kwargs)

        Returns:
            Dictionary mapping visualization names to file paths
        """
        visualizations = {}

        if not data:
            logger.warning(f"No {self.__class__.__name__} data to visualize")
            return visualizations

        for name, (vis_func, kwargs) in visualization_map.items():
            # Extract data for this visualization
            data_key = kwargs.pop("data_key", name)

            # Support for nested data keys (e.g., 'cohorts.user_types')
            vis_data = self._get_nested_data(data, data_key)

            # Only proceed if we have data
            if vis_data:
                vis_path = self.create_visualization(vis_func, vis_data, name, **kwargs)
                if vis_path:
                    visualizations[name] = vis_path
            else:
                logger.warning(
                    f"No data found for visualization: {name} (key: {data_key})"
                )

        logger.info(f"Generated {len(visualizations)} visualizations")
        return visualizations

    def _get_nested_data(self, data: Dict[str, Any], key_path: str) -> Any:
        """
        Get data from nested dictionary using dot notation.

        Args:
            data: Data dictionary
            key_path: Key path using dot notation (e.g., 'cohorts.user_types')

        Returns:
            Value at the specified path or None if not found
        """
        if not key_path or not data:
            return None

        # Split the key path
        keys = key_path.split(".")

        # Traverse the nested dictionary
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def save_visualization_index(
        self, visualizations: Dict[str, str], filename: str = "visualization_index"
    ) -> Optional[str]:
        """
        Save an index of visualizations as JSON.

        Args:
            visualizations: Dictionary mapping visualization names to file paths
            filename: Base filename for the index file

        Returns:
            Path to the saved index file or None if an error occurred
        """
        try:
            # Create index with metadata
            index = {
                "component": self.__class__.__name__.replace("Visualizer", ""),
                "timestamp": datetime.now().isoformat(),
                "count": len(visualizations),
                "visualizations": {},
            }

            # Add metadata for each visualization
            for name, path in visualizations.items():
                # Get relative path from vis_dir
                rel_path = os.path.relpath(path, self.vis_dir)

                # Add to index
                index["visualizations"][name] = {
                    "filename": os.path.basename(path),
                    "relative_path": rel_path,
                    "absolute_path": path,
                    "format": self.format,
                    "created": datetime.fromtimestamp(
                        os.path.getctime(path)
                    ).isoformat(),
                }

            # Save index using FileHandler
            output_path = os.path.join(self.vis_dir, f"{filename}.json")
            success = self.file_handler.save_json(index, output_path)

            if success:
                logger.info(f"Saved visualization index to {output_path}")
                return output_path
            else:
                logger.error(f"Failed to save visualization index")
                return None

        except Exception as e:
            logger.error(f"Error saving visualization index: {str(e)}")
            return None

    def save_visualization_report(
        self,
        visualizations: Dict[str, str],
        filename: str = "visualization_report",
        title: str = None,
    ) -> Optional[str]:
        """
        Save an HTML report of visualizations.

        Args:
            visualizations: Dictionary mapping visualization names to file paths
            filename: Base filename for the report file
            title: Custom title for the report

        Returns:
            Path to the saved report file or None if an error occurred
        """
        try:
            if not title:
                title = f"{self.__class__.__name__.replace('Visualizer', '')} Visualization Report"

            # Create HTML report content
            html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }}
                    header {{
                        background-color: #f8f8f8;
                        padding: 20px;
                        border-bottom: 1px solid #ddd;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        margin: 0;
                        color: #2c3e50;
                    }}
                    .vis-item {{
                        margin-bottom: 30px;
                        border: 1px solid #eee;
                        padding: 15px;
                        border-radius: 5px;
                    }}
                    .vis-item h2 {{
                        margin-top: 0;
                        color: #3498db;
                    }}
                    .vis-item img {{
                        max-width: 100%;
                        height: auto;
                        border: 1px solid #ddd;
                    }}
                    .timestamp {{
                        color: #777;
                        font-size: 0.9em;
                        margin-top: 5px;
                    }}
                </style>
            </head>
            <body>
                <header>
                    <h1>{title}</h1>
                    <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </header>
            """

            # Add visualizations
            for name, path in visualizations.items():
                # Get relative path from output directory
                rel_path = os.path.relpath(path, self.vis_dir)

                # Format name for display
                display_name = name.replace("_", " ").title()

                html_content += f"""
                <div class="vis-item">
                    <h2>{display_name}</h2>
                    <img src="{rel_path}" alt="{display_name}">
                    <p class="timestamp">File: {os.path.basename(path)}</p>
                </div>
                """

            # Close HTML
            html_content += """
            </body>
            </html>
            """

            # Save HTML report using FileHandler
            output_path = os.path.join(self.vis_dir, f"{filename}.html")
            success = self.file_handler.save_text(html_content, output_path)

            if success:
                logger.info(f"Saved visualization report to {output_path}")
                return output_path
            else:
                logger.error(f"Failed to save visualization report")
                return None

        except Exception as e:
            logger.error(f"Error saving visualization report: {str(e)}")
            return None

    def create_visualization(
        self, vis_func: Callable, data: Any, filename: str, **kwargs
    ) -> Optional[str]:
        """
        Create a visualization with standardized error handling.

        Args:
            vis_func: Visualization function to call
            data: Data to pass to visualization function
            filename: Base filename for the output (without extension)
            **kwargs: Additional arguments to pass to visualization function

        Returns:
            Path to visualization file or None if an error occurred
        """
        try:
            logger.info(f"Creating visualization: {filename}")
            result = vis_func(data, filename, **kwargs)
            if result:
                logger.info(f"Successfully created visualization: {filename}")
            return result
        except Exception as e:
            logger.error(f"Error creating {filename} visualization: {str(e)}")
            # Clean up any partial figures that might be open
            plt.close("all")
            return None

    def save_figure(
        self, filename: str, dpi: int = 300, add_timestamp: bool = False
    ) -> Optional[str]:
        """
        Save the current figure to a file with standardized settings.

        Args:
            filename: Base filename (without extension)
            dpi: Resolution for the saved figure
            add_timestamp: Whether to add a timestamp to the filename

        Returns:
            Path to the saved file or None if an error occurred
        """
        try:
            # Use FileHandler to ensure output directory exists
            self.file_handler.ensure_directory_exists(self.vis_dir)

            if add_timestamp:
                # Generate timestamped filename using FileHandler
                output_path = self.file_handler.generate_filename(
                    self.vis_dir,
                    prefix=filename,
                    extension=self.format,
                    add_timestamp=True,
                )
            else:
                # Generate the standard output path
                output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")

            # Save the figure
            plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
            plt.close()

            logger.info(f"Successfully saved figure to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving figure {filename}.{self.format}: {str(e)}")
            plt.close()  # Ensure figure is closed even if saving fails
            return None

    # TODO Remove if not used
    def save_figure_with_timestamp(
        self, filename: str, dpi: int = 300
    ) -> Optional[str]:
        """
        Save the current figure with a timestamp in the filename.

        Args:
            filename: Base filename (without extension)
            dpi: Resolution for the saved figure

        Returns:
            Path to the saved file or None if an error occurred
        """
        return self.save_figure(filename, dpi, add_timestamp=True)

    def setup_figure(
        self,
        figsize: Tuple[int, int] = (12, 8),
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = None,
    ) -> plt.Figure:
        """
        Set up a figure with common parameters.

        Args:
            figsize: Figure size (width, height) in inches
            title: Figure title
            xlabel: X-axis label
            ylabel: Y-axis label
            xlim: X-axis limits
            ylim: Y-axis limits

        Returns:
            Configured figure object
        """
        fig = plt.figure(figsize=figsize)

        if title:
            plt.title(title, fontsize=16)

        if xlabel:
            plt.xlabel(xlabel, fontsize=12)

        if ylabel:
            plt.ylabel(ylabel, fontsize=12)

        if xlim:
            plt.xlim(xlim)

        if ylim:
            plt.ylim(ylim)

        return fig

    def setup_subplots(
        self, nrows: int = 1, ncols: int = 1, figsize: Tuple[int, int] = (12, 8)
    ) -> Tuple[plt.Figure, Union[plt.Axes, np.ndarray]]:
        """
        Set up a figure with subplots.

        Args:
            nrows: Number of rows
            ncols: Number of columns
            figsize: Figure size (width, height) in inches

        Returns:
            Tuple of (figure, axes)
        """
        return plt.subplots(nrows, ncols, figsize=figsize)

    def add_value_labels(
        self,
        ax: plt.Axes,
        bars: List,
        format_str: str = "{:.0f}",
        offset: Tuple[float, float] = (0, 0.5),
        **kwargs,
    ) -> None:
        """
        Add value labels to bars in a bar chart.

        Args:
            ax: Axes object
            bars: List of bar containers
            format_str: String format for labels
            offset: (x, y) offset for labels
            **kwargs: Additional arguments for text
        """
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2 + offset[0],
                height + offset[1],
                format_str.format(height),
                ha="center",
                va="bottom",
                **kwargs,
            )

    def get_color_gradient(
        self,
        n: int,
        scheme: str = "default",
        min_val: float = 0.1,
        max_val: float = 0.9,
    ) -> List:
        """
        Get a color gradient of n colors from a color scheme.

        Args:
            n: Number of colors
            scheme: Color scheme name
            min_val: Minimum value in the color range (0-1)
            max_val: Maximum value in the color range (0-1)

        Returns:
            List of n colors
        """
        cmap = self.COLOR_SCHEMES.get(scheme, self.COLOR_SCHEMES["default"])
        return cmap(np.linspace(min_val, max_val, n))

    def get_tool_color(self, tool_version: Optional[str]) -> str:
        """
        Get standard color for a tool version.

        Args:
            tool_version: Tool version string or None

        Returns:
            Color string
        """
        if tool_version is None:
            return self.STANDARD_COLORS["notool"]
        elif tool_version == "v1":
            return self.STANDARD_COLORS["toolv1"]
        else:
            return self.STANDARD_COLORS["toolv2"]

    # TODO Remove if not used
    def get_visualization_files(self, pattern: str = "*") -> List[str]:
        """
        Get a list of visualization files in the component's directory.

        Args:
            pattern: Optional glob pattern for filtering files

        Returns:
            List of file paths
        """
        try:
            # Use FileHandler to list files
            return self.file_handler.list_files(self.vis_dir, pattern)
        except Exception as e:
            logger.error(f"Error listing visualization files: {str(e)}")
            return []

    def get_latest_visualization(self, pattern: Optional[str] = None) -> Optional[str]:
        """
        Get the most recently created visualization file.

        Args:
            pattern: Optional glob pattern for filtering files

        Returns:
            Path to the latest file, or None if no files found
        """
        try:
            # Use FileHandler to get the latest file
            return self.file_handler.get_latest_file(self.vis_dir, pattern)
        except Exception as e:
            logger.error(f"Error getting latest visualization: {str(e)}")
            return None

    def format_date_axis(
        self,
        ax: plt.Axes,
        date_format: str = "%b %Y",
        interval: int = 1,
        rotation: int = 45,
    ) -> None:
        """
        Format axis for date display.

        Args:
            ax: Axes object to format
            date_format: Date format string
            interval: Month interval for ticks
            rotation: Rotation angle for tick labels
        """
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
        plt.setp(ax.get_xticklabels(), rotation=rotation, ha="right")

    def highlight_tool_changes(
        self, ax: plt.Axes, tool_versions: List, offset: float = 0.5, **kwargs
    ) -> None:
        """
        Add vertical lines to highlight tool version changes.

        Args:
            ax: Axes object
            tool_versions: List of tool versions
            offset: X-offset for line placement
            **kwargs: Additional line style parameters
        """
        default_style = {"color": "red", "linestyle": "--", "alpha": 0.5}
        style = {**default_style, **kwargs}

        for i in range(1, len(tool_versions)):
            if tool_versions[i] != tool_versions[i - 1]:
                ax.axvline(x=i - offset, **style)

    def add_trend_line(
        self, ax: plt.Axes, x: List, y: List, label: Optional[str] = None, **kwargs
    ) -> None:
        """
        Add a trend line to a plot.

        Args:
            ax: Axes object
            x: X values
            y: Y values
            label: Label for the trend line
            **kwargs: Additional line style parameters
        """
        if len(x) < 2 or len(y) < 2:
            return

        # Calculate trend
        trend = StatsUtils.calculate_trend(y)

        if trend.get("slope") is not None:
            # Create trend line points
            x_vals = range(len(x))
            trend_y = [trend["slope"] * x_i + trend["intercept"] for x_i in x_vals]

            # Set default style
            default_style = {"linestyle": "--", "alpha": 0.7, "color": "red"}
            style = {**default_style, **kwargs}

            # Add label with R-squared if available
            if label is None and trend.get("r_squared") is not None:
                label = f"Trend (R² = {trend['r_squared']:.2f})"

            # Plot trend line
            ax.plot(x, trend_y, label=label, **style)

    def create_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: Union[str, List] = None,
        add_value_labels: bool = True,
        horizontal: bool = False,
        rotation: int = 0,
        figsize: Tuple[int, int] = (12, 8),
        format_str: str = "{:.0f}",
    ) -> Optional[str]:
        """
        Create a bar chart visualization.

        Args:
            labels: Bar labels
            values: Bar values
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            color: Bar color(s)
            add_value_labels: Whether to add value labels to bars
            horizontal: Whether to create a horizontal bar chart
            rotation: Rotation angle for x-tick labels
            figsize: Figure size (width, height) in inches
            format_str: Format string for value labels

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Set default color if not provided
            if color is None:
                color = self.STANDARD_COLORS["primary"]

            # Create bar chart (horizontal or vertical)
            if horizontal:
                bars = plt.barh(labels, values, color=color)

                # Add value labels if requested
                if add_value_labels:
                    for bar in bars:
                        width = bar.get_width()
                        plt.text(
                            width + 0.3,
                            bar.get_y() + bar.get_height() / 2,
                            format_str.format(width),
                            ha="left",
                            va="center",
                        )
            else:
                bars = plt.bar(labels, values, color=color)

                # Add value labels if requested
                if add_value_labels:
                    self.add_value_labels(plt.gca(), bars, format_str)

            # Add rotation to labels if needed
            plt.xticks(rotation=rotation, ha="right" if rotation > 0 else "center")

            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating bar chart visualization {filename}: {str(e)}")
            plt.close()
            return None

    def create_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        filename: str,
        title: Optional[str] = None,
        colors: Optional[List] = None,
        autopct: str = "%1.1f%%",
        add_legend: bool = True,
        figsize: Tuple[int, int] = (10, 8),
        explode: Optional[List[float]] = None,
    ) -> Optional[str]:
        """
        Create a pie chart visualization.

        Args:
            labels: Slice labels
            values: Slice values
            filename: Base filename for saving
            title: Chart title
            colors: Custom colors for slices
            autopct: Format string for percentage labels
            add_legend: Whether to add a legend
            figsize: Figure size (width, height) in inches
            explode: List of offset values for slices (to "explode" them)

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(figsize=figsize, title=title)

            # Create pie chart
            if colors is None:
                colors = self.get_color_gradient(len(values), "categorical")

            plt.pie(
                values,
                labels=labels,
                autopct=autopct,
                startangle=90,
                colors=colors,
                explode=explode,
                shadow=True,
                wedgeprops={"edgecolor": "w", "linewidth": 1},
            )

            # Add legend if requested
            if add_legend:
                legend_labels = [
                    f"{label} ({value})" for label, value in zip(labels, values)
                ]
                plt.legend(legend_labels, loc="best", bbox_to_anchor=(1, 0.5))

            # Equal aspect ratio ensures the pie chart is circular
            plt.axis("equal")
            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating pie chart visualization {filename}: {str(e)}")
            plt.close()
            return None

    def create_line_chart(
        self,
        x: List,
        y: List,
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: str = "royalblue",
        add_trend: bool = False,
        marker: str = "o",
        linestyle: str = "-",
        fill: bool = False,
        figsize: Tuple[int, int] = (14, 7),
        date_format: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a line chart visualization.

        Args:
            x: X values
            y: Y values
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            color: Line color
            add_trend: Whether to add a trend line
            marker: Marker style
            linestyle: Line style
            fill: Whether to fill area under the line
            figsize: Figure size (width, height) in inches
            date_format: Format for date axes (if x contains dates)

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Create line chart
            plt.plot(
                x,
                y,
                marker=marker,
                linestyle=linestyle,
                color=color,
                linewidth=2,
                markersize=8,
            )

            # Fill area under the line if requested
            if fill:
                plt.fill_between(x, y, alpha=0.3, color=color)

            # Format x-axis as dates if requested
            if date_format is not None:
                self.format_date_axis(plt.gca(), date_format=date_format)

            # Add trend line if requested
            if add_trend:
                self.add_trend_line(plt.gca(), x, y)

            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(
                f"Error creating line chart visualization {filename}: {str(e)}"
            )
            plt.close()
            return None

    def create_heatmap(
        self,
        data: np.ndarray,
        row_labels: List[str],
        col_labels: List[str],
        filename: str,
        title: Optional[str] = None,
        cmap: str = "viridis",
        add_values: bool = True,
        figsize: Tuple[int, int] = (14, 10),
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a heatmap visualization.

        Args:
            data: 2D array of data values
            row_labels: Labels for rows
            col_labels: Labels for columns
            filename: Base filename for saving
            title: Chart title
            cmap: Colormap name
            add_values: Whether to add value labels in cells
            figsize: Figure size (width, height) in inches
            xlabel: X-axis label
            ylabel: Y-axis label

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            plt.figure(figsize=figsize)

            # Calculate value range for consistent colormap
            valid_data = data[~np.isnan(data)]
            vmin = np.min(valid_data) if len(valid_data) > 0 else 0
            vmax = np.max(valid_data) if len(valid_data) > 0 else 1

            # Create heatmap
            im = plt.imshow(data, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)

            # Add colorbar
            cbar = plt.colorbar(im)

            # Add labels
            plt.xticks(np.arange(len(col_labels)), col_labels, rotation=45, ha="right")
            plt.yticks(np.arange(len(row_labels)), row_labels)

            if xlabel:
                plt.xlabel(xlabel, fontsize=12)

            if ylabel:
                plt.ylabel(ylabel, fontsize=12)

            if title:
                plt.title(title, fontsize=16)

            # Add values in each cell
            if add_values:
                for i in range(len(row_labels)):
                    for j in range(len(col_labels)):
                        value = data[i, j]
                        if not np.isnan(value):
                            plt.text(
                                j,
                                i,
                                f"{value:.2f}",
                                ha="center",
                                va="center",
                                color="white" if value < (vmin + vmax) / 2 else "black",
                            )

            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating heatmap visualization {filename}: {str(e)}")
            plt.close()
            return None

    def create_stacked_bar_chart(
        self,
        labels: List[str],
        data_dict: Dict[str, List[float]],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        figsize: Tuple[int, int] = (12, 8),
        rotation: int = 0,
        show_percentages: bool = False,
        horizontal: bool = False,
    ) -> Optional[str]:
        """
        Create a stacked bar chart visualization.

        Args:
            labels: Bar labels (x-axis)
            data_dict: Dictionary mapping stack levels to values lists
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            colors: Dictionary mapping stack levels to colors
            figsize: Figure size (width, height) in inches
            rotation: Rotation angle for x-tick labels
            show_percentages: Whether to show percentages in each segment
            horizontal: Whether to create a horizontal stacked bar chart

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Get stack levels in desired order
            stack_levels = list(data_dict.keys())

            # Set default colors if not provided
            if colors is None:
                color_list = self.get_color_gradient(len(stack_levels), "categorical")
                colors = {
                    level: color for level, color in zip(stack_levels, color_list)
                }

            # Calculate totals for percentage display if needed
            if show_percentages:
                totals = [
                    sum(data_dict[level][i] for level in stack_levels)
                    for i in range(len(labels))
                ]

            # Create stacked bar chart
            bottom = np.zeros(len(labels))
            bars = {}

            for level in stack_levels:
                values = data_dict[level]
                color = colors.get(level, "gray")

                if horizontal:
                    bars[level] = plt.barh(
                        labels, values, left=bottom, label=f"{level}", color=color
                    )
                else:
                    bars[level] = plt.bar(
                        labels, values, bottom=bottom, label=f"{level}", color=color
                    )

                # Add percentage labels if requested
                if show_percentages:
                    for i, bar in enumerate(bars[level]):
                        if horizontal:
                            width = bar.get_width()
                            if width > 0 and totals[i] > 0:
                                percentage = width / totals[i] * 100
                                if (
                                    percentage >= 5
                                ):  # Only show label if segment is large enough
                                    plt.text(
                                        bar.get_x() + width / 2,
                                        bar.get_y() + bar.get_height() / 2,
                                        f"{percentage:.1f}%",
                                        ha="center",
                                        va="center",
                                        color=(
                                            "black"
                                            if colors.get(level, "gray")
                                            in ["lightyellow", "lightgray"]
                                            else "white"
                                        ),
                                        fontweight="bold",
                                    )
                        else:
                            height = bar.get_height()
                            if height > 0 and totals[i] > 0:
                                percentage = height / totals[i] * 100
                                if (
                                    percentage >= 5
                                ):  # Only show label if segment is large enough
                                    plt.text(
                                        bar.get_x() + bar.get_width() / 2,
                                        bottom[i] + height / 2,
                                        f"{percentage:.1f}%",
                                        ha="center",
                                        va="center",
                                        color=(
                                            "black"
                                            if colors.get(level, "gray")
                                            in ["lightyellow", "lightgray"]
                                            else "white"
                                        ),
                                        fontweight="bold",
                                    )

                # Update bottom for next stack level
                bottom += values

            # Add rotation to labels if needed
            plt.xticks(rotation=rotation, ha="right" if rotation > 0 else "center")

            # Add legend
            plt.legend(loc="best")

            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(
                f"Error creating stacked bar chart visualization {filename}: {str(e)}"
            )
            plt.close()
            return None

    def create_grouped_bar_chart(
        self,
        labels: List[str],
        data_dict: Dict[str, List[float]],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        figsize: Tuple[int, int] = (12, 8),
        rotation: int = 0,
        add_value_labels: bool = True,
        format_str: str = "{:.0f}",
    ) -> Optional[str]:
        """
        Create a grouped bar chart visualization.

        Args:
            labels: Bar group labels
            data_dict: Dictionary mapping series names to values lists
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            colors: Dictionary mapping series names to colors
            figsize: Figure size (width, height) in inches
            rotation: Rotation angle for x-tick labels
            add_value_labels: Whether to add value labels to bars
            format_str: Format string for value labels

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Get group names and set positions
            series_names = list(data_dict.keys())
            num_groups = len(labels)
            num_series = len(series_names)

            # Calculate bar width and positions
            group_width = 0.8
            bar_width = group_width / num_series
            index = np.arange(num_groups)

            # Set default colors if not provided
            if colors is None:
                color_list = self.get_color_gradient(len(series_names), "categorical")
                colors = {name: color for name, color in zip(series_names, color_list)}

            # Create grouped bars
            bars = {}
            for i, name in enumerate(series_names):
                values = data_dict[name]
                color = colors.get(name, "gray")
                position = index - group_width / 2 + (i + 0.5) * bar_width

                bars[name] = plt.bar(
                    position, values, bar_width, label=name, color=color
                )

                # Add value labels if requested
                if add_value_labels:
                    for bar in bars[name]:
                        height = bar.get_height()
                        plt.text(
                            bar.get_x() + bar.get_width() / 2,
                            height + 0.1,
                            format_str.format(height),
                            ha="center",
                            va="bottom",
                        )

            # Set x-axis ticks and labels
            plt.xticks(
                index,
                labels,
                rotation=rotation,
                ha="right" if rotation > 0 else "center",
            )

            # Add legend
            plt.legend(loc="best")

            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(
                f"Error creating grouped bar chart visualization {filename}: {str(e)}"
            )
            plt.close()
            return None

    def create_scatter_plot(
        self,
        x: List[float],
        y: List[float],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: Union[str, List[str]] = "royalblue",
        sizes: Optional[List[float]] = None,
        add_trend: bool = False,
        add_labels: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (12, 8),
    ) -> Optional[str]:
        """
        Create a scatter plot visualization.

        Args:
            x: X values
            y: Y values
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            color: Point color(s)
            sizes: Point sizes
            add_trend: Whether to add a trend line
            add_labels: Optional point labels
            figsize: Figure size (width, height) in inches

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Create scatter plot
            scatter = plt.scatter(x, y, c=color, s=sizes, alpha=0.7)

            # Add trend line if requested
            if add_trend:
                self.add_trend_line(plt.gca(), x, y)

            # Add point labels if provided
            if add_labels:
                for i, label in enumerate(add_labels):
                    plt.annotate(
                        label,
                        (x[i], y[i]),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=9,
                    )

            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(
                f"Error creating scatter plot visualization {filename}: {str(e)}"
            )
            plt.close()
            return None

    def create_histogram(
        self,
        data: List[float],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: str = "royalblue",
        bins: Union[int, List[float]] = 10,
        add_kde: bool = False,
        figsize: Tuple[int, int] = (12, 8),
        add_mean_line: bool = False,
    ) -> Optional[str]:
        """
        Create a histogram visualization.

        Args:
            data: Data values
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            color: Bar color
            bins: Number of bins or bin edges
            add_kde: Whether to add a kernel density estimate curve
            figsize: Figure size (width, height) in inches
            add_mean_line: Whether to add a vertical line at the mean

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Create histogram
            plt.hist(data, bins=bins, color=color, alpha=0.7, edgecolor="black")

            # Add KDE if requested
            if add_kde:
                try:
                    import scipy.stats as stats

                    density = stats.gaussian_kde(data)
                    x_vals = np.linspace(min(data), max(data), 1000)
                    y_vals = density(x_vals)

                    # Scale KDE to match histogram height
                    hist_heights, _ = np.histogram(data, bins=bins)
                    max_hist = max(hist_heights)
                    y_vals = y_vals * max_hist / max(y_vals)

                    plt.plot(x_vals, y_vals, "r-", linewidth=2, label="KDE")
                    plt.legend()
                except ImportError:
                    logger.warning("scipy not available, skipping KDE")

            # Add mean line if requested
            if add_mean_line and data:
                mean_val = np.mean(data)
                plt.axvline(
                    x=mean_val, color="r", linestyle="--", label=f"Mean: {mean_val:.2f}"
                )
                plt.legend()

            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating histogram visualization {filename}: {str(e)}")
            plt.close()
            return None

    def create_boxplot(
        self,
        data: List[List[float]],
        labels: List[str],
        filename: str,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
        horizontal: bool = False,
        add_grid: bool = True,
    ) -> Optional[str]:
        """
        Create a box plot visualization.

        Args:
            data: List of data series
            labels: Box labels
            filename: Base filename for saving
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size (width, height) in inches
            horizontal: Whether to create a horizontal box plot
            add_grid: Whether to add grid lines

        Returns:
            Path to the saved figure or None if an error occurred
        """
        try:
            # Setup figure
            fig = self.setup_figure(
                figsize=figsize, title=title, xlabel=xlabel, ylabel=ylabel
            )

            # Create box plot
            if horizontal:
                plt.boxplot(data, labels=labels, vert=False)
            else:
                plt.boxplot(data, labels=labels)

            # Add grid if requested
            if add_grid:
                plt.grid(True, linestyle="--", alpha=0.7)

            plt.tight_layout()

            # Save and return
            return self.save_figure(filename)

        except Exception as e:
            logger.error(f"Error creating box plot visualization {filename}: {str(e)}")
            plt.close()
            return None

"""
Base visualization module with shared functionality for the AI thesis analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime

from src.utils import get_logger

logger = get_logger("visualizer")


class BaseVisualizer(ABC):
    """Abstract base class for all visualizers with shared functionality."""
    
    # Default color schemes
    COLOR_SCHEMES = {
        'default': plt.cm.viridis,
        'sequential': plt.cm.Blues,
        'diverging': plt.cm.RdYlGn,
        'categorical': plt.cm.tab20,
        'highlight': plt.cm.Reds,
        'monochrome': plt.cm.Greys
    }
    
    # Standard colors for common elements
    STANDARD_COLORS = {
        'primary': 'steelblue',
        'secondary': 'coral',
        'tertiary': 'mediumseagreen',
        'neutral': 'gray',
        'highlight': 'crimson',
        'toolv1': 'lightblue',
        'toolv2': 'cornflowerblue',
        'notool': 'lightgray',
        'fall': 'orange',
        'spring': 'green',
        'high': 'darkgreen',
        'medium': 'yellowgreen',
        'low': 'gold',
        'none': 'lightcoral'
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
        
        # Create output directory with component-specific subdirectory
        component_name = self.__class__.__name__.replace('Visualizer', '').lower()
        self.vis_dir = os.path.join(output_dir, component_name)
        os.makedirs(self.vis_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        logger.info(f"Initialized {self.__class__.__name__} with output directory: {self.vis_dir}")
    
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
    
    def create_visualization(self, 
                            vis_func: Callable, 
                            data: Any, 
                            filename: str, 
                            **kwargs) -> Optional[str]:
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
            return vis_func(data, filename, **kwargs)
        except Exception as e:
            logger.error(f"Error creating {filename} visualization: {str(e)}")
            return None
    
    def save_figure(self, filename: str, dpi: int = 300) -> str:
        """
        Save the current figure to a file with standardized settings.
        
        Args:
            filename: Base filename (without extension)
            dpi: Resolution for the saved figure
            
        Returns:
            Path to the saved file
        """
        output_path = os.path.join(self.vis_dir, f"{filename}.{self.format}")
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        return output_path
    
    def setup_figure(self, 
                    figsize: Tuple[int, int] = (12, 8),
                    title: Optional[str] = None,
                    xlabel: Optional[str] = None,
                    ylabel: Optional[str] = None,
                    xlim: Optional[Tuple[float, float]] = None,
                    ylim: Optional[Tuple[float, float]] = None) -> plt.Figure:
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
    
    def setup_subplots(self, 
                      nrows: int = 1, 
                      ncols: int = 1, 
                      figsize: Tuple[int, int] = (12, 8)) -> Tuple[plt.Figure, Union[plt.Axes, np.ndarray]]:
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
    
    def add_value_labels(self, 
                         ax: plt.Axes, 
                         bars: List, 
                         format_str: str = '{:.0f}', 
                         offset: Tuple[float, float] = (0, 0.5),
                         **kwargs) -> None:
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
                bar.get_x() + bar.get_width()/2 + offset[0],
                height + offset[1],
                format_str.format(height),
                ha='center', 
                va='bottom',
                **kwargs
            )
    
    def get_color_gradient(self, 
                          n: int, 
                          scheme: str = 'default', 
                          min_val: float = 0.1,
                          max_val: float = 0.9) -> List:
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
        cmap = self.COLOR_SCHEMES.get(scheme, self.COLOR_SCHEMES['default'])
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
            return self.STANDARD_COLORS['notool']
        elif tool_version == 'v1':
            return self.STANDARD_COLORS['toolv1']
        else:
            return self.STANDARD_COLORS['toolv2']
    
    def format_date_axis(self, 
                        ax: plt.Axes, 
                        date_format: str = '%b %Y', 
                        interval: int = 1,
                        rotation: int = 45) -> None:
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
        plt.setp(ax.get_xticklabels(), rotation=rotation, ha='right')
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse a date string in various formats.
        
        Args:
            date_string: Date string to parse
            
        Returns:
            Datetime object or None if parsing failed
        """
        if not date_string:
            return None
        
        # Try various date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with milliseconds
            '%Y-%m-%dT%H:%M:%SZ',     # ISO format without milliseconds
            '%Y-%m-%d',               # Simple date format
            '%Y/%m/%d',               # Alternative date format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        return None
    
    def highlight_tool_changes(self, 
                              ax: plt.Axes, 
                              tool_versions: List, 
                              offset: float = 0.5,
                              **kwargs) -> None:
        """
        Add vertical lines to highlight tool version changes.
        
        Args:
            ax: Axes object
            tool_versions: List of tool versions
            offset: X-offset for line placement
            **kwargs: Additional line style parameters
        """
        default_style = {'color': 'red', 'linestyle': '--', 'alpha': 0.5}
        style = {**default_style, **kwargs}
        
        for i in range(1, len(tool_versions)):
            if tool_versions[i] != tool_versions[i-1]:
                ax.axvline(x=i-offset, **style)
    
    def calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate a simple linear trend from a series of values.
        
        Args:
            values: List of numerical values
            
        Returns:
            Dictionary with trend metrics
        """
        if not values or len(values) < 2:
            return {
                'direction': 'unknown',
                'slope': None,
                'consistent': None
            }
        
        # Calculate simple slope between first and last value
        first = values[0]
        last = values[-1]
        total_change = last - first
        
        # Determine direction
        if total_change > 0:
            direction = 'increasing'
        elif total_change < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Calculate a simple linear regression
        x = list(range(len(values)))
        n = len(x)
        
        # Calculate slope and intercept
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))
        
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Calculate predicted values and R-squared
            y_pred = [slope * x_i + intercept for x_i in x]
            
            ss_total = sum((y - (sum_y / n))**2 for y in values)
            ss_residual = sum((values[i] - y_pred[i])**2 for i in range(n))
            
            r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
            
            return {
                'direction': direction,
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'total_change': total_change,
                'percent_change': (total_change / first) * 100 if first != 0 else None
            }
        except ZeroDivisionError:
            return {
                'direction': direction,
                'slope': 0,
                'total_change': total_change
            }
    
    def add_trend_line(self, 
                      ax: plt.Axes, 
                      x: List, 
                      y: List, 
                      label: Optional[str] = None, 
                      **kwargs) -> None:
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
        trend = self.calculate_trend(y)
        
        if trend.get('slope') is not None:
            # Create trend line points
            x_vals = range(len(x))
            trend_y = [trend['slope'] * x_i + trend['intercept'] for x_i in x_vals]
            
            # Set default style
            default_style = {'linestyle': '--', 'alpha': 0.7, 'color': 'red'}
            style = {**default_style, **kwargs}
            
            # Add label with R-squared if available
            if label is None and trend.get('r_squared') is not None:
                label = f"Trend (R² = {trend['r_squared']:.2f})"
            
            # Plot trend line
            ax.plot(x, trend_y, label=label, **style)
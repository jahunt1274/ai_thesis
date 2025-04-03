"""
Statistics utility functions for data analysis.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict


class StatsUtils:
    """Utility class for statistical operations."""
    
    @staticmethod
    def calculate_average(values: List[float], min_values: int = 1) -> Optional[float]:
        """
        Calculate average of a list of values.
        
        Args:
            values: List of values to average
            min_values: Minimum number of values required (default: 1)
            
        Returns:
            Average value, or None if insufficient values
        """
        if not values or len(values) < min_values:
            return None
        
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_percentages(counts: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate percentages from a dictionary of counts.
        
        Args:
            counts: Dictionary mapping keys to counts
            
        Returns:
            Dictionary mapping keys to percentages
        """
        total = sum(counts.values())
        
        if total == 0:
            return {k: 0.0 for k in counts}
        
        return {k: (v / total) * 100 for k, v in counts.items()}
    
    @staticmethod
    def calculate_trend(values: List[float]) -> Dict[str, Any]:
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
        
        # Check if trend is consistent or fluctuating
        increasing_segments = 0
        decreasing_segments = 0
        
        for i in range(1, len(values)):
            diff = values[i] - values[i-1]
            if diff > 0:
                increasing_segments += 1
            elif diff < 0:
                decreasing_segments += 1
        
        # Calculate consistency
        total_segments = len(values) - 1
        if direction == 'increasing':
            consistency = increasing_segments / total_segments
        elif direction == 'decreasing':
            consistency = decreasing_segments / total_segments
        else:
            consistency = 1.0
        
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
                'consistent': consistency > 0.5,
                'consistency': consistency,
                'total_change': total_change,
                'percent_change': (total_change / first) * 100 if first != 0 else None
            }
        except ZeroDivisionError:
            return {
                'direction': direction,
                'slope': 0,
                'total_change': total_change
            }
    
    @staticmethod
    def calculate_correlation(x_values: List[float], y_values: List[float]) -> Dict[str, Any]:
        """
        Calculate correlation between two sets of values.
        
        Args:
            x_values: First set of values
            y_values: Second set of values
            
        Returns:
            Dictionary with correlation metrics
        """
        if not x_values or not y_values or len(x_values) != len(y_values) or len(x_values) < 2:
            return {
                'correlation': None,
                'direction': 'unknown',
                'strength': 'unknown'
            }
        
        n = len(x_values)
        
        # Calculate means
        mean_x = sum(x_values) / n
        mean_y = sum(y_values) / n
        
        # Calculate covariance and standard deviations
        covariance = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n)) / n
        
        std_dev_x = (sum((x - mean_x) ** 2 for x in x_values) / n) ** 0.5
        std_dev_y = (sum((y - mean_y) ** 2 for y in y_values) / n) ** 0.5
        
        # Calculate Pearson correlation coefficient
        if std_dev_x > 0 and std_dev_y > 0:
            correlation = covariance / (std_dev_x * std_dev_y)
        else:
            correlation = 0
        
        # Interpret correlation
        direction = 'positive' if correlation > 0 else 'negative' if correlation < 0 else 'none'
        
        # Determine correlation strength
        abs_corr = abs(correlation)
        if abs_corr < 0.3:
            strength = 'weak'
        elif abs_corr < 0.7:
            strength = 'moderate'
        else:
            strength = 'strong'
        
        return {
            'correlation': correlation,
            'direction': direction,
            'strength': strength
        }
    
    @staticmethod
    def find_top_n(data: Dict[str, Any], n: int = 10, key_func=None) -> List:
        """
        Find the top N items in a dictionary by value.
        
        Args:
            data: Dictionary to search
            n: Number of top items to return (default: 10)
            key_func: Optional function to extract comparison value
            
        Returns:
            List of top N items as (key, value) tuples
        """
        if not key_func:
            key_func = lambda x: x[1]
            
        return sorted(data.items(), key=key_func, reverse=True)[:n]
    
    @staticmethod
    def distribution_buckets(values: List[float], bucket_size: float = 10.0) -> Dict[float, int]:
        """
        Create distribution buckets from a list of values.
        
        Args:
            values: List of values to bucket
            bucket_size: Size of each bucket (default: 10.0)
            
        Returns:
            Dictionary mapping bucket starting values to counts
        """
        buckets = defaultdict(int)
        
        for value in values:
            bucket = int(value / bucket_size) * bucket_size
            buckets[bucket] += 1
            
        return dict(buckets)
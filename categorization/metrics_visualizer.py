#!/usr/bin/env python
"""
Metrics Visualizer for IdeaCategorizer

This script visualizes performance metrics collected from the IdeaCategorizer
to help analyze and optimize batch sizes, payload sizes, and other parameters.

Usage:
    python metrics_visualizer.py --metrics-file path/to/metrics.json

"""

import argparse
import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


class MetricsVisualizer:
    """Visualizes performance metrics from IdeaCategorizer runs."""
    
    def __init__(self, metrics_file, output_dir=None):
        """
        Initialize the metrics visualizer.
        
        Args:
            metrics_file: Path to the metrics JSON file
            output_dir: Directory to save visualization outputs (defaults to same dir as metrics file)
        """
        self.metrics_file = metrics_file
        
        # Set default output directory if not provided
        if output_dir is None:
            self.output_dir = os.path.dirname(os.path.abspath(metrics_file))
        else:
            self.output_dir = output_dir
            
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load metrics
        with open(metrics_file, 'r') as f:
            self.metrics = json.load(f)
        
        # Generate timestamp for output files
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_filename(self, prefix, extension="png"):
        """Generate a filename for output visualizations."""
        model = self.metrics.get("config", {}).get("model", "unknown")
        return os.path.join(
            self.output_dir, 
            f"{prefix}_{model}_{self.timestamp}.{extension}"
        )
        
    def visualize_runtime_breakdown(self):
        """Create a pie chart of runtime breakdown."""
        runtime = self.metrics.get("runtime", {})
        breakdown = runtime.get("breakdown", {})
        
        # Extract data for the pie chart
        labels = []
        sizes = []
        
        for key, data in breakdown.items():
            # Skip if time is very small
            if data.get("seconds", 0) < 0.1:
                continue
                
            labels.append(key.capitalize())
            sizes.append(data.get("seconds", 0))
        
        # Create figure
        plt.figure(figsize=(10, 7))
        
        # Create pie chart
        plt.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            shadow=True,
        )
        plt.axis('equal')  # Equal aspect ratio ensures the pie is circular
        
        # Add title and other information
        total_time = runtime.get("formatted", "Unknown")
        plt.title(f'Runtime Breakdown (Total: {total_time})')
        
        # Add config information as text
        config = self.metrics.get("config", {})
        config_text = (
            f"Model: {config.get('model', 'Unknown')}\n"
            f"Batch Size: {config.get('batch_size', 'Unknown')}\n"
            f"Mode: {config.get('processing_mode', 'Unknown')}"
        )
        plt.figtext(0.01, 0.01, config_text, fontsize=8)
        
        # Save figure
        output_file = self.generate_filename("runtime_breakdown")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created runtime breakdown visualization: {output_file}")
        return output_file
        
    def visualize_batch_processing_times(self):
        """Create a scatter plot of batch processing times vs. payload size."""
        batch_data = self.metrics.get("batch_timing", [])
        
        # Extract data
        batch_nums = []
        api_times = []
        processing_times = []
        total_times = []
        payload_sizes = []
        ideas_counts = []
        token_counts = []
        
        for batch in batch_data:
            # Skip batches with errors
            if batch.get("status") != "success":
                continue
                
            batch_nums.append(batch.get("batch_num", 0))
            total_times.append(batch.get("total_time", 0))
            api_times.append(batch.get("api_time", 0))
            processing_times.append(batch.get("processing_time", 0))
            ideas_counts.append(batch.get("ideas_count", 0))
            
            # Get API metrics
            api_metrics = batch.get("api_metrics", {})
            payload_sizes.append(api_metrics.get("payload_size", 0) / 1024)  # Convert to KB
            token_counts.append(api_metrics.get("total_tokens", 0))
        
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Processing time vs batch number
        axs[0, 0].bar(batch_nums, api_times, label='API Time', alpha=0.7)
        axs[0, 0].bar(batch_nums, processing_times, bottom=api_times, label='Processing Time', alpha=0.7)
        axs[0, 0].set_xlabel('Batch Number')
        axs[0, 0].set_ylabel('Time (seconds)')
        axs[0, 0].set_title('Processing Time by Batch')
        axs[0, 0].legend()
        axs[0, 0].grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Processing time vs payload size
        axs[0, 1].scatter(payload_sizes, api_times, label='API Time', alpha=0.7)
        axs[0, 1].set_xlabel('Payload Size (KB)')
        axs[0, 1].set_ylabel('API Time (seconds)')
        axs[0, 1].set_title('API Time vs Payload Size')
        
        # Add trend line
        if payload_sizes and api_times:
            z = np.polyfit(payload_sizes, api_times, 1)
            p = np.poly1d(z)
            axs[0, 1].plot(
                sorted(payload_sizes), 
                p(sorted(payload_sizes)), 
                "r--", 
                label=f'Trend: y={z[0]:.4f}x+{z[1]:.4f}'
            )
        
        axs[0, 1].legend()
        axs[0, 1].grid(True, linestyle='--', alpha=0.7)
        
        # Plot 3: API time vs ideas count
        axs[1, 0].scatter(ideas_counts, api_times, alpha=0.7)
        axs[1, 0].set_xlabel('Number of Ideas in Batch')
        axs[1, 0].set_ylabel('API Time (seconds)')
        axs[1, 0].set_title('API Time vs Number of Ideas')
        
        # Add trend line
        if ideas_counts and api_times:
            z = np.polyfit(ideas_counts, api_times, 1)
            p = np.poly1d(z)
            axs[1, 0].plot(
                sorted(ideas_counts), 
                p(sorted(ideas_counts)), 
                "r--", 
                label=f'Trend: y={z[0]:.4f}x+{z[1]:.4f}'
            )
        
        axs[1, 0].legend()
        axs[1, 0].grid(True, linestyle='--', alpha=0.7)
        
        # Plot 4: Tokens per second vs payload size
        tokens_per_second = []
        for i, api_time in enumerate(api_times):
            if api_time > 0:
                tokens_per_second.append(token_counts[i] / api_time)
            else:
                tokens_per_second.append(0)
                
        axs[1, 1].scatter(payload_sizes, tokens_per_second, alpha=0.7)
        axs[1, 1].set_xlabel('Payload Size (KB)')
        axs[1, 1].set_ylabel('Tokens per Second')
        axs[1, 1].set_title('Processing Efficiency vs Payload Size')
        axs[1, 1].grid(True, linestyle='--', alpha=0.7)
        
        # Add overall information
        plt.tight_layout()
        fig.suptitle('Batch Processing Performance Analysis', fontsize=16)
        plt.subplots_adjust(top=0.92)
        
        # Add config information
        config = self.metrics.get("config", {})
        config_text = (
            f"Model: {config.get('model', 'Unknown')}, "
            f"Batch Size: {config.get('batch_size', 'Unknown')}, "
            f"Mode: {config.get('processing_mode', 'Unknown')}"
        )
        fig.text(0.5, 0.01, config_text, ha='center', fontsize=10)
        
        # Save figure
        output_file = self.generate_filename("batch_performance")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created batch performance visualization: {output_file}")
        return output_file
        
    def visualize_optimal_batch_size(self):
        """
        Create a visualization to help determine the optimal batch size.
        
        This is more useful when comparing multiple runs with different batch sizes.
        """
        batch_data = self.metrics.get("batch_timing", [])
        
        # Extract data
        payload_sizes = []
        tokens_per_second = []
        ideas_per_second = []
        
        for batch in batch_data:
            # Skip batches with errors
            if batch.get("status") != "success":
                continue
                
            # Get basic batch info
            ideas_count = batch.get("ideas_count", 0)
            total_time = batch.get("total_time", 0)
            
            # Skip if time is zero
            if total_time <= 0:
                continue
                
            # Get API metrics
            api_metrics = batch.get("api_metrics", {})
            total_tokens = api_metrics.get("total_tokens", 0)
            payload_size = api_metrics.get("payload_size", 0) / 1024  # Convert to KB
            
            # Calculate rates
            payload_sizes.append(payload_size)
            if api_metrics.get("response_time", 0) > 0:
                tokens_per_second.append(total_tokens / api_metrics.get("response_time", 1))
            else:
                tokens_per_second.append(0)
                
            ideas_per_second.append(ideas_count / total_time)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot tokens per second
        ax1 = plt.gca()
        ax1.set_xlabel('Payload Size (KB)')
        ax1.set_ylabel('Tokens per Second', color='blue')
        line1 = ax1.scatter(payload_sizes, tokens_per_second, color='blue', alpha=0.7, label='Tokens/Second')
        ax1.tick_params(axis='y', labelcolor='blue')
        
        # Add trend line
        if payload_sizes and tokens_per_second:
            z = np.polyfit(payload_sizes, tokens_per_second, 2)  # Quadratic fit
            p = np.poly1d(z)
            x_range = np.linspace(min(payload_sizes), max(payload_sizes), 100)
            ax1.plot(x_range, p(x_range), "b--", alpha=0.7)
            
            # Find the maximum value of the fitted curve
            max_x = x_range[np.argmax(p(x_range))]
            max_y = p(max_x)
            ax1.axvline(x=max_x, color='blue', linestyle='--', alpha=0.5)
            ax1.text(
                max_x, 
                max_y * 0.9, 
                f'Optimal: {max_x:.1f} KB', 
                color='blue', 
                horizontalalignment='center'
            )
        
        # Create second y-axis for ideas per second
        ax2 = ax1.twinx()
        ax2.set_ylabel('Ideas per Second', color='red')
        line2 = ax2.scatter(payload_sizes, ideas_per_second, color='red', alpha=0.7, label='Ideas/Second')
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Add combined legend
        lines = [line1, line2]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        plt.title('Efficiency vs Batch Size')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add config information
        config = self.metrics.get("config", {})
        config_text = (
            f"Model: {config.get('model', 'Unknown')}, "
            f"Batch Size: {config.get('batch_size', 'Unknown')}, "
            f"Mode: {config.get('processing_mode', 'Unknown')}"
        )
        plt.figtext(0.5, 0.01, config_text, ha='center', fontsize=10)
        
        # Save figure
        output_file = self.generate_filename("optimal_batch_size")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created optimal batch size visualization: {output_file}")
        return output_file
    
    def generate_summary_report(self):
        """Generate a text summary report of the performance metrics."""
        report = []
        
        # Add header
        report.append("=" * 80)
        report.append("PERFORMANCE METRICS SUMMARY REPORT")
        report.append("=" * 80)
        
        # Add configuration
        config = self.metrics.get("config", {})
        report.append("\nCONFIGURATION:")
        report.append(f"  Model: {config.get('model', 'Unknown')}")
        report.append(f"  Batch Size: {config.get('batch_size', 'Unknown')}")
        report.append(f"  Processing Mode: {config.get('processing_mode', 'Unknown')}")
        report.append(f"  Max Workers: {config.get('max_workers', 'Unknown')}")
        report.append(f"  Input File: {config.get('input_file', 'Unknown')}")
        report.append(f"  Output File: {config.get('output_file', 'Unknown')}")
        
        # Add runtime information
        runtime = self.metrics.get("runtime", {})
        report.append("\nRUNTIME:")
        report.append(f"  Total Runtime: {runtime.get('formatted', 'Unknown')}")
        
        # Add breakdown
        breakdown = runtime.get("breakdown", {})
        report.append("\nRUNTIME BREAKDOWN:")
        for key, data in breakdown.items():
            # Skip if time is very small
            if data.get("seconds", 0) < 0.1:
                continue
                
            report.append(f"  {key.capitalize()}: {data.get('formatted', 'Unknown')} ({data.get('percentage', 0):.1f}%)")
        
        # Add results
        results = self.metrics.get("results", {})
        report.append("\nRESULTS:")
        report.append(f"  Total Ideas: {results.get('total_ideas', 'Unknown')}")
        report.append(f"  Processed Ideas: {results.get('processed_ideas', 'Unknown')}")
        report.append(f"  Success Rate: {results.get('success_rate', 0):.1f}%")
        
        # Add API metrics
        api = self.metrics.get("api", {})
        report.append("\nAPI METRICS:")
        report.append(f"  Total API Time: {api.get('total_time', 0):.2f} seconds")
        report.append(f"  Total Tokens: {api.get('total_tokens', 0)}")
        report.append(f"  Input Tokens: {api.get('total_prompt_tokens', 0)}")
        report.append(f"  Output Tokens: {api.get('total_completion_tokens', 0)}")
        report.append(f"  Average Tokens/Second: {api.get('avg_tokens_per_second', 0):.2f}")
        
        # Add request statistics
        report.append("\nREQUEST STATISTICS:")
        report.append(f"  Successful Requests: {api.get('successful_requests', 0)}")
        report.append(f"  Failed Requests: {api.get('failed_requests', 0)}")
        if api.get('successful_requests', 0) > 0:
            report.append(f"  Average Response Time: {api.get('avg_response_time', 0):.2f} seconds")
            report.append(f"  Average Tokens per Request: {api.get('avg_tokens', 0):.2f}")
            report.append(f"  Average Payload Size: {api.get('avg_payload_size', 0) / 1024:.2f} KB")
        
        # Add recommendations
        report.append("\nRECOMMENDATIONS:")
        
        # Check if batch size seems good
        batch_data = self.metrics.get("batch_timing", [])
        payload_sizes = [
            batch.get("api_metrics", {}).get("payload_size", 0) / 1024 
            for batch in batch_data 
            if batch.get("status") == "success"
        ]
        
        if payload_sizes:
            avg_payload = sum(payload_sizes) / len(payload_sizes)
            max_payload = max(payload_sizes)
            
            if avg_payload < 1:
                report.append("  [!] Batch size seems very small. Consider increasing batch size.")
            elif avg_payload > 50:
                report.append("  [!] Batch size seems very large. Consider decreasing batch size.")
            else:
                report.append("  [✓] Batch size seems reasonable.")
                
            if max_payload > 100:
                report.append("  [!] Some batches are very large. Check for outliers.")
        
        # Check if parallel processing is effective
        if config.get("processing_mode") == "Parallel" and config.get("max_workers", 0) > 1:
            if runtime.get("total_runtime", 0) > 0:
                api_percentage = (api.get("total_time", 0) / runtime.get("total_runtime", 1)) * 100
                if api_percentage > 90:
                    report.append("  [✓] Parallel processing is effective (API time dominates).")
                else:
                    report.append("  [!] Parallel processing may not be optimal. Consider tuning batch size or reducing max workers.")
        
        # Generate output file path
        output_file = self.generate_filename("summary_report", "txt")
        
        # Write report to file
        with open(output_file, 'w') as f:
            f.write("\n".join(report))
        
        print(f"Created summary report: {output_file}")
        return output_file, "\n".join(report)
        
    def run_all_visualizations(self):
        """Run all visualizations and generate a comprehensive report."""
        outputs = {}
        
        try:
            outputs["runtime_breakdown"] = self.visualize_runtime_breakdown()
        except Exception as e:
            print(f"Error generating runtime breakdown: {e}")
        
        try:
            outputs["batch_performance"] = self.visualize_batch_processing_times()
        except Exception as e:
            print(f"Error generating batch performance visualization: {e}")
        
        try:
            outputs["optimal_batch"] = self.visualize_optimal_batch_size()
        except Exception as e:
            print(f"Error generating optimal batch size visualization: {e}")
        
        try:
            outputs["summary_report"], report_text = self.generate_summary_report()
            print("\nSUMMARY REPORT:")
            print("-" * 80)
            print(report_text)
        except Exception as e:
            print(f"Error generating summary report: {e}")
        
        return outputs


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Visualize performance metrics from IdeaCategorizer')
    
    parser.add_argument('--metrics-file', type=str, required=True,
                        help='Path to the performance metrics JSON file')
    
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save visualization outputs')
    
    args = parser.parse_args()
    
    # Check if metrics file exists
    if not os.path.exists(args.metrics_file):
        print(f"Error: Metrics file not found: {args.metrics_file}")
        sys.exit(1)
    
    # Create visualizer and run all visualizations
    visualizer = MetricsVisualizer(args.metrics_file, args.output_dir)
    visualizer.run_all_visualizations()
    
    print("\nVisualization complete!")


if __name__ == "__main__":
    main()
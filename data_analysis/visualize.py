#!/usr/bin/env python
"""
Visualization tool for AI Thesis Analysis.

This script generates visualizations from existing analysis results.

Usage:
    python visualize.py --results-file path/to/analysis_results.json [--output-dir path/to/output]
"""

import argparse
import os
import sys
import json
from typing import Dict, Any

from config import OUTPUT_DIR
from src.utils import get_logger, FileHandler
from src.visualizers import VisualizationManager

logger = get_logger("visualize")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate visualizations from analysis results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--results-file", "-r", type=str, required=True,
        help="Path to analysis results JSON file")
    
    parser.add_argument("--output-dir", "-o", type=str, default=None,
        help="Directory to save visualizations (defaults to 'output/visualizations')")
    
    parser.add_argument("--format", "-f", type=str, default="png", choices=["png", "pdf", "svg"],
        help="Output format for visualizations")
    
    parser.add_argument("--component", "-c", type=str, default=None,
        choices=["demographics", "usage", "engagement", "categorization"],
        help="Specific component to visualize (defaults to all)")
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Set default output directory if not provided
    if args.output_dir is None:
        args.output_dir = os.path.join(OUTPUT_DIR, "visualizations")
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if results file exists
    if not os.path.exists(args.results_file):
        logger.error(f"Results file not found: {args.results_file}")
        return 1
    
    # Load results file
    try:
        file_handler = FileHandler()
        results = file_handler.load_json(args.results_file)
        logger.info(f"Loaded analysis results from {args.results_file}")
    except Exception as e:
        logger.error(f"Error loading results file: {str(e)}")
        return 1
    
    # Create visualization manager
    vis_manager = VisualizationManager(args.output_dir, args.format)
    
    # Generate visualizations
    if args.component:
        # Visualize specific component
        if args.component not in results:
            logger.error(f"Component '{args.component}' not found in results file")
            return 1
        
        logger.info(f"Generating visualizations for {args.component}...")
        vis_outputs = vis_manager.visualize_component(args.component, results[args.component])
        
        if not vis_outputs:
            logger.warning(f"No visualizations generated for {args.component}")
            return 1
            
        logger.info(f"Generated {len(vis_outputs)} visualizations for {args.component}")
        
    else:
        # Visualize all components
        logger.info("Generating visualizations for all components...")
        vis_outputs = vis_manager.visualize_all(results)
        
        if not vis_outputs:
            logger.warning("No visualizations generated")
            return 1
            
        # Count total visualizations
        total_vis = sum(len(vis) for vis in vis_outputs.values())
        logger.info(f"Generated {total_vis} visualizations across {len(vis_outputs)} components")
    
    logger.info(f"Visualizations saved to {args.output_dir}")
    logger.info("HTML report generated at: visualizations/visualization_report/visualization_report.html")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
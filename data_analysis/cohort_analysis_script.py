#!/usr/bin/env python
"""
Cohort Analysis Script for AI Thesis

This script performs cohort analysis as part of the AI thesis research,
analyzing how different cohorts use the Orbit tool.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

from config import (
    USER_DATA_FILE, IDEA_DATA_FILE, STEP_DATA_FILE, 
    OUTPUT_DIR
)
from src.loaders import DataLoader
from src.processors.cohort_analyzer import CohortAnalyzer
from src.visualizers.cohort_visualizer import CohortVisualizer
from src.utils import get_logger, FileHandler, DataFilter

logger = get_logger("cohort_analysis")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Perform cohort analysis for AI thesis research",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input data options
    parser.add_argument(
        "--user-file",
        type=str,
        default=USER_DATA_FILE,
        help="Path to user data file"
    )
    parser.add_argument(
        "--idea-file",
        type=str,
        default=IDEA_DATA_FILE,
        help="Path to idea data file"
    )
    parser.add_argument(
        "--step-file",
        type=str,
        default=STEP_DATA_FILE,
        help="Path to step data file"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(OUTPUT_DIR, "cohort_analysis"),
        help="Directory to save output files"
    )

    # Data filter options
    parser.add_argument(
        "--course",
        type=str,
        default="15.390",
        help="Filter analysis to users enrolled in this course"
    )
    
    # Additional options
    parser.add_argument(
        "--visualize-only",
        action="store_true",
        help="Only generate visualizations from existing analysis results"
    )
    parser.add_argument(
        "--results-file",
        type=str,
        default=None,
        help="Path to existing analysis results file (for --visualize-only)"
    )
    
    return parser.parse_args()


def run_cohort_analysis(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the cohort analysis.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Analysis results
    """
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create file handler
    file_handler = FileHandler()
    
    # If visualize-only mode, load existing results
    if args.visualize_only:
        if not args.results_file or not os.path.exists(args.results_file):
            logger.error("Results file is required for visualize-only mode")
            return {}
        
        logger.info(f"Loading existing analysis results from {args.results_file}")
        try:
            results = file_handler.load_json(args.results_file)
            return results
        except Exception as e:
            logger.error(f"Error loading results file: {str(e)}")
            return {}
    
    # Otherwise, run the full analysis
    logger.info("Loading and processing data...")
    
    # Load data
    data_loader = DataLoader(args.user_file, args.idea_file, args.step_file)
    users, ideas, steps = data_loader.load_and_process_all()
    
    # If data filters are present, filter data appropriately
    if args.course:
        logger.info(f"Filtering users enrolled in course {args.course}...")
        users, ideas, steps = DataFilter.filter_by_course(users, ideas, steps, args.course)
        logger.info(f"Filtered to {len(users)} users, {len(ideas)} ideas, and {len(steps)} steps")

    
    # Run cohort analysis
    logger.info("Running cohort analysis...")
    cohort_analyzer = CohortAnalyzer(users, ideas, steps)
    results = cohort_analyzer.analyze()
    
    # Save results
    results_file = os.path.join(args.output_dir, "cohort_analysis_results.json")
    file_handler.save_json(results, results_file)
    logger.info(f"Saved analysis results to {results_file}")
    
    return results


def generate_visualizations(results: Dict[str, Any], output_dir: str) -> None:
    """
    Generate visualizations from analysis results.
    
    Args:
        results: Analysis results
        output_dir: Output directory
    """
    if not results:
        logger.error("No analysis results to visualize")
        return
    
    # Create visualizer
    visualizer = CohortVisualizer(output_dir)
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    vis_outputs = visualizer.visualize(results)
    
    if vis_outputs:
        logger.info(f"Generated {len(vis_outputs)} visualizations")
        for name, path in vis_outputs.items():
            logger.info(f"  - {name}: {path}")
    else:
        logger.warning("No visualizations were generated")


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    try:
        # Run analysis
        results = run_cohort_analysis(args)
        
        # Generate visualizations
        generate_visualizations(results, args.output_dir)
        
        logger.info("Cohort analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during cohort analysis: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
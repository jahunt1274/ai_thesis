#!/usr/bin/env python
"""
Course Evaluation Analysis Script for AI Thesis

This script performs focused analysis on course evaluation data as part of the 
AI thesis research, examining the impact of different Jetpack tool versions on 
course evaluations.
"""

import os
import sys
import argparse
from typing import Dict, Any

from config import COURSE_EVAL_DIR, COURSE_EVAL_RESULTS_DIR, OUTPUT_DIR
from src.loaders.course_eval_loader import CourseEvaluationLoader
from src.processors.course_eval_analyzer import CourseEvaluationAnalyzer
from src.visualizers.course_eval_visualizer import CourseEvaluationVisualizer
from src.utils import get_logger, FileHandler

logger = get_logger("course_eval_analysis")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze course evaluation data for AI thesis research",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input options
    parser.add_argument(
        "--eval-dir",
        type=str,
        default=COURSE_EVAL_DIR,
        help="Directory containing course evaluation JSON files"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default=COURSE_EVAL_RESULTS_DIR,
        help="Directory to save output files"
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


def run_evaluation_analysis(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the course evaluation analysis.
    
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
    logger.info("Loading and processing course evaluation data...")
    
    # Load evaluations
    course_eval_loader = CourseEvaluationLoader(args.eval_dir)
    # course_eval_loader.load_all()
    evaluations = course_eval_loader.process()
    
    if not evaluations:
        logger.error("No valid course evaluation data found")
        return {}
    
    # Run analysis
    logger.info("Running course evaluation analysis...")
    course_eval_analyzer = CourseEvaluationAnalyzer(evaluations)
    results = course_eval_analyzer.analyze()
    
    # Save results
    results_file = os.path.join(args.output_dir, "course_evaluation_results.json")
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
    visualizer = CourseEvaluationVisualizer(output_dir)
    
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
        results = run_evaluation_analysis(args)
        
        # Generate visualizations
        generate_visualizations(results, args.output_dir)
        
        logger.info("Course evaluation analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during course evaluation analysis: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
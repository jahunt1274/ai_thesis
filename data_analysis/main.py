#!/usr/bin/env python
"""
AI Thesis Analysis System

This script provides the main command-line interface for the AI thesis analysis system.
"""

import argparse
import os
import sys
from typing import Dict, Any

from config import (
    USER_DATA_FILE,
    IDEA_DATA_FILE,
    STEP_DATA_FILE,
    CATEGORIZED_IDEA_FILE,
    COURSE_EVAL_DIR,
    OUTPUT_DIR,
    COMBINED_RESULTS_DIR,
)
from src.analyzer import Analyzer
from src.utils import get_logger, FileHandler

logger = get_logger("main")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Thesis Analysis System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input data options
    parser.add_argument(
        "--user-file", type=str, default=USER_DATA_FILE, help="Path to user data file"
    )
    parser.add_argument(
        "--idea-file", type=str, default=IDEA_DATA_FILE, help="Path to idea data file"
    )
    parser.add_argument(
        "--step-file", type=str, default=STEP_DATA_FILE, help="Path to step data file"
    )
    parser.add_argument(
        "--categorized-file",
        type=str,
        default=CATEGORIZED_IDEA_FILE,
        help="Path to pre-categorized ideas JSON file",
    )
    parser.add_argument(
        "--eval-dir",
        type=str,
        default=COURSE_EVAL_DIR,
        help="Directory containing course evaluation files",
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIR,
        help="Directory to save output files",
    )

    # Analysis options
    parser.add_argument(
        "--analyze-evaluations",
        action="store_true",
        help="Run course evaluation analysis",
    )

    # Data filtering options
    parser.add_argument(
        "--filter-course",
        type=str,
        default=None,
        help="Filter analysis to users enrolled in this course",
    )
    parser.add_argument(
        "--filter-user-type",
        type=str,
        default=None,
        help="Filter analysis to users of this type",
    )
    parser.add_argument(
        "--filter-activity",
        action="store_true",
        help="Filter out inactive users (no ideas or steps)",
    )
    parser.add_argument(
        "--filter-date-range",
        type=str,
        nargs=2,
        metavar=("START_DATE", "END_DATE"),
        help="Filter data by date range (YYYY-MM-DD format)",
    )

    # Visualization options
    parser.add_argument(
        "--visualize-only",
        action="store_true",
        help="Only generate visualizations from existing analysis results",
    )
    parser.add_argument(
        "--results-file",
        type=str,
        default=None,
        help="Path to existing analysis results file (for --visualize-only)",
    )

    # Selective analysis options (mutually exclusive)
    analysis_group = parser.add_mutually_exclusive_group()
    analysis_group.add_argument(
        "--run-all", action="store_true", help="Run all analysis types (default)"
    )
    analysis_group.add_argument(
        "--user-only", action="store_true", help="Run only user analysis"
    )
    analysis_group.add_argument(
        "--activity-only", action="store_true", help="Run only activity analysis"
    )
    analysis_group.add_argument(
        "--idea-only", action="store_true", help="Run only idea analysis"
    )
    analysis_group.add_argument(
        "--evaluations-only",
        action="store_true",
        help="Run only course evaluation analysis",
    )

    return parser.parse_args()

def get_selected_analyses(args: argparse.Namespace) -> Dict[str, bool]:
    """
    Determine which analyses to run based on command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        Dictionary mapping analysis types to boolean flags
    """
    # Check for selective options
    if args.user_only:
        return {"user": True}
    elif args.activity_only:
        return {"activity": True}
    elif args.idea_only:
        return {"idea": True}
    elif args.evaluations_only:
        return {"course_eval": True}

    # Default: run standard analyses plus any additionally requested ones
    analyses = {
        "user": True,
        "activity": True,
        "idea": True,
        "course_eval": args.analyze_evaluations,
    }

    return analyses


def prepare_filter_params(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Prepare filter parameters from command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        Dictionary of filter parameters
    """
    filter_params = {}

    if args.filter_course:
        filter_params["course"] = args.filter_course

    if args.filter_user_type:
        filter_params["user_type"] = args.filter_user_type

    if args.filter_activity:
        filter_params["activity"] = True
        filter_params["min_ideas"] = 1
        filter_params["min_steps"] = 0

    if args.filter_date_range:
        filter_params["date_range"] = args.filter_date_range

    return filter_params

def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    # Validate input files based on the analyses to be run
    selected_analyses = get_selected_analyses(args)
    file_handler = FileHandler()

    # Validate input files
    for file_path in [
        args.user_file,
        args.idea_file,
        args.step_file,
        args.categorized_file,
    ]:
        file_handler.ensure_file_exists(file_path)

    # Check evaluation directory if evaluation analysis is requested
    file_handler.ensure_directory_exists(args.eval_dir)

    # Visualize-only mode - find latest results file if none specified
    if args.visualize_only and not args.results_file:
        latest_file = file_handler.get_latest_file(
            COMBINED_RESULTS_DIR, pattern="analysis_results_combined_*.json"
        )

        if latest_file:
            args.results_file = latest_file
            logger.info(f"Using latest results file: {latest_file}")
        else:
            latest_file = os.path.join(
                COMBINED_RESULTS_DIR, "analysis_results_combined_latest.json"
            )

            if os.path.exists(latest_file):
                args.results_file = latest_file
                logger.info(f"Using latest results file: {latest_file}")
            else:
                logger.error("No results file found for visualization-only mode")
                return 1

    try:
        # Initialize and run the analyzer
        analyzer = Analyzer(
            user_file=args.user_file,
            idea_file=args.idea_file,
            step_file=args.step_file,
            categorized_ideas_file=args.categorized_file,
            output_dir=args.output_dir,
            eval_dir=args.eval_dir,
            analyze_evaluations=args.analyze_evaluations,
        )

        # Run analysis based on mode
        if args.visualize_only:
            # Visualization-only mode
            results = analyzer.run_from_results(args.results_file)
        else:
            # Apply filters if specified
            filter_params = prepare_filter_params(args)
            if filter_params:
                # Load data first
                analyzer.data_loader.load_and_process_all()
                # Apply filters
                analyzer.apply_filters(filter_params)

            # Run either selective or full analysis
            if any(
                option
                for option in [
                    args.user_only,
                    args.activity_only,
                    args.idea_only,
                    args.evaluations_only,
                ]
            ):
                # Selective analysis
                results = analyzer.selective_run(selected_analyses)
            else:
                # Full analysis
                results = analyzer.run()

        logger.info("Analysis completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

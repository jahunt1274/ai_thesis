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
    USER_DATA_FILE, IDEA_DATA_FILE, STEP_DATA_FILE, 
    OUTPUT_DIR, DEFAULT_MODEL, OPENAI_API_KEY
)
from src.analyzer import Analyzer
from src.utils import get_logger

logger = get_logger("main")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Thesis Analysis System",
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
        default=OUTPUT_DIR,
        help="Directory to save output files"
    )
    
    # Analysis options
    parser.add_argument(
        "--categorize-ideas",
        action="store_true",
        help="Run idea categorization using OpenAI API"
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        default=OPENAI_API_KEY,
        help="OpenAI API key for idea categorization"
    )
    parser.add_argument(
        "--openai-model",
        type=str,
        default=DEFAULT_MODEL,
        help="OpenAI model to use for idea categorization"
    )
    parser.add_argument(
        '--categorized-file',
        type=str,
        default=None,
        help='Path to pre-categorized ideas JSON file'
    )
    
    # Selective analysis options
    parser.add_argument(
        "--demographic-only",
        action="store_true",
        help="Run only demographic analysis"
    )
    parser.add_argument(
        "--usage-only",
        action="store_true",
        help="Run only usage analysis"
    )
    parser.add_argument(
        "--engagement-only",
        action="store_true",
        help="Run only engagement analysis"
    )
    parser.add_argument(
        "--categorization-only",
        action="store_true",
        help="Run only categorization analysis"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Validate input files
    for file_path, file_name in [
        (args.user_file, "user data"),
        (args.idea_file, "idea data"),
        (args.step_file, "step data")
    ]:
        if not os.path.exists(file_path):
            logger.error(f"Input {file_name} file not found: {file_path}")
            return 1
    
    # Check OpenAI API key if categorization is requested
    if args.categorize_ideas and not args.openai_key:
        logger.error("OpenAI API key is required for idea categorization")
        return 1
    
    # Check categorized file if provided
    if args.categorized_file and not os.path.exists(args.categorized_file):
        logger.error(f"Categorized ideas file not found: {args.categorized_file}")
        return 1
    
    try:
        # Initialize and run the analyzer
        analyzer = Analyzer(
            user_file=args.user_file,
            idea_file=args.idea_file,
            step_file=args.step_file,
            output_dir=args.output_dir,
            categorize_ideas=args.categorize_ideas,
            openai_api_key=args.openai_key,
            openai_model=args.openai_model,
            categorized_ideas_file=args.categorized_file
        )

        # Run only selected analyses if specified
        if args.demographic_only or args.usage_only or args.engagement_only or args.categorization_only:
            logger.info("Running selected analyses only")
            # Currently not implemented - would need to modify the Analyzer to support partial runs
            pass
        
        # Run the analyzer
        results = analyzer.run()
        
        logger.info("Analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
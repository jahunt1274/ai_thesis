#!/usr/bin/env python
"""
Team Analysis Example Script

This script demonstrates how to build team relationship data and perform team analysis
using the AI thesis analysis system. It shows how to:
1. Build relationship mapping files
2. Load relationship data
3. Run team analysis
4. Generate team visualizations

Usage:
    python team_analysis_example.py
"""

import os
import sys
import subprocess
from typing import Dict, Any

from config import (
    USER_DATA_FILE,
    IDEA_DATA_FILE,
    STEP_DATA_FILE,
    RELATIONSHIP_DIR,
    OUTPUT_DIR,
    DE_TEAMS_DIR,
    VISUALIZATION_OUTPUT_DIR,
)
from src.loaders import DataLoader
from src.loaders.relationship_loader import RelationshipLoader
from src.processors import ProcessorFactory
from src.visualizers import VisualizationManager
from src.utils import get_logger, FileHandler

logger = get_logger("team_analysis_example")
file_handler = FileHandler()


def build_relationship_data(student_file: str, team_file: str) -> bool:
    """
    Build relationship data using the build_relationships.py script.

    Args:
        student_file: Path to student data JSON file
        team_file: Path to team data JSON file

    Returns:
        True if successful, False otherwise
    """
    logger.info("Building relationship data...")

    try:
        # Construct command
        cmd = [
            "python",
            "data_analysis/build_relationships.py",
            "--student-file",
            student_file,
            "--team-file",
            team_file,
            "--output-dir",
            RELATIONSHIP_DIR,
            "--add-tool-versions",
        ]

        # Execute command
        logger.info(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Log results
        logger.info(f"Command output: {result.stdout}")

        if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing build_relationships.py: {e}")
        logger.error(f"Command stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error building relationship data: {e}")
        return False


def run_team_analysis() -> Dict[str, Any]:
    """
    Run team analysis using the AI thesis analysis system.

    Returns:
        Dictionary of analysis results
    """
    logger.info("Running team analysis...")

    try:
        # Load data
        data_loader = DataLoader(
            user_file=USER_DATA_FILE, idea_file=IDEA_DATA_FILE, step_file=STEP_DATA_FILE
        )
        users, ideas, steps, evaluations = data_loader.load_and_process_all()

        # Load relationship data
        relationship_loader = RelationshipLoader()
        relationships = relationship_loader.load_all()

        # Check if relationship data was loaded
        if not relationships:
            logger.error("No relationship data loaded")
            return {}

        # Create processor factory
        factory = ProcessorFactory()

        # Prepare data dictionary for processors
        data = {
            "users": users,
            "ideas": ideas,
            "steps": steps,
            "evaluations": evaluations,
        }

        # Run team analysis
        logger.info("Running team analyzer...")
        team_results = factory.run_analyzer(
            "team", data, relationship_loader=relationship_loader
        )

        # Save results
        results_file = os.path.join(OUTPUT_DIR, "team_analysis_results.json")
        file_handler.save_json(team_results, results_file)
        logger.info(f"Saved team analysis results to {results_file}")

        return team_results

    except Exception as e:
        logger.error(f"Error running team analysis: {e}")
        return {}


def generate_team_visualizations(team_results: Dict[str, Any]) -> bool:
    """
    Generate team visualizations from analysis results.

    Args:
        team_results: Team analysis results

    Returns:
        True if successful, False otherwise
    """
    logger.info("Generating team visualizations...")

    try:
        # Create visualization manager
        vis_manager = VisualizationManager(VISUALIZATION_OUTPUT_DIR)

        # Generate visualizations
        vis_outputs = vis_manager.visualize_component("team_analysis", team_results)

        if not vis_outputs:
            logger.warning("No visualizations generated")
            return False

        # Count total visualizations
        total_vis = len(vis_outputs)
        logger.info(f"Generated {total_vis} team visualizations")

        return True

    except Exception as e:
        logger.error(f"Error generating team visualizations: {e}")
        return False


def main() -> int:
    """Main entry point."""
    try:
        # Define paths to student and team data files
        student_file = os.path.join(DE_TEAMS_DIR, "de_users.json")
        student_file = os.path.join(DE_TEAMS_DIR, "de_user_teams_new.json")
        team_file = os.path.join(DE_TEAMS_DIR, "de_team_names.json")

        # Check if files exist
        if not os.path.exists(student_file):
            logger.error(f"Student file not found: {student_file}")
            logger.info("Please provide a valid path to student data JSON file")
            return 1

        if not os.path.exists(team_file):
            logger.error(f"Team file not found: {team_file}")
            logger.info("Please provide a valid path to team data JSON file")
            return 1

        # Step 1: Build relationship data
        logger.info("Step 1: Building relationship data...")
        if not build_relationship_data(student_file, team_file):
            logger.error("Failed to build relationship data")
            return 1

        # Step 2: Run team analysis
        logger.info("Step 2: Running team analysis...")
        team_results = run_team_analysis()
        if not team_results:
            logger.error("Failed to run team analysis")
            return 1

        # Step 3: Generate team visualizations
        logger.info("Step 3: Generating team visualizations...")
        if not generate_team_visualizations(team_results):
            logger.error("Failed to generate team visualizations")
            return 1

        logger.info("Team analysis completed successfully!")
        logger.info(f"Visualizations saved to: {VISUALIZATION_OUTPUT_DIR}/team")

        return 0

    except Exception as e:
        logger.error(f"Unhandled error in main: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

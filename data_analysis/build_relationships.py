#!/usr/bin/env python
"""
Relationship Builder for MIT SDM Thesis Analysis

This script builds relationship mapping files between teams, students, sections,
and semesters for use in the data analysis service. It reads student and team data
and produces JSON files that represent the relationships between entities.

Usage:
    python build_relationships.py --student-file path/to/students.json --team-file path/to/teams.json --output-dir path/to/output

The script will create the following files in the output directory:
- team_student_map.json: Maps team IDs to lists of student emails
- section_team_map.json: Maps section identifiers to lists of team IDs
- term_section_map.json: Maps term/year to section information
- team_metadata.json: Contains additional metadata about teams
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Any, Optional

from config import DATA_DIR, OUTPUT_DIR


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build relationship mapping files for thesis analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input files
    parser.add_argument(
        "--student-file", type=str, required=True, help="Path to student data JSON file"
    )
    parser.add_argument(
        "--team-file", type=str, required=True, help="Path to team data JSON file"
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/relationships",
        help="Directory to save relationship files",
    )

    # Tool version mappings
    parser.add_argument(
        "--add-tool-versions",
        action="store_true",
        help="Add tool version mappings to the semester data",
    )

    return parser.parse_args()


def load_json_file(file_path: str) -> Any:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Loaded JSON data

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Successfully loaded data from {file_path}")
        return data

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {str(e)}")
        raise
    except Exception as e:
        print(f"Error loading data from {file_path}: {str(e)}")
        raise


def save_json_file(data: Any, file_path: str) -> bool:
    """
    Save data to a JSON file.

    Args:
        data: Data to save
        file_path: Path to save the file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved data to {file_path}")
        return True

    except Exception as e:
        print(f"Error saving data to {file_path}: {str(e)}")
        return False


def build_team_student_map(students: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Build a mapping from team IDs to student emails.

    Args:
        students: List of student records

    Returns:
        Dictionary mapping team IDs to lists of student emails
    """
    team_student_map = defaultdict(list)

    for student in students:
        # if not student:
            # print("No Student")
            # continue
        team_id = student.get("team_number", 0)
        email = student.get("email")

        if email and team_id != 0:  # Skip students with no team
            team_student_map[str(team_id)].append(email)

    # Convert defaultdict to regular dict
    return dict(team_student_map)


def build_section_team_map(
    students: List[Dict[str, Any]], teams: List[Dict[str, Any]]
) -> Dict[str, List[int]]:
    """
    Build a mapping from section identifiers to team IDs.

    Args:
        students: List of student records
        teams: List of team records

    Returns:
        Dictionary mapping section identifiers to lists of team IDs
    """
    section_team_map = defaultdict(set)

    # Create mapping of team_id to team_info
    team_info = {team.get("team_id"): team for team in teams}

    # Create a mapping of team_id to sections (a team could span multiple sections)
    team_sections = defaultdict(set)

    for student in students:
        team_id = student.get("team_number", 0)
        section = student.get("section")
        term = student.get("term")
        year = student.get("year")

        if team_id != 0 and section and term and year:
            # Create a section identifier (Term_Year_Section)
            section_id = f"{term}_{year}_{section}"

            # Add the section for this team
            team_sections[team_id].add(section_id)

    # Now populate the section_team_map
    for team_id, sections in team_sections.items():
        for section_id in sections:
            section_team_map[section_id].add(team_id)

    # Convert sets to lists and defaultdict to regular dict
    return {
        section_id: list(team_ids) for section_id, team_ids in section_team_map.items()
    }


def build_term_section_map(students: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Build a mapping from term/year to section information.

    Args:
        students: List of student records

    Returns:
        Dictionary mapping term/year to section information
    """
    term_section_map = {}

    # Collect all sections by term/year
    term_sections = defaultdict(set)
    section_students = defaultdict(set)

    for student in students:
        term = student.get("term")
        year = student.get("year")
        section = student.get("section")
        email = student.get("email")

        if term and year and section and email:
            term_key = f"{term}_{year}"
            section_key = f"{term}_{year}_{section}"

            term_sections[term_key].add(section)
            section_students[section_key].add(email)

    # Create the term/section map with metadata
    for term_key, sections in term_sections.items():
        term_parts = term_key.split("_")
        term = term_parts[0]
        year = int(term_parts[1]) if len(term_parts) > 1 else None

        # Add term entry with sections
        term_section_map[term_key] = {
            "term": term,
            "year": year,
            "sections": sorted(list(sections)),
            "student_count": sum(
                len(section_students.get(f"{term_key}_{section}", []))
                for section in sections
            ),
            "section_details": {
                section: {
                    "student_count": len(
                        section_students.get(f"{term_key}_{section}", [])
                    )
                }
                for section in sections
            },
        }

    return term_section_map


def build_team_metadata(
    teams: List[Dict[str, Any]], team_student_map: Dict[str, List[str]]
) -> Dict[str, Dict[str, Any]]:
    """
    Build a metadata file with additional information about teams.

    Args:
        teams: List of team records
        team_student_map: Mapping of team IDs to student emails

    Returns:
        Dictionary with team metadata
    """
    team_metadata = {}

    for team in teams:
        team_id = str(team.get("team_id"))
        if not team_id:
            continue

        # Get actual member count from the team_student_map
        actual_member_count = len(team_student_map.get(team_id, []))

        team_metadata[team_id] = {
            "name": team.get("team_name"),
            "term": team.get("term"),
            "year": team.get("year"),
            "listed_member_count": team.get("listed_member_count", 0),
            "actual_member_count": actual_member_count,
            "discrepancy": team.get("listed_member_count", 0) - actual_member_count,
        }

    return team_metadata


def add_tool_versions(
    term_section_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Add tool version information to the term/section map.

    Args:
        term_section_map: Mapping of term/year to section information

    Returns:
        Updated term/section map with tool versions
    """
    # Define which semesters used which tool versions
    tool_versions = {
        "Fall_2023": None,  # Control group, no tool
        "Spring_2024": "v1",  # Jetpack v1
        "Fall_2024": "v2",  # Jetpack v2
        "Spring_2025": "v2",  # Jetpack v2
    }

    # Update the term_section_map with tool versions
    for term_key, term_data in term_section_map.items():
        term_data["tool_version"] = tool_versions.get(term_key)

    return term_section_map


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    try:
        # Load input data
        students = load_json_file(args.student_file)
        teams = load_json_file(args.team_file)

        # Validate that the data is in the expected format
        if not isinstance(students, list) or not isinstance(teams, list):
            print("Error: Input files must contain JSON arrays")
            return 1

        # Build relationship maps
        team_student_map = build_team_student_map(students)
        section_team_map = build_section_team_map(students, teams)
        term_section_map = build_term_section_map(students)
        team_metadata = build_team_metadata(teams, team_student_map)

        # Add tool versions if requested
        if args.add_tool_versions:
            term_section_map = add_tool_versions(term_section_map)

        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)

        # Save relationship maps
        save_json_file(
            {"team_student_map": team_student_map},
            os.path.join(args.output_dir, "team_student_map.json"),
        )

        save_json_file(
            {"section_team_map": section_team_map},
            os.path.join(args.output_dir, "section_team_map.json"),
        )

        save_json_file(
            {"term_section_map": term_section_map},
            os.path.join(args.output_dir, "term_section_map.json"),
        )

        save_json_file(
            {"team_metadata": team_metadata},
            os.path.join(args.output_dir, "team_metadata.json"),
        )

        print("Successfully built relationship mapping files")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

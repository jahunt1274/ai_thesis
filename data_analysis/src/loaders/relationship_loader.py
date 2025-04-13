"""
Relationship data loader for the AI thesis analysis.
"""

import os
from typing import Dict, List, Any, Optional

from config import RELATIONSHIP_DIR
from src.utils import get_logger, FileHandler


class RelationshipLoader:
    """Loads and processes relationship mapping data."""

    def __init__(self, relationship_dir: str = RELATIONSHIP_DIR):
        """
        Initialize the relationship loader.

        Args:
            relationship_dir: Directory containing relationship mapping files
        """
        self.relationship_dir = relationship_dir
        self.file_handler = FileHandler()
        self.team_student_map = {}
        self.section_team_map = {}
        self.term_section_map = {}
        self.team_metadata = {}
        self.logger = get_logger(self.__class__.__name__.lower())

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all relationship mapping files.

        Returns:
            Dictionary containing all relationship maps
        """
        self.logger.info(f"Loading relationship mapping files from {self.relationship_dir}")

        # Define files to load
        relationship_files = [
            "team_student_map.json",
            "section_team_map.json",
            "term_section_map.json",
            "team_metadata.json"
        ]

        relationships = {}

        # Load each file
        for file_name in relationship_files:
            file_path = os.path.join(self.relationship_dir, file_name)
            
            try:
                if os.path.exists(file_path):
                    # Load file and extract the main data key
                    data = self.file_handler.load_json(file_path)
                    
                    # Extract the main key from the file (should be same as file name without extension)
                    key = file_name.split(".")[0]
                    if key in data:
                        relationships[key] = data[key]
                        self.logger.info(f"Loaded {key} from {file_name}")
                    else:
                        self.logger.warning(f"Key '{key}' not found in {file_name}")
                else:
                    self.logger.warning(f"Relationship file not found: {file_path}")
            
            except Exception as e:
                self.logger.error(f"Error loading {file_name}: {str(e)}")

        # Store maps in instance variables for easier access
        self.team_student_map = relationships.get("team_student_map", {})
        self.section_team_map = relationships.get("section_team_map", {})
        self.term_section_map = relationships.get("term_section_map", {})
        self.team_metadata = relationships.get("team_metadata", {})

        self.logger.info(f"Loaded {len(relationships)} relationship mapping files")
        return relationships

    def get_team_members(self, team_id: int) -> List[str]:
        """
        Get email addresses of team members for a given team ID.

        Args:
            team_id: Team ID

        Returns:
            List of student email addresses
        """
        return self.team_student_map.get(str(team_id), [])

    def get_teams_in_section(self, term: str, year: int, section: str) -> List[int]:
        """
        Get team IDs for a specific course section.

        Args:
            term: Academic term (e.g., "Fall", "Spring")
            year: Academic year
            section: Section identifier (e.g., "A", "B")

        Returns:
            List of team IDs
        """
        section_id = f"{term}_{year}_{section}"
        return self.section_team_map.get(section_id, [])

    def get_section_info(self, term: str, year: int) -> Dict[str, Any]:
        """
        Get information about sections for a specific term/year.

        Args:
            term: Academic term (e.g., "Fall", "Spring")
            year: Academic year

        Returns:
            Dictionary with section information
        """
        term_key = f"{term}_{year}"
        return self.term_section_map.get(term_key, {})
    
    def get_tool_version(self, term: str, year: int) -> Optional[str]:
        """
        Get the tool version used in a specific term/year.

        Args:
            term: Academic term (e.g., "Fall", "Spring")
            year: Academic year

        Returns:
            Tool version string or None if no tool was used
        """
        term_key = f"{term}_{year}"
        term_data = self.term_section_map.get(term_key, {})
        return term_data.get("tool_version")

    def get_team_metadata(self, team_id: int) -> Dict[str, Any]:
        """
        Get metadata for a specific team.

        Args:
            team_id: Team ID

        Returns:
            Dictionary with team metadata
        """
        return self.team_metadata.get(str(team_id), {})

    def get_students_by_term(self, term: str, year: int) -> List[str]:
        """
        Get all student emails for a specific term/year across all sections.

        Args:
            term: Academic term (e.g., "Fall", "Spring")
            year: Academic year

        Returns:
            List of student email addresses
        """
        term_key = f"{term}_{year}"
        term_data = self.term_section_map.get(term_key, {})
        
        # Get all sections for this term/year
        sections = term_data.get("sections", [])
        
        # Get all teams in these sections
        all_teams = []
        for section in sections:
            section_id = f"{term}_{year}_{section}"
            teams = self.section_team_map.get(section_id, [])
            all_teams.extend(teams)
        
        # Get all students in these teams
        all_students = []
        for team_id in all_teams:
            students = self.get_team_members(team_id)
            all_students.extend(students)
        
        # Remove duplicates and return
        return list(set(all_students))
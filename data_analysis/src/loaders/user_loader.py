"""
User data loader for the AI thesis analysis.
"""

from typing import Dict, List, Any, Optional

from config import USER_DATA_FILE
from src.utils import FileHandler, get_logger

logger = get_logger("user_loader")


class UserLoader:
    """Loads and processes user data."""
    
    def __init__(self, file_path: str = USER_DATA_FILE):
        """
        Initialize the user loader.
        
        Args:
            file_path: Path to the user data file
        """
        self.file_path = file_path
        self.file_handler = FileHandler()
        self.raw_users = None
        self.processed_users = None
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Load user data from the file.
        
        Returns:
            List of user records
        """
        logger.info(f"Loading user data from {self.file_path}")
        self.raw_users = self.file_handler.load_json(self.file_path)
        
        # Check data format
        if not isinstance(self.raw_users, list):
            raise ValueError("User data must be a list of objects")
        
        logger.info(f"Loaded {len(self.raw_users)} user records")
        return self.raw_users
    
    def process(self) -> List[Dict[str, Any]]:
        """
        Process raw user data into a standardized format.
        
        Returns:
            List of processed user records
        """
        if self.raw_users is None:
            self.load()
        
        logger.info("Processing user data")
        self.processed_users = []
        
        for user in self.raw_users:
            processed_user = self._process_user(user)
            if processed_user:
                self.processed_users.append(processed_user)
        
        logger.info(f"Processed {len(self.processed_users)} user records")
        return self.processed_users
    
    def _process_user(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single user record.
        
        Args:
            user: Raw user record
            
        Returns:
            Processed user record, or None if invalid
        """
        try:
            # Basic validation
            if not user:
                logger.warning("Empty user record")
                return None
            
            # Check for required fields
            for field in ['id', 'email']:
                if field not in user:
                    logger.warning(f"User missing required field: {field}")
                    return None
            
            # Extract identifier - can be in different formats
            user_id = user.get('id')
            if isinstance(user_id, dict) and '$oid' in user_id:
                user_id = user_id['$oid']
            
            # Extract timestamps with standardized format
            created_date = self._extract_timestamp(user.get('created'))
            last_login = self._extract_timestamp(user.get('last_login'))
            updated = self._extract_timestamp(user.get('updated'))
            
            # Extract affiliations
            affiliations = self._extract_affiliations(user)
            
            # Extract enrollments
            enrollments = self._extract_enrollments(user)
            
            # Standardize email (lowercase, strip)
            email = user.get('email', '').lower().strip()
            
            # Create processed user
            processed_user = {
                'id': user_id,
                'email': email,
                'created_date': created_date,
                'last_login': last_login,
                'updated': updated,
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'type': user.get('type'),
                'affiliations': affiliations,
                'enrollments': enrollments,
                'institution': self._extract_institution(user),
                'student_affiliation': self._extract_student_affiliation(user),
                'orbit_profile': self._extract_orbit_profile(user)
            }
            
            return processed_user
            
        except Exception as e:
            logger.error(f"Error processing user {user.get('id', 'unknown')}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_timestamp(timestamp: Any) -> Optional[str]:
        """Extract timestamp from various formats."""
        if not timestamp:
            return None
            
        if isinstance(timestamp, dict) and '$date' in timestamp:
            return timestamp['$date']
        
        return str(timestamp)
    
    @staticmethod
    def _extract_affiliations(user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract affiliations from user record."""
        if 'affiliations' not in user or not user['affiliations']:
            return []
            
        affiliations = []
        for affiliation in user['affiliations']:
            if not isinstance(affiliation, dict):
                continue
                
            processed_affiliation = {
                'type': affiliation.get('type'),
                'title': affiliation.get('title'),
                'departments': []
            }
            
            # Process departments
            if 'departments' in affiliation and affiliation['departments']:
                for dept in affiliation['departments']:
                    if isinstance(dept, dict):
                        processed_affiliation['departments'].append({
                            'code': dept.get('code'),
                            'name': dept.get('name')
                        })
            
            affiliations.append(processed_affiliation)
            
        return affiliations
    
    @staticmethod
    def _extract_enrollments(user: Dict[str, Any]) -> List[str]:
        """Extract enrollments from user record."""
        if 'enrollments' not in user or not user['enrollments']:
            return []
            
        return [str(enrollment) for enrollment in user['enrollments'] if enrollment]
    
    @staticmethod
    def _extract_institution(user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract institution information from user record."""
        if 'institution' not in user or not user['institution']:
            return None
            
        institution = user['institution']
        return {
            'name': institution.get('name'),
            'affiliation_type': (institution.get('affiliation', {}) or {}).get('type')
        }
    
    @staticmethod
    def _extract_student_affiliation(user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract student affiliation information from user record."""
        if 'student_affiliation' not in user or not user['student_affiliation']:
            return None
            
        affiliation = user['student_affiliation']
        if isinstance(affiliation, dict):
            return {
                'type': affiliation.get('type'),
                'class_year': affiliation.get('classYear'),
                'student_type': affiliation.get('student_type')
            }
        return None
    
    @staticmethod
    def _extract_orbit_profile(user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract Orbit profile information from user record."""
        if 'orbitProfile' not in user or not user['orbitProfile']:
            return None
            
        profile = user['orbitProfile']
        return {
            'experience': profile.get('experience'),
            'interests': profile.get('interest', []),
            'needs': profile.get('need', []),
            'persona': profile.get('persona', []),
            'has_image': profile.get('has_image', False)
        }
from typing import Dict, Any, List
from collections import defaultdict

class DemographicAnalyzer:
    def __init__(self, users_data: List[Dict[str, Any]]):
        self.users = users_data

    def analyze_affiliations(self) -> Dict[str, Any]:
        """Analyze user affiliations and distributions."""
        affiliations = defaultdict(int)
        for user in self.users:
            # Extract affiliation from user data
            if 'affiliations' in user:
                for affiliation in user['affiliations']:
                    aff_type = affiliation.get('type', 'unknown')
                    affiliations[aff_type] += 1
            elif 'type' in user:
                affiliations[user['type']] += 1

        return dict(affiliations)

    def analyze_cohorts(self) -> Dict[str, Any]:
        """Analyze user cohorts based on various criteria."""
        cohorts = {
            'by_creation_date': self._analyze_creation_cohorts(),
            'by_application': self._analyze_application_cohorts(),
            'by_department': self._analyze_department_cohorts()
        }
        return cohorts

    def _analyze_creation_cohorts(self) -> Dict[str, int]:
        """Group users by account creation date."""
        creation_cohorts = defaultdict(int)
        for user in self.users:
            if 'created' in user:
                created_date = user['created'].get('$date', '')[:7]  # Get YYYY-MM
                creation_cohorts[created_date] += 1
        return dict(creation_cohorts)

    def _analyze_application_cohorts(self) -> Dict[str, int]:
        """Group users by application participation."""
        app_cohorts = defaultdict(int)
        for user in self.users:
            if 'applications' in user:
                for app in user['applications']:
                    app_cohorts[app] += 1
        return dict(app_cohorts)

    def _analyze_department_cohorts(self) -> Dict[str, int]:
        """Group users by department affiliation."""
        dept_cohorts = defaultdict(int)
        for user in self.users:
            if 'affiliations' in user:
                for aff in user['affiliations']:
                    for dept in aff.get('departments', []):
                        dept_cohorts[dept.get('name', 'unknown')] += 1
        return dict(dept_cohorts)
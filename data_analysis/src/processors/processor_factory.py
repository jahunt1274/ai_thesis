"""
Factory for data analysis processors.
"""

from typing import Dict, List, Any, Optional

from src.processors.base_analyzer import BaseAnalyzer
from src.processors import (
    ActivityAnalyzer,
    CourseEvaluationAnalyzer,
    IdeaAnalyzer,
    UserAnalyzer,
)


class ProcessorFactory:
    """Factory for creating processor instances."""

    @staticmethod
    def create_analyzer(
        analyzer_type: str, data: Dict[str, List[Dict[str, Any]]], **kwargs
    ) -> Optional[BaseAnalyzer]:
        """
        Create appropriate analyzer based on analysis type.

        Args:
            analyzer_type: Type of analyzer to create ('user', 'activity', 'idea', 'course_eval')
            data: Dictionary of data to pass to the analyzer ('users', 'ideas', 'steps', 'evaluations')
            **kwargs: Additional keyword arguments to pass to the analyzer

        Returns:
            Initialized analyzer instance or None if type is not recognized
        """
        users = data.get("users", [])
        ideas = data.get("ideas", [])
        steps = data.get("steps", [])
        evaluations = data.get("evaluations", [])

        if analyzer_type == "user":
            return UserAnalyzer(users, ideas, steps, **kwargs)
        elif analyzer_type == "activity":
            return ActivityAnalyzer(users, ideas, steps, **kwargs)
        elif analyzer_type == "idea":
            return IdeaAnalyzer(ideas, **kwargs)
        elif analyzer_type == "course_eval":
            return CourseEvaluationAnalyzer(evaluations, **kwargs)
        else:
            return None

    @staticmethod
    def create_analyzers(
        analyzer_types: List[str], data: Dict[str, List[Dict[str, Any]]], **kwargs
    ) -> Dict[str, BaseAnalyzer]:
        """
        Create multiple analyzers at once.

        Args:
            analyzer_types: List of analyzer types to create
            data: Dictionary of data to pass to the analyzers
            **kwargs: Additional keyword arguments to pass to the analyzers

        Returns:
            Dictionary mapping analyzer types to initialized analyzer instances
        """
        analyzers = {}

        for analyzer_type in analyzer_types:
            analyzer = ProcessorFactory.create_analyzer(analyzer_type, data, **kwargs)
            if analyzer:
                analyzers[analyzer_type] = analyzer

        return analyzers

    @staticmethod
    def run_analyzer(
        analyzer_type: str, data: Dict[str, List[Dict[str, Any]]], **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Create and run an analyzer in a single step.

        Args:
            analyzer_type: Type of analyzer to create and run
            data: Dictionary of data to pass to the analyzer
            **kwargs: Additional keyword arguments to pass to the analyzer

        Returns:
            Analysis results or None if analyzer type is not recognized
        """
        analyzer = ProcessorFactory.create_analyzer(analyzer_type, data, **kwargs)

        if analyzer:
            return analyzer.analyze()

        return None

    @staticmethod
    def run_analyzers(
        analyzer_types: List[str], data: Dict[str, List[Dict[str, Any]]], **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create and run multiple analyzers in a single step.

        Args:
            analyzer_types: List of analyzer types to create and run
            data: Dictionary of data to pass to the analyzers
            **kwargs: Additional keyword arguments to pass to the analyzers

        Returns:
            Dictionary mapping analyzer types to analysis results
        """
        results = {}

        for analyzer_type in analyzer_types:
            result = ProcessorFactory.run_analyzer(analyzer_type, data, **kwargs)
            if result:
                results[analyzer_type] = result

        return results

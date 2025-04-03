"""
Idea analyzer for data analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional

from src.constants.data_constants import IDEA_DOMAIN_CATEGORIES
from src.processors.base_analyzer import BaseAnalyzer
from src.utils import get_logger, DataGroupingUtils, FileHandler, StatsUtils


class IdeaAnalyzer(BaseAnalyzer):
    """Analyzes idea categories, domains, and merges categorization data."""
    
    def __init__(self, ideas: List[Dict[str, Any]], categorized_ideas_file: Optional[str] = None):
        """
        Initialize the idea analyzer.
        
        Args:
            ideas: List of idea records to analyze
            categorized_ideas_file: Optional path to pre-categorized ideas JSON file
        """
        super().__init__("idea_analyzer")
        self.ideas = ideas
        self.categorized_ideas_file = categorized_ideas_file
        self.categorized_ideas = []
        self.file_handler = FileHandler()
        
        # Define domain mappings for category grouping
        self.domain_categories = IDEA_DOMAIN_CATEGORIES
    
    def preprocess(self) -> None:
        """Preprocess idea data including loading categorized ideas if available."""
        # Check if we need to load categorized ideas
        if self.categorized_ideas_file:
            self.logger.info(f"Loading pre-categorized ideas from {self.categorized_ideas_file}")
            self._load_and_merge_categories()
        
        # Filter ideas to only include those with categories
        self.categorized_ideas = [idea for idea in self.ideas if "category" in idea]
        self.logger.info(f"Found {len(self.categorized_ideas)} categorized ideas")
    
    def perform_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive idea analysis.
        
        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Performing idea analysis")
        
        # Skip analysis if no categorized ideas are available
        if not self.categorized_ideas:
            self.logger.warning("No categorized ideas available for analysis")
            return {
                "total_categorized": 0,
                "category_counts": {},
                "error": "No categorized ideas available"
            }
        
        results = {
            'total_categorized': len(self.categorized_ideas),
            'category_counts': self._analyze_category_counts(),
            'category_percentages': self._analyze_category_percentages(),
            'top_categories': self._find_top_categories(),
            'domain_grouping': self._group_categories_by_domain(),
            'trends': self._analyze_category_trends()
        }
        
        return results
    
    def _load_and_merge_categories(self) -> None:
        """Load categorized ideas from a file and merge with main idea dataset."""
        try:
            # Load categorized ideas
            categorized_ideas = self.file_handler.load_json(self.categorized_ideas_file)
            
            if not isinstance(categorized_ideas, list):
                self.logger.error("Categorized ideas file must contain a list of objects")
                return
            
            self.logger.info(f"Loaded {len(categorized_ideas)} pre-categorized ideas")
            
            # Create lookup map of categorized ideas by ID
            category_map = {}
            
            for cat_idea in categorized_ideas:
                # Extract ID from different possible formats
                idea_id = self._extract_id(cat_idea.get("_id"))
                category = cat_idea.get("category")
                
                if idea_id and category:
                    category_map[idea_id] = category
            
            self.logger.info(f"Found {len(category_map)} valid categorized ideas")
            
            # Merge categories into main idea dataset
            merged_count = 0
            
            for idea in self.ideas:
                # Extract ID from different possible formats
                idea_id = self._extract_id(idea.get("id"))
                
                # If a category exists for this ID, add it to the idea
                if idea_id in category_map:
                    idea["category"] = category_map[idea_id]
                    merged_count += 1
            
            self.logger.info(f"Merged categories into {merged_count} out of {len(self.ideas)} ideas")
            
        except Exception as e:
            self.logger.error(f"Error merging categories: {str(e)}")
    
    def _analyze_category_counts(self) -> Dict[str, int]:
        """Count ideas by category."""
        return DataGroupingUtils.count_by_key(self.categorized_ideas, 'category')
    
    def _analyze_category_percentages(self) -> Dict[str, float]:
        """Calculate percentages of ideas by category."""
        category_counts = self._analyze_category_counts()
        return StatsUtils.calculate_percentages(category_counts)
    
    def _find_top_categories(self, limit: int = 10) -> List[tuple]:
        """Find the top N categories by idea count."""
        category_counts = self._analyze_category_counts()
        return StatsUtils.find_top_n(category_counts, limit)
    
    def _group_categories_by_domain(self) -> Dict[str, Dict[str, Any]]:
        """
        Group categories into high-level domains.
        
        Returns:
            Dictionary of domain groupings
        """
        # Get category counts
        category_counts = self._analyze_category_counts()
        
        # Count ideas by domain
        domain_counts = defaultdict(int)
        domain_categories_found = defaultdict(list)
        
        for category, count in category_counts.items():
            domain_assigned = False
            
            for domain, categories in self.domain_categories.items():
                if category in categories:
                    domain_counts[domain] += count
                    domain_categories_found[domain].append((category, count))
                    domain_assigned = True
                    break
            
            if not domain_assigned and category != "Uncategorized":
                domain_counts["Other"] += count
                domain_categories_found["Other"].append((category, count))
        
        # Calculate domain percentages
        total = sum(domain_counts.values())
        domain_percentages = {}
        
        if total > 0:
            for domain, count in domain_counts.items():
                domain_percentages[domain] = (count / total) * 100
        
        return {
            "domain_counts": dict(domain_counts),
            "domain_percentages": domain_percentages,
            "domain_categories": {k: v for k, v in domain_categories_found.items() if v}
        }
    
    def _analyze_category_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in the categorized ideas.
        
        Returns:
            Dictionary of trend analysis results
        """
        # This is a placeholder for potential trend analysis
        # In a real implementation, this might analyze trends over time,
        # correlations with other data, etc.
        
        # Calculate diversity of categories
        unique_categories = len(set(idea.get("category", "Uncategorized") 
                                  for idea in self.categorized_ideas))
        
        return {
            "category_diversity": unique_categories,
            "category_diversity_ratio": unique_categories / len(self.categorized_ideas) if self.categorized_ideas else 0
        }
    
    @staticmethod
    def _extract_id(id_value: Any) -> Optional[str]:
        """Extract ID from different possible formats."""
        if id_value is None:
            return None
            
        # Handle dict format with $oid
        if isinstance(id_value, dict) and "$oid" in id_value:
            return id_value["$oid"]
        
        # Handle string format
        if isinstance(id_value, str):
            return id_value
        
        # Handle other formats by converting to string
        return str(id_value)
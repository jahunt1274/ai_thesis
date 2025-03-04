"""
Idea category analyzer for the AI thesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Any, Optional

from src.utils import get_logger

logger = get_logger("idea_category_analyzer")


class IdeaCategoryAnalyzer:
    """Analyzes categorized ideas to extract insights."""
    
    def __init__(self, categorized_ideas: List[Dict[str, Any]]):
        """
        Initialize the idea category analyzer.
        
        Args:
            categorized_ideas: List of categorized idea records
        """
        self.categorized_ideas = categorized_ideas
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze categorized ideas to extract insights.
        
        Returns:
            Dictionary of analysis results
        """
        logger.info(f"Analyzing {len(self.categorized_ideas)} categorized ideas")
        
        # Count ideas by category
        category_counts = {}
        
        for idea in self.categorized_ideas:
            category = idea.get("category", "Uncategorized")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate percentages
        total_ideas = len(self.categorized_ideas)
        category_percentages = {}
        
        if total_ideas > 0:
            for category, count in category_counts.items():
                category_percentages[category] = (count / total_ideas) * 100
        
        # Find top categories
        top_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 categories
        
        # Group categories by domain
        domain_grouping = self._group_categories_by_domain(category_counts)
        
        # Analyze trends
        trends = self._analyze_category_trends()
        
        return {
            "total_categorized": total_ideas,
            "category_counts": category_counts,
            "category_percentages": category_percentages,
            "top_categories": top_categories,
            "domain_grouping": domain_grouping,
            "trends": trends
        }
    
    def _group_categories_by_domain(self, category_counts: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
        """
        Group categories into high-level domains.
        
        Args:
            category_counts: Counts of ideas by category
            
        Returns:
            Dictionary of domain groupings
        """
        # Define domain mappings
        domain_categories = {
            "Technology": ["Artificial Intelligence", "Software", "Hardware", "Data Analytics", 
                          "Information Technology", "Mobile", "Apps", "Platforms", 
                          "Internet Services", "Robotics"],
            "Business Services": ["Corporate Services", "Professional Services", "Administrative Services",
                                 "Consulting", "Sales and Marketing", "Financial Services"],
            "Consumer": ["Consumer Goods", "Consumer Electronics", "Commerce and Shopping", 
                        "Clothing and Apparel", "Food and Beverage", "Consumer Services", "Retail"],
            "Health & Science": ["Biotechnology", "Health Care", "Science and Engineering", 
                                "Medical Devices", "Pharmaceuticals"],
            "Media & Entertainment": ["Media and Entertainment", "Content and Publishing", 
                                     "Entertainment", "Music and Audio", "Gaming"],
            "Education": ["Education", "E-Learning", "EdTech"],
            "Sustainability": ["Climate Tech", "Sustainability", "Energy", "Renewable Energy"],
            "Finance": ["Financial Services", "Lending and Investments", "Payments", 
                       "Insurance", "Banking", "Cryptocurrency", "Venture Capital", "Private Equity"],
            "Other": []  # Catch-all for others
        }
        
        # Count ideas by domain
        domain_counts = defaultdict(int)
        domain_categories_found = defaultdict(list)
        
        for category, count in category_counts.items():
            domain_assigned = False
            
            for domain, categories in domain_categories.items():
                if category in categories:
                    domain_counts[domain] += count
                    domain_categories_found[domain].append((category, count))
                    domain_assigned = True
                    break
            
            if not domain_assigned and domain_counts != "Uncategorized":
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
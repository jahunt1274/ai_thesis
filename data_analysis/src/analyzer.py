"""
Main analysis orchestrator for the AI thesis analysis.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple

from config import OUTPUT_DIR
from src.loaders import DataLoader
from src.processors import DemographicAnalyzer, UsageAnalyzer, EngagementAnalyzer, IdeaCategorizer
from src.utils import FileHandler, get_logger

logger = get_logger("analyzer")


class Analyzer:
    """Orchestrates the AI thesis analysis process."""
    
    def __init__(
            self,
            user_file: Optional[str] = None,
            idea_file: Optional[str] = None,
            step_file: Optional[str] = None,
            output_dir: str = OUTPUT_DIR,
            categorize_ideas: bool = False,
            openai_api_key: Optional[str] = None,
            openai_model: Optional[str] = None
        ):
        """
        Initialize the analyzer.
        
        Args:
            user_file: Path to user data file (optional)
            idea_file: Path to idea data file (optional)
            step_file: Path to step data file (optional)
            output_dir: Directory to save outputs
            categorize_ideas: Whether to run idea categorization
            openai_api_key: OpenAI API key (required if categorize_ideas=True)
            openai_model: OpenAI model to use for categorization
        """
        self.output_dir = output_dir
        self.categorize_ideas = categorize_ideas
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        
        # Initialize file handler
        self.file_handler = FileHandler()
        
        # Initialize data loader
        self.data_loader = DataLoader(user_file, idea_file, step_file)
        
        # Initialize result storage
        self.users = None
        self.ideas = None
        self.steps = None
        self.analysis_results = {}
        self.performance_metrics = {
            "start_time": None,
            "end_time": None,
            "total_runtime": 0,
            "component_times": {}
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Analyzer with output directory: {output_dir}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the full analysis pipeline.
        
        Returns:
            Dictionary of analysis results
        """
        self.performance_metrics["start_time"] = time.time()
        
        # Load and process data
        logger.info("Loading and processing data...")
        component_start = time.time()
        self.users, self.ideas, self.steps = self.data_loader.load_and_process_all()
        self.performance_metrics["component_times"]["data_loading"] = time.time() - component_start
        
        # Run demographic analysis
        logger.info("Running demographic analysis...")
        component_start = time.time()
        demographic_analyzer = DemographicAnalyzer(self.users)
        demographic_results = demographic_analyzer.analyze()
        self.analysis_results["demographics"] = demographic_results
        self.performance_metrics["component_times"]["demographic_analysis"] = time.time() - component_start
        
        # Run usage analysis
        logger.info("Running usage analysis...")
        component_start = time.time()
        usage_analyzer = UsageAnalyzer(self.users, self.ideas)
        usage_results = usage_analyzer.analyze()
        self.analysis_results["usage"] = usage_results
        self.performance_metrics["component_times"]["usage_analysis"] = time.time() - component_start
        
        # Run engagement analysis
        logger.info("Running engagement analysis...")
        component_start = time.time()
        engagement_analyzer = EngagementAnalyzer(self.users, self.ideas, self.steps)
        engagement_results = engagement_analyzer.analyze()
        self.analysis_results["engagement"] = engagement_results
        self.performance_metrics["component_times"]["engagement_analysis"] = time.time() - component_start
        
        # Run idea categorization if requested
        if self.categorize_ideas:
            if not self.openai_api_key:
                logger.warning("OpenAI API key not provided. Skipping idea categorization.")
            else:
                logger.info("Running idea categorization...")
                component_start = time.time()
                idea_categorizer = IdeaCategorizer(
                    ideas=self.ideas,
                    output_dir=os.path.join(self.output_dir, "categorization"),
                    api_key=self.openai_api_key,
                    model=self.openai_model
                )
                categorized_ideas = idea_categorizer.categorize()
                self.analysis_results["categorization"] = self._analyze_categorization(categorized_ideas)
                self.performance_metrics["component_times"]["idea_categorization"] = time.time() - component_start
        
        # Save results
        logger.info("Saving analysis results...")
        component_start = time.time()
        self._save_results()
        self.performance_metrics["component_times"]["saving_results"] = time.time() - component_start
        
        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"] - self.performance_metrics["start_time"]
        )
        
        logger.info(f"Analysis completed in {self.performance_metrics['total_runtime']:.2f} seconds")
        
        return self.analysis_results
    
    def _analyze_categorization(self, categorized_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze categorization results.
        
        Args:
            categorized_ideas: List of categorized ideas
            
        Returns:
            Dictionary of categorization analysis
        """
        # Count ideas by category
        category_counts = {}
        
        for idea in categorized_ideas:
            category = idea.get("category", "Uncategorized")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate percentages
        total_ideas = len(categorized_ideas)
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
        
        return {
            "total_categorized": total_ideas,
            "category_counts": category_counts,
            "category_percentages": category_percentages,
            "top_categories": top_categories
        }
    
    def _save_results(self):
        """Save analysis results to files."""
        # Save combined results
        results_file = self.file_handler.generate_filename(
            self.output_dir,
            prefix="analysis_results",
            suffix="combined"
        )
        self.file_handler.save_json(self.analysis_results, results_file)
        logger.info(f"Saved combined results to {results_file}")
        
        # Save individual component results
        for component, results in self.analysis_results.items():
            component_file = self.file_handler.generate_filename(
                self.output_dir,
                prefix=f"analysis_{component}"
            )
            self.file_handler.save_json(results, component_file)
            logger.info(f"Saved {component} results to {component_file}")
        
        # Save performance metrics
        metrics_file = self.file_handler.generate_filename(
            self.output_dir,
            prefix="performance_metrics"
        )
        self.file_handler.save_json(self.performance_metrics, metrics_file)
        logger.info(f"Saved performance metrics to {metrics_file}")
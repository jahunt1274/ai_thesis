"""
Main analysis orchestrator for the AI thesis analysis.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple

from config import OUTPUT_DIR, ANALYSIS_RESULTS_DIR, COMBINED_RESULTS_DIR
from src.loaders import DataLoader
from src.processors import (
    DemographicAnalyzer, 
    UsageAnalyzer, 
    EngagementAnalyzer, 
    IdeaCategorizer, 
    CategoryMerger,
    IdeaCategoryAnalyzer
)
from src.visualizers import VisualizationManager
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
            openai_model: Optional[str] = None,
            categorized_ideas_file: Optional[str] = None
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
        self.categorized_ideas_file = categorized_ideas_file
        
        # Initialize file handler
        self.file_handler = FileHandler()
        
        # Initialize data loader
        self.data_loader = DataLoader(user_file, idea_file, step_file)
        
        # Initialize result storage
        self.users = None
        self.ideas = None
        self.steps = None
        self.categorized_ideas = None
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
        
        # Handle categorized ideas (either from file or by running categorization)
        categorized_ideas = self._handle_categorization()
        if categorized_ideas:
            # Run category analysis
            logger.info("Running category analysis...")
            component_start = time.time()
            category_analyzer = IdeaCategoryAnalyzer(categorized_ideas)
            category_results = category_analyzer.analyze()
            self.analysis_results["categorization"] = category_results
            self.performance_metrics["component_times"]["category_analysis"] = time.time() - component_start
        
        # Run idea categorization analysis
        logger.info("Running idea categorization analysis...")
        component_start = time.time()
        
        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"] - self.performance_metrics["start_time"]
        )

        # Create visualizations
        logger.info("Creating visualizations...")
        component_start = time.time()
        self._create_visualizations()
        self.performance_metrics["component_times"]["visualization"] = time.time() - component_start

        # Save results
        logger.info("Saving analysis results...")
        component_start = time.time()
        self._save_results()
        self.performance_metrics["component_times"]["saving_results"] = time.time() - component_start
        
        logger.info(f"Analysis completed in {self.performance_metrics['total_runtime']:.2f} seconds")
        
        return self.analysis_results
    
    def _handle_categorization(self) -> List[Dict[str, Any]]:
        """
        Handle idea categorization, either from file or via API.
        
        Returns:
            List of categorized ideas, or empty list if categorization is disabled
        """
        categorized_ideas = []
        
        # Check if we have a pre-categorized ideas file
        if self.categorized_ideas_file and os.path.exists(self.categorized_ideas_file):
            logger.info(f"Using pre-categorized ideas from {self.categorized_ideas_file}")
            component_start = time.time()
            
            # Merge categories into ideas
            category_merger = CategoryMerger(self.ideas)
            self.ideas = category_merger.load_and_merge_categories(self.categorized_ideas_file)
            
            # Filter to only include ideas with categories
            categorized_ideas = [idea for idea in self.ideas if "category" in idea]
            
            self.performance_metrics["component_times"]["category_merging"] = time.time() - component_start
            logger.info(f"Merged categories into {len(categorized_ideas)} ideas")
            
            return categorized_ideas
            
        # Otherwise, check if we should run categorization via API
        elif self.categorize_ideas:
            # Check if ideas already have categories
            already_categorized = all("category" in idea for idea in self.ideas)
            
            if already_categorized:
                logger.info("Ideas already have categories. Using existing categories.")
                return self.ideas
                
            elif not self.openai_api_key:
                logger.warning("OpenAI API key not provided. Skipping idea categorization.")
                return []
                
            else:
                logger.info("Running idea categorization via API...")
                component_start = time.time()
                
                # Run categorization
                idea_categorizer = IdeaCategorizer(
                    ideas=self.ideas,
                    output_dir=os.path.join(self.output_dir, "categorization"),
                    api_key=self.openai_api_key,
                    model=self.openai_model
                )
                
                categorized_ideas = idea_categorizer.categorize()
                self.performance_metrics["component_times"]["idea_categorization"] = time.time() - component_start
                
                # Update main ideas list with categories
                self._update_ideas_with_categories(categorized_ideas)
                
                return categorized_ideas
        
        # If we get here, categorization is disabled
        return []

    def _update_ideas_with_categories(self, categorized_ideas: List[Dict[str, Any]]) -> None:
        """
        Update the main ideas list with categories from categorized ideas.
        
        Args:
            categorized_ideas: List of categorized ideas
        """
        # Create a map of idea IDs to categories
        category_map = {}
        
        for idea in categorized_ideas:
            if "id" in idea and "category" in idea:
                category_map[idea["id"]] = idea["category"]
        
        # Update main ideas list
        updated_count = 0
        
        for idea in self.ideas:
            if idea.get("id") in category_map:
                idea["category"] = category_map[idea["id"]]
                updated_count += 1
        
        logger.info(f"Updated {updated_count} ideas with categories")
    
    def _create_visualizations(self):
        """Create visualizations for analysis results."""
        try:
            # Create visualization manager
            vis_manager = VisualizationManager(self.output_dir)
            
            # Create visualizations for all components
            self.visualization_outputs = vis_manager.visualize_all(self.analysis_results)
            
            logger.info(f"Created visualizations for {len(self.visualization_outputs)} analysis components")
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            self.visualization_outputs = {}
    
    def _save_results(self):
        """Save analysis results to files."""
        # Save combined results
        results_file = self.file_handler.generate_filename(
            # self.output_dir,
            COMBINED_RESULTS_DIR,
            prefix="analysis_results",
            suffix="combined"
        )
        latest_results_file = self.file_handler.generate_filename(
            # self.output_dir,
            COMBINED_RESULTS_DIR,
            prefix="analysis_results",
            suffix="combined_latest",
            add_timestamp=False
        )
        self.file_handler.save_json(self.analysis_results, results_file)
        self.file_handler.save_json(self.analysis_results, latest_results_file)
        logger.info(f"Saved combined results to {results_file}")
        
        # Save individual component results
        for component, results in self.analysis_results.items():
            component_output_dir = f"{ANALYSIS_RESULTS_DIR}/{component}"
            component_file = self.file_handler.generate_filename(
                # self.output_dir,
                component_output_dir,
                prefix=f"analysis_{component}"
            )
            self.file_handler.save_json(results, component_file)
            logger.info(f"Saved {component} results to {component_file}")
        
        # Save performance metrics
        metrics_output_dir = f"{self.output_dir}/performance_metrics"
        metrics_file = self.file_handler.generate_filename(
            # self.output_dir,
            metrics_output_dir,
            prefix="performance_metrics"
        )
        self.file_handler.save_json(self.performance_metrics, metrics_file)
        logger.info(f"Saved performance metrics to {metrics_file}")
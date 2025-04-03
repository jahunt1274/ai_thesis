"""
Main analysis orchestrator for the AI thesis analysis.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional

from config import (
    OUTPUT_DIR, 
    ANALYSIS_RESULTS_DIR, 
    COMBINED_RESULTS_DIR, 
    COURSE_EVAL_DIR
)
from src.loaders import DataLoader, CourseEvaluationLoader
from src.processors import CategoryMerger, ProcessorFactory
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
            categorized_ideas_file: Optional[str] = None,
            analyze_evaluations: bool = False,
            eval_dir: Optional[str] = COURSE_EVAL_DIR
        ):
        """
        Initialize the analyzer.
        
        Args:
            user_file:              Path to user data file (optional)
            idea_file:              Path to idea data file (optional)
            step_file:              Path to step data file (optional)
            output_dir:             Directory to save outputs
            categorize_ideas:       Whether to run idea categorization
            openai_api_key:         OpenAI API key (required if categorize_ideas=True)
            openai_model:           OpenAI model to use for categorization
            analyze_evaluations:    Whether to run course evaluation analysis
            eval_dir:               Directory containing course evaluation files
        """
        self.output_dir = output_dir
        self.categorize_ideas = categorize_ideas
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.categorized_ideas_file = categorized_ideas_file
        self.analyze_evaluations = analyze_evaluations
        self.eval_dir = eval_dir
        
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
        
        # Initialize visualization_outputs attribute
        self.visualization_outputs = {}

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
        
        # Prepare data dictionary for processors
        data = {
            'users': self.users,
            'ideas': self.ideas,
            'steps': self.steps,
            'evaluations': []  # Will be filled later if needed
        }
        
        # Create analyzer factory
        factory = ProcessorFactory()
        
        # Run user analysis
        logger.info("Running user analysis...")
        component_start = time.time()
        user_results = factory.run_analyzer('user', data)
        self.analysis_results["user_analysis"] = user_results
        self.performance_metrics["component_times"]["user_analysis"] = time.time() - component_start
        
        # Run activity analysis
        logger.info("Running activity analysis...")
        component_start = time.time()
        activity_results = factory.run_analyzer('activity', data)
        self.analysis_results["activity_analysis"] = activity_results
        self.performance_metrics["component_times"]["activity_analysis"] = time.time() - component_start
        
        # Handle idea categorization and analysis
        if self.categorized_ideas_file:
            logger.info("Running idea categorization analysis...")
            component_start = time.time()
            idea_results = factory.run_analyzer('idea', data, 
                                               categorized_ideas_file=self.categorized_ideas_file)
            self.analysis_results["idea_analysis"] = idea_results
            self.performance_metrics["component_times"]["idea_analysis"] = time.time() - component_start
        
        # Run course evaluation analysis if enabled
        if self.analyze_evaluations:
            logger.info("Running course evaluation analysis...")
            component_start = time.time()

            # Load course evaluations
            course_eval_loader = CourseEvaluationLoader(self.eval_dir)
            evaluations = course_eval_loader.process()
            
            # Add evaluations to data
            data['evaluations'] = evaluations
            
            # Run analysis
            eval_results = factory.run_analyzer('course_eval', data)
            self.analysis_results["course_evaluations"] = eval_results
            self.performance_metrics["component_times"]["course_evaluation_analysis"] = time.time() - component_start
        
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
    
    def selective_run(self, analyses: Dict[str, bool]) -> Dict[str, Any]:
        """
        Run only selected analyses.
        
        Args:
            analyses: Dictionary mapping analysis names to boolean flags
            
        Returns:
            Dictionary of analysis results
        """
        self.performance_metrics["start_time"] = time.time()
        
        # Create mapping from old analysis names to new processor types
        analysis_mapping = {
            'demographics': 'user',
            'usage': 'activity',
            'engagement': 'activity',
            'categorization': 'idea',
            'course_evaluations': 'course_eval'
        }
        
        # Create list of processor types to run
        processor_types = []
        for analysis_name, selected in analyses.items():
            if selected and analysis_name in analysis_mapping:
                processor_type = analysis_mapping[analysis_name]
                if processor_type not in processor_types:
                    processor_types.append(processor_type)
        
        # Load data if any analysis is selected
        if processor_types:
            logger.info("Loading and processing data...")
            component_start = time.time()
            self.users, self.ideas, self.steps = self.data_loader.load_and_process_all()
            self.performance_metrics["component_times"]["data_loading"] = time.time() - component_start
            
            # Prepare data dictionary for processors
            data = {
                'users': self.users,
                'ideas': self.ideas,
                'steps': self.steps,
                'evaluations': []  # Will be filled later if needed
            }
            
            # Create analyzer factory
            factory = ProcessorFactory()
            
            # Run each selected processor
            for processor_type in processor_types:
                logger.info(f"Running {processor_type} analysis...")
                component_start = time.time()
                
                # Special handling for idea analyzer
                if processor_type == 'idea':
                    results = factory.run_analyzer(processor_type, data, 
                                                 categorized_ideas_file=self.categorized_ideas_file)
                    self.analysis_results["idea_analysis"] = results
                
                # Special handling for course evaluation analyzer
                elif processor_type == 'course_eval':
                    # Load course evaluations
                    course_eval_loader = CourseEvaluationLoader(self.eval_dir)
                    evaluations = course_eval_loader.process()
                    
                    # Add evaluations to data
                    data['evaluations'] = evaluations
                    
                    # Run analysis
                    results = factory.run_analyzer(processor_type, data)
                    self.analysis_results["course_evaluations"] = results
                
                # Standard handling for other analyzers
                else:
                    results = factory.run_analyzer(processor_type, data)
                    self.analysis_results[f"{processor_type}_analysis"] = results
                
                self.performance_metrics["component_times"][f"{processor_type}_analysis"] = time.time() - component_start
        
        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"] - self.performance_metrics["start_time"]
        )

        # Create visualizations only for the analyses that were run
        logger.info("Creating visualizations...")
        component_start = time.time()
        self._create_selective_visualizations(analyses)
        self.performance_metrics["component_times"]["visualization"] = time.time() - component_start

        # Save results
        logger.info("Saving analysis results...")
        component_start = time.time()
        self._save_results()
        self.performance_metrics["component_times"]["saving_results"] = time.time() - component_start
        
        logger.info(f"Selected analyses completed in {self.performance_metrics['total_runtime']:.2f} seconds")
        
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
            
        # Log error if no categorization file is found
        else:
            logger.error("No file found for categorized ideas")
        
        # If we get here, categorization is disabled
        return []
    
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
    
    def _create_selective_visualizations(self, analyses: Dict[str, bool]):
        """
        Create visualizations only for selected analyses.
        
        Args:
            analyses: Dictionary mapping analysis names to boolean flags
        """
        try:
            # Create visualization manager
            vis_manager = VisualizationManager(self.output_dir)
            
            # Create visualizations only for components that were analyzed
            for component, selected in analyses.items():
                if selected and component in self.analysis_results:
                    logger.info(f"Creating visualizations for {component}")
                    vis_outputs = vis_manager.visualize_component(component, self.analysis_results[component])
                    
                    if vis_outputs:
                        self.visualization_outputs[component] = vis_outputs
                        logger.info(f"Created {len(vis_outputs)} visualizations for {component}")
            
            logger.info(f"Created visualizations for {len(self.visualization_outputs)} analysis components")
            
        except Exception as e:
            logger.error(f"Error creating selective visualizations: {str(e)}")
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
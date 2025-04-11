"""
Main analysis orchestrator for the AI thesis analysis.
"""

import time
from typing import Dict, Any, Optional

from config import (
    OUTPUT_DIR,
    ANALYSIS_RESULTS_DIR,
    COMBINED_RESULTS_DIR,
    COURSE_EVAL_DIR,
    VISUALIZATION_OUTPUT_DIR,
)
from src.loaders import DataLoader
from src.processors import ProcessorFactory
from src.visualizers import VisualizationManager
from src.utils import FileHandler, get_logger, DataFilter

logger = get_logger("analyzer")


class Analyzer:
    """Orchestrates the AI thesis analysis process."""

    def __init__(
        self,
        user_file: Optional[str] = None,
        idea_file: Optional[str] = None,
        step_file: Optional[str] = None,
        categorized_ideas_file: Optional[str] = None,
        output_dir: str = OUTPUT_DIR,
        eval_dir: Optional[str] = COURSE_EVAL_DIR,
        vis_output_dir: Optional[str] = VISUALIZATION_OUTPUT_DIR,
        filter_params: Optional[Dict[str, Any]] = {},
    ):
        """
        Initialize the analyzer.

        Args:
            user_file:              Path to user data file (optional)
            idea_file:              Path to idea data file (optional)
            step_file:              Path to step data file (optional)
            categorized_ideas_file: Path to pre-categorized ideas file (optional)
            output_dir:             Directory to save outputs
            eval_dir:               Directory containing course evaluation files
        """
        self.output_dir = output_dir
        self.categorized_ideas_file = categorized_ideas_file
        self.eval_dir = eval_dir
        self.vis_output_dir = vis_output_dir

        # Initialize file handler
        self.file_handler = FileHandler()

        # Initialize data loader
        self.data_loader = DataLoader(user_file, idea_file, step_file, eval_dir)

        # Initialize result storage
        self.users = None
        self.ideas = None
        self.steps = None
        self.evaluations = None
        self.categorized_ideas = None
        self.analysis_results = {}
        self.performance_metrics = {
            "start_time": None,
            "end_time": None,
            "total_runtime": 0,
            "component_times": {},
        }
        self.data_loaded = False
        self.filter_params = filter_params

        # Initialize visualization_outputs attribute
        self.visualization_outputs = {}

        # Ensure output directory exists
        self.file_handler.ensure_directory_exists(output_dir)

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
        self.users, self.ideas, self.steps, self.evaluations = (
            self.data_loader.load_and_process_all()
        )
        self.performance_metrics["component_times"]["data_loading"] = (
            time.time() - component_start
        )

        if self.filter_params:
            logger.info("Applying filters to data...")
            component_start = time.time()
            self.apply_filters(self.filter_params)
            self.performance_metrics["component_times"]["filtering"] = (
                time.time() - component_start
            )

        # Prepare data dictionary for processors
        data = {
            "users": self.users,
            "ideas": self.ideas,
            "steps": self.steps,
            "evaluations": self.evaluations,
        }

        # Create processor factory
        factory = ProcessorFactory()

        # Run user analysis
        logger.info("Running user analysis...")
        component_start = time.time()
        user_results = factory.run_analyzer("user", data)
        self.analysis_results["user_analysis"] = user_results
        self.performance_metrics["component_times"]["user_analysis"] = (
            time.time() - component_start
        )

        # Run activity analysis
        logger.info("Running activity analysis...")
        component_start = time.time()
        activity_results = factory.run_analyzer("activity", data)
        self.analysis_results["activity_analysis"] = activity_results
        self.performance_metrics["component_times"]["activity_analysis"] = (
            time.time() - component_start
        )

        # Run course evaluation analysis
        logger.info("Running course evaluation analysis...")
        component_start = time.time()
        eval_results = factory.run_analyzer("course_eval", data)
        self.analysis_results["course_evaluations"] = eval_results
        self.performance_metrics["component_times"]["course_evaluation_analysis"] = (
            time.time() - component_start
        )

        # Handle idea categorization and analysis
        logger.info("Running idea categorization analysis...")
        component_start = time.time()
        idea_results = factory.run_analyzer(
            "idea", data, categorized_ideas_file=self.categorized_ideas_file
        )
        self.analysis_results["idea_analysis"] = idea_results
        self.performance_metrics["component_times"]["idea_analysis"] = (
            time.time() - component_start
        )

        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"]
            - self.performance_metrics["start_time"]
        )

        # Create visualizations
        logger.info("Creating visualizations...")
        component_start = time.time()
        self._create_visualizations()
        self.performance_metrics["component_times"]["visualization"] = (
            time.time() - component_start
        )

        # Save results
        logger.info("Saving analysis results...")
        component_start = time.time()
        self._save_results()
        self.performance_metrics["component_times"]["saving_results"] = (
            time.time() - component_start
        )

        logger.info(
            f"Analysis completed in {self.performance_metrics['total_runtime']:.2f} seconds"
        )

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
        # # Create list of processor types to run
        processor_types = set()
        for analysis_name, selected in analyses.items():
            if processor_type not in processor_types:
                processor_types.append(processor_type)

        # Load data if any analysis is selected
        if processor_types:
            logger.info("Loading and processing data...")
            component_start = time.time()
            self.users, self.ideas, self.steps, self.evaluations = (
                self.data_loader.load_and_process_all()
            )
            self.performance_metrics["component_times"]["data_loading"] = (
                time.time() - component_start
            )

            if self.filter_params:
                logger.info("Applying filters to data...")
                component_start = time.time()
                self.apply_filters(self.filter_params)
                self.performance_metrics["component_times"]["filtering"] = (
                    time.time() - component_start
                )

            # Prepare data dictionary for processors
            data = {
                "users": self.users,
                "ideas": self.ideas,
                "steps": self.steps,
                "evaluations": self.evaluations,
            }

            # Create processor factory
            factory = ProcessorFactory()

            # Run each selected processor
            for processor_type in processor_types:
                logger.info(f"Running {processor_type} analysis...")
                component_start = time.time()

                # Special handling for idea analyzer with categorized idea file
                if processor_type == "idea":
                    results = factory.run_analyzer(
                        processor_type,
                        data,
                        categorized_ideas_file=self.categorized_ideas_file,
                    )
                    self.analysis_results[f"{processor_type}_analysis"] = results
                else:
                    # Standard handling for other analyzers
                    results = factory.run_analyzer(processor_type, data)
                    self.analysis_results[f"{processor_type}_analysis"] = results

                self.performance_metrics["component_times"][
                    f"{processor_type}_analysis"
                ] = (time.time() - component_start)

        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"]
            - self.performance_metrics["start_time"]
        )

        # Create visualizations only for the analyses that were run
        logger.info("Creating visualizations...")
        component_start = time.time()
        self._create_selective_visualizations(analyses)
        self.performance_metrics["component_times"]["visualization"] = (
            time.time() - component_start
        )

        # Save results
        logger.info("Saving analysis results...")
        component_start = time.time()
        self._save_results()
        self.performance_metrics["component_times"]["saving_results"] = (
            time.time() - component_start
        )

        logger.info(
            f"Selected analyses completed in {self.performance_metrics['total_runtime']:.2f} seconds"
        )

        return self.analysis_results

    def run_from_results(self, results_file: str) -> Dict[str, Any]:
        """
        Load previously saved results and generate visualizations.

        Args:
            results_file: Path to the results file

        Returns:
            Dictionary of analysis results
        """
        self.performance_metrics["start_time"] = time.time()

        # Load results
        component_start = time.time()
        logger.info(f"Loading analysis results from {results_file}")
        self.analysis_results = self.file_handler.load_json(results_file)
        self.performance_metrics["component_times"]["loading_results"] = (
            time.time() - component_start
        )

        # Create visualizations
        logger.info("Creating visualizations...")
        component_start = time.time()
        self._create_visualizations()
        self.performance_metrics["component_times"]["visualization"] = (
            time.time() - component_start
        )

        # Calculate total runtime
        self.performance_metrics["end_time"] = time.time()
        self.performance_metrics["total_runtime"] = (
            self.performance_metrics["end_time"]
            - self.performance_metrics["start_time"]
        )

        logger.info(
            f"Visualization completed in {self.performance_metrics['total_runtime']:.2f} seconds"
        )

        return self.analysis_results

    def apply_filters(self, filter_params: Dict[str, Any]) -> None:
        """
        Apply filters to the data.

        Args:
            filter_params: Dictionary of filter parameters
        """
        if not self.users or not self.ideas or not self.steps:
            logger.warning("No data loaded yet. Call load_and_process_all() first.")
            return

        filters = []

        # Filter by course if specified
        if "course" in filter_params and filter_params["course"]:
            logger.info(
                f"Filtering users enrolled in course {filter_params['course']}..."
            )
            filters.append(
                lambda u, i, s: DataFilter.filter_by_course(
                    u, i, s, filter_params["course"]
                )
            )

        # Filter by user type if specified
        if "user_type" in filter_params and filter_params["user_type"]:
            logger.info(f"Filtering users of type {filter_params['user_type']}...")
            filters.append(
                lambda u, i, s: DataFilter.filter_by_user_type(
                    u, i, s, filter_params["user_type"]
                )
            )

        # Filter by activity if specified
        if "activity" in filter_params and filter_params["activity"]:
            min_ideas = filter_params.get("min_ideas", 1)
            min_steps = filter_params.get("min_steps", 0)
            logger.info(
                f"Filtering users by activity (min ideas: {min_ideas}, min steps: {min_steps})..."
            )
            filters.append(
                lambda u, i, s: DataFilter.filter_by_activity(
                    u, i, s, min_ideas=min_ideas, min_steps=min_steps
                )
            )

        # Filter by date range if specified
        if "date_range" in filter_params and filter_params["date_range"]:
            start_date, end_date = filter_params["date_range"]
            logger.info(f"Filtering data by date range: {start_date} to {end_date}...")
            filters.append(
                lambda u, i, s: DataFilter.filter_by_time_period(
                    u, i, s, start_date, end_date
                )
            )

        # Apply filters if any were created
        if filters:
            logger.info(f"Applying {len(filters)} filters to data...")
            before_counts = (len(self.users), len(self.ideas), len(self.steps))

            self.users, self.ideas, self.steps = DataFilter.compose_filters(
                self.users, self.ideas, self.steps, filters
            )

            after_counts = (len(self.users), len(self.ideas), len(self.steps))
            logger.info(
                f"Filtering reduced users from {before_counts[0]} to {after_counts[0]}, "
                f"ideas from {before_counts[1]} to {after_counts[1]}, "
                f"steps from {before_counts[2]} to {after_counts[2]}"
            )
        else:
            logger.info("No filters to apply")

    def _create_visualizations(self):
        """Create visualizations for analysis results."""
        try:
            vis_manager = VisualizationManager(self.vis_output_dir)

            # Create visualizations for all components
            self.visualization_outputs = vis_manager.visualize_all(
                self.analysis_results
            )

            # Count total visualizations
            total_vis = sum(len(vis) for vis in self.visualization_outputs.values())
            logger.info(
                f"Created {total_vis} visualizations across {len(self.visualization_outputs)} components"
            )

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
            vis_manager = VisualizationManager(self.vis_output_dir)

            # Create visualizations only for components that were analyzed
            for component, selected in analyses.items():
                if selected and component in self.analysis_results:
                    logger.info(f"Creating visualizations for {component}")
                    vis_outputs = vis_manager.visualize_component(
                        component, self.analysis_results[component]
                    )

                    if vis_outputs:
                        self.visualization_outputs[component] = vis_outputs
                        logger.info(
                            f"Created {len(vis_outputs)} visualizations for {component}"
                        )

            # Count total visualizations
            total_vis = sum(len(vis) for vis in self.visualization_outputs.values())
            logger.info(
                f"Created {total_vis} visualizations across {len(self.visualization_outputs)} components"
            )

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
            suffix="combined",
        )
        latest_results_file = self.file_handler.generate_filename(
            # self.output_dir,
            COMBINED_RESULTS_DIR,
            prefix="analysis_results",
            suffix="combined_latest",
            add_timestamp=False,
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
                prefix=f"analysis_{component}",
            )
            self.file_handler.save_json(results, component_file)
            logger.info(f"Saved {component} results to {component_file}")

        # Save performance metrics
        metrics_output_dir = f"{self.output_dir}/performance_metrics"
        metrics_file = self.file_handler.generate_filename(
            # self.output_dir,
            metrics_output_dir,
            prefix="performance_metrics",
        )
        self.file_handler.save_json(self.performance_metrics, metrics_file)
        logger.info(f"Saved performance metrics to {metrics_file}")

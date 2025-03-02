import argparse
import inquirer
from typing import Dict, Any
from runners.summary_runner import SummaryRunner
from runners.results_runner import ResultsRunner
from processors.summary_processors.category_processor import CategoryProcessor
from utils.json_reducer import JSONReducer
from utils.file_combiner import FileCombiner
from utils.json_schema_generator import JSONSchemaGenerator
from config import DATA_DIR, OUTPUT_DIR

class ApplicationManager:
    def __init__(self):
        # Initialize file paths
        # self.idea_input_file = f'{DATA_DIR}/ideas.json'
        self.idea_input_file = f'{DATA_DIR}/ideas_edited.json'
        self.idea_output_file = f'{OUTPUT_DIR}/llm_input/ideas.json'
        self.idea_fields_to_keep = ['_id', 'title']
        self.ideas_with_categories_filepath = f'{DATA_DIR}/categorized_ideas_gpt-4o.json'
        self.categories_filepath = f'{DATA_DIR}/idea_categories.json'
        self.categorization_output_filepath = f'{OUTPUT_DIR}/ideas_category_count_gpt-4o.json'
        self.idea_by_category_output_filepath = f'{OUTPUT_DIR}/uncatecorized_ideas.json'

        # JSON schema file paths
        self.json_schema_generator_input_filepath = f"{DATA_DIR}/steps.json"
        self.json_schema_generator_output_filepath = f"{OUTPUT_DIR}/schemas/steps_schema.json"

        # File combiner file paths
        self.file_combiner_llm_categorized_idea_filepath = f"{DATA_DIR}/llm_responses/categorized_ideas_gpt-4o_fixed.json"
        self.file_combiner_orbit_idea_filepath = f"{DATA_DIR}/ideas.json"
        self.file_combiner_output_filepath = f"{OUTPUT_DIR}/categorized_ideas/categorized_ideas_gpt-4o.json"

        # Initialize runners
        self.summary_runner = SummaryRunner(DATA_DIR, OUTPUT_DIR)
        self.results_runner = ResultsRunner(DATA_DIR, OUTPUT_DIR)
        self.json_reducer = JSONReducer(self.idea_input_file, self.idea_output_file)
        self.category_processor = CategoryProcessor(
            self.ideas_with_categories_filepath,
            self.categories_filepath,
            self.categorization_output_filepath
        )
        self.file_combiner = FileCombiner(
            self.file_combiner_llm_categorized_idea_filepath,
            self.file_combiner_orbit_idea_filepath,
            self.file_combiner_output_filepath
        )
        self.json_schema_generator = JSONSchemaGenerator(
            self.json_schema_generator_input_filepath,
            self.json_schema_generator_output_filepath
        )

        # Define available runners with descriptions
        self.runners: Dict[str, Dict[str, Any]] = {
            'summary': {
                'name': 'Process Summary Data',
                'description': 'Run the summary processing pipeline',
                'function': self.run_summary
            },
            'results': {
                'name': 'Analyze Results',
                'description': 'Run the results analysis pipeline',
                'function': self.run_results
            },
            'reducer': {
                'name': 'Reduce JSON Fields',
                'description': 'Reduce JSON to specified fields',
                'function': self.run_reducer
            },
            "categorizor" : {
                'name': 'Analyze Idea Categories',
                'description': 'Get different information about the idea categories',
                'function': self.run_categorizor
            },
            "combiner": {
                'name': 'Combine JSON Files',
                'description': 'Combine ideas and categories based on matching IDs',
                'function': self.run_combiner
            },
            "schema_generator": {
                'name': 'Generate JSON Schema',
                'description': 'Generate schema from JSON array of objects',
                'function': self.run_schema_generator
            }
        }

    def run_summary(self) -> None:
        """Run the summary processing pipeline"""
        print("Starting summary processing...")
        self.summary_runner.process_data()
        print("Summary processing completed")

    def run_results(self) -> None:
        """Run the results analysis pipeline"""
        print("Starting results analysis...")
        self.results_runner.analyze()
        print("Results analysis completed")

    def run_reducer(self) -> None:
        """Run the JSON reducer"""
        print("Starting JSON reduction...")
        self.json_reducer.reduce_json_fields(self.idea_fields_to_keep)
        print("JSON reduction completed")

    def run_categorizor(self) -> None:
        """Run the idea categorizor"""
        print("Starting idea category analysis...")
        self.category_processor.run()
        print("Idea categorization completed")

    def run_combiner(self) -> None:
        """Run the file combiner to merge ideas with categories"""
        print("Starting file combination process...")
        self.file_combiner.combine_json_files()
        print(f"File combined completed, file saved to {self.file_combiner_output_filepath}")
    
    def run_schema_generator(self) -> None:
        """Generate schema from JSON file"""
        print(f"Generating schema...")
        self.json_schema_generator.run()
        print("Schema generation completed")
    
    def prompt_runner_selection(self) -> str:
        """Prompt user to select a runner"""
        questions = [
            inquirer.List(
                'runner',
                message="Which process would you like to run?",
                choices=[(f"{info['name']} - {info['description']}", 
                        runner_key) 
                        for runner_key, info in self.runners.items()],
                carousel=True
            )
        ]
        answers = inquirer.prompt(questions)
        return answers['runner']

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='Data Processing Pipeline Manager'
        )
        parser.add_argument(
            '--runner',
            choices=list(self.runners.keys()),
            help='Specify which runner to execute (omit for interactive mode)'
        )
        return parser

    def run(self) -> None:
        """Main execution method"""
        parser = self.create_parser()
        args = parser.parse_args()

        # If no runner specified, use interactive mode
        selected_runner = args.runner if args.runner else self.prompt_runner_selection()
        
        # Execute the selected runner
        try:
            self.runners[selected_runner]['function']()
        except Exception as e:
            print(f"Error running {selected_runner}: {str(e)}")
            raise

if __name__ == "__main__":
    app = ApplicationManager()
    app.run()

# from runners.summary_runner import SummaryRunner
# from runners.results_runner import ResultsRunner
# from utils.json_reducer import JSONReducer
# from config import DATA_DIR, OUTPUT_DIR

# idea_input_file = f'{DATA_DIR}/ideas.json'
# idea_output_file = f'{OUTPUT_DIR}/llm_input/ideas.json'

# idea_fields_to_keep = [
#     '_id',
#     'title'
# ]

# summaryRunner = SummaryRunner(DATA_DIR, OUTPUT_DIR)
# resultsRunner = ResultsRunner(DATA_DIR, OUTPUT_DIR)
# jsonReducer = JSONReducer(idea_input_file, idea_output_file)

# if __name__ == "__main__":
#     summaryRunner.process_data()
#     resultsRunner.analyze()
#     jsonReducer.reduce_json_fields(idea_fields_to_keep)
import json
from typing import List, Dict, Any
import sys
from processors.summary_processors.idea_processor import IdeaProcessor
from processors.summary_processors.step_processor import StepProcessor
from processors.summary_processors.user_processor import UserJourneyProcessor
from processors.summary_processors.profile_processor import ProfileProcessor
from processors.summary_analyzer import SummaryAnalyzer

class SummaryRunner:
    def __init__(self, data_filepath_prefix: str, output_filepath_prefix: str):
        self.data_filepath_prefix = data_filepath_prefix
        self.output_filepath_prefix = output_filepath_prefix

    def _analyze_results(self):
        try:
            analyzer = SummaryAnalyzer(f'{self.output_filepath_prefix}/analysis_results.json')
            
            # Open output file
            with open(f'{self.output_filepath_prefix}/analysis_summary.txt', 'w') as f:
                # Write summary report
                f.write(analyzer.generate_summary_report())
                
                # Write key metrics
                f.write("\n\nKey Metrics:\n")
                metrics = analyzer.get_key_metrics()
                for metric, value in metrics.items():
                    f.write(f"{metric}: {value}\n")
                
                # Write enrollment trends
                f.write("\nTop 5 Courses by Enrollment:\n")
                trends = analyzer.get_enrollment_trends()
                for course in trends[:5]:
                    f.write(f"{course['course']}: {course['enrollments']} ({course['percentage']:.1f}%)\n")
            
            print(f"Analysis complete. Results written to output/analysis_summary.txt")
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load JSON data from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # If data is a string, try to parse it as JSON
                if isinstance(data, str):
                    data = json.loads(data)
                # If single object, convert to list
                if isinstance(data, dict):
                    data = [data]
                return data
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            print("First 100 characters of file content:")
            with open(file_path, 'r') as f:
                print(f.read(100))
            return []

    def process_data(self):
        # Load data with error handling
        print("Loading data files...")
        
        users_data = self.load_data(f'{self.data_filepath_prefix}/users.json')
        print(f"Loaded {len(users_data)} user records")
        
        ideas_data = self.load_data(f'{self.data_filepath_prefix}/ideas.json')
        print(f"Loaded {len(ideas_data)} idea records")
        
        steps_data = self.load_data(f'{self.data_filepath_prefix}/steps.json')
        print(f"Loaded {len(steps_data)} step records")
        
        # Initialize processors
        try:
            print("\nInitializing processors...")
            profile_processor = ProfileProcessor(users_data)
            idea_processor = IdeaProcessor(ideas_data)
            step_processor = StepProcessor(steps_data)
            journey_processor = UserJourneyProcessor(users_data)
            
            # Process data
            print("\nProcessing data...")
            results = {
                "profiles": profile_processor.process(),
                "ideas": idea_processor.process(),
                "steps": step_processor.process(),
                "journeys": journey_processor.process()
            }
            
            # Save results
            print("\nSaving results...")
            with open(f'{self.output_filepath_prefix}/analysis_results.json', 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print("\nAnalysis complete. Results saved to output/analysis_results.json")
            
        except Exception as e:
            print(f"\nError during processing: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        print("\nAnalyzing results...")
        self.analyze_results()
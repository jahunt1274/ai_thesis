import json
from typing import Dict, Any
from processors.demographic_analyzer import DemographicAnalyzer
from processors.usage_analyzer import UsageAnalyzer
from processors.engagement_analyzer import EngagementAnalyzer

class ResultsRunner:
    def __init__(self, data_filepath_prefix: str, output_filepath_prefix: str):
        self.data_filepath_prefix = data_filepath_prefix
        self.output_filepath_prefix = output_filepath_prefix
    
    def analyze(self):
        """Process and analyze all data."""
        try:
            # Load all data
            with open(f'{self.data_filepath_prefix}/users.json', 'r') as f:
                users_data = json.load(f)
            with open(f'{self.data_filepath_prefix}/ideas.json', 'r') as f:
                ideas_data = json.load(f)
            with open(f'{self.data_filepath_prefix}/steps.json', 'r') as f:
                steps_data = json.load(f)

            # Initialize analyzers
            demographic_analyzer = DemographicAnalyzer(users_data)
            usage_analyzer = UsageAnalyzer(users_data, ideas_data)
            engagement_analyzer = EngagementAnalyzer(users_data, ideas_data, steps_data)

            # Generate analysis
            analysis_results = {
                "1_user_demographics": {
                    "1_affiliations": demographic_analyzer.analyze_affiliations(),
                    "2_cohorts": demographic_analyzer.analyze_cohorts()
                },
                "2_usage_patterns": {
                    "1_engagement_levels": usage_analyzer.analyze_user_engagement(),
                    "2_idea_analysis": usage_analyzer.analyze_idea_rankings()
                },
                "3_engagement_depth": {
                    "1_process_completion": engagement_analyzer.analyze_process_completion(),
                    "2_temporal_patterns": engagement_analyzer.analyze_temporal_patterns()
                }
            }

            # Write results to files
            with open(f'{self.output_filepath_prefix}/detailed_analysis.json', 'w') as f:
                json.dump(analysis_results, f, indent=2)

            # Generate human-readable summary
            with open(f'{self.output_filepath_prefix}/analysis_summary.txt', 'w') as f:
                f.write("=== Detailed Analysis Summary ===\n\n")
                
                # Write demographics summary
                f.write("1. User Demographics\n")
                f.write("-------------------\n")
                affiliations = analysis_results["1_user_demographics"]["1_affiliations"]
                f.write("User Affiliations:\n")
                for affiliation, count in affiliations.items():
                    f.write(f"- {affiliation}: {count} users\n")
                f.write("\n")

                # Write usage patterns
                f.write("2. Usage Patterns\n")
                f.write("----------------\n")
                engagement = analysis_results["2_usage_patterns"]["1_engagement_levels"]
                f.write("Engagement Levels:\n")
                for level, count in engagement.items():
                    f.write(f"- {level.title()}: {count} users\n")
                f.write("\n")

                # Write engagement depth
                f.write("3. Engagement Depth\n")
                f.write("-----------------\n")
                completion = analysis_results["3_engagement_depth"]["1_process_completion"]["completion_stats"]
                f.write("Process Completion:\n")
                for metric, value in completion.items():
                    if isinstance(value, (int, float)):
                        f.write(f"- {metric.replace('_', ' ').title()}: {value}\n")

            print("Analysis complete. Results written to:")
            print("- output/detailed_analysis.json")
            print("- output/analysis_summary.txt")

        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise
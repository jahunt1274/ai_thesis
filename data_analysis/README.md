# AI Thesis Analysis System

This repository contains the analysis system for the MIT SDM thesis on analyzing the usage of AI tools by entrepreneurs who are starting new businesses. The system analyzes data from the JetPack/Orbit tool developed by the MIT Martin Trust Center for Entrepreneurship.

## Overview

The AI Thesis Analysis System processes and analyzes four key datasets:

1. **User Data**: Information about users, their affiliations, enrollments, and profiles
2. **Idea Data**: Business ideas entered by users
3. **Step Data**: Steps taken by users in developing their ideas within the entrepreneurship frameworks
4. **Course Evaluation Data**: Course evaluation feedback from different semesters, with and without the Jetpack tool

The system performs five main types of analysis:

1. **Demographic Analysis**: Analyzes user demographics, affiliations, and cohorts
2. **Usage Analysis**: Analyzes idea generation patterns and tool usage 
3. **Engagement Analysis**: Analyzes process completion and user progression through the entrepreneurship frameworks
4. **Cohort Analysis**: Analyzes differences between user cohorts from different time periods, specifically comparing tool versions' impact on learning outcomes
5. **Course Evaluation Analysis**: Analyzes course evaluation data across different semesters to measure the impact of the Jetpack tool on learning outcomes

Additionally, the system can categorize business ideas using OpenAI's API to identify trends in the types of ideas generated.

## Project Structure

```
data_analysis/
├── config/                # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── data/                  # Data directory (input files)
│   ├── __init__.py
│   └── course_evaluations/ # Course evaluation JSON files
├── output/                # Output directory (results)
│   ├── analysis_results/  # Analysis results by component
│   ├── categorization/    # Idea categorization results
│   ├── course_evaluations/ # Course evaluation results
│   └── visualizations/    # Generated visualizations
├── schemas/               # JSON schemas for validation
│   └── course_evaluation_schema.py  # Schema for course evaluations
├── src/                   # Source code
│   ├── loaders/           # Data loading modules
│   │   ├── __init__.py
│   │   ├── user_loader.py
│   │   ├── idea_loader.py
│   │   ├── step_loader.py
│   │   └── course_eval_loader.py
│   ├── processors/        # Analysis processors
│   │   ├── __init__.py
│   │   ├── demographic_analyzer.py
│   │   ├── usage_analyzer.py
│   │   ├── engagement_analyzer.py
│   │   ├── idea_categorizer.py
│   │   ├── idea_category_analyzer.py
│   │   ├── category_merger.py
│   │   ├── cohort_analyzer.py
│   │   └── course_eval_analyzer.py
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py
│   │   ├── logger.py
│   │   └── filters.py
│   ├── visualizers/       # Visualization modules
│   │   ├── __init__.py
│   │   ├── base_visualizer.py
│   │   ├── demographic_visualizer.py
│   │   ├── usage_visualizer.py
│   │   ├── engagement_visualizer.py
│   │   ├── categorization_visualizer.py
│   │   ├── cohort_visualizer.py
│   │   ├── course_eval_visualizer.py
│   │   └── visualization_manager.py
│   ├── __init__.py
│   └── analyzer.py        # Main analysis orchestrator
├── main.py                # Command-line interface for full analysis
├── visualize.py           # Command-line interface for visualization generation
├── cohort_analysis_script.py # Script for focused cohort analysis
├── course_eval_analysis.py   # Script for focused course evaluation analysis
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jahunt1274/data_analysis.git
   cd data_analysis
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables (optional):
   ```
   export OPENAI_API_THESIS_KEY="your-api-key"  # Required for idea categorization
   ```

## Usage

### Basic Analysis

To run a complete analysis using default file paths:

```
python main.py
```

### Custom Input Files

To specify custom input file paths:

```
python main.py --user-file path/to/users.json --idea-file path/to/ideas.json --step-file path/to/steps.json
```

### Course Evaluation Analysis

To include course evaluation analysis:

```
python main.py --analyze-evaluations --eval-dir path/to/course_evaluations
```

Or to run only course evaluation analysis:

```
python main.py --evaluations-only --analyze-evaluations --eval-dir path/to/course_evaluations
```

You can also use the dedicated course evaluation script:

```
python course_eval_analysis.py --eval-dir path/to/course_evaluations
```

### Idea Categorization

To include idea categorization using OpenAI's API:

```
python main.py --categorize-ideas --openai-key your-api-key --openai-model gpt-4o
```

You can also use pre-categorized ideas:
```
python main.py --categorized-file path/to/categorized_ideas.json
```

### Custom Output Directory

To specify a custom output directory:

```
python main.py --output-dir path/to/output
```

### Visualization Only

To generate visualizations from existing analysis results:

```
python visualize.py --results-file path/to/analysis_results.json --output-dir path/to/visualizations
```

By default, the script looks for the latest combined results file.

To generate visualizations from existing course evaluation results:

```
python course_eval_analysis.py --visualize-only --results-file path/to/course_evaluation_results.json
```

### Cohort Analysis

To run the dedicated cohort analysis script:

```
python cohort_analysis_script.py
```

This script conducts a more focused analysis on how different cohorts (particularly across different time periods) use the tool, which is especially valuable for the thesis research comparing different tool versions.

To visualize existing cohort analysis results:
```
python cohort_analysis_script.py --visualize-only --results-file path/to/cohort_results.json
```

## Results

The analysis results are saved to the output directory as JSON files:

- `analysis_results_combined_*.json`: All analysis results combined
- `analysis_demographics_*.json`: Demographic analysis results
- `analysis_usage_*.json`: Usage analysis results
- `analysis_engagement_*.json`: Engagement analysis results
- `analysis_categorization_*.json`: Categorization results (if enabled)
- `analysis_course_evaluations_*.json`: Course evaluation results (if enabled)
- `performance_metrics_*.json`: Performance metrics for the analysis

If idea categorization is enabled, additional files will be saved to the `output/categorization` directory:

- `categorized_ideas_*.json`: Ideas with their assigned categories
- `categorization_metrics_*.json`: Performance metrics for the categorization process

## Visualizations

The system generates a comprehensive set of visualizations for each analysis component:

1. **Demographics**:
   - User counts
   - Affiliations
   - User types distribution
   - Activity cohorts
   - User registration timeline
   - Enrollment statistics
   - User interests
   - Institutions

2. **Usage**:
   - Idea generation overview
   - Ideas by ranking
   - Engagement levels
   - Framework engagement
   - Monthly active users
   - Iteration patterns
   - Progress statistics
   - Framework counts and completion

3. **Engagement**:
   - Step distribution
   - Framework completion comparison
   - Step progression and dropout points
   - Monthly activity
   - Seasonal patterns
   - Step intervals
   - User type cohorts
   - Institution cohorts

4. **Categorization**:
   - Category distribution
   - Top categories
   - Category percentages
   - Category clusters

5. **Cohorts**:
   - Time cohort comparison
   - Usage metrics by cohort
   - Tool adoption rates
   - Framework completion by cohort
   - Learning metrics comparison

6. **Course Evaluations**:
   - Semester comparison
   - Tool impact
   - Section performance
   - Key question analysis
   - Rating trends

All visualizations are combined into an HTML report for easy viewing:
```
output/visualizations/visualization_report/visualization_report.html
```

## Course Evaluation Analysis

The course evaluation analysis component examines how different versions of the Jetpack tool impact course evaluations and learning outcomes. It provides insights into:

- **Overall satisfaction levels** across semesters with and without the tool
- **Seasonal differences** between fall and spring semesters
- **Tool version impact** on specific evaluation metrics
- **Section performance** across different aspects of the course
- **Key question analysis** for metrics like overall satisfaction, learning experience, feedback quality, and materials quality
- **Rating trends** over time with tool version change points highlighted

This analysis is particularly valuable for the thesis research on how AI tools affect educational outcomes in entrepreneurship courses.

## Thesis Research Context

This analysis system supports MIT SDM thesis research focused on understanding how the Orbit tool impacts entrepreneurial experiences and learning outcomes in MIT courses, particularly 15.390 (Disciplined Entrepreneurship). The research compares multiple cohorts:

- Fall 2023: No Jetpack (Control group)
- Spring 2024: Jetpack v1
- Fall 2024: Jetpack v2
- Spring 2025: Upcoming cohort

The analysis helps answer key research questions:
- How Orbit is helping accelerate the entrepreneurial process
- Whether it's freeing founders to spend more time with customers
- If it's speeding up the iteration process
- The impact on educational outcomes and learning experiences

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
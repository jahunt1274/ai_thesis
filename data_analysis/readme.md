# AI Thesis Analysis System

This repository contains the analysis system for the MIT SDM thesis on analyzing the usage of AI tools by entrepreneurs who are starting new businesses. The system analyzes data from the JetPack/Orbit tool developed by the MIT Martin Trust Center for Entrepreneurship.

## Overview

The AI Thesis Analysis System processes and analyzes three key datasets:

1. **User Data**: Information about users, their affiliations, enrollments, and profiles
2. **Idea Data**: Business ideas entered by users
3. **Step Data**: Steps taken by users in developing their ideas within the entrepreneurship frameworks

The system performs three main types of analysis:

1. **Demographic Analysis**: Analyzes user demographics, affiliations, and cohorts
2. **Usage Analysis**: Analyzes idea generation patterns and tool usage 
3. **Engagement Analysis**: Analyzes process completion and user progression through the entrepreneurship frameworks

Additionally, the system can categorize business ideas using OpenAI's API to identify trends in the types of ideas generated.

## Project Structure

```
ai_thesis/
├── config/                # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── data/                  # Data directory (input files)
│   └── __init__.py
├── output/                # Output directory (results)
│   └── __init__.py
├── src/                   # Source code
│   ├── loaders/           # Data loading modules
│   │   ├── __init__.py
│   │   ├── user_loader.py
│   │   ├── idea_loader.py
│   │   └── step_loader.py
│   ├── processors/        # Analysis processors
│   │   ├── __init__.py
│   │   ├── demographic_analyzer.py
│   │   ├── usage_analyzer.py
│   │   ├── engagement_analyzer.py
│   │   └── idea_categorizer.py
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py
│   │   └── logger.py
│   ├── visualizers/       # Visualization modules (placeholder)
│   │   ├── __init__.py
│   │   └── base_visualizer.py
│   ├── __init__.py
│   └── analyzer.py        # Main analysis orchestrator
├── main.py                # Command-line interface
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai_thesis.git
   cd ai_thesis
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
   export OPENAI_API_KEY="your-api-key"  # Required for idea categorization
   ```

## Usage

### Basic Analysis

To run a basic analysis using default file paths:

```
python main.py
```

### Custom Input Files

To specify custom input file paths:

```
python main.py --user-file path/to/users.json --idea-file path/to/ideas.json --step-file path/to/steps.json
```

### Idea Categorization

To include idea categorization using OpenAI's API:

```
python main.py --categorize-ideas --openai-key your-api-key --openai-model gpt-4o
```

### Selective Analysis

To run only specific analyses:

```
python main.py --demographic-only
python main.py --usage-only 
python main.py --engagement-only
```

### Custom Output Directory

To specify a custom output directory:

```
python main.py --output-dir path/to/output
```

## Results

The analysis results are saved to the output directory as JSON files:

- `analysis_results_combined_*.json`: All analysis results combined
- `analysis_demographics_*.json`: Demographic analysis results
- `analysis_usage_*.json`: Usage analysis results
- `analysis_engagement_*.json`: Engagement analysis results
- `analysis_categorization_*.json`: Categorization results (if enabled)
- `performance_metrics_*.json`: Performance metrics for the analysis

If idea categorization is enabled, additional files will be saved to the `output/categorization` directory:

- `categorized_ideas_*.json`: Ideas with their assigned categories
- `categorization_metrics_*.json`: Performance metrics for the categorization process

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
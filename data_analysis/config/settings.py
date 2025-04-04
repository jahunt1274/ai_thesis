"""
Centralized configuration settings for the AI thesis analysis system.
"""

import os
from pathlib import Path

# Path Configuration
# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Define paths relative to the project root
DATA_DIR = os.environ.get('AI_THESIS_DATA_DIR', str(PROJECT_ROOT / 'data'))
OUTPUT_DIR = os.environ.get('AI_THESIS_OUTPUT_DIR', str(PROJECT_ROOT / 'output'))
LOG_DIR = os.environ.get('AI_THESIS_LOG_DIR', str(PROJECT_ROOT / 'logs'))
SCHEMA_DIR = os.environ.get('AI_THESIS_LOG_DIR', str(PROJECT_ROOT / 'schemas'))

# Define path for analysis results relative to the output directory
ANALYSIS_RESULTS_DIR = os.environ.get('AI_THESIS_ANALYSIS_RESULTS_DIR', str(Path(OUTPUT_DIR) / 'analysis_results'))

# Define paths for individual analysis results relative to output directory
CATEGORIZATION_RESULTS_DIR = os.environ.get('AI_THESIS_ANALYSIS_RESULTS_DIR', str(Path(ANALYSIS_RESULTS_DIR) / 'categorization'))
DEMOGRAPHICS_RESULTS_DIR = os.environ.get('AI_THESIS_DEMOGRAPHICS_RESULTS_DIR', str(Path(ANALYSIS_RESULTS_DIR) / 'demographics'))
ENGAGEMENT_RESULTS_DIR = os.environ.get('AI_THESIS_ENGAGEMENT_RESULTS_DIR', str(Path(ANALYSIS_RESULTS_DIR) / 'engagement'))
USAGE_RESULTS_DIR = os.environ.get('USAGE_RESULTS_DIR', str(Path(ANALYSIS_RESULTS_DIR) / 'usage'))
COMBINED_RESULTS_DIR = os.environ.get('AI_THESIS_COMBINED_RESULTS_DIR', str(Path(ANALYSIS_RESULTS_DIR) / 'combined'))

# Define paths for course evaluation data
COURSE_EVAL_DIR = os.environ.get('AI_THESIS_COURSE_EVAL_DIR', str(Path(DATA_DIR) / 'course_evaluations'))
COURSE_EVAL_RESULTS_DIR = os.environ.get('AI_THESIS_COURSE_EVAL_RESULTS_DIR', str(Path(OUTPUT_DIR) / 'course_eval_analysis'))

# Define path for visualization output
VISUALIZATION_OUTPUT_DIR = os.environ.get('AI_THESIS_VISUALIZATION_OUTPUT_DIR', str(Path(OUTPUT_DIR) / 'visualizations'))

# Ensure directories exist
for directory in [
    DATA_DIR, 
    OUTPUT_DIR, 
    LOG_DIR,
    ANALYSIS_RESULTS_DIR,
    CATEGORIZATION_RESULTS_DIR,
    DEMOGRAPHICS_RESULTS_DIR,
    ENGAGEMENT_RESULTS_DIR,
    COMBINED_RESULTS_DIR,
    COURSE_EVAL_DIR,
    COURSE_EVAL_RESULTS_DIR,
    VISUALIZATION_OUTPUT_DIR
]:
    Path(directory).mkdir(exist_ok=True, parents=True)

# File Configuration
USER_DATA_FILE = os.environ.get('AI_THESIS_USER_DATA', str(Path(DATA_DIR) / 'users.json'))
IDEA_DATA_FILE = os.environ.get('AI_THESIS_IDEA_DATA', str(Path(DATA_DIR) / 'ideas.json'))
STEP_DATA_FILE = os.environ.get('AI_THESIS_STEP_DATA', str(Path(DATA_DIR) / 'steps.json'))
CATEGORIZED_IDEA_FILE = os.environ.get('AI_THESIS_CATEGORIZED_IDEA_DATA', str(Path(DATA_DIR) / 'categorized_ideas_latest.json'))

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_THESIS_KEY', '')
DEFAULT_MODEL = os.environ.get('AI_THESIS_MODEL', 'gpt-4o')

# Available OpenAI models
OPENAI_MODELS = [
    'gpt-4o',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo'
]

# Analysis Configuration
DEFAULT_BATCH_SIZE = int(os.environ.get('AI_THESIS_BATCH_SIZE', '15'))
DEFAULT_MAX_WORKERS = int(os.environ.get('AI_THESIS_MAX_WORKERS', '2'))

# Idea categories for categorization
IDEA_CATEGORIES = [
    "Administrative Services",
    "Agriculture and Farming",
    "Angel Investing",
    "Apps",
    "Artificial Intelligence",
    "Arts",
    "Biotechnology",
    "Climate Tech",
    "Clothing and Apparel",
    "Commerce and Shopping",
    "Community and Lifestyle",
    "Construction",
    "Consumer Electronics",
    "Consumer Goods",
    "Content and Publishing",
    "Corporate Services",
    "Data Analytics",
    "Design",
    "Education",
    "Energy",
    "Entertainment",
    "Events",
    "Financial Services",
    "Food and Beverage",
    "Gaming",
    "Government and Military",
    "Hardware",
    "Health Care",
    "Information Technology",
    "Internet Services",
    "Lending and Investments",
    "Manufacturing",
    "Media and Entertainment",
    "Mobile",
    "Music and Audio",
    "Natural Resources",
    "Navigation and Mapping",
    "Payments",
    "Platforms",
    "Privacy and Security",
    "Private Equity",
    "Professional Services",
    "Public Admin and Safety",
    "Real Estate",
    "Retail",
    "Sales and Marketing",
    "Science and Engineering",
    "Social and Non-Profit",
    "Software",
    "Sports",
    "Sustainability",
    "Transportation",
    "Travel and Tourism",
    "Venture Capital"
]

# Logging Configuration
LOG_LEVEL = os.environ.get('AI_THESIS_LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Schema configurations
COURSE_EVAL_SCHEMA = os.environ.get('AI_THESIS_COURSE_EVAL_SCHEMA', str(Path(SCHEMA_DIR) / 'course_evaluation_schema.json'))
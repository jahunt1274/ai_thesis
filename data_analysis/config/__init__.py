"""
Configuration package for AI thesis analysis.
"""

from config.settings import (
    # Path configurations
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_DIR,
    LOG_DIR,
    ANALYSIS_RESULTS_DIR,
    USAGE_RESULTS_DIR,
    COMBINED_RESULTS_DIR,
    VISUALIZATION_OUTPUT_DIR,
    COURSE_EVAL_DIR,
    RELATIONSHIP_DIR,
    DE_TEAMS_DIR,
    # File configurations
    USER_DATA_FILE,
    IDEA_DATA_FILE,
    STEP_DATA_FILE,
    CATEGORIZED_IDEA_FILE,
    # OpenAI configurations
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    OPENAI_MODELS,
    # Analysis configurations
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_WORKERS,
    IDEA_CATEGORIES,
    # Schema configurations
    COURSE_EVAL_SCHEMA,
    # Logging configurations
    LOG_LEVEL,
    LOG_FORMAT,
)

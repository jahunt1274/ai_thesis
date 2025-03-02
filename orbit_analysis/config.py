from pathlib import Path
import sys

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to Python path automatically
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Define paths relative to project root
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'
LOG_DIR = PROJECT_ROOT / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
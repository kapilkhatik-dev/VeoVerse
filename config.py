"""
Configuration and default values for Veo video generation.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Version Information
__version__ = "1.0.0"

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    # Don't raise immediately - allow import but fail on actual use

# Default Generation Parameters
DEFAULT_MODEL = "veo-3.1-generate-preview"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "720p"
DEFAULT_DURATION_SECONDS = 8
DEFAULT_NUMBER_OF_VIDEOS = 1

# Supported Values
SUPPORTED_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.1-fast-generate-preview",
    "veo-3.0-generate-001",
    "veo-3.0-fast-generate-001",
    "veo-2.0-generate-001"
]

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16"]
SUPPORTED_RESOLUTIONS = ["720p", "1080p"]
SUPPORTED_DURATIONS = [4, 6, 8]

# Output Configuration
OUTPUT_DIR = Path("output")
try:
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    logger.info(f"Output directory configured: {OUTPUT_DIR.absolute()}")
except Exception as e:
    logger.error(f"Failed to create output directory: {e}")
    raise RuntimeError(f"Cannot create output directory: {e}")

# Polling Configuration
POLL_INTERVAL_SECONDS = 10
MAX_POLL_ATTEMPTS = 180  # 30 minutes max (180 * 10 seconds)

# Video Extension Configuration
EXTENSION_DURATION = 7  # Veo extends by 7 seconds
MAX_EXTENSIONS = 20  # Maximum 20 extensions allowed
MAX_INPUT_VIDEO_LENGTH = 141  # Max input video length in seconds

# File Naming
VIDEO_FILENAME_TEMPLATE = "{timestamp}_{model}_{hash}.mp4"

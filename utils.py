"""
Utility functions for Veo video generation.
"""
import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from google import genai
except ImportError as e:
    logging.error("Failed to import google.genai. Please install: pip install google-genai")
    raise ImportError("google-genai package is required. Install with: pip install google-genai") from e

from config import POLL_INTERVAL_SECONDS, MAX_POLL_ATTEMPTS, OUTPUT_DIR, VIDEO_FILENAME_TEMPLATE

logger = logging.getLogger(__name__)


def generate_filename(prompt: str, model: str, extension: str = "mp4") -> str:
    """
    Generate a consistent and meaningful filename for a video.
    
    Args:
        prompt: The prompt used to generate the video
        model: The model used
        extension: File extension (default: mp4)
    
    Returns:
        Generated filename
    
    Raises:
        ValueError: If prompt or model is empty
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    if not model or not isinstance(model, str):
        raise ValueError("Model must be a non-empty string")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a short hash of the prompt for uniqueness
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]
        
        # Clean model name (remove prefixes and suffixes)
        model_clean = model.replace("veo-", "").replace("-generate", "").replace("-preview", "").replace(".", "_")
        
        # Sanitize extension
        extension = extension.lstrip('.')
        
        filename = f"{timestamp}_{model_clean}_{prompt_hash}.{extension}"
        logger.debug(f"Generated filename: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to generate filename: {e}")
        raise ValueError(f"Cannot generate filename: {e}") from e


def get_output_path(filename: str) -> Path:
    """
    Get full output path for a video file.
    
    Args:
        filename: The filename
    
    Returns:
        Full path to the output file
    
    Raises:
        ValueError: If filename is invalid
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")
    
    # Sanitize filename to prevent directory traversal
    filename = Path(filename).name
    
    output_path = OUTPUT_DIR / filename
    logger.debug(f"Output path: {output_path}")
    return output_path


def poll_operation(client: genai.Client, operation) -> any:
    """
    Poll a long-running operation until completion.
    
    Args:
        client: The GenAI client
        operation: The operation object to poll
    
    Returns:
        The completed operation
    
    Raises:
        TimeoutError: If polling exceeds maximum attempts
        RuntimeError: If the operation fails
        ValueError: If client or operation is invalid
    """
    if not client:
        raise ValueError("Client cannot be None")
    
    if not operation:
        raise ValueError("Operation cannot be None")
    
    attempts = 0
    
    try:
        while not operation.done:
            if attempts >= MAX_POLL_ATTEMPTS:
                logger.error(f"Polling timed out after {attempts} attempts")
                raise TimeoutError(
                    f"Video generation timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS} seconds"
                )
            
            logger.info(f"Waiting for video generation... (attempt {attempts + 1}/{MAX_POLL_ATTEMPTS})")
            
            time.sleep(POLL_INTERVAL_SECONDS)
            
            try:
                operation = client.operations.get(operation)
            except Exception as e:
                logger.error(f"Failed to get operation status: {e}")
                raise RuntimeError(f"Failed to poll operation: {e}") from e
            
            attempts += 1
        
        # Check for errors
        if hasattr(operation, 'error') and operation.error:
            error_msg = str(operation.error)
            logger.error(f"Video generation failed: {error_msg}")
            raise RuntimeError(f"Video generation failed: {error_msg}")
        
        logger.info("Video generation completed successfully")
        return operation
        
    except TimeoutError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during polling: {e}")
        raise RuntimeError(f"Operation polling failed: {e}") from e


def download_video(client: genai.Client, video_object, output_path: Path) -> Path:
    """
    Download a generated video to a file.
    
    Args:
        client: The GenAI client
        video_object: The video object from the API response
        output_path: Path where to save the video
    
    Returns:
        Path to the downloaded video file
    
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If download fails
    """
    if not client:
        raise ValueError("Client cannot be None")
    
    if not video_object:
        raise ValueError("Video object cannot be None")
    
    if not output_path:
        raise ValueError("Output path cannot be None")
    
    try:
        logger.info(f"Downloading video to {output_path}...")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        client.files.download(file=video_object)
        video_object.save(str(output_path))
        
        # Verify file was created
        if not output_path.exists():
            raise RuntimeError("Video file was not created")
        
        logger.info(f"Video saved successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise RuntimeError(f"Video download failed: {e}") from e


def validate_parameters(
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    model: Optional[str] = None
) -> None:
    """
    Validate generation parameters.
    
    Args:
        aspect_ratio: Video aspect ratio
        resolution: Video resolution
        duration_seconds: Video duration
        model: Model name
    
    Raises:
        ValueError: If any parameter is invalid
    """
    from config import (
        SUPPORTED_ASPECT_RATIOS, 
        SUPPORTED_RESOLUTIONS, 
        SUPPORTED_DURATIONS,
        SUPPORTED_MODELS
    )
    
    if aspect_ratio and aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        raise ValueError(f"Invalid aspect_ratio. Must be one of: {SUPPORTED_ASPECT_RATIOS}")
    
    if resolution and resolution not in SUPPORTED_RESOLUTIONS:
        raise ValueError(f"Invalid resolution. Must be one of: {SUPPORTED_RESOLUTIONS}")
    
    if duration_seconds and duration_seconds not in SUPPORTED_DURATIONS:
        raise ValueError(f"Invalid duration_seconds. Must be one of: {SUPPORTED_DURATIONS}")
    
    if model and model not in SUPPORTED_MODELS:
        print(f"Warning: Model '{model}' is not in the known list of supported models.")
        print(f"Supported models: {SUPPORTED_MODELS}")
    
    # Additional validation rules from documentation
    if resolution == "1080p" and duration_seconds and duration_seconds != 8:
        raise ValueError("1080p resolution only supports 8 second duration")
    
    if resolution == "1080p" and aspect_ratio == "9:16":
        print("Warning: 1080p with 9:16 aspect ratio may have limited support")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "10.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_video_info(video_path: Path) -> None:
    """
    Print information about a generated video.
    
    Args:
        video_path: Path to the video file
    """
    try:
        if video_path and video_path.exists():
            size = video_path.stat().st_size
            created = datetime.fromtimestamp(video_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"Video created: {video_path.name}")
            logger.info(f"  Size: {format_file_size(size)}")
            logger.info(f"  Path: {video_path}")
            logger.info(f"  Created: {created}")
        else:
            logger.warning(f"Video file not found: {video_path}")
    except Exception as e:
        logger.error(f"Error displaying video info: {e}")
